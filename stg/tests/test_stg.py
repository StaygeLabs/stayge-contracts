import unittest
import logging
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.builder.transaction_builder import (
    TransactionBuilder,
    DeployTransactionBuilder,
    CallTransactionBuilder,
    MessageTransactionBuilder
)
from iconsdk.signed_transaction import SignedTransaction

class TestSTG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.icon_service = IconService(HTTPProvider('http://localhost:9000/api/v3'))
        cls.owner_wallet = KeyWallet.load('../conf/test_owner.keystore', 'test123!')
        cls.user1_wallet = KeyWallet.load('../conf/test_user1.keystore', 'test123!')
        cls.user2_wallet = KeyWallet.load('../conf/test_user2.keystore', 'test123!')
        cls.stg_score_address = 'cx63eb7813408055717194f2f25aaeb3e837a3858d'

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_name(self):
        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('name')\
                            .build()

        result = self.icon_service.call(call)

        print('name = {}'.format(result))
        self.assertEqual(result, 'STG')

    def test_symbol(self):
        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('symbol')\
                            .build()

        result = self.icon_service.call(call)

        print('symbol = {}'.format(result))
        self.assertEqual(result, 'STG')

    def test_decimals(self):
        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('decimals')\
                            .build()

        result = self.icon_service.call(call)
        decimals = int(result, 16)

        print('decimals = {}'.format(decimals))
        self.assertEqual(decimals, 18)

    def test_totalSupply(self):
        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('totalSupply')\
                            .build()

        result = self.icon_service.call(call)
        totalSupply = int(int(result, 16)/10**18)

        print('totalSupply = {}'.format(totalSupply))
        self.assertEqual(totalSupply, 10000000000)

    def test_balanceOf(self):
        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('balanceOf')\
                            .params({"_owner":self.user1_wallet.get_address()})\
                            .build()

        result = self.icon_service.call(call)
        balance = int(result, 16)/10**18

        print('balance = {}'.format(balance))
        self.assertEqual(balance, 110)

        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('balanceOf')\
                            .params({"_owner":"hx3938461680520062e9fe7e46288d6b74a8682ce5"})\
                            .build()

        result = self.icon_service.call(call)
        balance = int(result, 16)/10**18

        print('balance = {}'.format(balance))
        self.assertEqual(balance, 0)

    def test_transfer(self):

        transaction = CallTransactionBuilder()\
            .from_(self.owner_wallet.get_address())\
            .to(self.stg_score_address)\
            .step_limit(1000000)\
            .nid(3)\
            .nonce(100)\
            .method("transfer")\
            .params({"_to":self.user1_wallet.get_address(), "_value":"0x8ac7230489e80000"})\
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, wallet)

        # Sends the transaction
        txhash = self.icon_service.send_transaction(signed_transaction)

        print('txhash = [{}] {}'.format(type(txhash), txhash))


if __name__ == '__main__':
    unittest.main()
