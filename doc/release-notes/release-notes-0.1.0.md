Bitcoin Vault core version 0.1.0 is now available from https://github.com/bitcoinvault/bitcoinvault/releases.

Initial release
===============

This is the first release of the github.com/bitcoinvault reference implementation. This release is based on Bitcoin Core 0.18.0.

This Bitcoin Vault protocol implementation is still work in progress and contains the minimum feature set required for starting the expedited bootstrap period defined in the protocol.

Notable features
================

2MB block size
--------------

The protocol requires that eventually an alert section will be added to the block. This means that all transactions will placed in blocks twice - once in the alerts and once more as committed transactions. To prepare for this redundancy, the default 1MB block size of Bitcoin has been doubled in Bitcoin Vault.

Protocol params
---------------

The various protocol defining params like the genesis block, activation block number of various BIPs, address prefixes have been adapted to Bitcoin Vault.

Expedited reward schedule
-------------------------

The reward schedule of Bitcoin has been modified to create a shorter catch-up period. The schedule is defined in BRIP-3 since it was modified from the original white paper and increased in duration from 1 year to 4.5 years.

Per block difficulty
--------------------

Bitcoin's default difficulty adjustment algorithm has been changed. Instead of difficulty updates every 2 weeks, the protocol now updates difficulty after every block. The chosen difficulty adjustment algorithm is LWMA by zawy12.

E2E Testing
-----------

To assist community contributors in pushing code, a manual end-to-end test has been added as a form of QA process to verify the system is operational. In future versions this test should be automated.

Branding
--------

Since the original codebase is Bitcoin Core, all branding of "Bitcoin" has been converted to "Bitcoin Vault". This includes executables which have been renamed to `bvault*` and the coin itself that is named `BTCV`.

0.1.0 Change log
================

Block size:
- `48418d67` Block size: doubled

Difficulty:
- `2fd851c0` Merge pull request #1 from tazman97-BR/difficulty_per_block
- `b5accc9f` #include cleanup
- `f696acd2` LWMA DAA parameters (BRIP-3)
- `036b5ff4` zawy12 lwma difficulty adjustment algorithm
- `27759137` BRIP-3: LWMA parameter tuning, see pow-difficulty-simulations
- `07f76331` BRIP-3: parameter changed to 30 per discussion with zawy12

Rewards:
- `6298b7ee` Rewards: integration tests
- `fe35edd6` Rewards: implementation and unit tests
- `ba0f899f` BRIP-1: integration tests
- `b13d74e1` BRIP-1: implementation and unit tests

Params:
- `42e98109` Params: second testnet trial (new genesis)
- `28969cac` Params: first testnet trial
- `d26ac422` Params: address prefix, everything except genesis
- `a22149ce` Params: removed allowMinDifficultyBlocks from testnet
- `c6207670` Params: segwit deployment block height sensitive BIP
- `b8a65b42` Params: block height sensitive BIPs
- `fba3e364` Params: fixed unit tests due to address prefix change
- `788f0556` Params: change R addresses to be the script ones and the Y to legacy
- `1c20a0e0` Params: fixed functional tests due to address prefix change
- `33716831` Params: fixed minor typo in functional test
- `55f4fe00` Params: genesis block

Testing:
- `ccc4f004` Testing: added docs for testing process
- `ed2decba` Testing: print logs to debug unit tests
- `317bc8a6` Testing: improve robustness of test

Branding:
- `e8e4329b` Branding: root markdown files
- `dcc19279` Branding: github repo
- `e71fbef2` Branding: move default data dir
- `bf55dd87` Branding: rename bitcoin-cli binary
- `e7cbb511` Branding: rename bitcoin.conf
- `badd840e` Branding: rename bitcoind, fixed failing test
- `1c4123a8` Branding: rename bitcoind binary (in contrib)
- `8d981cb2` Branding: rename bitcoind binary
- `013da35b` Branding: Bitcoin Core
- `23eb67bd` Branding: org website
- `a2d3c3e5` Branding: improve README
- `787cfcce` Branding: fixed mistakes in Makefile due to binary renames
- `ec771662` Branding: updated new Bitcoin Vault files with the branding
- `4a0d4276` Branding: rename bitcoin-qt binary
- `f72e1473` Branding: coin name BTCV
- `92b46253` Branding: welcome message
- `1bd658d4` Branding: minor fix in README
- `af4eeec7` Branding: added coin metrics to README

Credits
=======

Thanks to everyone who contributed to this release:

- ianduoteli
- tazman97-BR
- zawy12