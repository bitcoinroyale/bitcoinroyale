New bvaultd RPC commands:

- `getnewvaultalertaddress "recovery_key" ( "label" "address_type" )`

  Creates and adds to the wallet an alert address which generates recoverable transaction alert when signed
  with 1 signature of 2 keys. It returns a json object with the address and redeemScript.


- `getnewvaultinstantaddress "instant_key" "recovery_key" ( "label" "address_type" )`

  Creates and adds to the wallet an instant/alert address which generates: recoverable transaction alert when signed
  with 1 signature of 3 keys and instant transaction when signed with 2 signatures of 3 keys.
  It returns a json object with the address and redeemScript.

  
- `createvaultalertaddress "alert_key" "recovery_key" ( "address_type" )`
  
  Creates a vault address which generates recoverable transaction alert when signed with 1 signature of 2 keys.
  It returns a json object with the address and redeemScript.

  
- `createvaultinstantaddress "alert_key" "instant_key" "recovery_key" ( "address_type" )`
  
  Creates an instant/alert address which generates: recoverable transaction alert when signed with 1 signature of 3 keys and instant transaction when signed with 2 signatures of 3 keys.
  It returns a json object with the address and redeemScript.


- `createrecoverytransaction "atxid" [{"address":amount},{"data":"hex"},...] ( locktime replaceable )`

  Create a transaction recovering given alert id and creating new outputs.
  Outputs can be addresses or data.
  Returns hex-encoded raw transaction.
  Note that the transaction's inputs are not signed, and it is not stored in the wallet or transmitted to the network.


- `signrecoverytransaction "hexstring" ["privatekey",...] "redeemScript" ( "witnessScript" "sighashtype" )`

  Sign inputs for raw recovery transaction (serialized, hex-encoded).
  The second argument is an array of base58-encoded private
  keys that will be the only keys used to sign the transaction.
  The third argument is address redeem script.
 
 
- `signinstanttransaction "hexstring" ["privatekey",...] ( [{"txid":"hex","vout":n,"scriptPubKey":"hex","redeemScript":"hex","witnessScript":"hex","amount":amount},...] "sighashtype" )`

  Sign inputs for raw instant transaction (serialized, hex-encoded).
  The second argument is an array of base58-encoded private
  keys that will be the only keys used to sign the transaction.
  The third optional argument (may be null) is an array of previous transaction outputs that
  this transaction depends on but may not yet be in the block chain.
  
  
- `signalerttransaction "hexstring" ( [{"txid":"hex","vout":n,"scriptPubKey":"hex","redeemScript":"hex","witnessScript":"hex","amount":amount},...] "sighashtype" )`
  
  Sign inputs for raw alert transaction (serialized, hex-encoded).
  The second optional argument (may be null) is an array of previous transaction outputs that
  this transaction depends on but may not yet be in the block chain.

- `sendalerttoaddress "address" amount ( "comment" "comment_to" subtractfeefromamount replaceable conf_target "estimate_mode" )`
  Send an amount to a given address as alert.

- `sendinstanttoaddress "address" amount ( ["privatekey",...] "comment" "comment_to" subtractfeefromamount replaceable conf_target "estimate_mode" )`
  Send an amount to a given address as instant transaction.

- `getalertbalance ( "dummy" minconf include_watchonly )`
  Returns the total available balance on alert and instant addresses.
  The available balance is what the wallet considers currently spendable, and is
  thus affected by options which limit spendability such as -spendzeroconfchange.

- `getinstantbalance ( "dummy" minconf include_watchonly )`
  Returns the total available balance on instant addresses.
  The available balance is what the wallet considers currently spendable, and is
  thus affected by options which limit spendability such as -spendzeroconfchange.

