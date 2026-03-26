# Vara Network Endpoints

## Vara Network (Substrate)

| Network | WebSocket RPC | Purpose |
|---------|--------------|---------|
| Mainnet | `wss://rpc.vara.network` | Production |
| Testnet | `wss://testnet.vara.network` | Development and testing |

## Explorers

| Tool | URL | Use |
|------|-----|-----|
| Gear IDEA | `https://idea.gear-tech.io` | Program upload, message sending, state inspection |
| Vara Subscan | `https://vara.subscan.io` | Block and extrinsic browsing (mainnet) |
| Vara Testnet Subscan | `https://vara-testnet.subscan.io` | Block and extrinsic browsing (testnet) |

## Testnet Faucet

Get testnet VARA tokens from the Gear IDEA portal at `https://idea.gear-tech.io`. Connect a Substrate wallet and request tokens through the portal interface.

## Account And Address Format

- **SS58 prefix:** 137 (Vara-specific)
- **Token decimals:** 1 VARA = 10^12 minimal units
- **Existential deposit:** ~1 VARA on mainnet
- **Address converter:** `https://ss58.org`

### ActorId vs SS58

- **ActorId** is a 256-bit hex value (`0x...`, 64 hex characters). Programs and on-chain logic use ActorId exclusively.
- **SS58** is a base-58 encoded display format with a network prefix. Wallets, explorers, and UIs show SS58.
- When calling Sails methods or sending messages on-chain, use hex ActorId.
- When displaying addresses in a frontend, use SS58.
- For bridge interactions on the Ethereum side, use `0x`-prefixed hex Ethereum addresses. Vara-side bridge programs use hex H256 ActorIds, not SS58.

## Program Lifecycle

Programs must be uploaded, initialized, and funded before they accept messages. For the full lifecycle (upload, create, active, exit) and rent system details, see `gear-execution-model.md`.

## Vara.eth Network

For Vara.eth (Ethereum-anchored) endpoints, chain ID, and RPC configuration, see `varaeth-extension-notes.md`.
