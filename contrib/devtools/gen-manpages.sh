#!/usr/bin/env bash

export LC_ALL=C
TOPDIR=${TOPDIR:-$(git rev-parse --show-toplevel)}
BUILDDIR=${BUILDDIR:-$TOPDIR}

BINDIR=${BINDIR:-$BUILDDIR/src}
MANDIR=${MANDIR:-$TOPDIR/doc/man}

BVAULTD=${BVAULTD:-$BINDIR/bvaultd}
BITCOINCLI=${BITCOINCLI:-$BINDIR/bvault-cli}
BITCOINTX=${BITCOINTX:-$BINDIR/bitcoin-tx}
WALLET_TOOL=${WALLET_TOOL:-$BINDIR/bitcoin-wallet}
BITCOINQT=${BITCOINQT:-$BINDIR/qt/bvault-qt}

[ ! -x $BVAULTD ] && echo "$BVAULTD not found or not executable." && exit 1

# The autodetected version git tag can screw up manpage output a little bit
BTCVER=($($BITCOINCLI --version | head -n1 | awk -F'[ -]' '{ print $6, $7 }'))

# Create a footer file with copyright content.
# This gets autodetected fine for bvaultd if --version-string is not set,
# but has different outcomes for bvault-qt and bvault-cli.
echo "[COPYRIGHT]" > footer.h2m
$BVAULTD --version | sed -n '1!p' >> footer.h2m

for cmd in $BVAULTD $BITCOINCLI $BITCOINTX $WALLET_TOOL $BITCOINQT; do
  cmdname="${cmd##*/}"
  help2man -N --version-string=${BTCVER[0]} --include=footer.h2m -o ${MANDIR}/${cmdname}.1 ${cmd}
  sed -i "s/\\\-${BTCVER[1]}//g" ${MANDIR}/${cmdname}.1
done

rm -f footer.h2m
