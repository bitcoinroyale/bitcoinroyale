#ifndef BITCOIN_POLICY_AUXPOW_H
#define BITCOIN_POLICY_AUXPOW_H

#include <uint256.h>
#include <set>

// A list of pre-hardfork mainnet blocks that have the auxpow flag set to 1,
// despite not having the auxpow header. We have to manually recognize them as
// not merged-mined.

const std::set<uint256> FAKE_AUXPOW_PREFORK_BLOCKS {
    uint256S("00000000000000002027ff541d87aa8c8f86b6c9a0d382e64317fd0759a3e059"),
    uint256S("00000000000000001f681336cb01354a5f61116fd7441822b4dfa43ee000ecc2"),
    uint256S("0000000000000000297cdc35b437991e391665d027bde8e3e67bfa3cb4364911"),
    uint256S("00000000000000000491ee8ac245c4cc31e64ee1e5d00ae9b0d258c17dd97ad1")
};
 
bool IsFakeAuxpowPreforkBlock(const uint256& hash);

#endif //BITCOIN_POLICY_AUXPOW_H
