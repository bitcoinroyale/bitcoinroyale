from authproxy import AuthServiceProxy, HTTP_TIMEOUT, JSONRPCException
from pathlib import Path


class RPCProxyWrapper(AuthServiceProxy):
    def __init__(self, rpcport, rpcuser, rpcpass, datadir=None, service_name=None, timeout=HTTP_TIMEOUT, connection=None):
        self.timeout = timeout
        self.connection = connection
        self.service_name = service_name
        self.datadir = datadir
        self.rpcport = rpcport
        self.rpcuser = rpcuser
        self.rpcpass = rpcpass

        super().__init__(f"http://{self.rpcuser}:{self.rpcpass}@127.0.0.1:{self.rpcport}", self.service_name, self.timeout, self.connection)

    @classmethod
    def killall(cls):
        import psutil
        import signal
        import time

        [p.send_signal(signal.SIGINT) for p in psutil.process_iter() if p.name() == 'bvaultd']
        time.sleep(2)
        [p.kill() for p in psutil.process_iter() if p.name() == 'bvaultd']
        if 'bvaultd' in [p.name() for p in psutil.process_iter()]: raise RuntimeError('looks like bvaultd is still running')

    def reset(self):
        import os
        import shutil

        if not self.datadir: raise RuntimeError('datadir not set')
        if os.path.exists(self.datadir): shutil.rmtree(self.datadir)
        os.mkdir(self.datadir)

    def listreceivedbyaddress(self, minconf=1, include_empty=True, include_watchonly=True):
        return self.__getattr__('listreceivedbyaddress')(minconf, include_empty, include_watchonly)

    def getblockbyheight(self, height):
        hash = self.__getattr__('getblockhash')(height)
        return self.__getattr__('getblock')(hash)

    def getbestblock(self):
        hash = self.__getattr__('getbestblockhash')()
        return self.__getattr__('getblock')(hash)

    def getrawtransaction(self, txhash, verbose=True):
        return self.__getattr__('getrawtransaction')(txhash, verbose)

    def send(self, addr, amount):
        return self.__getattr__('sendtoaddress')(addr, amount)

    def gen(self, amount, addr):
        return self.__getattr__('generatetoaddress')(amount, addr)

    def get_script_pubkey(self, txid, vout_n):
        txhex = self.gettransaction(txid)['hex']
        tx = self.decoderawtransaction(txhex)
        return tx['vout'][vout_n]['scriptPubKey']


class __test_key:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv


TEST_KEYS = [__test_key("02ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c",
                        "cRfYLWua6WcpGbxuv5rJgA2eDESWxqgzmQjKQuqDFMfgbnEpqhrP"),
             __test_key("0263451a52f3d3ae6918969e1c5ce934743185578481ef8130336ad1726ba61ddb",
                        "cN1XR72dusJgxpkT2AwENtTviskB96iB2Q6FTvAxqi24fT9DQZiR")]

COINBASE_MATURITY = 100
COINBASE_AMOUNT = 175

conn = conn1 = RPCProxyWrapper(rpcport=18887, rpcuser='user', rpcpass='pass', datadir=Path.home() / '.bvault1')
conn2 = RPCProxyWrapper(rpcport=18888, rpcuser='user', rpcpass='pass', datadir=Path.home() / '.bvault2')


def print_json(*args, **kwargs):
    import simplejson
    print(simplejson.dumps(*args, sort_keys=True, indent=4), **kwargs)


def find_vout_n(rawtransaction, amount):
    for vout in rawtransaction['vout']:
        if vout['value'] == amount: return vout['n']

    raise RuntimeError('vout not found')


def find_address(listreceivedbyaddress, address):
    for addr in listreceivedbyaddress:
        if addr['address'] == address: return addr

    raise RuntimeError('address not found')


def wait_for_bvaultd(num_instances):
    import psutil
    input(f'Start {num_instances} bvaultd daemons and input anything to continue...')
    if [p.name() for p in psutil.process_iter()].count('bvaultd') != num_instances: raise RuntimeError('looks like bvaultd is still running')
