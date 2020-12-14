#!/usr/bin/env bash

echo --- STARTING NETWORK

bvault-qt -regtest -datadir=./node1-miner/ -rpcport=16111 -rpcuser=bitcoinrpc -rpcpassword=123456 -listen -port=17111 -connect=127.0.0.1:17222 -server -deprecatedrpc=generate &
bvault-qt -regtest -datadir=./node2-peer/ -rpcport=16222 -rpcuser=bitcoinrpc -rpcpassword=123456 -listen -port=17222 -connect=127.0.0.1:17111 -server &
sleep 4
bvault-cli -regtest -datadir=./node1-miner/ -rpcport=16111 -rpcuser=bitcoinrpc -rpcpassword=123456 generate 101

echo --- DONE