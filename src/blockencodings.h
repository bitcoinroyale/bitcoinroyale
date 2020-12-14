// Copyright (c) 2016-2018 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_BLOCKENCODINGS_H
#define BITCOIN_BLOCKENCODINGS_H

#include <primitives/block.h>

#include <memory>

class CTxMemPool;

// Dumb helper to handle CTransaction compression at serialize-time
template <typename T>
struct TransactionCompressor {
private:
    T& tx;
public:
    explicit TransactionCompressor(T& txIn) : tx(txIn) {}

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action) {
        READWRITE(tx); //TODO: Compress tx encoding
    }
};

class BlockTransactionsRequest {
public:
    // A BlockTransactionsRequest message
    uint256 blockhash;
    std::vector<uint16_t> indexes;
    std::vector<uint16_t> aindexes;

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action) {
        READWRITE(blockhash);

        auto readWriteIndexes = [&] (std::vector<uint16_t>& idxs, uint64_t idxs_size) {
            READWRITE(COMPACTSIZE(idxs_size));

            if (ser_action.ForRead()) {
                size_t i = 0;
                while (idxs.size() < idxs_size) {
                    idxs.resize(std::min((uint64_t)(1000 + idxs.size()), idxs_size));
                    for (; i < idxs.size(); i++) {
                        uint64_t index = 0;
                        READWRITE(COMPACTSIZE(index));
                        if (index > std::numeric_limits<uint16_t>::max())
                            throw std::ios_base::failure("index overflowed 16 bits");
                        idxs[i] = index;
                    }
                }

                int32_t offset = 0;
                for (size_t j = 0; j < idxs.size(); j++) {
                    if (int32_t(idxs[j]) + offset > std::numeric_limits<uint16_t>::max())
                        throw std::ios_base::failure("indexes overflowed 16 bits");
                    idxs[j] = idxs[j] + offset;
                    offset = int32_t(idxs[j]) + 1;
                }
            } else {
                for (size_t i = 0; i < idxs.size(); i++) {
                    uint64_t index = idxs[i] - (i == 0 ? 0 : (idxs[i - 1] + 1));
                    READWRITE(COMPACTSIZE(index));
                }
            }
        };

        uint64_t indexes_size = (uint64_t)indexes.size();
        readWriteIndexes(indexes, indexes_size);

        uint64_t aindexes_size = (uint64_t)aindexes.size();
        readWriteIndexes(aindexes, aindexes_size);
    }
};

class BlockTransactions {
public:
    // A BlockTransactions message
    uint256 blockhash;
    std::vector<CTransactionRef> txn;
    std::vector<CAlertTransactionRef> atxn;

    BlockTransactions() {}
    explicit BlockTransactions(const BlockTransactionsRequest& req) :
        blockhash(req.blockhash), txn(req.indexes.size()), atxn(req.aindexes.size()) {}

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action) {
        READWRITE(blockhash);
        uint64_t txn_size = (uint64_t)txn.size();
        READWRITE(COMPACTSIZE(txn_size));
        if (ser_action.ForRead()) {
            size_t i = 0;
            while (txn.size() < txn_size) {
                txn.resize(std::min((uint64_t)(1000 + txn.size()), txn_size));
                for (; i < txn.size(); i++)
                    READWRITE(TransactionCompressor<CTransactionRef>(txn[i]));
            }
        } else {
            for (size_t i = 0; i < txn.size(); i++)
                READWRITE(TransactionCompressor<CTransactionRef>(txn[i]));
        }

        uint64_t atxn_size = (uint64_t)atxn.size();
        READWRITE(COMPACTSIZE(atxn_size));
        if (ser_action.ForRead()) {
            size_t i = 0;
            while (atxn.size() < atxn_size) {
                atxn.resize(std::min((uint64_t)(1000 + atxn.size()), atxn_size));
                for (; i < atxn.size(); i++)
                    READWRITE(TransactionCompressor<CAlertTransactionRef>(atxn[i]));
            }
        } else {
            for (size_t i = 0; i < atxn.size(); i++)
                READWRITE(TransactionCompressor<CAlertTransactionRef>(atxn[i]));
        }
    }
};

// Dumb serialization/storage-helper for CBlockHeaderAndShortTxIDs and PartiallyDownloadedBlock
template <typename T>
struct PrefilledTransaction {
    // Used as an offset since last prefilled tx in CBlockHeaderAndShortTxIDs,
    // as a proper transaction-in-block-index in PartiallyDownloadedBlock
    uint16_t index;
    T tx;

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action) {
        uint64_t idx = index;
        READWRITE(COMPACTSIZE(idx));
        if (idx > std::numeric_limits<uint16_t>::max())
            throw std::ios_base::failure("index overflowed 16-bits");
        index = idx;
        READWRITE(TransactionCompressor<T>(tx));
    }
};

