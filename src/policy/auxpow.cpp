#include <policy/auxpow.h>

bool IsFakeAuxpowPreforkBlock(const uint256& hash) {
    return FAKE_AUXPOW_PREFORK_BLOCKS.find(hash) != FAKE_AUXPOW_PREFORK_BLOCKS.end();
}
