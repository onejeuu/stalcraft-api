from . import AppClan, Auction, BaseApi, BaseUrl, Region, UserClan, Rank
from . import schemas


class Client(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        """
        Client for working with the API.

        Args:
            token: Token for authorization
            base_url: Optional parameter, API url
        """

        super().__init__(token, base_url)

    def regions(self):
        """
        Returns list of regions which can be access by api calls.
        """

        method = "regions"
        response = self._request(method)

        return [
            schemas.RegionInfo(
                id=region.get("id"),
                name=region.get("name")
            )
            for region in response
        ]

    def emission(self, region=Region.RU):
        """
        Returns information about current emission, if any, and recorded time of the previous one.

        Args:
            region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/emission"
        response = self._request(method)

        return schemas.Emission(
            current_start=self._format_datetime(response.get("currentStart")),
            previous_start=self._format_datetime(response.get("previousStart")),
            previous_end=self._format_datetime(response.get("previousEnd"))
        )

    def clans(self, offset=0, limit=20, region=Region.RU):
        """
        Returns all clans which are currently registered in the game on specified region.

        Args:
            offset: Amount of clans in list to skip, default 0
            limit: Amount of clans to return, starting from offset, minimum 0, maximum 100, default 20
            region: Stalcraft region, default Region.RU
        """

        self._offset_and_limit(offset, limit)

        method = f"{region.value}/clans"
        params = {"offset": offset, "limit": limit}
        response = self._request(method, params)

        return schemas.Clans(
            total=response.get("totalClans"),
            clans=[
                schemas.ClanInfo(
                    id=clan.get("id"),
                    name=clan.get("name"),
                    tag=clan.get("tag"),
                    level=clan.get("level"),
                    level_points=clan.get("levelPoints"),
                    registration_time=clan.get("registrationTime"),
                    alliance=clan.get("alliance"),
                    description=clan.get("description"),
                    leader=clan.get("leader"),
                    member_count=clan.get("memberCount")
                )
                for clan in response.get("data", [{}])
            ]
        )

    def auction(self, item_id, region=Region.RU):
        """
        Interface for working with auction

        Args:
            item_id: Item ID, for example "y1q9"
            region: Stalcraft region, default Region.RU
        """

        return Auction(self.token, self.base_url, item_id, region)

    def __repr__(self):
        return f"<Client> base_url='{self.base_url}' token='{self.part_of_token}'"


class AppClient(Client):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        super().__init__(token, base_url)

    def clan(self, clan_id: str = "", region=Region.RU):
        """
        Interface for working with clans

        Args:
            clan_id: Clan ID, for example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
            region: Stalcraft region, default Region.RU
        """

        return AppClan(self.token, self.base_url, clan_id, region)

    def __repr__(self):
        return f"<AppClient> base_url='{self.base_url}' token='{self.part_of_token}'"


class UserClient(Client):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        super().__init__(token, base_url)

    def characters(self, region=Region.RU):
        """
        Returns list of characters created by the user by which used access token was provided.

        Args:
            region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/characters"
        response = self._request(method)

        return [
            schemas.Character(
                info=schemas.CharacterInfo(
                    id=character.get("information").get("id"),
                    name=character.get("information").get("name"),
                    creation_time=self._format_datetime(character.get("information").get("creationTime"))
                ),
                clan=schemas.CharacterClan(
                    info=schemas.ClanInfo(
                        id=character.get("clan").get("info").get("id"),
                        name=character.get("clan").get("info").get("name"),
                        tag=character.get("clan").get("info").get("tag"),
                        level=character.get("clan").get("info").get("level"),
                        level_points=character.get("clan").get("info").get("levelPoints"),
                        registration_time=character.get("clan").get("info").get("registrationTime"),
                        alliance=character.get("clan").get("info").get("alliance"),
                        description=character.get("clan").get("info").get("description"),
                        leader=character.get("clan").get("info").get("leader"),
                        member_count=character.get("clan").get("info").get("memberCount")
                    ),
                    member=schemas.ClanMember(
                        name=character.get("clan").get("member").get("name"),
                        rank=Rank[character.get("clan").get("member").get("rank")],
                        join_time=self._format_datetime(character.get("clan").get("member").get("joinTime"))
                    )
                )
            )
            for character in response
        ]

        characters = []

        for character in response:
            info = character.get("information")
            clan = character.get("clan", {})
            clan_info = clan.get("info", {})
            clan_member = clan.get("member", {})

            characters.append(
                schemas.Character(
                    info=schemas.CharacterInfo(
                        id=info.get("id"),
                        name=info.get("name"),
                        creation_time=self._format_datetime(info.get("creationTime"))
                    ),
                    clan=schemas.CharacterClan(
                        info=schemas.ClanInfo(
                            id=clan_info.get("id"),
                            name=clan_info.get("name"),
                            tag=clan_info.get("tag"),
                            level=clan_info.get("level"),
                            level_points=clan_info.get("levelPoints"),
                            registration_time=clan_info.get("registrationTime"),
                            alliance=clan_info.get("alliance"),
                            description=clan_info.get("description"),
                            leader=clan_info.get("leader"),
                            member_count=clan_info.get("memberCount")
                        ),
                        member=schemas.ClanMember(
                            name=clan_member.get("name"),
                            rank=Rank[clan_member.get("rank")],
                            join_time=self._format_datetime(clan_member.get("joinTime"))
                        )
                    )
                )
            )

        return characters


    def friends(self, character: str, region=Region.RU):
        """
        Returns list of character names who are friend with specified character.

        Args:
            character: Character name
            region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/friends/{character}"
        return self._request(method)

    def clan(self, clan_id: str, region=Region.RU):
        """
        Interface for working with clans

        Args:
            clan_id: Clan ID, for example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
            region: Stalcraft region, default Region.RU
        """

        return UserClan(self.token, self.base_url, clan_id, region)

    def __repr__(self):
        return f"<UserClient> base_url='{self.base_url}' token='{self.part_of_token}'"