Basic end-user flow:
```bash
$ bvaultd-cli getnewvaultalertaddress '02ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c'
  {
    "address": "2Mt65Q7ARUYhev6HXtDCrxWbFYF8XJ2T2wG",
    "redeemScript": "63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52ae"
  }
$ # get some coins
$ bvaultd-cli sendtoaddress '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi' 10  # sign with wallet key and send alert transaction from alert address
  c2119cf6ae1d89e19d0b566f70b55f27ceb8395bca29977b96d8a6a2aaef82cd
$ bvaultd-cli createrecoverytransaction '"c2119cf6ae1d89e19d0b566f70b55f27ceb8395bca29977b96d8a6a2aaef82cd"' '[{"2NCQR2117wUpqXT4euTMVQFXApNQAh3AMS9": 174.99}]' 
  020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d94340000000000ffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000
$ bvaultd-cli signrecoverytransaction '"020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d94340000000000ffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000"' '["cRfYLWua6WcpGbxuv5rJgA2eDESWxqgzmQjKQuqDFMfgbnEpqhrP"]' '"63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52ae"'
  {
      "hex": "020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d943400000000df00473044022058f01583834e4d8ba2bceae550bdb484af8575c24403104adf2134c5b4130f13022048147bf5f6d69a827526377c8eb66ffc7b8ff38d581874e89c53fb185bf3869f014730440220224754a6b0bd96a601da0d282fad309fc8ab720d023f891cc3eec3dc3446bc4c022034495280624ae006004700d0daba9d1f741584a177256341abd8a4e442acc8760101004b63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52aeffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000",
      "complete": true
  }
$ bvaultd-cli sendrawtransaction "020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d943400000000df00473044022058f01583834e4d8ba2bceae550bdb484af8575c24403104adf2134c5b4130f13022048147bf5f6d69a827526377c8eb66ffc7b8ff38d581874e89c53fb185bf3869f014730440220224754a6b0bd96a601da0d282fad309fc8ab720d023f891cc3eec3dc3446bc4c022034495280624ae006004700d0daba9d1f741584a177256341abd8a4e442acc8760101004b63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52aeffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000"
  714e5433cd70f6fe827a0e0b4db0835161de66ff5ad2fa1c7445640069880e18
```
```python
>>> from RPCProxyWrapper import *
>>> conn = RPCProxyWrapper(rpcport=18887, rpcuser='user', rpcpass='pass')
>>> conn.getnewvaultalertaddress('02ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c')
    {
        "address": "2Mt65Q7ARUYhev6HXtDCrxWbFYF8XJ2T2wG",
        "redeemScript": "63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52ae"
    }
>>> # get some coins
>>> conn.send('2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi', 10)
    c2119cf6ae1d89e19d0b566f70b55f27ceb8395bca29977b96d8a6a2aaef82cd
>>> conn.createrecoverytransaction('c2119cf6ae1d89e19d0b566f70b55f27ceb8395bca29977b96d8a6a2aaef82cd' [{'2NCQR2117wUpqXT4euTMVQFXApNQAh3AMS9': 174.99}])
    020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d94340000000000ffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000
>>> conn.signrecoverytransaction('020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d94340000000000ffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000', ['cRfYLWua6WcpGbxuv5rJgA2eDESWxqgzmQjKQuqDFMfgbnEpqhrP'], '63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52ae')
    {
          "hex": "020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d943400000000df00473044022058f01583834e4d8ba2bceae550bdb484af8575c24403104adf2134c5b4130f13022048147bf5f6d69a827526377c8eb66ffc7b8ff38d581874e89c53fb185bf3869f014730440220224754a6b0bd96a601da0d282fad309fc8ab720d023f891cc3eec3dc3446bc4c022034495280624ae006004700d0daba9d1f741584a177256341abd8a4e442acc8760101004b63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52aeffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000",
          "complete": true
    }
>>> conn.sendrawtransaction('020000000108631a1eb168d3f55785c45945fa2fa069b6365dec687df787bb44c8354d943400000000df00473044022058f01583834e4d8ba2bceae550bdb484af8575c24403104adf2134c5b4130f13022048147bf5f6d69a827526377c8eb66ffc7b8ff38d581874e89c53fb185bf3869f014730440220224754a6b0bd96a601da0d282fad309fc8ab720d023f891cc3eec3dc3446bc4c022034495280624ae006004700d0daba9d1f741584a177256341abd8a4e442acc8760101004b63516752682103c10bb9a7cabc41b28251cf4dfeb9da199696157052ecedf7b03647dd2f22b89a2102ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c52aeffffffff0100ca9a3b0000000017a914d2275731482d31473695126727c442339dd7b50b8700000000')
    714e5433cd70f6fe827a0e0b4db0835161de66ff5ad2fa1c7445640069880e18
```

See `RPCProxyWrapper/main.py` for more advanced usage.

Also see `test/functional/feature_alerts.py` for automated functional tests.

Suggested bvaultd run arguments for testing purposes:
- instance 1: `-regtest -rpcuser=user -rpcpassword=pass -rpcport=18887 -port=18444 -datadir="${HOME}/.bvault1" -addnode=127.0.0.1:18445 -txindex -reindex`
- instance 2: `-regtest -rpcuser=user -rpcpassword=pass -rpcport=18888 -port=18445 -datadir="${HOME}/.bvault2" -addnode=127.0.0.1:18444 -txindex -reindex`
