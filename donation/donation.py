from iconservice import *

TAG = 'DONATION'

class ActToken(InterfaceScore):
    @interface
    def name(self) -> str:
        pass


class Donation(IconScoreBase):

    @eventlog(indexed=3)
    def Donate(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass

    @eventlog
    def DonationOpened(self):
        pass

    @eventlog
    def DonationClosed(self):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._name = VarDB('name', db, value_type=str)
        self._total_donation_amt = VarDB('total_donation_amt', db, value_type=int)
        self._closed = VarDB('closed', db, value_type=bool)

        self._donation_details = DictDB('_donation_details', db, value_type=int, depth=2)
        self._community_donations = DictDB('community_donations', db, value_type=int)
        self._artist_donations = DictDB('artist_donations', db, value_type=int)
        self._communities = ArrayDB('communities', db, value_type=str)
        self._artists = ArrayDB('artists', db, value_type=str)
        self._users = ArrayDB('users', db, value_type=str)
        self._total_users = VarDB('total_users', db, value_type=int)
        self._community_artist = DictDB('community_artist', db, value_type=str)

    def on_install(
        self,
        name: str,
    ) -> None:

        super().on_install()

        self._name.set(name)
        self._closed.set(True)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return self._name.get()

    @external(readonly=True)
    def total_donation_amt(self) -> int:
        return self._total_donation_amt.get()

    @external(readonly=True)
    def total_users(self) -> int:
        return len(self._users)

    @external(readonly=True)
    def total_artists(self) -> int:
        return len(self._artists)

    @external(readonly=True)
    def ranking(self, _page: int) -> list:
        output = []

        for c in self._artists:
            artist = {}
            artist[c] = self._artist_donations[c]
            output.append(artist)

        output.sort(reverse=True, key = lambda a : a[list(a.keys())[0]])

        ranked_output = []

        idx = 1
        for c in output:
            keys = list(c.keys())

            item = {}
            item[f'[{idx}] {keys[0]}'] = str(c[keys[0]])
            ranked_output.append(item)
            idx += 1

        return ranked_output[_page * 10 : _page * 10 + 10]

    @external(readonly=True)
    def artist(self, _artistname: str) -> list:

        output = []

        for c in self._artists:
            if c.lower().find(_artistname.lower()) != -1:
                item = {}
                item['artist_name'] = c
                item['donation_amt'] = str(self._artist_donations[c])
                item['communities'] = self._get_communities_for_artist(c)
                output.append(item)

        return output

    @external(readonly=True)
    def donation_details(self, _userAddr: Address) -> list:

        output = []
        for c in self._communities:
            community_addr = Address.from_string(c)
            if self._donation_details[_userAddr][community_addr] > 0:
                item = {}
                item['artist_name'] = self._community_artist[community_addr]
                act_token = self.create_interface_score(community_addr, ActToken)
                item['community_name'] = act_token.name()
                item['donation_amt'] = str(self._donation_details[_userAddr][community_addr])
                output.append(item)

        return output

    @external(readonly=True)
    def closed(self) -> bool:
        return self._closed.get()

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        self._when_opened()
        self._only_positive(_value)
        self._only_contract(self.msg.sender)

        artistname = _data.decode('utf-8')

        self._donation_details[_from][self.msg.sender] += _value
        self._community_donations[self.msg.sender] += _value
        self._artist_donations[artistname] += _value

        if str(self.msg.sender) not in self._communities:
            self._communities.put(str(self.msg.sender))
            self._community_artist[self.msg.sender] = artistname

        if str(_from) not in self._users:
            self._users.put(str(_from))

        if artistname not in self._artists:
            self._artists.put(artistname)

        self._total_donation_amt.set(self._total_donation_amt.get() + _value)

        self.Donate(_from, self.msg.sender, _value, _data)

    @external
    def open_donation(self):
        self._only_owner()

        self._closed.set(False)
        self.DonationOpened()

    @external
    def close_donation(self):
        self._only_owner()

        self._closed.set(True)
        self.DonationClosed()

    def _only_positive(self, _value: int):
        if _value < 0:
            self.revert("Only the positive value allowed")

    def _when_opened(self):
        if self._closed.get():
            self.revert("Donation closed")

    def _only_owner(self):
        if self.owner != self.msg.sender:
            self.revert("Only the owner is allowed")

    def _only_contract(self, _addr):
        if not _addr.is_contract:
            self.revert("Only contract addresses are allowed")

    def _get_communities_for_artist(self, _artistname):
        output = []
        for c in self._communities:
            community_addr = Address.from_string(c)
            if self._community_artist[community_addr] == _artistname:
                item = {}
                act_token = self.create_interface_score(community_addr, ActToken)
                item['community_name'] = act_token.name()
                item['donation_amt'] = str(self._community_donations[community_addr])
                output.append(item)

        return output

