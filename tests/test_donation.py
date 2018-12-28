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

def call_score(_score_address, _from, _method, _params):
    call = CallBuilder()\
        .from_(_from)\
        .to(_score_address)\
        .method(_method)\
        .params(_params)\
        .build()

    result = TestACT.icon_service.call(call)
    return result

def balance_of(_score_address, _from, _owner):
    result = call_score(_score_address, _from, 'balanceOf', {"_owner":_owner})
    return int(result, 16)/10**18

def total_supply(_score_address, _from):
    result = call_score(_score_address, _from, 'totalSupply', {})
    return int(int(result, 16)/10**18)


def call_transaction(_score_address, _fromWallet, _method, _params):
    transaction = CallTransactionBuilder()\
        .from_(_fromWallet.get_address())\
        .to(_score_address)\
        .step_limit(1000000000)\
        .nid(3)\
        .nonce(100)\
        .method(_method)\
        .params(_params)\
        .build()

    signed_transaction = SignedTransaction(transaction, _fromWallet)
    txhash = TestACT.icon_service.send_transaction(signed_transaction)

    #print('txhash = [{}] {}'.format(type(txhash), txhash))
    time.sleep(5)

    txresult = TestACT.icon_service.get_transaction_result(txhash)
    #print('txresult = [{}] {}'.format(type(txresult), txresult))

    return txresult


class TestACT(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        icon_endpoint = os.environ['ICON_ENDPOINT']

        if icon_endpoint == 'testnet':
            cls.icon_service = IconService(HTTPProvider('https://bicon.net.solidwallet.io/api/v3'))
            cls.donation_address = 'cxf748d371e3de681a91edebb0959acfbe6b5f3735'
            cls.act_kard_score_address = 'cx3d85fc30097cb8b18eb52de927b444833c690705'
            cls.act_ace_score_address = 'cxdccbc7ee2d5581e62c8ba300219a5e8d05b58215'
        else:
            cls.icon_service = IconService(HTTPProvider('http://127.0.0.1:9000/api/v3'))
            cls.donation_address = 'cxc8e860b2e66313c3613aa1e0efabe33938faac02'
            cls.act_kard_score_address = 'cxdfc6f0cd56d80ea61c106a3505898a38910e25da'
            cls.act_ace_score_address = 'cxb149a966dc26c7a30f823224387e14ba661488ae'

        cls.owner_wallet = KeyWallet.load('conf/test_owner.keystore', 'test123!')
        cls.user1_wallet = KeyWallet.load('conf/test_user1.keystore', 'test123!')
        cls.user2_wallet = KeyWallet.load('conf/test_user2.keystore', 'test123!')

    def test_name(self):
        result = call_score(self.donation_address, self.owner_wallet.get_address(), 'name', {})
        print('name = {}'.format(result))
        #self.assertEqual(result, '[LOCAL]2018 STAYGE\'s Donation Project')

    '''
    def test_total_donation_amt(self):
        result = call_score(self.donation_address, self.owner_wallet.get_address(), 'total_donation_amt', {})
        print('total_amt = {}'.format(int(result, 16)))
        self.assertTrue(int(result, 16) >= 0)

    def test_get_user_donation(self):
        result = call_score(self.donation_address, self.owner_wallet.get_address(), 'get_user_donation', {'_addr': self.user1_wallet.get_address()})
        print('user_donation = {}'.format(int(result, 16)))
        self.assertTrue(int(result, 16) >= 0)

    def test_get_community_donation(self):
        result = call_score(self.donation_address, self.owner_wallet.get_address(), 'get_community_donation', {'_addr': self.act_kard_score_address})
        print('community_donation = {}'.format(int(result, 16)))
        self.assertTrue(int(result, 16) >= 0)
    '''

    def test_closed(self):
        result = call_score(self.donation_address, self.owner_wallet.get_address(), 'closed', {})
        print('closed = {}'.format(bool(int(result, 16))))
        #self.assertTrue(int(result, 16) >= 0)

    def test_open(self):
        txresult = call_transaction(\
            self.donation_address,\
            self.owner_wallet,\
            'open_donation',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

'''
    def test_donate(self):
        txresult = call_transaction(\
            self.act_kard_score_address,\
            self.owner_wallet,\
            'mint',\
            {'_to': self.user1_wallet.get_address(), '_amount': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        txresult = call_transaction(\
            self.act_kard_score_address,\
            self.owner_wallet,\
            'mint',\
            {'_to': self.user1_wallet.get_address(), '_amount': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        txresult = call_transaction(\
            self.act_ace_score_address,\
            self.owner_wallet,\
            'mint',\
            {'_to': self.user2_wallet.get_address(), '_amount': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Transfer(Address,Address,int,bytes)')

        txresult = call_transaction(\
            self.donation_address,\
            self.owner_wallet,\
            'open_donation',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        txresult = call_transaction(\
            self.act_kard_score_address,\
            self.user1_wallet,\
            'transfer',\
            {'_to': self.donation_address, '_value': '0x8ac7230489e80000', '_data': 'BlackPink'.encode('utf-8').hex()}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        txresult = call_transaction(\
            self.donation_address,\
            self.owner_wallet,\
            'close_donation',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        txresult = call_transaction(\
            self.act_kard_score_address,\
            self.user1_wallet,\
            'transfer',\
            {'_to': self.donation_address, '_value': '0x8ac7230489e80000'}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        txresult = call_transaction(\
            self.donation_address,\
            self.owner_wallet,\
            'open_donation',\
            {}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))


        txresult = call_transaction(\
            self.act_ace_score_address,\
            self.user2_wallet,\
            'transfer',\
            {'_to': self.donation_address, '_value': '0x8ac7230489e80000', '_data': '에일리'.encode('utf-8').hex()}
        )
        print('txresult = [{}] {}'.format(type(txresult), txresult))

        #self.assertEqual(txresult['eventLogs'][0]['indexed'][0], 'Transfer(Address,Address,int,bytes)')
        #self.assertEqual(txresult['eventLogs'][0]['indexed'][1], self.act_kard_score_address)
'''



if __name__ == '__main__':
    unittest.main()
