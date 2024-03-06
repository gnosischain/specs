# London Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [london specs](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/london.md). Table below lists differences if any.

| EIP |  |
| - | - |
| [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559): Fee market change for ETH 1.0 chain                  | Modified
| [EIP-3198](https://eips.ethereum.org/EIPS/eip-3198): BASEFEE opcode                                       | Not modified?
| [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529): Reduction in refunds                                 | Not modified?
| [EIP-3541](https://eips.ethereum.org/EIPS/eip-3541): Reject new contract code starting with the 0xEF byte | Not modified?

## Differences with Ethereum mainnet

### [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)

Gnosis chain native token is xDAI (wrapped DAI). Each xDAI token represents a claim over 1 DAI locked on the foreign side of the `erc-to-native` bridge. Therefore xDAI should not be burned to mantain the bridge invariant of 1:1 backing.

| Constant | Value |
| - | - |
| EIP1559_FEE_COLLECTOR | 0x6BBe78ee9e474842Dbd4AB4987b3CeFE88426A92 |

Block validity is modified by extending the reference implementation in the EIP. The burned fee is transfered to a pre-definied address as part of block processing.

```diff
 class World(ABC):
 	def validate_block(self, block: Block) -> None:
         ...
         for unnormalized_transaction in transactions:
             ...
+            self.account(EIP1559_FEE_COLLECTOR).balance += gas_used * block.base_fee_per_gas
```

## Upgrade Schedule

| Network | Block    | Date & Time (UTC)             | 
| ------- | -------- | ----------------------------- | 
| Mainnet | 19040000 | Nov-12-2021 09:46:20 PM +UTC  | 

