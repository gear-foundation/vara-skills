# Vara-Ethereum Bridge Flows

## Overview

The Vara-Ethereum bridge uses different trust models in each direction. Both directions are trustless — no centralized intermediary holds funds or controls message passing.

Permissionless relayers carry data between chains. They earn fees but cannot forge messages.

## Vara to Ethereum

Uses zero-knowledge proofs for cross-chain message verification.

1. User locks tokens via the VFT Manager program on Vara.
2. The `gear_eth_bridge` pallet collects messages into an outbound queue.
3. At each finalized block, a Merkle root of the message queue is calculated.
4. A relayer generates a ZK proof (Plonky2) that the Merkle root was signed by Vara's active validator set.
5. The relayer submits the proof to the Proof Verification Contract on Ethereum (verified with GNARK).
6. Ethereum records the Merkle root as an approved source of truth.
7. The relayer submits the individual message with a Merkle inclusion proof to the Bridge Message Contract.
8. The contract verifies inclusion, marks the message as used, and triggers the action (e.g., minting wVARA via the ERC-20 Manager).

Typical transfer time: ~30 minutes.

## Ethereum to Vara

Uses Ethereum's native finality via Beacon Chain light client verification. No ZK proofs needed in this direction.

1. User burns or locks tokens on Ethereum (e.g., burns wVARA in the ERC-20 Manager).
2. Relayers monitor the Ethereum Beacon Chain and its Sync Committee.
3. Once a block is finalized, a relayer submits the block header and aggregated BLS signatures to Vara.
4. The `checkpoint-light-client` program on Vara verifies the BLS signatures against the known Sync Committee.
5. Once Vara accepts the block as finalized, the relevant Ethereum event (e.g., Burn event) is proven via Merkle proof.
6. The `vft-manager` program on Vara processes the proof and executes the corresponding action (e.g., minting native VARA or releasing locked tokens).

Typical transfer time: ~30 minutes.

## Fee Model

Gas fees depend on the source network:

- **Vara to Ethereum:** only VARA tokens needed. No ETH required for the initial transfer.
- **Ethereum to Vara:** ETH is required regardless of the asset being bridged (VARA, ETH, or stablecoins).

Keep a small balance of the native gas token on the source chain to avoid transaction failures.

## Programmatic Integration

For Sails programs that need to interact with the bridge:

- The `vft-manager` program is the key integration point. It mediates between the bridge infrastructure and VFT token contracts.
- For VFT token patterns and bridge-aware token design, see `awesome-sails-token-patterns.md`.
- For deployed bridge program addresses and token contract addresses, see `vara-eth-bridge-contracts.md`.

## Builder Warnings

- **Pre-confirmation vs finality:** Vara.eth pre-confirmed state may be newer than finalized state on Ethereum. Bridge transfers require full finality, not pre-confirmations.
- **Relay delays:** Relayers are permissionless and incentivized but not instant. Transfers take ~30 minutes under normal conditions; network congestion can increase this.
- **Testnet instability:** Ethereum testnets have a history of deprecation (Ropsten, Rinkeby, Goerli, Sepolia, Holesky, Hoodi). Bridge testnet addresses will change when the underlying testnet changes.
- **Address format mismatch:** Ethereum uses 0x-prefixed 20-byte hex addresses. Vara uses 0x-prefixed 32-byte hex ActorIds. Bridge programs handle the mapping internally; do not convert between formats manually.
