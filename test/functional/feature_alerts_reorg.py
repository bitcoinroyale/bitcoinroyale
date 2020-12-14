#!/usr/bin/env python3
# Copyright (c) 2016-2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the Alerts changeover logic."""
import os
import shutil

from decimal import Decimal
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    connect_nodes,
    get_datadir_path
)


class VaultReorgTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2
        self.extra_args = [
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

    def setup_network(self):
        self.setup_nodes()

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
        self.COINBASE_MATURITY = 100
        self.COINBASE_AMOUNT = Decimal(175)

        self.reset_blockchain()
        self.log.info("Test node reorganize blocks with tx alerts")
        self.test_node_reorganize_blocks_with_tx_alerts()

        self.reset_blockchain()
        self.log.info("Test node reorganize blocks with recovery tx")
        self.test_node_reorganize_blocks_with_recovery_tx()

    def test_node_reorganize_blocks_with_tx_alerts(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        # generate 1 block to addr0 and 109 blocks to addr1
        self.nodes[0].generatetoaddress(1, addr0)
        self.nodes[0].generatetoaddress(109, addr1)  # 110

        # send tx
        self.nodes[0].sendtoaddress(alert_addr0['address'], 174.99)
        self.nodes[0].generatetoaddress(10, addr1)  # 120

        # send atx
        self.nodes[0].sendalerttoaddress(addr1, 174.98)
        self.nodes[0].generatetoaddress(1, addr1)  # 121

        # confirm atx
        self.nodes[0].generatetoaddress(144 + 35, addr1)  # 300

        # generate longer chain on node1
        self.nodes[1].generatetoaddress(400, addr1)  # 400

        # pre-reorganization assert
        assert self.nodes[0].getbestblock()['height'] == 300
        assert self.nodes[0].getbalance() > 0  # coinbase (175) - spent (174.99) - fee
        assert self.nodes[0].getbestblock() != self.nodes[1].getbestblock()

        # synchronize nodes what cause reorganization on node0
        connect_nodes(self.nodes[1], 0)
        self.sync_all()

        # post-reorganization assert
        assert self.nodes[1].getbestblock()['height'] == 400
        assert self.nodes[0].getbalance() == 0
        assert self.nodes[0].getbestblock() == self.nodes[1].getbestblock()

    def test_node_reorganize_blocks_with_recovery_tx(self):
        alert_addr0 = self.nodes[0].getnewvaultalertaddress(self.alert_recovery_pubkey)
        other_addr0 = self.nodes[0].getnewaddress()
        attacker_addr1 = self.nodes[1].getnewaddress()

        # mine some coins to node0
        self.nodes[0].generatetoaddress(200, alert_addr0['address'])  # 200
        assert self.nodes[0].getalertbalance() == (200 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT

        # send atx to node1
        atx_to_recover = self.nodes[0].sendalerttoaddress(attacker_addr1, 10)
        atx_to_recover = self.nodes[0].gettransaction(atx_to_recover)['hex']
        atx_to_recover = self.nodes[0].decoderawtransaction(atx_to_recover)
        amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])

        # generate block with atx above
        self.nodes[0].generatetoaddress(1, alert_addr0['address'])  # 201

        # assert
        assert self.nodes[0].getalertbalance() + 10 < (201 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT
        assert atx_to_recover['txid'] in self.nodes[0].getbestblock()['atx']

        # recover atx
        recovery_tx = self.nodes[0].createrecoverytransaction(atx_to_recover['txid'], {other_addr0: amount_to_recover})
        recovery_tx = self.nodes[0].signrecoverytransaction(recovery_tx, [self.alert_recovery_privkey], alert_addr0['redeemScript'])
        self.nodes[0].sendrawtransaction(recovery_tx['hex'])
        self.nodes[0].generatetoaddress(144 + 5, alert_addr0['address'])  # 350

        # generate longer chain on node1
        self.nodes[1].generatetoaddress(400, attacker_addr1)  # 400

        # pre-reorganization assert
        assert self.nodes[0].getbestblock()['height'] == 350
        assert self.nodes[0].getbalance() > 0  # coinbase (175) - spent (174.99) - fee
        assert self.nodes[0].getbestblock() != self.nodes[1].getbestblock()

        # synchronize nodes what cause reorganization on node0
        connect_nodes(self.nodes[1], 0)
        self.sync_all()

        self.restart_node(0, self.extra_args[0])
        self.sync_all()

        # post-reorganization assert
        assert self.nodes[1].getbestblock()['height'] == 400
        assert self.nodes[0].getbalance() == 0
        assert self.nodes[0].getbestblock() == self.nodes[1].getbestblock()


if __name__ == '__main__':
    VaultReorgTest().main()