typedef enum ReadStatus_t
{
    READ_STATUS_OK,
    READ_STATUS_INVALID, // Invalid object, peer is sending bogus crap
    READ_STATUS_FAILED, // Failed to process object
    READ_STATUS_CHECKBLOCK_FAILED, // Used only by FillBlock to indicate a
                                   // failure in CheckBlock.
} ReadStatus;

class CBlockHeaderAndShortTxIDs {
private:
    mutable uint64_t shorttxidk0, shorttxidk1;
    uint64_t nonce;

    void FillShortTxIDSelector() const;

    friend class PartiallyDownloadedBlock;

    static const int SHORTTXIDS_LENGTH = 6;
protected:
    std::vector<uint64_t> shorttxids;
    std::vector<uint64_t> shortatxids;
    std::vector<PrefilledTransaction<CTransactionRef>> prefilledtxn;
    std::vector<PrefilledTransaction<CAlertTransactionRef>> prefilledatxn;

public:
    CBlockHeader header;

    // Dummy for deserialization
    CBlockHeaderAndShortTxIDs() {}

    CBlockHeaderAndShortTxIDs(const CBlock& block, bool fUseWTXID);

    uint64_t GetShortID(const uint256& txhash) const;

    size_t BlockTxCount() const { return shorttxids.size() + prefilledtxn.size(); }

    size_t BlockAlertTxCount() const { return shortatxids.size() + prefilledatxn.size(); }

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action) {
        READWRITE(header);
        READWRITE(nonce);

        auto readWiteShortTxIds = [&] (std::vector<uint64_t>& txids) {
            uint64_t shorttxids_size = (uint64_t)txids.size();
            READWRITE(COMPACTSIZE(shorttxids_size));
            if (ser_action.ForRead()) {
                size_t i = 0;
                while (txids.size() < shorttxids_size) {
                    txids.resize(std::min((uint64_t)(1000 + txids.size()), shorttxids_size));
                    for (; i < txids.size(); i++) {
                        uint32_t lsb = 0; uint16_t msb = 0;
                        READWRITE(lsb);
                        READWRITE(msb);
                        txids[i] = (uint64_t(msb) << 32) | uint64_t(lsb);
                        static_assert(SHORTTXIDS_LENGTH == 6, "shorttxids serialization assumes 6-byte shorttxids");
                    }
                }
            } else {
                for (size_t i = 0; i < txids.size(); i++) {
                    uint32_t lsb = txids[i] & 0xffffffff;
                    uint16_t msb = (txids[i] >> 32) & 0xffff;
                    READWRITE(lsb);
                    READWRITE(msb);
                }
            }
        };

        readWiteShortTxIds(shorttxids);
        READWRITE(prefilledtxn);

        if (BlockTxCount() > std::numeric_limits<uint16_t>::max())
            throw std::ios_base::failure("indexes overflowed 16 bits");

        readWiteShortTxIds(shortatxids);
        READWRITE(prefilledatxn);

        if (BlockAlertTxCount() > std::numeric_limits<uint16_t>::max())
            throw std::ios_base::failure("alert indexes overflowed 16 bits");

        if (ser_action.ForRead())
            FillShortTxIDSelector();
    }
};

class PartiallyDownloadedBlock {
protected:
    std::vector<CTransactionRef> txn_available;
    std::vector<CAlertTransactionRef> atxn_available;
    size_t prefilled_count = 0, mempool_count = 0, extra_count = 0;
    CTxMemPool* pool;
public:
    CBlockHeader header;
    explicit PartiallyDownloadedBlock(CTxMemPool* poolIn) : pool(poolIn) {}

    // extra_txn is a list of extra transactions to look at, in <witness hash, reference> form
    ReadStatus InitData(const CBlockHeaderAndShortTxIDs& cmpctblock, const std::vector<std::pair<uint256, CTransactionRef>>& extra_txn);
    bool IsTxAvailable(size_t index) const;
    bool IsAlertTxAvailable(size_t index) const;
    ReadStatus FillBlock(CBlock& block, const std::vector<CTransactionRef>& vtx_missing, const std::vector<CAlertTransactionRef>& vatx_missing);
private:
    ReadStatus InitTxData(const CBlockHeaderAndShortTxIDs& cmpctblock, const std::vector<std::pair<uint256, CTransactionRef>>& extra_txn);
    ReadStatus InitAlertTxData(const CBlockHeaderAndShortTxIDs& cmpctblock, const std::vector<std::pair<uint256, CTransactionRef>>& extra_txn);
};

#endif // BITCOIN_BLOCKENCODINGS_H
