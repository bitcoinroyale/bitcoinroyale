from RPCProxyWrapper import *
from pathlib import Path

import time

rpc_connection1 = RPCProxyWrapper(rpcport=18887, rpcuser='user', rpcpass='pass', datadir=Path.home() / '.bvault1')

rpc_connection2 = RPCProxyWrapper(rpcport=18888, rpcuser='user', rpcpass='pass', datadir=Path.home() / '.bvault2')


def construct_atx_from_utxo():
    amount_to_send = 174.99
    addr2 = rpc_connection2.getnewaddress()

    # mine coins to alert address
    alert_addr1 = rpc_connection1.getnewvaultalertaddress(TEST_KEYS[0].pub)
    rpc_connection1.generatetoaddress(200, alert_addr1['address'])

    # create and sign tx from alert address
    txtospendhash = rpc_connection1.getblockbyheight(10)['tx'][0]
    txtospend = rpc_connection1.getrawtransaction(txtospendhash)
    vouttospend = find_vout_n(txtospend, 175)
    txtosend = rpc_connection1.createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr2: amount_to_send})
    txtosend = rpc_connection1.signrawtransactionwithwallet(txtosend, [
        {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'],
         'amount': amount_to_send}])
    # txtosend = rpc_connection1.signrawtransactionwithkey(txtosend, [TEST_KEYS[0].priv], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': amount_to_send}])

    # generate block with tx above
    rpc_connection1.generatetoaddress(200, alert_addr1['address'])


def atx_from_alert_addr_to_normal_addr():
    addr2 = rpc_connection2.getnewaddress()

    # mine coins to alert address
    alert_addr1 = rpc_connection1.getnewvaultalertaddress(TEST_KEYS[0].pub)
    rpc_connection1.generatetoaddress(200, alert_addr1['address'])

    # send from alert address
    txid = rpc_connection1.sendtoaddress(addr2, 10)
    rpc_connection1.generatetoaddress(1, alert_addr1['address'])

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == rpc_connection2.getbestblock()
    assert txid in rpc_connection2.getbestblock()['atx']
    assert rpc_connection2.getbalance() == 0

    # make transaction from alert
    rpc_connection1.generatetoaddress(200, alert_addr1['address'])

    # assert
    time.sleep(3)
    assert rpc_connection2.getbalance() == 10
    assert txid in find_address(rpc_connection2.listreceivedbyaddress(), addr2)['txids']


def tx_from_normal_addr_to_alert_addr():
    alert_addr1 = rpc_connection1.getnewvaultalertaddress(TEST_KEYS[0].pub)

    # mine coins to normal address
    addr2 = rpc_connection2.getnewaddress()
    rpc_connection2.generatetoaddress(200, addr2)

    # send to alert address
    txid = rpc_connection2.sendtoaddress(alert_addr1['address'], 10)
    rpc_connection2.generatetoaddress(1, addr2)

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == rpc_connection2.getbestblock()
    assert txid in rpc_connection2.getbestblock()['tx']
    assert rpc_connection1.getbalance() == 10
    assert txid in find_address(rpc_connection1.listreceivedbyaddress(), alert_addr1['address'])['txids']


def tx_from_normal_addr_to_normal_addr():
    addr1 = rpc_connection1.getnewaddress()

    # mine coins to normal address
    addr2 = rpc_connection2.getnewaddress()
    rpc_connection2.generatetoaddress(200, addr2)

    # send to normal address
    txid = rpc_connection2.sendtoaddress(addr1, 10)
    rpc_connection2.generatetoaddress(1, addr2)

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == rpc_connection2.getbestblock()
    assert txid in rpc_connection2.getbestblock()['tx']
    assert rpc_connection1.getbalance() == 10
    assert txid in find_address(rpc_connection1.listreceivedbyaddress(), addr1)['txids']


def test_synchronization_when_restart():
    # generate some blocks
    addr2 = rpc_connection2.getnewaddress()
    rpc_connection2.generatetoaddress(200, addr2)
    bestblock = rpc_connection2.getbestblock()

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == bestblock

    # restart nodes
    RPCProxyWrapper.killall()
    wait_for_bvaultd(2)

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == bestblock == rpc_connection2.getbestblock()


