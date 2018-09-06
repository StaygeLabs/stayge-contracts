from iconservice import *
from .irc2 import IRC2


class STG(IRC2):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(
        self,
        name: str,
        symbol: str,
        initialSupply: int,
        decimals: int
    ) -> None:
        super().on_install(name, symbol, initialSupply, decimals)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        print(f'Hello, world!')
        return "Hello"
