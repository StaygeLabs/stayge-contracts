from iconservice import *
from .irc2 import IRC2

TAG = 'ACT'

class ACT(IRC2):

    _ALLOWED = 'allowed'
    _PAUSED = 'paused'
    _BLACKLIST = 'blacklist'
    _WHITELIST = 'whitelist'
    EOA_ZERO = Address.from_string('hx' + '0' * 40)

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
        self._when_not_paused(self.msg.sender, _to)
        self._only_positive(_value)

        super().transfer(_to, _value, _data)

    @external(readonly=True)
    def allowance(self, _owner: Address, _spender: Address) -> int:
        return self._allowed[_owner][_spender]

    @external
    def approve(self, _spender: Address, _value: int):
        self._when_not_paused(self.msg.sender, _spender)
        self._only_nonnegative(_value)

        self._allowed[self.msg.sender][_spender] = _value
        self.Approval(self.msg.sender, _spender, _value)

    @external
    def inc_allowance(self, _spender: Address, _value: int):
        self._when_not_paused(self.msg.sender, _spender)
        self._only_positive(_value)

        self._allowed[self.msg.sender][_spender] = self._allowed[self.msg.sender][_spender] + _value

        self.Approval(self.msg.sender, _spender, self._allowed[self.msg.sender][_spender])

    @external
    def dec_allowance(self, _spender: Address, _value: int):
        self._when_not_paused(self.msg.sender, _spender)
        self._only_positive(_value)

        if self._allowed[self.msg.sender][_spender] < _value:
            self.revert("The allowance can be negative")

        self._allowed[self.msg.sender][_spender] = self._allowed[self.msg.sender][_spender] - _value

        self.Approval(self.msg.sender, _spender, self._allowed[self.msg.sender][_spender])

    @external
    def transfer_from(self, _from: Address, _to: Address, _value: int):
        self._when_not_paused(_from, _to)
        self._when_allowed(_from, _value)
        self._only_positive(_value)

        self._allowed[_from][self.msg.sender] = self._allowed[_from][self.msg.sender] - _value

        self._transfer(_from, _to, _value, b'')

    @external
    def mint(self, _to: Address, _amount: int):
        self._only_owner()
        self._only_positive(_amount)

        self._total_supply.set(self._total_supply.get() + _amount)
        self._balances[_to] = self._balances[_to] + _amount
        self.Transfer(self.EOA_ZERO, _to, _amount, b'Minted')

    @external
    def burn(self, _amount: int):
        self._only_positive(_amount)
        self._has_enough_balance(self.msg.sender, _amount)

        self._total_supply.set(self._total_supply.get() - _amount)
        self._balances[self.msg.sender] = self._balances[self.msg.sender] - _amount
        self.Transfer(self.msg.sender, self.EOA_ZERO, _amount, b'Burned')

    @external
    def pause(self):
        self._only_owner()

        self._paused.set(1)
        self.Paused()

    @external
    def unpause(self):
        self._only_owner()

        self._paused.set(0)
        self.Unpaused()

    @external(readonly=True)
    def paused(self) -> int:
        return self._paused.get()

    @external
    def set_blacklist(self, _account: Address, _value: int):
        self._only_owner()

        self._blacklist[_account] = _value
        self.Blacklist(_account, _value)

    @external
    def set_whitelist(self, _account: Address, _value: int):
        self._only_owner()

        self._whitelist[_account] = _value
        self.Whitelist(_account, _value)

    def _only_positive(self, _value: int):
        if _value <= 0:
            self.revert("Only the positive value allowed")

    def _only_nonnegative(self, _value: int):
        if _value < 0:
            self.revert("Only the nonnegative value allowed")

    def _has_enough_balance(self, _account: Address, _amount: int):
        if _amount > self._balances[_account]:
            self.revert("Out of balance")

    def _only_owner(self):
        if self.owner != self.msg.sender:
            self.revert("Only the owner is allowed")

    def _when_allowed(self, _from: Address, _value: int):
        if _value > self._allowed[_from][self.msg.sender]:
            self.revert("_value is more than allowed")

    def _when_not_paused(self, _from: Address, _to: Address):
        if self._paused.get() == 1 and (self._whitelist[_from] == 0 or self._whitelist[_to] == 0):
            self.revert("Paused")

        if self._paused.get() == 0 and (self._blacklist[_from] == 1 or self._blacklist[_to] == 1):
            self.revert("Paused")