def test_synchronization_when_reset():
    # generate some blocks
    addr2 = rpc_connection2.getnewaddress()
    rpc_connection2.generatetoaddress(200, addr2)
    bestblock = rpc_connection2.getbestblock()

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == bestblock

    # reset 1st node
    RPCProxyWrapper.killall()
    rpc_connection1.reset()
    wait_for_bvaultd(2)

    # assert
    time.sleep(3)
    assert rpc_connection1.getbestblock() == bestblock == rpc_connection2.getbestblock()


def test_construct_recovery_tx():
    alert_addr = rpc_connection1.getnewvaultalertaddress(TEST_KEYS[0].pub)
    attacker_addr = rpc_connection1.getnewaddress()
    other_addr = rpc_connection1.getnewaddress()

    rpc_connection1.generatetoaddress(200, alert_addr['address'])
    atx_to_recover = rpc_connection1.send(attacker_addr, 10)
    atx_to_recover = rpc_connection1.gettransaction(atx_to_recover)['hex']
    atx_to_recover = rpc_connection1.decoderawtransaction(atx_to_recover)
    rpc_connection1.generatetoaddress(1, alert_addr['address'])

    # assert
    time.sleep(3)
    assert atx_to_recover['hash'] in rpc_connection1.getbestblock()['atx']

    inputs_to_recover = [{'txid': vin['txid'], 'vout': vin['vout']} for vin in atx_to_recover['vin']]
    amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])

    recovery_tx = rpc_connection1.createrawtransaction(inputs_to_recover, {other_addr: amount_to_recover})
    recovery_tx2 = rpc_connection1.createrecoverytransaction(atx_to_recover['hash'], {other_addr: amount_to_recover})
    assert recovery_tx == recovery_tx2

    recovery_data = [{'txid': vin['txid'],
                      'vout': vin['vout'],
                      'scriptPubKey': rpc_connection1.get_script_pubkey(vin['txid'], vin['vout'])['hex'],
                      'redeemScript': alert_addr['redeemScript']} for vin in atx_to_recover['vin']]

    recovery_tx = rpc_connection1.signrawtransactionwithwallet(recovery_tx, recovery_data)
    recovery_tx = rpc_connection1.signrawtransactionwithkey(recovery_tx['hex'], [TEST_KEYS[0].priv], recovery_data)
    recovery_tx2 = rpc_connection1.signrecoverytransaction(recovery_tx2, [TEST_KEYS[0].priv], recovery_data)
    assert recovery_tx == recovery_tx2  # ?

    recovery_txid = rpc_connection1.sendrawtransaction(recovery_tx['hex'])
    a = 42


def test_recover_transaction():
    alert_addr = rpc_connection1.getnewvaultalertaddress(TEST_KEYS[0].pub)
    attacker_addr = rpc_connection1.getnewaddress()
    other_addr = rpc_connection1.getnewaddress()

    # send alert tx
    rpc_connection1.generatetoaddress(200, alert_addr['address'])
    atx_to_recover = rpc_connection1.send(attacker_addr, 10)
    atx_to_recover = rpc_connection1.gettransaction(atx_to_recover)['hex']
    atx_to_recover = rpc_connection1.decoderawtransaction(atx_to_recover)
    rpc_connection1.generatetoaddress(1, alert_addr['address'])

    # assert
    time.sleep(3)
    assert atx_to_recover['hash'] in rpc_connection1.getbestblock()['atx']

    # recover tx
    amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])
    recovery_tx = rpc_connection1.createrecoverytransaction(atx_to_recover['hash'], {other_addr: amount_to_recover})
    recovery_tx = rpc_connection1.signrecoverytransaction(recovery_tx, [TEST_KEYS[0].priv], alert_addr['redeemScript'])
    recovery_txid = rpc_connection1.sendrawtransaction(recovery_tx['hex'])
    rpc_connection1.generatetoaddress(1, alert_addr['address'])

    # assert
    time.sleep(3)
    assert recovery_txid in rpc_connection1.getbestblock()['tx']
    assert recovery_txid in find_address(rpc_connection1.listreceivedbyaddress(), other_addr)['txids']

    rpc_connection1.gen(143, alert_addr['address'])

    # assert
    time.sleep(3)
    assert atx_to_recover['hash'] not in rpc_connection1.getbestblock()['tx']
    
    rpc_connection1.gen(200, alert_addr['address'])
    
    # assert
    time.sleep(3)
    assert find_address(rpc_connection1.listreceivedbyaddress(), attacker_addr)['amount'] == 0
    assert find_address(rpc_connection1.listreceivedbyaddress(), attacker_addr)['txids'] == []


