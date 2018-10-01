import unittest
import logging
import time
import os
import json
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

def call_score(_from, _method, _params):
    call = CallBuilder()\
        .from_(_from)\
        .to(TestSTG.stg_score_address)\
        .method(_method)\
        .params(_params)\
        .build()

    result = TestSTG.icon_service.call(call)
    return result

def balance_of(_from, _owner):
    result = call_score(_from, 'balanceOf', {"_owner":_owner})
    return int(result, 16)/10**18

def total_supply(_from):
    result = call_score(_from, 'totalSupply', {})
    return int(int(result, 16)/10**18)


def call_transaction(_fromWallet, _method, _params):
    transaction = CallTransactionBuilder()\
        .from_(_fromWallet.get_address())\
        .to(TestSTG.stg_score_address)\
        .step_limit(1000000000)\
        .nid(3)\
        .nonce(100)\
        .method(_method)\
        .params(_params)\
        .build()

    signed_transaction = SignedTransaction(transaction, _fromWallet)
    txhash = TestSTG.icon_service.send_transaction(signed_transaction)

    #print('txhash = [{}] {}'.format(type(txhash), txhash))
    time.sleep(10)

    txresult = TestSTG.icon_service.get_transaction_result(txhash)
    #print('txresult = [{}] {}'.format(type(txresult), txresult))

    return txresult


