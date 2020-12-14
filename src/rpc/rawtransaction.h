// Copyright (c) 2017-2018 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_RPC_RAWTRANSACTION_H
#define BITCOIN_RPC_RAWTRANSACTION_H

class CBaseTransaction;
class CBasicKeyStore;
struct CMutableTransaction;
class UniValue;
class uint256;

namespace interfaces {
class Chain;
} // namespace interfaces


void TxToJSON(const CBaseTransaction& tx, const uint256 hashBlock, const vaulttxntype txType, const vaulttxnstatus txStatus, UniValue& entry);

/** Sign a transaction with the given keystore and previous transactions */
UniValue SignTransaction(interfaces::Chain& chain, CMutableTransaction& mtx, const UniValue& prevTxs, CBasicKeyStore *keystore, bool tempKeystore, const UniValue& hashType, bool expectSpent = false, vaulttxntype txType = TX_INVALID);

/** Create a transaction from univalue parameters */
CMutableTransaction ConstructTransaction(const UniValue& inputs_in, const UniValue& outputs_in, const UniValue& locktime, const UniValue& rbf);

#endif // BITCOIN_RPC_RAWTRANSACTION_H
