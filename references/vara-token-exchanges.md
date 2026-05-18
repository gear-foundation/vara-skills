# Vara Token Exchanges

Where the VARA token (native asset of Vara Network) is listed for trading on centralized exchanges. Lookup-only — for on-chain interaction patterns see `vara-network-endpoints.md`, and for the Ethereum-bridged form see `vara-eth-bridge-flows.md`.

## Centralized Exchanges

| Exchange | Pair(s) | Listing / Price Page |
|----------|---------|----------------------|
| Coinbase | VARA-USD, VARA-USDT, VARA-BTC | `https://www.coinbase.com/price/vara` |
| Gate | VARA/USDT | `https://www.gate.com/trade/VARA_USDT` |
| Crypto.com | VARA spot | `https://crypto.com/en/price/vara-network` |

Coinbase added VARA support in 2024 with the VARA-USD pair launched in phases. Gate.io was the launch venue (January 2024) and historically the deepest VARA/USDT market. Crypto.com lists VARA on its centralized exchange and price index.

## Verification

Exchange listings, available pairs, and per-region availability change. Before quoting any pair or URL to a user — especially inside generated frontend copy or `vara-brand-system` artifacts — open the listing page above and confirm the pair is still active. Treat this file as a starting point, not a source of truth.

For aggregate views across all listing venues (including DEXes and ones not covered here), CoinGecko's `vara-network` page and CoinMarketCap's `vara-network` page maintain a markets list.

## Related References

- `vara-network-endpoints.md` — RPC, explorers, SS58 format, **testnet faucet** (note: faucet gives free testnet VARA, not mainnet — "buy VARA" and "get testnet VARA" are distinct flows)
- `vara-eth-bridge-flows.md` — bridge between Vara mainnet and Ethereum for users holding the wrapped form
- `vara-eth-bridge-contracts.md` — bridge contract addresses and bridged token program IDs
