# Ethereum Wire Protocol (ETH)

'eth' is a protocol on the [RLPx] transport that facilitates exchange of Ethereum
blockchain information between peers. Gnosis chain supports all protocol versions
stated in the [ethereum/devp2p spec](https://github.com/ethereum/devp2p/blob/master/caps/eth.md)
unless stated otherwise. The scope of this spec includes only version differences
after"the merge" upgrade on December 2022. 

## Change Log

### eth/68 ([EIP-5793], October 2022, Gnosis)

Version 68 Gnosis extends the cannonical eth/68 version but still includes GetNodeData and
NodeData messages.
