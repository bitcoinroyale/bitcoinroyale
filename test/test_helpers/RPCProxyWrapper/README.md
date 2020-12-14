RPCProxyWrapper.py contains proxy wrapper for bvaultd JSON-RPC. Requires python >= 3.6. Basic usage:

```python
>>> from RPCProxyWrapper import *
>>> rpc_connection = RPCProxyWrapper(rpcport=18887, rpcuser='user', rpcpass='pass')
>>> rpc_connection.getnewaddress()
'2NFt1A4Mp9Ki1KvpRdhyebvAhCX2ye2NmS9'
```

Basically this tool is supposed to be used instead of `bvaultd-cli` and provides the same functionalities. See `main.py` for more examples.
