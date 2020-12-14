#!/usr/bin/env python3
# Copyright (c) 2016-2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the Alerts changeover logic."""
import os
import shutil

from decimal import Decimal
from test_framework.test_framework import BitcoinTestFramework
from test_framework.authproxy import JSONRPCException
from test_framework.util import get_datadir_path, hex_str_to_bytes
from test_framework.address import key_to_p2pkh

def introduce_and_reset_blockchain(func):
    def func_wrapper(self):
        self.reset_blockchain()
        self.log.info(func.__name__.replace('_',' '))
        return func(self)
    return func_wrapper

class AlertsInstantTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 3
        self.extra_args = [
            [
                "-reindex",
                "-txindex",
            ],
            [
                "-reindex",
                "-txindex",
            ],
            [
                "-reindex",
                "-txindex",
            ],
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def find_address(self, listreceivedbyaddress, address):
        for addr in listreceivedbyaddress:
            if addr['address'] == address: return addr

    def find_vout_n(self, rawtransaction, amount):
        for vout in rawtransaction['vout']:
            if vout['value'] == amount: return vout['n']

    def sum_vouts_value(self, rawtransaction):
        return sum(vout['value'] for vout in rawtransaction['vout'])

    def reset_blockchain(self):
        self.stop_nodes(wait=1)
        for i in range(self.num_nodes):
            datadir = get_datadir_path(self.options.tmpdir, i)
            if os.path.exists(datadir):
                shutil.rmtree(datadir)
                os.mkdir(datadir)

        self.nodes = []
        self.setup_chain()
        self.start_nodes(extra_args=self.extra_args)
        self.setup_network()
        self.sync_all()

    def reset_node(self, i):
        self.stop_node(i, wait=1)
        datadir = get_datadir_path(self.options.tmpdir, i)
        if os.path.exists(datadir):
            shutil.rmtree(datadir)
            os.mkdir(datadir)

        self.start_node(i, extra_args=self.extra_args)

    def run_test(self):
        self.alert_recovery_pubkey = "02ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c"
        self.alert_recovery_privkey = "cRfYLWua6WcpGbxuv5rJgA2eDESWxqgzmQjKQuqDFMfgbnEpqhrP"

        self.alert_instant_pubkey = "0263451a52f3d3ae6918969e1c5ce934743185578481ef8130336ad1726ba61ddb"
        self.alert_instant_privkey = "cN1XR72dusJgxpkT2AwENtTviskB96iB2Q6FTvAxqi24fT9DQZiR"

        self.COINBASE_MATURITY = 100
        self.COINBASE_AMOUNT = Decimal(175)

        self.test_alert_tx_generate_transactions_and_filter_them_by_label()

        self.test_alert_tx_generate_transactions_with_invalid_address_type()

        self.test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_wallet_comments()

        self.test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_replaceable_yes()

        self.test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_conf_target_range_only()

        self.test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_estimate_mode_check_only()

        self.test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_replaceable_no()

        self.reset_blockchain()
        self.log.info("Test alert tx change is by default sent back to the sender")
        self.test_alert_tx_change_is_by_default_sent_back_to_the_sender()

        self.reset_blockchain()
        self.log.info("Test instant tx change is by default sent back to the sender")
        self.test_instant_tx_change_is_by_default_sent_back_to_the_sender()

        self.reset_blockchain()
        self.log.info("Test sendinstanttoaddress selects coins on instant addresses only")
        self.test_sendinstanttoaddress_selects_coins_on_instant_addresses_only()

        self.test_sendinstanttoaddress_selects_coins_on_instant_addresses_only_with_label()

        self.test_sendinstanttoaddress_selects_coins_on_instant_addresses_only_differnet_addr_type()

        self.reset_blockchain()
        self.log.info("Test sendinstanttoaddress with multiple instant addresses")
        self.test_sendinstanttoaddress_with_multiple_instant_addresses()

        self.reset_blockchain()
        self.log.info("Test sendinstanttoaddress fails when no coins available on instant addresses")
        self.test_sendinstanttoaddress_fails_when_no_coins_available_on_instant_addresses()

        self.reset_blockchain()
        self.log.info("Test sendalerttoaddress selects coins on instant addresses only")
        self.test_sendalerttoaddress_selects_coins_on_instant_addresses_only()

        self.reset_blockchain()
        self.log.info("Test sendalerttoaddress selects coins on instant and alert addresses only")
        self.test_sendalerttoaddress_selects_coins_on_instant_and_alert_addresses_only()

        self.reset_blockchain()
        self.log.info("Test sendtoaddress fails when no coins available on regular addresses")
        self.test_sendtoaddress_fails_when_no_coins_available_on_regular_addresses()

        self.reset_blockchain()
        self.log.info("Test sendtoaddress selects coins on regular addresses only")
        self.test_sendtoaddress_selects_coins_on_regular_addresses_only()

        self.reset_blockchain()
        self.log.info("Test signalerttransaction when both instant and recovery keys imported")
        self.test_signalerttransaction_when_both_recovery_and_instant_keys_imported()

        self.reset_blockchain()
        self.log.info("Test standard signalerttransaction flow")
        self.test_signalerttransaction()

        self.reset_blockchain()
        self.log.info("Test standard signinstanttransaction flow")
        self.test_signinstanttransaction()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when instant key imported")
        self.test_signinstanttransaction_when_instant_key_imported()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when both instant and recovery keys imported")
        self.test_signinstanttransaction_when_both_instant_and_recovery_keys_imported()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction is incomplete and rejected when missing key")
        self.test_signinstanttransaction_is_incomplete_and_rejected_when_missing_key()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when recovery key imported")
        self.test_signinstanttransaction_when_recovery_key_imported()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when all keys given")
        self.test_signinstanttransaction_when_all_keys_given()

        self.reset_blockchain()
        self.log.info("Test recovery tx is incomplete and rejected when missing recovery key")
        self.test_recovery_tx_is_incomplete_and_rejected_when_missing_recovery_key()

        self.reset_blockchain()
        self.log.info("Test recovery tx is incomplete and rejected when missing instant key")
        self.test_recovery_tx_is_incomplete_and_rejected_when_missing_instant_key()

        self.reset_blockchain()
        self.log.info("Test recovery tx when all keys imported")
        self.test_recovery_tx_when_all_keys_imported()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when missing both instant and recovery keys")
        self.test_recovery_tx_is_rejected_when_missing_both_instant_and_recovery_keys()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when only recovery key imported")
        self.test_recovery_tx_is_rejected_when_only_recovery_key_imported()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when only instant key imported")
        self.test_recovery_tx_is_rejected_when_only_instant_key_imported()

        self.reset_blockchain()
        self.log.info("Test recovery tx when instant key imported and recovery key given")
        self.test_recovery_tx_when_instant_key_imported_and_recovery_key_given()

        self.reset_blockchain()
        self.log.info("Test recovery tx when recovery key imported and instant key given")
        self.test_recovery_tx_when_recovery_key_imported_and_instant_key_given()

        self.test_recovery_tx_when_recovery_key_imported_and_instant_key_given_replaceable_no()

        self.test_recovery_tx_when_recovery_key_imported_and_instant_key_given_locktime()

        self.test_recovery_tx_when_recovery_key_imported_and_instant_key_given_sighashtype()

        self.reset_blockchain()
        self.log.info("Test recovery tx when both instant and recovery keys given")
        self.test_recovery_tx_when_both_instant_and_recovery_keys_given()

        self.reset_blockchain()
        self.log.info("Test dumpwallet / importwallet with instant address")
        self.test_dumpwallet()

        self.reset_blockchain()
        self.log.info("Test atx from imported instant address")
        self.test_atx_from_imported_instant_address()

        self.reset_blockchain()
        self.log.info("Test getaddressinfo on instant address")
        self.test_getaddressinfo_on_instant_address()

        self.reset_blockchain()
        self.log.info("Test getaddressinfo on imported instant address")
        self.test_getaddressinfo_on_imported_instant_address()

        self.reset_blockchain()
        self.log.info("Test add watch-only instant address")
        self.test_add_watchonly_instant_address()

        self.reset_blockchain()
        self.log.info("Test import instant address privkey")
        self.test_import_instant_address_privkey()

        self.reset_blockchain()
        self.log.info("Test signrawtransactionwithwallet should reject alert transaction")
        self.test_signrawtransactionwithwallet_should_reject_alert_transaction()

        self.reset_blockchain()
        self.log.info("Test signrawtransactionwithwallet should reject instant transaction")
        self.test_signrawtransactionwithwallet_should_reject_instant_transaction()

        self.reset_blockchain()
        self.log.info("Test sign atx with recovery key")
        self.test_sign_atx_with_recovery_key()

        self.reset_blockchain()
        self.log.info("Test tx from normal address to instant address")
        self.test_tx_from_normal_addr_to_instant_addr()

        self.reset_blockchain()
        self.log.info("Test atx from instant address to normal address")
        self.test_atx_from_instant_addr_to_normal_addr()

        self.test_atx_with_multiple_inputs_from_alert_addr_to_normal_addr_invalid_address_type()

        self.reset_blockchain()
        self.log.info("Test atx with multiple inputs from alert address to normal address")
        self.test_atx_with_multiple_inputs_from_alert_addr_to_normal_addr()

        self.reset_blockchain()
        self.log.info("Test atx becomes tx after 144 blocks")
        self.test_atx_becomes_tx()

        self.reset_blockchain()
        self.log.info("Test atx fee is paid to original miner")
        self.test_atx_fee_is_paid_to_original_miner()

        self.reset_blockchain()
        self.log.info("Test atx with inputs of different source")
        self.test_atx_with_inputs_of_different_source()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by wallet when contains non-alert type inputs")
        self.test_atx_is_rejected_by_wallet_when_contains_non_alert_inputs()

        self.reset_blockchain()
        self.log.info("Test atx signed by signrawtransactionwithkey with inputs of different source")
        self.test_atx_signed_by_signrawtransactionwithkey_with_inputs_of_different_source()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by signrawtransactionwithkey when contains non-alert type inputs")
        self.test_atx_is_rejected_by_signrawtransactionwithkey_when_contains_non_alert_inputs()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by node when inputs are spent")
        self.test_atx_is_rejected_by_node_when_inputs_are_spent()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by node when inputs are spent by parallel atx")
        self.test_atx_is_rejected_by_node_when_inputs_are_spent_by_parallel_atx()

        self.reset_blockchain()
        self.log.info("Test standard recovery transaction flow")
        self.test_recovery_tx_flow()

        self.reset_blockchain()
        self.log.info("Test recovery transaction flow for two alerts")
        self.test_recovery_tx_flow_for_two_alerts()

        self.reset_blockchain()
        self.log.info("Test recovery transaction when alert is confirmed at the same height")
        self.test_recovery_tx_when_alert_is_confirmed_at_the_same_height()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when alert inputs are missing")
        self.test_recovery_tx_is_rejected_when_alert_inputs_are_missing()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when inputs are non alert")
        self.test_recovery_tx_is_rejected_when_inputs_are_non_alert()

        self.reset_blockchain()
        self.log.info("Test getrawtransaction returns information about unconfirmed atx")
        self.test_getrawtransaction_returns_information_about_unconfirmed_atx()

        self.test_get_getalertbalance_dummy()

        self.test_get_getalertbalance_miniconf()

        self.test_get_getalertbalance_include_watchonly() #@TODO not implemented

    @introduce_and_reset_blockchain
    def test_alert_tx_generate_transactions_and_filter_them_by_label(self):
        label = 'This is my super awesome label'
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey, label)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        listaddr = self.nodes[1].listaddressgroupings()
        transactions = self.nodes[1].listtransactions(label)

        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert alert_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]
        assert listaddr[0][0][2] == label
        assert transactions != None
        for transaction in transactions:
            assert transaction['label'] == label

    @introduce_and_reset_blockchain
    def test_alert_tx_generate_transactions_with_invalid_address_type(self):
        label = 'This is my super awesome label'
        texts = { 'random text': -5 , 'p2sh-segwit': -1, 'bech32': -1 }
        cnt = len(texts)
        for text in texts:
            try:
                self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey, label, text)
            except JSONRPCException as e:
                assert 'Unknown address type' in e.error['message']
                assert text in e.error['message']
                assert e.error['code'] == texts[text]
                cnt -= 1

        assert cnt == 2

    @introduce_and_reset_blockchain
    def test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_wallet_comments(self):
        comment = "my comment"
        to = "my comment to"
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount, comment, to)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        cnt = 3
        transactions = self.nodes[1].listtransactions()
        for transaction in transactions:
            if transaction['category'] in ['receive', 'send']:
                assert  transaction['comment'] == comment
                assert transaction['to'] == to
                cnt -= 1
        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert alert_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]
        assert cnt == 0

    @introduce_and_reset_blockchain
    def test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_replaceable_no(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount, '', '', False, False)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        cnt = 10
        transactions = self.nodes[1].listtransactions()
        for transaction in transactions:
            if transaction['bip125-replaceable'] == 'no':
                cnt -= 1
        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert alert_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]
        assert cnt == 0

    @introduce_and_reset_blockchain
    def test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_replaceable_yes(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount, '', '', False, True)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        cnt = 3
        transactions = self.nodes[1].listtransactions()
        for transaction in transactions:
            if transaction['bip125-replaceable'] == 'yes':
                cnt -= 1
        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert alert_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]
        assert cnt == 0

    @introduce_and_reset_blockchain
    def test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_conf_target_range_only(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        conf_targets = [0, 1, 10, 1009, "lubie placki", 1008]
        # create atx
        amount = 10
        cnt = 3
        for conf_target in conf_targets:
            try:
                atxid = self.nodes[1].sendalerttoaddress(addr0, amount, '', '', False, False, conf_target)
            except JSONRPCException as e:
                cnt -= 1

        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert alert_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]
        assert cnt == 0

    @introduce_and_reset_blockchain
    def test_alert_tx_change_is_by_default_sent_back_to_the_sender_with_tx_estimate_mode_check_only(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])
        estimate_mode = [ "UNSET", "ECONOMICAL", "CONSERVATIVE", "WRONG_OPTION" ]
        # create atx
        amount = 10
        try:
            atxid = self.nodes[1].sendalerttoaddress(addr0, amount, '', '', False, False, 1, estimate_mode[3])
            assert(False)
        except JSONRPCException as e:
            pass

        for i in estimate_mode[:-1]:
            self.nodes[1].sendalerttoaddress(addr0, amount, '', '', False, False, 1, i)

    def test_alert_tx_change_is_by_default_sent_back_to_the_sender(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert alert_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]

    def test_instant_tx_change_is_by_default_sent_back_to_the_sender(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # create itx
        amount = 10
        atxid = self.nodes[1].sendinstanttoaddress(addr0, amount, [self.alert_instant_privkey])
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        # assert
        assert len(change_vout['scriptPubKey']['addresses']) == 1
        assert instant_addr1['address'] == change_vout['scriptPubKey']['addresses'][0]

    def test_sendalerttoaddress_selects_coins_on_instant_addresses_only(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])
        self.nodes[0].generatetoaddress(200, addr0)

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] == instant_addr0['address']]
        assert len(coins_to_use) == 200

        atxid = self.nodes[0].sendalerttoaddress(other_addr, self.COINBASE_AMOUNT * 200, '', '', True)
        atx = self.nodes[0].getrawtransaction(atxid, True)
        self.nodes[0].generatetoaddress(1, other_addr)

        # assert
        self.sync_all()
        assert len(atx['vin']) == 200
        assert {v['txid']: v['vout'] for v in atx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_sendalerttoaddress_selects_coins_on_instant_and_alert_addresses_only(self):
        alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_instant_pubkey)
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(100, instant_addr0['address'])
        self.nodes[0].generatetoaddress(100, alert_addr0['address'])
        self.nodes[0].generatetoaddress(200, addr0)

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] == alert_addr0['address']]
        assert len(coins_to_use) == 100

        atxid = self.nodes[0].sendalerttoaddress(other_addr, self.COINBASE_AMOUNT * 100, '', '', True)
        atx = self.nodes[0].getrawtransaction(atxid, True)
        self.nodes[0].generatetoaddress(1, other_addr)

        # assert
        self.sync_all()
        assert len(atx['vin']) == 100
        assert {v['txid']: v['vout'] for v in atx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_sendinstanttoaddress_selects_coins_on_instant_addresses_only(self):
        alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_recovery_pubkey)
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(100, alert_addr0['address'])
        self.nodes[0].generatetoaddress(100, instant_addr0['address'])
        self.nodes[0].generatetoaddress(200, addr0)

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] == instant_addr0['address']]
        assert len(coins_to_use) == 100

        txid = self.nodes[0].sendinstanttoaddress(other_addr, self.COINBASE_AMOUNT * 100, [self.alert_instant_privkey], '', '', True)
        tx = self.nodes[0].getrawtransaction(txid, True)
        self.nodes[0].generatetoaddress(1, other_addr)

        # assert
        self.sync_all()
        assert len(tx['vin']) == 100
        assert {v['txid']: v['vout'] for v in tx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}
        assert txid in self.nodes[0].getbestblock()['tx']

    @introduce_and_reset_blockchain
    def test_sendinstanttoaddress_selects_coins_on_instant_addresses_only_with_label(self):
        label = "rainy day"
        alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_recovery_pubkey, label)
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(100, alert_addr0['address'])
        self.nodes[0].generatetoaddress(100, instant_addr0['address'])
        self.nodes[0].generatetoaddress(200, addr0)

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] == instant_addr0['address']]

        txid = self.nodes[0].sendinstanttoaddress(other_addr, self.COINBASE_AMOUNT * 100, [self.alert_instant_privkey], '', '', True)
        tx = self.nodes[0].getrawtransaction(txid, True)
        self.nodes[0].generatetoaddress(1, other_addr)

        transactions = self.nodes[0].listtransactions(label)

        # assert
        self.sync_all()
        assert len(tx['vin']) == 100
        assert {v['txid']: v['vout'] for v in tx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}
        assert txid in self.nodes[0].getbestblock()['tx']

        assert transactions != None
        for transaction in transactions:
            assert transaction['label'] == label

    @introduce_and_reset_blockchain
    def test_sendinstanttoaddress_selects_coins_on_instant_addresses_only_differnet_addr_type(self):
        addresss = ['legacy', 'p2sh-segwit', 'bech32', 'invalid']
        cnt = 1
        for address in addresss:
            try:
                alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_recovery_pubkey, '', address)
                instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
                addr0 = self.nodes[0].getnewaddress()
                other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

                self.nodes[0].generatetoaddress(100, alert_addr0['address'])
                self.nodes[0].generatetoaddress(100, instant_addr0['address'])
                self.nodes[0].generatetoaddress(200, addr0)

                coins_to_use = self.nodes[0].listunspent()
                coins_to_use = [c for c in coins_to_use if c['address'] == instant_addr0['address']]

                txid = self.nodes[0].sendinstanttoaddress(other_addr, self.COINBASE_AMOUNT * 100, [self.alert_instant_privkey], '', '', True)
                tx = self.nodes[0].getrawtransaction(txid, True)
            except JSONRPCException as e:
                cnt -= 1
        assert  cnt == 0

    def test_sendinstanttoaddress_with_multiple_instant_addresses(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        instant_addr01 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(100, instant_addr01['address'])
        self.nodes[0].generatetoaddress(100, instant_addr0['address'])
        self.nodes[0].generatetoaddress(200, addr0)

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] in [instant_addr0['address'], instant_addr01['address']]]
        assert len(coins_to_use) == 200

        txid = self.nodes[0].sendinstanttoaddress(other_addr, self.COINBASE_AMOUNT * 200, [self.alert_instant_privkey], '', '', True)
        tx = self.nodes[0].getrawtransaction(txid, True)
        self.nodes[0].generatetoaddress(1, other_addr)

        # assert
        self.sync_all()
        assert len(tx['vin']) == 200
        assert {v['txid']: v['vout'] for v in tx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}
        assert txid in self.nodes[0].getbestblock()['tx']

    def test_sendinstanttoaddress_fails_when_no_coins_available_on_instant_addresses(self):
        alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_instant_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        self.nodes[0].generatetoaddress(200, alert_addr0['address'])  # coins are available on alert address ...
        self.nodes[0].generatetoaddress(200, addr0)  # ... and regular address ...
        error = None
        try:
            self.nodes[0].sendinstanttoaddress(other_addr, 10)  # ... so this call should fail
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -4
        assert 'Insufficient funds' in error['message']

    def test_sendtoaddress_fails_when_no_coins_available_on_regular_addresses(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])  # coins are available only on instant address ...
        error = None
        try:
            self.nodes[0].sendtoaddress(other_addr, 10)  # ... so this call should fail
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -4
        assert 'Insufficient funds' in error['message']

    def test_sendtoaddress_selects_coins_on_regular_addresses_only(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(200, addr0)
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] == addr0]
        assert len(coins_to_use) == 200

        txid = self.nodes[0].sendtoaddress(other_addr, self.COINBASE_AMOUNT * 200, '', '', True)
        tx = self.nodes[0].getrawtransaction(txid, True)
        self.nodes[0].generatetoaddress(1, other_addr)

        # assert
        self.sync_all()
        assert len(tx['vin']) == 200
        assert {v['txid']: v['vout'] for v in tx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}
        assert txid in self.nodes[0].getbestblock()['tx']

    def test_recovery_tx_is_incomplete_and_rejected_when_missing_recovery_key(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], info['hex'], instant_addr0['redeemScript'])

        assert not recoverytx['complete']
        error = None
        try:
            self.nodes[0].sendrawtransaction(recoverytx['hex'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -26
        assert 'non-mandatory-script-verify-flag' in error['message']

    def test_recovery_tx_is_rejected_when_missing_both_instant_and_recovery_keys(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        assert int(self.nodes[0].getalertbalance()) == 17325
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        error = None
        try:
            self.nodes[0].signrecoverytransaction(recoverytx, [], info['hex'], instant_addr0['redeemScript'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert int(self.nodes[0].getalertbalance('*', 1)) == 17500
        assert error['code'] == -5
        assert 'Produced invalid transaction type, type vaultrecovery was expected' in error['message']

    def test_recovery_tx_is_incomplete_and_rejected_when_missing_instant_key(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_recovery_privkey], info['hex'], instant_addr0['redeemScript'])

        assert not recoverytx['complete']
        error = None
        try:
            self.nodes[0].sendrawtransaction(recoverytx['hex'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -26
        assert 'non-mandatory-script-verify-flag' in error['message']

    def test_recovery_tx_when_all_keys_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [], info['hex'], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_recovery_tx_is_rejected_when_only_recovery_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [], instant_addr0['redeemScript'])

        self.sync_all()
        assert not recoverytx['complete']
        assert 'Unable to sign input, zero signature (possibly missing key)' in recoverytx['errors'][0]['error']

    def test_recovery_tx_is_rejected_when_only_instant_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [], instant_addr0['redeemScript'])

        self.sync_all()
        assert not recoverytx['complete']
        assert 'Unable to sign input, zero signature (possibly missing key)' in recoverytx['errors'][0]['error']

    def test_recovery_tx_when_instant_key_imported_and_recovery_key_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_recovery_privkey], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_recovery_tx_when_recovery_key_imported_and_instant_key_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    @introduce_and_reset_blockchain
    def test_recovery_tx_when_recovery_key_imported_and_instant_key_given_replaceable_no(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], instant_addr0['redeemScript'])

        cnt = 10
        transactions = self.nodes[0].listtransactions()
        assert transactions != []
        for transaction in transactions:
            if transaction['bip125-replaceable'] == 'unknown':# valid state due to bip-125 is not used
                cnt -= 1
            if transaction['bip125-replaceable'] == 'no':
                cnt -= 1
        self.log.debug("Counter %d" % cnt)
        assert cnt == 0

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    @introduce_and_reset_blockchain
    def test_recovery_tx_when_recovery_key_imported_and_instant_key_given_locktime(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        options = [ -1, 0, 1, 10 , 666, 0xFFFFFFFF , 0xFFFFFFFF+1]
        cnt = 2
        # recover atx
        for i in options:
            try:
                recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}], i)
                recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], instant_addr0['redeemScript'])
            except JSONRPCException as e:
                cnt -= 1
        assert cnt == 0

    @introduce_and_reset_blockchain
    def test_recovery_tx_when_recovery_key_imported_and_instant_key_given_sighashtype(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        sighashtypes = [ "ALL" , "NONE", "SINGLE", "ALL|ANYONECANPAY", "NONE|ANYONECANPAY", "SINGLE|ANYONECANPAY", "XFGH"]
        cnt = 6
        # recover atx
        for sighashtype in sighashtypes:
            try:
                recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
                recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], instant_addr0['redeemScript'], instant_addr0['redeemScript'], sighashtype)
            except JSONRPCException as e:
                self.log.debug(e)
                cnt -= 1
        self.log.debug("@TODO counter %d" % cnt)
        #assert cnt == 0

    def test_recovery_tx_when_both_instant_and_recovery_keys_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendalerttoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_dumpwallet(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # get pubkey
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        pubkey = info['embedded']['pubkeys'] if 'embedded' in info else info['pubkeys']
        pubkey.remove(self.alert_recovery_pubkey)
        pubkey = pubkey[0]

        # dump wallet
        wallet_path = os.path.join(self.nodes[0].datadir, "wallet.dump")
        result = self.nodes[0].dumpwallet(wallet_path)
        assert result['filename'] == wallet_path

        # import wallet
        self.nodes[1].importwallet(wallet_path)
        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is True
        assert info['iswatchonly'] is False
        if 'embedded' in info: info = info['embedded']
        assert sorted(info['pubkeys']) == sorted([pubkey, self.alert_recovery_pubkey, self.alert_instant_pubkey])

    def test_add_watchonly_instant_address(self):
        instant_addr0 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # import alert_addr1 to node0 as watch-only
        self.nodes[0].importaddress(instant_addr0['redeemScript'], '', True, True)
        self.nodes[0].importaddress(info['hex'], '', True, True)

        # mine some coins to node2 and send tx to instant_addr0
        self.nodes[2].generate(200)
        txid = self.nodes[2].sendtoaddress(instant_addr0['address'], 10)
        self.nodes[2].generate(1)

        # assert
        self.sync_all()
        receivedbyaddress = self.find_address(self.nodes[0].listreceivedbyaddress(), instant_addr0['address'])
        assert self.nodes[0].getinstantbalance() == 0
        assert 'involvesWatchonly' in receivedbyaddress
        assert receivedbyaddress['involvesWatchonly'] is True
        assert receivedbyaddress['amount'] == 10
        assert txid in receivedbyaddress['txids']

    def test_getaddressinfo_on_instant_address(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is True
        assert info['solvable'] is True
        assert info['iswatchonly'] is False
        assert info['isscript'] is True
        if 'embedded' in info: info = info['embedded']
        assert info['script'] == 'vaultinstant'
        assert info['sigsrequired'] == 1
        assert len(info['pubkeys']) == 3
        assert self.alert_recovery_pubkey in info['pubkeys']
        assert self.alert_instant_pubkey in info['pubkeys']

    def test_getaddressinfo_on_imported_instant_address(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])

        # import instant_addr0 to node0 as watch-only
        self.nodes[1].importaddress(instant_addr0['redeemScript'], '', True, True)
        self.nodes[1].importaddress(info['hex'], '', True, True)

        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is False
        assert info['solvable'] is True  # Whether we know how to spend coins sent to this address, ignoring the possible lack of private keys
        assert info['iswatchonly'] is True
        assert info['isscript'] is True
        if 'embedded' in info: info = info['embedded']
        assert info['script'] == 'vaultinstant'
        assert info['sigsrequired'] == 1
        assert len(info['pubkeys']) == 3
        assert self.alert_recovery_pubkey in info['pubkeys']
        assert self.alert_instant_pubkey in info['pubkeys']

    def test_import_instant_address_privkey(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # get pubkey
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        pubkey = info['embedded']['pubkeys'] if 'embedded' in info else info['pubkeys']
        pubkey.remove(self.alert_recovery_pubkey)
        pubkey = pubkey[0]

        # dump privkey
        p2pkh = key_to_p2pkh(pubkey)
        privkey = self.nodes[0].dumpprivkey(p2pkh)

        # import address and privkey on node1
        self.nodes[1].importaddress(instant_addr0['redeemScript'], '', True, True)
        self.nodes[1].importaddress(info['hex'], '', True, True)
        self.nodes[1].importprivkey(privkey)

        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is True
        assert info['iswatchonly'] is False
        if 'embedded' in info: info = info['embedded']
        assert sorted(info['pubkeys']) == sorted([pubkey, self.alert_recovery_pubkey, self.alert_instant_pubkey])

    def test_atx_from_imported_instant_address(self):
        # TODO-fork: fails sometimes because of nodes synchronization timing?
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'  # not owned by test nodes

        # mine some coins to instant_addr0
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # get pubkey
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        pubkey = info['embedded']['pubkeys'] if 'embedded' in info else info['pubkeys']
        pubkey.remove(self.alert_recovery_pubkey)
        pubkey = pubkey[0]

        # dump privkey
        p2pkh = key_to_p2pkh(pubkey)
        privkey = self.nodes[0].dumpprivkey(p2pkh)

        # import address and privkey on node1
        self.nodes[1].importaddress(instant_addr0['redeemScript'], '', True, True)
        self.nodes[1].importaddress(info['hex'], '', True, True)
        self.nodes[1].importprivkey(privkey)

        # send atx from node1 and mine block with this atx
        atxid = self.nodes[1].sendalerttoaddress(other_addr, 10)
        self.nodes[1].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert atxid is not None
        assert atxid != ''
        
        self.sync_all()
        assert atxid in self.nodes[1].getbestblock()['atx']

    def test_tx_from_normal_addr_to_instant_addr(self):
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to node0
        self.nodes[0].generate(200)

        # send tx from node0 to instant_addr1 and generate block with this tx
        txid = self.nodes[0].sendtoaddress(instant_addr1['address'], 10)
        self.nodes[0].generate(1)

        # assert
        self.sync_all()
        assert self.nodes[1].getinstantbalance() == 10
        assert txid in self.nodes[0].getbestblock()['tx']
        assert txid not in self.nodes[0].getbestblock()['atx']
        assert txid in self.find_address(self.nodes[1].listreceivedbyaddress(), instant_addr1['address'])['txids']

    def test_atx_from_instant_addr_to_normal_addr(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # send atx from instant_addr1 to addr0 and generate block with this atx
        atxid = self.nodes[1].sendalerttoaddress(addr0, 10)
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 0
        assert atxid in self.nodes[0].getbestblock()['atx']

        # generate more blocks so atx becomes tx
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])
        txid = atxid

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 10
        assert txid in self.find_address(self.nodes[0].listreceivedbyaddress(), addr0)['txids']

    @introduce_and_reset_blockchain
    def test_atx_with_multiple_inputs_from_alert_addr_to_normal_addr_invalid_address_type(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']

        address_types = ["legacy", "p2sh-segwit", "bech32", "invalid"]
        cnt = 1
        for address_type in address_types:
            try:
                # mine some coins to alert_addr1
                alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, self.alert_instant_pubkey, self.alert_recovery_pubkey, address_type)
                self.nodes[1].generatetoaddress(300, alert_addr1['address'])
            except JSONRPCException as e:
                cnt -= 1
        assert cnt == 0

    def test_atx_with_multiple_inputs_from_alert_addr_to_normal_addr(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr0_p2pkh = key_to_p2pkh(addr0_pubkey)
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0_p2pkh)

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(300, alert_addr1['address'])

        # import key
        self.nodes[1].importprivkey(addr0_prvkey)

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create atx
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 175},
            {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 175}
        ])

        # send atx
        atxid = self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        # assert
        self.sync_all()
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_atx_becomes_tx(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # send atx from instant_addr1 to addr0 and generate block with this atx
        atxid = self.nodes[1].sendalerttoaddress(addr0, 10)
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 0
        assert atxid in self.nodes[0].getbestblock()['atx']

        # generate 144 more blocks
        self.nodes[1].generatetoaddress(144, instant_addr1['address'])
        txid = atxid

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 10
        assert txid in self.nodes[0].getbestblock()['tx']
        assert txid in self.find_address(self.nodes[0].listreceivedbyaddress(), addr0)['txids']

    def test_signrawtransactionwithwallet_should_reject_alert_transaction(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from instant_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        error = None
        try:
            self.nodes[1].signrawtransactionwithwallet(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 175}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Unable to sign transaction from vault address' in error['message']

    def test_signrawtransactionwithwallet_should_reject_instant_transaction(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # import instant key
        self.nodes[1].importprivkey(self.alert_instant_privkey)

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign instant tx from instant_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        error = None
        try:
            self.nodes[1].signrawtransactionwithwallet(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 175}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Unable to sign transaction from vault address' in error['message']

    def test_sign_atx_with_recovery_key(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from instant_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [self.alert_recovery_privkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        atxsent = self.nodes[1].decoderawtransaction(atxtosend['hex'])

        # broadcast atx and mine block with this atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert atxsent['txid'] in self.nodes[0].getbestblock()['atx']

    def test_signalerttransaction_when_both_recovery_and_instant_keys_imported(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # import key
        self.nodes[1].importprivkey(self.alert_recovery_privkey)
        self.nodes[1].importprivkey(self.alert_instant_privkey)

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from alert_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        atxtosend = self.nodes[1].signalerttransaction(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        atxsent = self.nodes[1].decoderawtransaction(atxtosend['hex'])

        # broadcast atx and mine block with this atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert atxsent['txid'] in self.nodes[0].getbestblock()['atx']

    def test_signalerttransaction(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from alert_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        atxtosend = self.nodes[1].signalerttransaction(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        atxsent = self.nodes[1].decoderawtransaction(atxtosend['hex'])

        # broadcast atx and mine block with this atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert atxsent['txid'] in self.nodes[0].getbestblock()['atx']

    def test_atx_fee_is_paid_to_original_miner(self):
        mine_addr = self.nodes[0].getnewaddress()
        mine_addr2 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine coins and send 10 to instant_addr0
        self.nodes[0].generatetoaddress(200, mine_addr)
        amount = 10
        self.nodes[0].sendtoaddress(instant_addr1['address'], amount)
        self.nodes[0].generatetoaddress(1, mine_addr)

        # send coins back by atx and confirm it
        self.sync_all()
        assert self.nodes[1].getalertbalance() == amount
        txid = self.nodes[1].sendalerttoaddress(mine_addr, amount - 1)
        tx = self.nodes[1].getrawtransaction(txid, 1)
        fee = amount - tx['vout'][0]['value'] - tx['vout'][1]['value']
        self.nodes[1].generatetoaddress(1, mine_addr2)  # mine to separate address
        self.nodes[1].generatetoaddress(144, mine_addr)

        # assert
        self.sync_all()
        coinbase_id = self.nodes[1].getbestblock()['tx'][0]
        coinbase = self.nodes[1].getrawtransaction(coinbase_id, 1)
        assert coinbase['vout'][1]['value'] == fee

    def test_atx_with_inputs_of_different_source(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info1 = self.nodes[1].getaddressinfo(instant_addr1['address'])
        self.nodes[1].generatetoaddress(50, instant_addr1['address'])
        instant_addr2 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info2 = self.nodes[1].getaddressinfo(instant_addr2['address'])
        self.nodes[1].generatetoaddress(50, instant_addr2['address'])
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create and sign atx from instant_addr1 and instant_addr2 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        atxtosend = self.nodes[1].signalerttransaction(atxtosend, [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info1['hex'], 'amount': 175},
            {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'witnessScript': instant_addr2['redeemScript'], 'redeemScript': info2['hex'], 'amount': 175}
        ])
        atxid = self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        self.sync_all()
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_atx_is_rejected_by_wallet_when_contains_non_alert_inputs(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])
        self.nodes[1].generatetoaddress(50, instant_addr1['address'])
        addr1 = self.nodes[1].getnewaddress()
        self.nodes[1].generatetoaddress(50, addr1)
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create and sign atx from instant_addr1 and alert_addr2 to addr0
        txtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        try:
            self.nodes[1].signalerttransaction(txtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced invalid transaction type, type vaultalert was expected' in error['message']

    def test_atx_signed_by_signrawtransactionwithkey_with_inputs_of_different_source(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        alert_addr2 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, alert_addr1['address'])
        self.nodes[1].generatetoaddress(50, alert_addr2['address'])
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create atx
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [self.alert_instant_privkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 175},
            {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': alert_addr2['redeemScript'], 'amount': 175}
        ])
        atxid = self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        self.sync_all()
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_atx_is_rejected_by_signrawtransactionwithkey_when_contains_non_alert_inputs(self):
        addr0 = self.nodes[1].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, alert_addr1['address'])
        self.nodes[1].generatetoaddress(50, addr1)
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})

        error = ''
        try:
            self.nodes[1].signrawtransactionwithkey(atxtosend, [self.alert_instant_privkey], [
                {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 175},
                {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'amount': 175}
            ])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced invalid transaction type, type vaultalert was expected' in error['message']

    def test_signinstanttransaction_when_instant_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # import instant key
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr0['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_when_recovery_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # import recovery key
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr0['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_when_all_keys_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [self.alert_recovery_privkey, self.alert_instant_privkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr0['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_when_both_instant_and_recovery_keys_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # import keys
        self.nodes[0].importprivkey(self.alert_instant_privkey)
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr0['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_is_incomplete_and_rejected_when_missing_key(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr0['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])

        assert not instant_tx['complete']

        error = None
        try:
            self.nodes[0].sendrawtransaction(instant_tx['hex'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -26
        assert 'non-mandatory-script-verify-flag' in error['message']

    def test_signinstanttransaction(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [self.alert_instant_privkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr0['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_atx_is_rejected_by_node_when_inputs_are_spent(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0)
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr1 = self.nodes[0].getnewaddress()
        addr1_prvkey = self.nodes[0].dumpprivkey(addr1)
        addr1_pubkey = self.nodes[0].getaddressinfo(addr1)['pubkey']

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, addr1_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(150, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and send 1st atx
        amount = 174.99
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
        ])
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        self.sync_all()

        # create and send 2nd atx
        amount = 174.98
        atxtosend = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[0].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
        ])

        error = ''
        try:
            self.nodes[0].sendrawtransaction(atxtosend['hex'])
        except Exception as e:
            error = e.error

        assert error['code'] == -26
        assert 'bad-txn-inputs-spent' in error['message']

    def test_atx_is_rejected_by_node_when_inputs_are_spent_by_parallel_atx(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0)
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr1 = self.nodes[0].getnewaddress()
        addr1_prvkey = self.nodes[0].dumpprivkey(addr1)
        addr1_pubkey = self.nodes[0].getaddressinfo(addr1)['pubkey']

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, addr1_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(150, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and send 1st atx
        amount = 174.99
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 175},
        ])
        self.nodes[1].sendrawtransaction(atxtosend['hex'])

        # create 2nd atx
        amount = 174.69
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 175},
        ])

        error = ''
        try:
            self.nodes[1].sendrawtransaction(atxtosend['hex'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -26
        assert 'txn-mempool-conflict' in error['message']

    def test_recovery_tx_flow(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr0 = self.nodes[0].getnewaddress()
        attacker_addr1 = self.nodes[1].getnewaddress()

        # mine some coins to node0
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])  # 200
        assert self.nodes[0].getinstantbalance() == (200 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT

        # send atx to node1
        atx_to_recover = self.nodes[0].sendalerttoaddress(attacker_addr1, 10)
        atx_to_recover = self.nodes[0].gettransaction(atx_to_recover)['hex']
        atx_to_recover = self.nodes[0].decoderawtransaction(atx_to_recover)
        amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])
        atx_fee = self.COINBASE_AMOUNT - amount_to_recover

        # generate block with atx above
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])  # 201

        # assert
        self.sync_all()
        assert self.nodes[0].getalertbalance() + 10 < (201 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT
        assert self.nodes[1].getbalance() == 0
        assert atx_to_recover['txid'] in self.nodes[0].getbestblock()['atx']

        # recover atx
        recovery_tx = self.nodes[0].createrecoverytransaction(atx_to_recover['txid'], {other_addr0: amount_to_recover})
        recovery_tx = self.nodes[0].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr0['redeemScript'])
        recovery_txid = self.nodes[0].sendrawtransaction(recovery_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])  # 202

        # assert
        self.sync_all()
        assert recovery_txid in self.nodes[0].getbestblock()['tx']
        assert recovery_txid in self.find_address(self.nodes[0].listreceivedbyaddress(), other_addr0)['txids']
        assert self.nodes[0].getbalance() + self.nodes[0].getalertbalance() == (202 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT - atx_fee

        # generate blocks so atx might become tx
        self.nodes[0].generatetoaddress(143, instant_addr0['address'])  # 345

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() + self.nodes[0].getalertbalance() == (345 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT  # dont subtract atx_fee because node0 takes it as a block miner
        assert atx_to_recover['txid'] not in self.nodes[0].getbestblock()['tx']
        assert self.find_address(self.nodes[1].listreceivedbyaddress(), attacker_addr1)['amount'] == 0
        assert self.find_address(self.nodes[1].listreceivedbyaddress(), attacker_addr1)['txids'] == []
        assert self.find_address(self.nodes[0].listreceivedbyaddress(), other_addr0)['amount'] == self.COINBASE_AMOUNT - atx_fee
        assert self.find_address(self.nodes[0].listreceivedbyaddress(), other_addr0)['txids'] == [recovery_txid]

    def test_recovery_tx_flow_for_two_alerts(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # create, sign and mine 1st atx from instant_addr1 to addr0
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        tx_alert1 = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        tx_alert1 = self.nodes[1].signalerttransaction(tx_alert1, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        self.nodes[1].sendrawtransaction(tx_alert1['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # create, sign and mine 2nd atx from instant_addr1 to addr0
        self.sync_all()
        txtospendhash2 = self.nodes[1].getblockbyheight(20)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)
        tx_alert2 = self.nodes[1].createrawtransaction([{'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 174.99})
        tx_alert2 = self.nodes[1].signalerttransaction(tx_alert2, [{'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 175}])
        self.nodes[1].sendrawtransaction(tx_alert2['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])
        self.sync_all()

        # create and sign recovery tx spending both alerts inputs
        recovery_tx = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        recovery_tx = self.nodes[1].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr1['redeemScript'])
        recovery_txid = self.nodes[1].sendrawtransaction(recovery_tx['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert recovery_txid in self.nodes[0].getbestblock()['tx']

        # generate blocks so atx 1 might become tx
        self.nodes[0].generatetoaddress(143, instant_addr1['address'])
        assert tx_alert1 not in self.nodes[0].getbestblock()['tx']

        # generate blocks so atx 2 might become tx
        self.nodes[0].generatetoaddress(1, instant_addr1['address'])
        assert tx_alert2 not in self.nodes[0].getbestblock()['tx']

    def test_recovery_tx_when_alert_is_confirmed_at_the_same_height(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr0 = self.nodes[0].getnewaddress()
        attacker_addr1 = self.nodes[1].getnewaddress()

        # mine some coins to node0
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])  # 200
        assert self.nodes[0].getalertbalance() == (200 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT

        # send atx to node1
        atx_to_recover = self.nodes[0].sendalerttoaddress(attacker_addr1, 10)
        atx_to_recover = self.nodes[0].gettransaction(atx_to_recover)['hex']
        atx_to_recover = self.nodes[0].decoderawtransaction(atx_to_recover)
        amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])
        atx_fee = self.COINBASE_AMOUNT - amount_to_recover

        # generate block with atx above
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])  # 201

        # assert
        self.sync_all()
        assert atx_to_recover['txid'] in self.nodes[0].getbestblock()['atx']

        # generate blocks to the end of alert confrirmation window
        self.nodes[0].generatetoaddress(143, instant_addr0['address'])  # 344

        # recover atx
        recovery_tx = self.nodes[0].createrecoverytransaction(atx_to_recover['txid'], {other_addr0: amount_to_recover})
        recovery_tx = self.nodes[0].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr0['redeemScript'])
        recovery_txid = self.nodes[0].sendrawtransaction(recovery_tx['hex'])

        self.nodes[0].generatetoaddress(1, instant_addr0['address'])  # 345

        self.sync_all()
        assert atx_to_recover['txid'] not in self.nodes[0].getbestblock()['tx']
        assert recovery_txid in self.nodes[0].getbestblock()['tx']

    def test_recovery_tx_is_rejected_when_alert_inputs_are_missing(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # create, sign and mine 1st atx from instant_addr1 to addr0
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(20)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)
        tx_alert1 = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        tx_alert1 = self.nodes[1].signalerttransaction(tx_alert1, [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175},
            {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}
        ])
        self.nodes[1].sendrawtransaction(tx_alert1['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # create, sign and mine 2nd atx from instant_addr1 to addr0
        self.sync_all()
        txtospendhash3 = self.nodes[1].getblockbyheight(30)['tx'][0]
        txtospend3 = self.nodes[1].getrawtransaction(txtospendhash3, True)
        vouttospend3 = self.find_vout_n(txtospend3, 175)
        tx_alert2 = self.nodes[1].createrawtransaction([{'txid': txtospendhash3, 'vout': vouttospend3}], {addr0: 174.99})
        tx_alert2 = self.nodes[1].signalerttransaction(tx_alert2, [{'txid': txtospendhash3, 'vout': vouttospend3, 'scriptPubKey': txtospend3['vout'][vouttospend3]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 175}])
        self.nodes[1].sendrawtransaction(tx_alert2['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])
        self.sync_all()

        # create and sign (invalid) recovery tx spending both alerts inputs
        recovery_tx = self.nodes[1].createrawtransaction([{'txid': txtospendhash2, 'vout': vouttospend2}, {'txid': txtospendhash3, 'vout': vouttospend3}], {addr0: 349.99})
        recovery_tx = self.nodes[1].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr1['redeemScript'])

        # broadcast recovery tx and mine block
        self.nodes[1].sendrawtransaction(recovery_tx['hex'])
        error = None
        try:
            self.nodes[1].generatetoaddress(1, instant_addr1['address'])
        except Exception as e:
            error = e.error

        assert error['code'] == -1
        assert 'bad-txn-recovery' in error['message']

    def test_recovery_tx_is_rejected_when_inputs_are_non_alert(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[1].getaddressinfo(instant_addr1['address'])
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # create, sign and mine 1st atx from instant_addr1 to addr0
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        tx_alert1 = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        tx_alert1 = self.nodes[1].signalerttransaction(tx_alert1, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'witnessScript': instant_addr1['redeemScript'], 'redeemScript': info['hex'], 'amount': 175}])
        self.nodes[1].sendrawtransaction(tx_alert1['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # create, sign and mine 2nd atx from instant_addr1 to addr0
        self.sync_all()
        txtospendhash2 = self.nodes[1].getblockbyheight(20)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create and sign (invalid) recovery tx spending both alerts inputs
        recovery_tx = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        recovery_tx = self.nodes[1].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr1['redeemScript'])

        # broadcast recovery tx and mine block
        error = None
        try:
            self.nodes[1].sendrawtransaction(recovery_tx['hex'])
        except Exception as e:
            error = e.error

        assert error['code'] == -26
        assert 'bad-txn-inputs-not-spent' in error['message']

    def test_getrawtransaction_returns_information_about_unconfirmed_atx(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # create atx
        atxid = self.nodes[1].sendalerttoaddress(addr0, 10)
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # getrawtransaction
        rawtx = self.nodes[1].getrawtransaction(atxid, True)

        # assert
        assert rawtx['txid'] == atxid

    @introduce_and_reset_blockchain
    def test_get_getalertbalance_dummy(self):
        label = 'label'
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey, label)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        self.sync_all()
        # assert
        try:
            self.log.debug(self.nodes[1].getalertbalance('label'))
            assert False
        except JSONRPCException as e:
            pass

        assert self.nodes[0].getalertbalance() == 0
        assert self.nodes[1].getalertbalance() >= 17325

    @introduce_and_reset_blockchain
    def test_get_getalertbalance_miniconf(self):
        label = 'label'
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey, label)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        amount = 10
        atxid = self.nodes[1].sendalerttoaddress(addr0, amount)
        atx = self.nodes[1].getrawtransaction(atxid, True)
        fee = self.COINBASE_AMOUNT - self.sum_vouts_value(atx)
        change = self.COINBASE_AMOUNT - amount - fee
        change_vout = atx['vout'][self.find_vout_n(atx, change)]

        # assert
        self.sync_all()

        assert self.nodes[0].getalertbalance('*', 0) == 0
        assert int(self.nodes[1].getalertbalance('*', 0)) == 17325
        assert self.nodes[0].getalertbalance('*', 1) == 0
        assert int(self.nodes[1].getalertbalance('*', 1)) == 17325
        assert self.nodes[0].getalertbalance('*', 666) == 0
        assert int(self.nodes[1].getalertbalance('*', 666)) == 0

    @introduce_and_reset_blockchain
    def test_get_getalertbalance_include_watchonly(self):
        # @TODO
        pass


if __name__ == '__main__':
    AlertsInstantTest().main()
