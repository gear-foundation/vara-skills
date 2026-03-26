# Vara-Ethereum Bridge Contract Addresses

Last Verified: 2026-03-26

**Testnet Warning:** Testnet addresses change when testnets are deprecated or bridge contracts are redeployed. Verify addresses against canonical sources before real deployments.

## Canonical Sources

- Vara wiki Bridge Developer Hub: `vara-wiki/content/docs/vara-network/bridge/developer_hub.mdx`
- Vara wiki Contract Addresses: `vara-wiki/content/docs/vara-eth/reference/contract-addresses.mdx`
- Source data: `vara-wiki/src/addresses/bridge-addresses.js`

## Vara.eth Contracts (Hoodi Testnet)

For Hoodi testnet network configuration (chain ID, RPC, explorer, faucet), see `vara-network-endpoints.md` and `varaeth-extension-notes.md`.

| Contract | Address |
|----------|---------|
| Router | `0xE549b0AfEdA978271FF7E712232B9F7f39A0b060` |
| wVARA (ERC-20) | `0xE1ab85A8B4d5d5B6af0bbD0203EB322DF33d0464` |
| Mirror (per program) | Deterministic: `CREATE2(Router, keccak256(codeId, salt))` |

Vara.eth mainnet contracts are not yet deployed.

## Ethereum Bridge Contracts — Mainnet

### Core Components

| Component | Address |
|-----------|---------|
| Verifier | `0xDdAAC7F0814368D58D40216C6391a5e40A8cd47E` |
| MessageQueue | `0x8E01Fbf136cA97627ca241dB9EFf1DFE3f2195F6` |
| Bridging Payment | `0x03Dd51eeE793CE5523D28752f3019B0c9DfeE6C5` |

### Token Contracts

| Token | Address |
|-------|---------|
| USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| USDT | `0xdAC17F958D2ee523a2206206994597C13D831ec7` |
| WETH | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| WVARA | `0xB67010F2246814e5c39593ac23A925D9e9d7E5aD` |
| WBTC | `0x2260fac5e5542a773aa44fbcfedf7c193bc2c599` |

### ERC20 Manager

| Component | Address |
|-----------|---------|
| ERC20Manager | `0x16fCff97822fcf3345Fa76D29c229b11C49EaE12` |

### Bridge Governance

| Component | Address |
|-----------|---------|
| GovernanceAdmin | `0x3681A3e25F5652389B8f52504D517E96352830C3` |
| GovernancePauser | `0x257936C55518609E47eAab53f40a6e19437BEF47` |

## Ethereum Bridge Contracts — Hoodi Testnet

### Core Components

| Component | Address |
|-----------|---------|
| Verifier | `0xc3ac0c364452acEE4366CD088F947965ec486e8F` |
| MessageQueue | `0xAb8F315Cc80cf2368750fE5A33E259d6241b3dEB` |
| MessageQueue Proxy | `0x55B97F9229dc310837A880c7898f7d411528cC6d` |
| Bridging Payment | `0x512Ac5b5f0830d1C5CB44741a5c0a0E5B66696FD` |

### Token Contracts

| Token | Address |
|-------|---------|
| USDC | `0x263898d2f6f8E153F1e4DD4CAEF86C93784fCf33` |
| USDT | `0x7728A33EBEBCfa852cf7f7Fc377BfC87C24a701A` |
| WETH | `0xE0decAa66aED871ac9eb924443D1Bf333Fdb062E` |
| WBTC | `0xa56a332d34b2db33ebc41dc0194afd28cb20d19b` |
| WTVARA | `0xE1ab85A8B4d5d5B6af0bbD0203EB322DF33d0464` |

### ERC20 Manager

| Component | Address |
|-----------|---------|
| ERC20Manager | `0xA17187De490dB5F7160822dA197bcAc39d64baCb` |
| ERC20Manager Proxy | `0xD2a0951DBCfdA8de36Ab315A57C30F0784d01342` |

### Bridge Governance

| Component | Address |
|-----------|---------|
| GovernanceAdmin | `0x3288b744ADbC25f07b636718d72ec07F8C77E5E9` |
| GovernancePauser | `0x384B68Fc08c59Df51694f7F6A24A112B8331eEb0` |

## Vara Bridge Programs — Mainnet

| Component | Program ID |
|-----------|-----------|
| checkpoint-light-client | `0xf0a411ed5b8c28194d60781306de2ef131ec7df28658f7a857fc95fd86db7e8b` |
| historical-proxy | `0x21b82d3ee72e0a5ac81db100c0a703050593b551c50e86b18c9da0be793660fb` |
| vft-manager | `0xe01ddc667f80cf57704352b557668b710c345395abcac0752c01402d16e3e81b` |
| bridging-payment | `0xcc1901de1f8134ed2c2d30775e4840084ad5d527cfcbf63c3247df24a2e3075e` |

### Bridged Tokens on Vara Mainnet

| Token | Program ID |
|-------|-----------|
| WUSDC | `0xd1de816d7dce6439504552686ab333e5b7302b1549763656b30af1f8a5871b6a` |
| WUSDT | `0x4255ff4a87a4c13dc39f74ace8c4948bbef2f75fb639d66639a1cfcc99e6243e` |
| WETH | `0xde45bdbb0345919a11561d43a5082e0b25061d4a2c6eb80009c1cfbccb80d0de` |
| WBTC | `0x4984671804477d0689eabcd5418eb751207f20f251eaf7884a25b98645f342b1` |
| Tokenized VARA | `0xdbf80fe5bd78b44510762770a14dc2a5b13a6bb167ff12c2edcc7ca3deadc16d` |

## Vara Bridge Programs — Testnet

| Component | Program ID |
|-----------|-----------|
| checkpoint-light-client | `0xdb7bbcaff8caa131a94d73f63c8f0dd1fec60e0d263e551d138a9dfb500134ca` |
| eth-events-electra | `0x0e81a4201bdb78fb313aa01a7764aa2c6bd254463026dc700db9f657c54d47b1` |
| historical-proxy | `0x5d2a0dcfc30301ad5eda002481e6d0b283f81a1221bef8ba2a3fa65fd56c8e0f` |
| vft-manager | `0x39514728b5828eccad02b8f1183e7ccea43849157ed6504c38b28420a85f0d12` |
| bridging-payment | `0x8b86f8cb74f2a0050bd2207efa22cdb59ce20051126618e2ebcacfe49c7e1e4c` |

### Bridged Tokens on Vara Testnet

| Token | Program ID |
|-------|-----------|
| WUSDC | `0x9f332e61589e0850dce6d8e6070ea5618de33d9f134a4a35d6d1164dc9002f48` |
| WUSDT | `0x464511231a1afe9108a689ed3dbbb047ca308d6f5dfb86453e4df5612a2d668a` |
| WETH | `0xba764e2836b28806be10fe6f674d89d1e0c86898d25728f776588f03bddc6f58` |
| WBTC | `0xc1ec06d99efcffd863f9c2ad2bc76f656aff861acf06f438046c64e5b41e3fd9` |
| Tokenized VARA | `0xa1a37e5a36e8a53921f6bedefadec91dc510636079a22238e9edf8233aaa494e` |

## Bridge UI

- Bridge interface: `https://bridge.vara.network`
- Supported assets: VARA/wVARA, ETH/wETH, USDT/wUSDT, USDC/wUSDC, WBTC
