import unittest
import logging
import time
import os
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

# assertEqual(a, b) : a == b
# assertNotEqual(a, b) : a != b
# assertTrue(x) : bool(x) is True
# assertFalse(x) : bool(x) is False
# assertIs(a, b) : a is b
# assertIsNot(a, b) : a is not b
# assertIsNone(x) : x is None
# assertIsNotNone(x) : x is not None
# assertIn(a, b) : a in b
# assertNotIn(a, b) : a not in b
# assertIsInstance(a, b) : isinstance(a, b)
# assertNotIsInstance(a, b) : not isinstance(a, b)
# assertRaises(exception, callable, *args, **kwds)

class TestSTG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        icon_endpoint = os.environ['ICON_ENDPOINT']

        if icon_endpoint == 'testnet':
            cls.icon_service = IconService(HTTPProvider('https://bicon.net.solidwallet.io/api/v3'))
            cls.stg_score_address = 'cx40ba15981ad7b0d7db0ebbaa01280cf8495cec34'
        else:
            cls.icon_service = IconService(HTTPProvider('http://127.0.0.1:9000/api/v3'))
            cls.stg_score_address = 'cx63eb7813408055717194f2f25aaeb3e837a3858d'

        cls.owner_wallet = KeyWallet.load('conf/test_owner.keystore', 'test123!')
        cls.user1_wallet = KeyWallet.load('conf/test_user1.keystore', 'test123!')
        cls.user2_wallet = KeyWallet.load('conf/test_user2.keystore', 'test123!')

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
        old_balance = int(result, 16)/10**18
        print('old_balance = {}'.format(old_balance))

        transaction = CallTransactionBuilder()\
            .from_(self.owner_wallet.get_address())\
            .to(self.stg_score_address)\
            .step_limit(1000000000)\
            .nid(3)\
            .nonce(100)\
            .method("transfer")\
            .params({"_to":self.user1_wallet.get_address(), "_value":"0x8ac7230489e80000"})\
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.owner_wallet)

        # Sends the transaction
        txhash = self.icon_service.send_transaction(signed_transaction)

        print('txhash = [{}] {}'.format(type(txhash), txhash))

        time.sleep(10)


        call = CallBuilder().from_(self.owner_wallet.get_address())\
                            .to(self.stg_score_address)\
                            .method('balanceOf')\
                            .params({"_owner":self.user1_wallet.get_address()})\
                            .build()
        result = self.icon_service.call(call)
        new_balance = int(result, 16)/10**18
        print('new_balance = {}'.format(new_balance))

        self.assertEqual(new_balance, old_balance + 10)

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
            .step_limit(1000000000)\
            .nid(3)\
            .nonce(100)\
            .method("transfer")\
            .params({"_to":self.user2_wallet.get_address(), "_value":"0x8ac7230489e80000"})\
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.owner_wallet)

        # Sends the transaction
        txhash = self.icon_service.send_transaction(signed_transaction)
        print('txhash = [{}] {}'.format(type(txhash), txhash))

        time.sleep(10)

        txresult = self.icon_service.get_transaction_result(txhash)
        print('txresult = [{}] {}'.format(type(txresult), txresult))


        # not enough balance
        transaction = CallTransactionBuilder()\
            .from_(self.user1_wallet.get_address())\
            .to(self.stg_score_address)\
            .step_limit(1000000000)\
            .nid(3)\
            .nonce(100)\
            .method("transfer")\
            .params({"_to":self.user2_wallet.get_address(), "_value":"0x152d02c7e14af6000000"})\
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.user1_wallet)

        # Sends the transaction
        txhash = self.icon_service.send_transaction(signed_transaction)
        print('txhash = [{}] {}'.format(type(txhash), txhash))

        time.sleep(10)

        txresult = self.icon_service.get_transaction_result(txhash)
        print('txresult = [{}] {}'.format(type(txresult), txresult))


if __name__ == '__main__':
    unittest.main()
