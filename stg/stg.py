from iconservice import *
from .irc2 import IRC2

TAG = 'STG'

class STG(IRC2):

    _ALLOWED = 'allowed'
    _PAUSED = 'paused'
    _BLACKLIST = 'blacklist'
    _WHITELIST = 'whitelist'

    @eventlog(indexed=3)
    def Approval(self, _owner: Address, _spender: Address, _value: int):
        pass

    @eventlog()
    def Paused(self):
        pass

    @eventlog()
    def Unpaused(self):
        pass

    @eventlog(indexed=2)
    def Blacklist(self, _account: Address, _value: int):
        pass

    @eventlog(indexed=2)
    def Whitelist(self, _account: Address, _value: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._allowed = DictDB(self._ALLOWED, db, value_type=int, depth=2)
        self._paused = VarDB(self._PAUSED, db, value_type=int)
        self._blacklist = DictDB(self._BLACKLIST, db, value_type=int)
        self._whitelist = DictDB(self._WHITELIST, db, value_type=int)

    def on_install(
        self,
        name: str,
        symbol: str,
        initialSupply: int,
        decimals: int
    ) -> None:
        super().on_install(name, symbol, initialSupply, decimals)
        self._paused.set(0)
        self._whitelist[self.msg.sender] = 1

    def on_update(self) -> None:
        super().on_update()

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes=None):
        self._whenNotPaused()

        super().transfer(_to, _value, _data)

    @external(readonly=True)
    def allowance(self, _owner: Address, _spender: Address):
        return self._allowed[_owner][_spender]

    @external
    def approve(self, _spender: Address, _value: int):
        self._whenNotPaused()
        self._whenNotContract(_spender)

        self._allowed[self.msg.sender][_spender] = _value
        self.Approval(self.msg.sender, _spender, _value)

    @external
    def inc_allowance(self, _spender: Address, _value: int):
        self._whenNotPaused()
        self._whenNotContract(_spender)

        self._allowed[self.msg.sender][_spender] = self._allowed[self.msg.sender][_spender] + _value

        self.Approval(self.msg.sender, _spender, self._allowed[self.msg.sender][_spender])

    @external
    def dec_allowance(self, _spender: Address, _value: int):
        self._whenNotPaused()
        self._whenNotContract(_spender)

        self._allowed[self.msg.sender][_spender] = self._allowed[self.msg.sender][_spender] - _value

        self.Approval(self.msg.sender, _spender, self._allowed[self.msg.sender][_spender])

    @external
    def transfer_from(self, _from: Address, _to: Address, _value: int):
        self._whenNotPaused()
        self._whenAllowed(_from, _value)

        self._allowed[_from][self.msg.sender] = self._allowed[_from][self.msg.sender] - _value

        self._tranfer(_from, _to, _value, None)

    @external
    def mint(self, _amount: int):
        self._onlyOwner()
        self._mint(self.msg.sender, _amount)

    @external
    def burn(self, _amount: int):
        self._burn(self.msg.sender, _amount)

    @external
    def pause(self):
        self._onlyOwner()

        self._paused.set(1)
        self.Paused()

    @external
    def unpause(self):
        self._onlyOwner()

        self._paused.set(0)
        self.Unpaused()

    @external(readonly=True)
    def paused(self):
        return self._paused.get()

    @external
    def set_blacklist(self, _account: Address, _value: int):
        self._onlyOwner()

        self._blacklist[_account] = _value
        self.Blacklist(_account, _value)

    @external
    def set_whitelist(self, _account: Address, _value: int):
        self._onlyOwner()

        self._whitelist[_account] = _value
        self.Whitelist(_account, _value)

    def _mint(self, _account: Address, _amount: int):
        self._total_supply.set(self._total_supply.get() + _amount)
        self._balances[_account] = self._balances[_account] + _amount
        self.Transfer(0, _account, _value, None)

    def _burn(self, _account: Address, _amount: int):
        if _amount > self._balances[_account]:
            self.revert("Out of balance")

        self._total_supply.set(self._total_supply.get() - _amount)
        self._balances[_account] = self._balances[_account] - _amount
        self.Transfer(_account, 0, _amount, None)

    def _onlyOwner(self):
        if self.owner != self.msg.sender
            self.revert("Only owner is allowed")

    def _whenNotContract(_spender: Address):
        if _spender == 0:
            self.revert("spender is contract address")

    def _whenAllowed(self, _from: Address, _value: int):
        if _value > self._allowed[_from][self.msg_sender]:
            self.revert("_value is more than allowed")

    def _whenNotPaused(self):
        if self._paused.get() == 1 and self._whitelist[self.msg.sender] == 0:
            self.revert("Paused")

        if self._paused.get() == 0 and self._blacklist[self.msg.sender] == 1:
            self.revert("Paused")
