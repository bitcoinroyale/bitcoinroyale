RPC method differences between Bitcoin and BitcoinVault
==============
BitcoinVault node is a direct fork of BitcoinCore so most of the RPC methods are identical. As the development of BTCV is still in progress, it is natural that some changes appeared in current methods and there are some new methods not included in BitcoinCore. The goal of this file is to list all differences between Bitcoin and BitcoinVault in terms of RPC interface and keep this list up-to-date to let users understands easier what is it all about. To keep in mind, if this file doesn't dispel your doubts, look at official documentation of BitcoinCore RPC methods. If all of above fails it is still possible that this file is out-of-date - then feel free to contribute.

### Mining

##### submitauxblock

Merge-mining related method. Implemented according to Namecoin's merge-mining specification.

```bash
Submits a solved auxpow for a block that was previously created by 'createauxblock'.

Arguments:
1. hash      (string, required) Hash of the block to submit
2. auxpow    (string, required) Serialised auxpow found

Result:
 (boolean) Whether the submitted block was correct

Examples:
> bvault-cli submitauxblock "hash" "serialised auxpow"
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "submitauxblock", "params": ["hash" "serialised auxpow"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### createauxblock

Merge-mining related method. Implemented according to Namecoin's merge-mining specification.

```bash
Creates a new block and returns information required to merge-mine it.

Arguments:
1. address    (string, required) Payout address for the coinbase transaction

Result:
{
  "hash" : "hash", (string) Hash of the created block
  "chainid" : n, (numeric) Chain ID for this block
  "previousblockhash" : "hash", (string) Hash of the previous block
  "coinbasevalue" : n, (numeric) Value of the block's coinbase
  "bits" : "xxxxxxxx", (string) Compressed target of the block
  "height" : n, (numeric) Height of the block
}
Examples:
> bvault-cli createauxblock "address"
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "createauxblock", "params": ["address"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

### Util

##### createvaultalertaddress

3-keys related method.

```bash
Creates a vault address which generates recoverable transaction alert when signed with 1 signature of 2 keys.
It returns a json object with the address and redeemScript.

Arguments:
1. alert_key       (string, required) The hex-encoded public key used to generates transaction alerts
2. recovery_key    (string, required) The hex-encoded public key used to recover transaction alerts
3. address_type    (string, optional, default=legacy) The address type to use. Options are "legacy", "p2sh-segwit", and "bech32".

Result:
{
  "address":"alertaddress",  (string) The value of the new alert address.
  "redeemScript":"script"    (string) The string value of the hex-encoded redemption script.
}

Examples:

Create an alert address from 2 public keys
> bvault-cli createvaultalertaddress "\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\"" "\"03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626\""

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "createvaultalertaddress", "params": ["\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\"", "\"03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626\""] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### createvaultinstantaddress

3-keys related method.

```bash
Creates an instant/alert address which generates: recoverable transaction alert when signed with 1 signature of 3 keys and instant transaction when signed with 2 signatures of 3 keys.
It returns a json object with the address and redeemScript.

Arguments:
1. alert_key       (string, required) The hex-encoded public key used to generates transaction alerts
2. instant_key     (string, required) The hex-encoded public key used to generates instant transaction
3. recovery_key    (string, required) The hex-encoded public key used to recover transaction alerts
4. address_type    (string, optional, default=legacy) The address type to use. Options are "legacy", "p2sh-segwit", and "bech32".

Result:
{
  "address":"instantalertaddress",  (string) The value of the new instant/alert address.
  "redeemScript":"script"           (string) The string value of the hex-encoded redemption script.
}

Examples:

Create an instant alert address from 3 public keys
> bvault-cli createvaultinstantaddress "\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\"" "\"03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626\"" "\"039d4b4d19413c726b359351273e9d5249b7c184561ff1e920384b04079ae74f36\""

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "createvaultinstantaddress", "params": ["\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\"", "\"03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626\"", "\"039d4b4d19413c726b359351273e9d5249b7c184561ff1e920384b04079ae74f36\""] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

### Wallet

##### getnewvaultalertaddress

3-keys related method.

```bash
Creates an alert address which generates recoverable transaction alert when signed with 1 signature of 2 keys.
It returns a json object with the address and redeemScript.

Arguments:
1. recovery_key    (string, required) The hex-encoded public key used to recover transaction alerts
2. label           (string, optional) A label to assign the addresses to.
3. address_type    (string, optional, default=set by -addresstype) The address type to use. Options are "legacy", "p2sh-segwit", and "bech32".

Result:
{
  "address":"alertaddress",  (string) The value of the new alert address.
  "redeemScript":"script"    (string) The string value of the hex-encoded redemption script.
}

Examples:

Create an alert address with given recovery key public keys
> bvault-cli getnewvaultalertaddress "03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getnewvaultalertaddress", "params": ["03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### getnewvaultinstantaddress

3-keys related method.

```bash
Creates an instant/alert address which generates: recoverable transaction alert when signed with 1 signature of 3 keys and instant transaction when signed with 2 signatures of 3 keys.
It returns a json object with the address and redeemScript.

Arguments:
1. instant_key     (string, required) The hex-encoded public key used to generates instant transaction
2. recovery_key    (string, required) The hex-encoded public key used to recover transaction alerts
3. label           (string, optional) A label to assign the addresses to.
4. address_type    (string, optional, default=legacy) The address type to use. Options are "legacy", "p2sh-segwit", and "bech32".

Result:
{
  "address":"alertaddress",  (string) The value of the new instant/alert address.
  "redeemScript":"script"    (string) The string value of the hex-encoded redemption script.
}

Examples:

Create an instant alert address from 3 public keys
> bvault-cli getnewvaultinstantaddress "\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\"" "\"039d4b4d19413c726b359351273e9d5249b7c184561ff1e920384b04079ae74f36\""

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getnewvaultinstantaddress", "params": ["\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\"", "\"039d4b4d19413c726b359351273e9d5249b7c184561ff1e920384b04079ae74f36\""] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### createrecoverytransaction