class TestSTG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        icon_endpoint = os.environ['ICON_ENDPOINT']

        if icon_endpoint == 'testnet':
            cls.icon_service = IconService(HTTPProvider('https://bicon.net.solidwallet.io/api/v3'))
            cls.stg_score_address = 'cx8ada5f95f337ae332c97f3375e7e4f8209617143'
        else:
            cls.icon_service = IconService(HTTPProvider('http://127.0.0.1:9000/api/v3'))
            cls.stg_score_address = 'cx63eb7813408055717194f2f25aaeb3e837a3858d'

        cls.owner_wallet = KeyWallet.load('conf/test_owner.keystore', 'test123!')
        cls.user1_wallet = KeyWallet.load('conf/test_user1.keystore', 'test123!')
        cls.user2_wallet = KeyWallet.load('conf/test_user2.keystore', 'test123!')

        owner_balance = balance_of(cls.owner_wallet.get_address(), cls.owner_wallet.get_address())
        print('owner_balance = {}'.format(owner_balance))

        user1_balance = balance_of(cls.user1_wallet.get_address(), cls.user1_wallet.get_address())
        print('user1_balance = {}'.format(user1_balance))

        user2_balance = balance_of(cls.user2_wallet.get_address(), cls.user2_wallet.get_address())
        print('user2_balance = {}'.format(user2_balance))

    def test_name(self):
        result = call_score(self.owner_wallet.get_address(), 'name', {})
        print('name = {}'.format(result))
        self.assertEqual(result, 'STG')

    def test_symbol(self):
        result = call_score(self.owner_wallet.get_address(), 'symbol', {})
        print('symbol = {}'.format(result))
        self.assertEqual(result, 'STG')

    def test_decimals(self):
        result = call_score(self.owner_wallet.get_address(), 'decimals', {})
        print('decimals = {}'.format(int(result, 16)))
        self.assertEqual(int(result, 16), 18)

    def test_totalSupply(self):
        self.assertEqual(total_supply(self.owner_wallet.get_address()), 10000000000)

    def test_balanceOf(self):
        old_balance = balance_of(self.owner_wallet.get_address(), self.user1_wallet.get_address())
        #print('old_balance = {}'.format(old_balance))

        txresult = call_transaction(\
            self.owner_wallet,\
            'transfer',\
            {\
                "_to":self.user1_wallet.get_address(),\
                "_value":"0x8ac7230489e80000"\
            }\
        )

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Transfer(Address,Address,int,bytes)')

        new_balance = balance_of(self.owner_wallet.get_address(), self.user1_wallet.get_address())

        #print('new_balance = {}'.format(new_balance))
        self.assertEqual(new_balance, old_balance + 10)

        balance = balance_of(\
            self.owner_wallet.get_address(),\
            'hx3938461680520062e9fe7e46288d6b74a8682ce5'\
        )

        self.assertEqual(balance, 0)

    def test_transfer(self):
        txresult = call_transaction(\
            self.owner_wallet,\
            'transfer',\
            {\
                "_to":self.user2_wallet.get_address(),\
                "_value":"0x8ac7230489e80000"\
            }\
        )

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Transfer(Address,Address,int,bytes)')

        # not enough balance
        txresult = call_transaction(\
            self.user1_wallet,\
            'transfer',\
            {\
                "_to":self.user2_wallet.get_address(),\
                "_value":"0x152d02c7e14af6000000"\
            }\
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

    def test_paused(self):
        result = call_score(self.owner_wallet.get_address(), 'paused', {})
        print(f'paused = {result}')
        self.assertEqual(result, '0x0')

    def test_pause(self):
        txresult = call_transaction(\
            self.owner_wallet,\
            'pause',\
            {}
        )

        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Paused()')

        result = call_score(self.owner_wallet.get_address(), 'paused', {})
        print(f'paused = {result}')
        self.assertEqual(result, '0x1')

        txresult = call_transaction(\
            self.owner_wallet,\
            'unpause',\
            {}
        )

        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Unpaused()')

        result = call_score(self.owner_wallet.get_address(), 'paused', {})
        print(f'paused = {result}')
        self.assertEqual(result, '0x0')


        txresult = call_transaction(\
            self.user1_wallet,\
            'pause',\
            {}
        )

        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['failure']['message'], 'Only the owner is allowed')

    def test_unpause(self):
        txresult = call_transaction(\
            self.owner_wallet,\
            'pause',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Paused()')

        txresult = call_transaction(\
            self.user1_wallet,\
            'unpause',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['failure']['message'], 'Only the owner is allowed')


        result = call_score(self.owner_wallet.get_address(), 'paused', {})
        print(f'paused = {result}')
        self.assertEqual(result, '0x1')


        txresult = call_transaction(\
            self.owner_wallet,\
            'unpause',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Unpaused()')

        result = call_score(self.owner_wallet.get_address(), 'paused', {})
        print(f'paused = {result}')
        self.assertEqual(result, '0x0')

    def test_mint(self):
        old_totalSupply = total_supply(self.owner_wallet.get_address())
        print('old_totalSupply = {}'.format(old_totalSupply))

        txresult = call_transaction(\
            self.owner_wallet,\
            'mint',\
            {'_amount': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Transfer(Address,Address,int,bytes)')
        self.assertEqual(txresult['eventLogs'][0]['indexed'][1], self.stg_score_address)


        new_totalSupply = total_supply(self.owner_wallet.get_address())
        print('new_totalSupply = {}'.format(new_totalSupply))
        self.assertEqual(new_totalSupply - old_totalSupply, 10)


        txresult = call_transaction(\
            self.user1_wallet,\
            'mint',\
            {'_amount': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['failure']['message'], 'Only the owner is allowed')

    def test_burn(self):
        old_totalSupply = total_supply(self.owner_wallet.get_address())
        print('old_totalSupply = {}'.format(old_totalSupply))

        txresult = call_transaction(\
            self.owner_wallet,\
            'burn',\
            {'_amount': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Transfer(Address,Address,int,bytes)')
        self.assertEqual(txresult['eventLogs'][0]['indexed'][2], self.stg_score_address)

        new_totalSupply = total_supply(self.owner_wallet.get_address())
        print('new_totalSupply = {}'.format(new_totalSupply))
        self.assertEqual(int(old_totalSupply - new_totalSupply), 10)

if __name__ == '__main__':
    unittest.main()