def test_recovery_balance():
    alert_addr = rpc_connection1.getnewvaultalertaddress(TEST_KEYS[0].pub)
    other_addr = rpc_connection1.getnewaddress()
    attacker_addr = rpc_connection2.getnewaddress()
    addr_to_mine = '2MyvyKzR4iHgWnprW1o2jeFv9KehNfT5F7N'

    # send alert tx
    rpc_connection1.generatetoaddress(200, alert_addr['address'])  # 200
    assert rpc_connection1.getbalance() == (200 - COINBASE_MATURITY) * COINBASE_AMOUNT
    atx_to_recover = rpc_connection1.send(attacker_addr, 10)
    assert rpc_connection1.getbalance() + 10 < (200 - COINBASE_MATURITY) * COINBASE_AMOUNT
    atx_fee = (200 - COINBASE_MATURITY) * COINBASE_AMOUNT - 10 - rpc_connection1.getbalance()
    atx_to_recover = rpc_connection1.gettransaction(atx_to_recover)['hex']
    atx_to_recover = rpc_connection1.decoderawtransaction(atx_to_recover)
    rpc_connection1.generatetoaddress(1, addr_to_mine)  # 201

    # assert
    time.sleep(3)
    assert rpc_connection2.getbalance() == 0
    assert atx_to_recover['hash'] in rpc_connection1.getbestblock()['atx']

    # recover atx
    amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])
    atx_fee2 = COINBASE_AMOUNT - amount_to_recover
    assert atx_fee == atx_fee2
    recovery_tx = rpc_connection1.createrecoverytransaction(atx_to_recover['hash'], {other_addr: amount_to_recover})
    recovery_tx = rpc_connection1.signrecoverytransaction(recovery_tx, [TEST_KEYS[0].priv], alert_addr['redeemScript'])
    recovery_txid = rpc_connection1.sendrawtransaction(recovery_tx['hex'])
    rpc_connection1.generatetoaddress(1, addr_to_mine)  # 202

    # assert
    time.sleep(3)
    assert recovery_txid in rpc_connection1.getbestblock()['tx']
    assert recovery_txid in find_address(rpc_connection1.listreceivedbyaddress(), other_addr)['txids']
    assert rpc_connection1.getbalance() == (202 - COINBASE_MATURITY) * COINBASE_AMOUNT - atx_fee

    rpc_connection1.gen(143, addr_to_mine)  # 345

    # assert
    time.sleep(3)
    assert rpc_connection1.getbalance() == 200 * COINBASE_AMOUNT - atx_fee
    assert atx_to_recover['hash'] not in rpc_connection1.getbestblock()['tx']
    assert find_address(rpc_connection2.listreceivedbyaddress(), attacker_addr)['amount'] == 0
    assert find_address(rpc_connection2.listreceivedbyaddress(), attacker_addr)['txids'] == []
    assert find_address(rpc_connection1.listreceivedbyaddress(), other_addr)['amount'] == COINBASE_AMOUNT - atx_fee
    assert find_address(rpc_connection1.listreceivedbyaddress(), other_addr)['txids'] == [recovery_txid]


def main():
    RPCProxyWrapper.killall()
    rpc_connection1.reset()
    rpc_connection2.reset()
    wait_for_bvaultd(2)

    # construct_atx_from_utxo()
    # atx_from_alert_addr_to_normal_addr()
    # tx_from_normal_addr_to_alert_addr()
    # tx_from_normal_addr_to_normal_addr()
    # test_synchronization_when_restart()
    # test_synchronization_when_reset()
    # test_construct_recovery_tx()
    # test_recover_transaction()
    test_recovery_balance()

    print('all ok!')