3-keys related method.

```bash
Create a transaction recovering given alert id and creating new outputs.
Outputs can be addresses or data.
Returns hex-encoded raw transaction.
Note that the transaction's inputs are not signed, and
it is not stored in the wallet or transmitted to the network.

Arguments:
1. atxid                       (string, required) The transaction id
2. outputs                     (json array, required) a json array with outputs (key-value pairs), where none of the keys are duplicated.
                               That is, each address can only appear once and there can only be one 'data' object.
                               For compatibility reasons, a dictionary, which holds the key-value pairs directly, is also
                               accepted as second parameter.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTCV
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data
       },
       ...
     ]
3. locktime                    (numeric, optional, default=0) Raw locktime. Non-0 value also locktime-activates inputs
4. replaceable                 (boolean, optional, default=false) Marks this transaction as BIP125-replaceable.
                               Allows this transaction to be replaced by a transaction with higher fees. If provided, it is an error if explicit sequence numbers are incompatible.

Result:
"transaction"              (string) hex string of the transaction

Examples:
> bvault-cli createrecoverytransaction "\"myid\"" "[{\"address\":0.01}]"
> bvault-cli createrecoverytransaction "\"myid\"" "[{\"data\":\"00010203\"}]"
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "createrecoverytransaction", "params": ["\"myid\"", "[{\"address\":0.01}]"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "createrecoverytransaction", "params": ["\"myid\"", "[{\"data\":\"00010203\"}]"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### getalertbalance

3-keys related method.

```bash
Returns the total available balance on alert and instant addresses.
The available balance is what the wallet considers currently spendable, and is
thus affected by options which limit spendability such as -spendzeroconfchange.

Arguments:
1. dummy                (string, optional) Remains for backward compatibility. Must be excluded or set to "*".
2. minconf              (numeric, optional, default=0) Only include transactions confirmed at least this many times.
3. include_watchonly    (boolean, optional, default=false) Also include balance in watch-only addresses (see 'importaddress')

Result:
amount              (numeric) The total amount in BTCV received for this wallet.

Examples:

The total amount in the wallet with 1 or more confirmations
> bvault-cli getalertbalance 

The total amount in the wallet at least 6 blocks confirmed
> bvault-cli getalertbalance "*" 6

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getalertbalance", "params": ["*", 6] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### getinstantbalance

3-keys related method.

```bash
Returns the total available balance on instant addresses.
The available balance is what the wallet considers currently spendable, and is
thus affected by options which limit spendability such as -spendzeroconfchange.

Arguments:
1. dummy                (string, optional) Remains for backward compatibility. Must be excluded or set to "*".
2. minconf              (numeric, optional, default=0) Only include transactions confirmed at least this many times.
3. include_watchonly    (boolean, optional, default=false) Also include balance in watch-only addresses (see 'importaddress')

Result:
amount              (numeric) The total amount in BTCV received for this wallet.

Examples:

The total amount in the wallet with 1 or more confirmations
> bvault-cli getinstantbalance 

The total amount in the wallet at least 6 blocks confirmed
> bvault-cli getinstantbalance "*" 6

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getinstantbalance", "params": ["*", 6] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### sendalerttoaddress

3-keys related method.

```bash
Send an amount to a given address as alert.

