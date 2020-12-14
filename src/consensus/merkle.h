// Copyright (c) 2015-2018 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_CONSENSUS_MERKLE_H
#define BITCOIN_CONSENSUS_MERKLE_H

#include <stdint.h>
#include <vector>

#include <primitives/transaction.h>
#include <primitives/block.h>
#include <uint256.h>

uint256 ComputeMerkleRoot(std::vector<uint256> hashes, bool* mutated = nullptr);

/*
 * Compute the Merkle root of the transactions in a given vector.
 * *mutated is set to true if a duplicated subtree was found.
 */
template <typename T>
uint256 BlockMerkleRoot(const std::vector<T>& vtx, bool* mutated = nullptr)
{
    std::vector<uint256> leaves;
    leaves.resize(vtx.size());
    for (size_t s = 0; s < vtx.size(); s++) {
        leaves[s] = vtx[s]->GetHash();
    }
    return ComputeMerkleRoot(std::move(leaves), mutated);
}

/*
 * Compute the Merkle root of the witness transactions in a given vector.
 * *mutated is set to true if a duplicated subtree was found.
 */
template <typename T, typename U>
uint256 BlockWitnessMerkleRoot(const std::vector<T>& vtx, const std::vector<U>& vatx, bool* mutated = nullptr)
{
    std::vector<uint256> leaves;
    leaves.resize(vtx.size() + vatx.size());
    leaves[0].SetNull(); // The witness hash of the coinbase is 0.
    for (size_t s = 1; s < vtx.size(); s++) {
        leaves[s] = vtx[s]->GetWitnessHash();
    }
    for (size_t s = 0; s < vatx.size(); s++) {
        leaves[s] = vatx[s]->GetWitnessHash();
    }
    return ComputeMerkleRoot(std::move(leaves), mutated);
}

#endif // BITCOIN_CONSENSUS_MERKLE_H
