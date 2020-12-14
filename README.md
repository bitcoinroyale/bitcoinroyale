Bitcoin Vault
==============

https://bitcoinvault.global

What is Bitcoin Vault?
-----------------------

Bitcoin Vault is a proposal for a digital currency based on Bitcoin which is focused on creating the best possible store of value and addressing the problem of theft.

For more information, read the [original whitepaper](https://bitcoinvault.global/bitcoinvault.pdf). For discussions about the whitepaper and the protocol, see [this repository](https://github.com/bitcoinvault/whitepaper).

| | |
|-----------|-----------------------|
| **Coin name** | BTCV |
| **Premine / ICO** | none |
| **Total number of coins** | 21,000,000 BTCV (like Bitcoin) |
| **Initial block reward** | 175 BTCV ([full schedule](https://github.com/bitcoinroyale/whitepaper/issues/14)) |
| **Average block time** | 10 minutes (like Bitcoin) |
| **Algorithm** | SHA256 PoW (like Bitcoin) |

----

License
-------

This example implementation of the Bitcoin Vault protocol is based on a fork of Bitcoin Core. Similarly, it is released under the terms of the MIT license. See [COPYING](COPYING) for more information or see https://opensource.org/licenses/MIT.

Development Process
-------------------

Bitcoin Vault is an open community project. Anyone in the community can make suggestions regarding modifications and offer a reference implementation. Miners and full nodes ultimately choose whether to accept these changes and upgrade.

The contribution workflow is described in [CONTRIBUTING.md](CONTRIBUTING.md) and useful hints for developers can be found in [doc/developer-notes.md](doc/developer-notes.md).

Testing
-------

Testing code modifications is critical before adopting any proposed codebase changes. You have the responsibility to test and verify that the code behaves according to the well accepted protocol. To assist with this process, see [TESTING.md](TESTING.md).

Installing
----------

For build and installation instructions, see [INSTALL.md](INSTALL.md). The file also contains the main differences in naming from Bitcoin Core, such as `bvaultd` instead of `bitcoind`.

Fair Play
---------

Similar to Bitcoin, Bitcoin Vault is a decentralized community-driven project. The authors of this reference implemntation provide no guarantees to its completeness, accuracy or future roadmap. You may become a member of the community by working on your own reference implementation or participating as a contributor on this one.