Arguments:
1. address                  (string, required) The bitcoin address to send to.
2. amount                   (numeric or string, required) The amount in BTCV to send. eg 0.1
3. comment                  (string, optional) A comment used to store what the transaction is for.
                            This is not part of the transaction, just kept in your wallet.
4. comment_to               (string, optional) A comment to store the name of the person or organization
                            to which you're sending the transaction. This is not part of the 
                            transaction, just kept in your wallet.
5. subtractfeefromamount    (boolean, optional, default=false) The fee will be deducted from the amount being sent.
                            The recipient will receive less bitcoins than you enter in the amount field.
6. replaceable              (boolean, optional, default=fallback to wallet's default) Allow this transaction to be replaced by a transaction with higher fees via BIP 125
7. conf_target              (numeric, optional, default=fallback to wallet's default) Confirmation target (in blocks)
8. estimate_mode            (string, optional, default=UNSET) The fee estimate mode, must be one of:
                            "UNSET"
                            "ECONOMICAL"
                            "CONSERVATIVE"

Result:
"txid"                  (string) The transaction id.

Examples:
> bvault-cli sendalerttoaddress "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" 0.1
> bvault-cli sendalerttoaddress "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" 0.1 "donation" "seans outpost"
> bvault-cli sendalerttoaddress "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" 0.1 "" "" true
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "sendalerttoaddress", "params": ["1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd", 0.1, "donation", "seans outpost"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### sendinstanttoaddress

3-keys related method.

```bash
Send an amount to a given address as instant transaction.

Arguments:
1. address                  (string, required) The bitcoin address to send to.
2. amount                   (numeric or string, required) The amount in BTCV to send. eg 0.1
3. privkeys                 (json array, optional) A json array of base58-encoded private keys for signing
     [
       "privatekey",        (string) private key in base58-encoding
       ...
     ]
4. comment                  (string, optional) A comment used to store what the transaction is for.
                            This is not part of the transaction, just kept in your wallet.
5. comment_to               (string, optional) A comment to store the name of the person or organization
                            to which you're sending the transaction. This is not part of the 
                            transaction, just kept in your wallet.
6. subtractfeefromamount    (boolean, optional, default=false) The fee will be deducted from the amount being sent.
                            The recipient will receive less bitcoins than you enter in the amount field.
7. replaceable              (boolean, optional, default=fallback to wallet's default) Allow this transaction to be replaced by a transaction with higher fees via BIP 125
8. conf_target              (numeric, optional, default=fallback to wallet's default) Confirmation target (in blocks)
9. estimate_mode            (string, optional, default=UNSET) The fee estimate mode, must be one of:
                            "UNSET"
                            "ECONOMICAL"
                            "CONSERVATIVE"

Result:
"txid"                  (string) The transaction id.

Examples:
> bvault-cli sendinstanttoaddress "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" 0.1
> bvault-cli sendinstanttoaddress "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" 0.1 "donation" "seans outpost"
> bvault-cli sendinstanttoaddress "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" 0.1 "" "" true
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "sendinstanttoaddress", "params": ["1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd", 0.1, "donation", "seans outpost"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### signalerttransaction

3-keys related method.

```bash
Sign inputs for raw alert transaction (serialized, hex-encoded).
The second optional argument (may be null) is an array of previous transaction outputs that
this transaction depends on but may not yet be in the block chain.

Arguments:
1. hexstring                        (string, required) The transaction alert hex string
2. prevtxs                          (json array, optional) A json array of previous dependent transaction outputs
     [
       {                            (json object)
         "txid": "hex",             (string, required) The transaction id
         "vout": n,                 (numeric, required) The output number
         "scriptPubKey": "hex",     (string, required) script key
         "redeemScript": "hex",     (string) (required for P2SH) redeem script
         "witnessScript": "hex",    (string) (required for P2WSH or P2SH-P2WSH) witness script
         "amount": amount,          (numeric or string, required) The amount spent
       },
       ...
     ]
3. sighashtype                      (string, optional, default=ALL) The signature hash type. Must be one of:
                                    "ALL"
                                    "NONE"
                                    "SINGLE"
                                    "ALL|ANYONECANPAY"
                                    "NONE|ANYONECANPAY"
                                    "SINGLE|ANYONECANPAY"
                                    

Result:
{
  "hex" : "value",                  (string) The hex-encoded raw transaction with signature(s)
  "complete" : true|false,          (boolean) If the transaction has a complete set of signatures
  "errors" : [                      (json array of objects) Script verification errors (if there are any)
    {
      "txid" : "hash",              (string) The hash of the referenced, previous transaction
      "vout" : n,                   (numeric) The index of the output to spent and used as input
      "scriptSig" : "hex",          (string) The hex-encoded signature script
      "sequence" : n,               (numeric) Script sequence number
      "error" : "text"              (string) Verification or signing error related to the input
    }
    ,...
  ]
}

Examples:
> bvault-cli signalerttransaction "myhex"
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "signalerttransaction", "params": ["myhex"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### signinstanttransaction

3-keys related method.

```bash
Sign inputs for raw instant transaction (serialized, hex-encoded).
The second argument is an array of base58-encoded private
keys that will be the only keys used to sign the transaction.
The third optional argument (may be null) is an array of previous transaction outputs that
this transaction depends on but may not yet be in the block chain.

Arguments:
1. hexstring                        (string, required) The transaction alert hex string
2. privkeys                         (json array, required) A json array of base58-encoded private keys for signing
     [
       "privatekey",                (string) private key in base58-encoding
       ...
     ]
3. prevtxs                          (json array, optional) A json array of previous dependent transaction outputs
     [
       {                            (json object)
         "txid": "hex",             (string, required) The transaction id
         "vout": n,                 (numeric, required) The output number
         "scriptPubKey": "hex",     (string, required) script key
         "redeemScript": "hex",     (string) (required for P2SH) redeem script
         "witnessScript": "hex",    (string) (required for P2WSH or P2SH-P2WSH) witness script
         "amount": amount,          (numeric or string, required) The amount spent
       },
       ...
     ]
4. sighashtype                      (string, optional, default=ALL) The signature hash type. Must be one of:
                                    "ALL"
                                    "NONE"
                                    "SINGLE"
                                    "ALL|ANYONECANPAY"
                                    "NONE|ANYONECANPAY"
                                    "SINGLE|ANYONECANPAY"
                                    

Result:
{
  "hex" : "value",                  (string) The hex-encoded raw transaction with signature(s)
  "complete" : true|false,          (boolean) If the transaction has a complete set of signatures
  "errors" : [                      (json array of objects) Script verification errors (if there are any)
    {
      "txid" : "hash",              (string) The hash of the referenced, previous transaction
      "vout" : n,                   (numeric) The index of the output to spent and used as input
      "scriptSig" : "hex",          (string) The hex-encoded signature script
      "sequence" : n,               (numeric) Script sequence number
      "error" : "text"              (string) Verification or signing error related to the input
    }
    ,...
  ]
}

Examples:
> bvault-cli signinstanttransaction "myhex"
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "signinstanttransaction", "params": ["myhex"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

##### signrecoverytransaction

3-keys related method.

```bash
Sign inputs for raw recovery transaction (serialized, hex-encoded).
The second argument is an array of base58-encoded private
keys that will be the only keys used to sign the transaction.
The third argument is address redeem script.

Arguments:
1. hexstring            (string, required) The transaction alert hex string
2. privkeys             (json array, required) A json array of base58-encoded private keys for signing
     [
       "privatekey",    (string) private key in base58-encoding
       ...
     ]
3. redeemScript         (string, required) (required for P2SH) redeem script
4. witnessScript        (string) (required for P2WSH or P2SH-P2WSH) witness script
5. sighashtype          (string, optional, default=ALL) The signature hash type. Must be one of:
                        "ALL"
                        "NONE"
                        "SINGLE"
                        "ALL|ANYONECANPAY"
                        "NONE|ANYONECANPAY"
                        "SINGLE|ANYONECANPAY"
                        

Result:
{
  "hex" : "value",                  (string) The hex-encoded raw transaction with signature(s)
  "complete" : true|false,          (boolean) If the transaction has a complete set of signatures
  "errors" : [                      (json array of objects) Script verification errors (if there are any)
    {
      "txid" : "hash",              (string) The hash of the referenced, previous transaction
      "vout" : n,                   (numeric) The index of the output to spent and used as input
      "scriptSig" : "hex",          (string) The hex-encoded signature script
      "sequence" : n,               (numeric) Script sequence number
      "error" : "text"              (string) Verification or signing error related to the input
    }
    ,...
  ]
}

Examples:
> bvault-cli signrecoverytransaction "myhex"
> curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "signrecoverytransaction", "params": ["myhex"] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```