# Shutterized Gnosis Chain — Specification

This is a specification of the Shutterized Beacon Chain proposal intended to be implemented on Gnosis Chain. It is organized by the various components in the system that interact with each other. The focus of the document is on the interfaces between these parts as well as high-level functionality. Internals on the other hand are left relatively open.

# Components

## Keypers

Responsibility: Shutter

### Functionality

Keypers watch the Keyper Set Manager and detect when they become part of a keyper set. When they do, they start generating an eon key with an index given by the keyper set index in the Keyper Set Manager. Key generation is done in advance so that the key is ready at the time the keyper set change comes into effect.

Keypers broadcast newly generated eon keys via the Key Broadcast Contract.

During the time the keyper set is active, keypers continuously generate decryption keys. To this end, they listen for Gnosis Chain blocks. As soon as they see a new block, they broadcast their decryption key share for the following slot on a p2p network. In addition, keypers listen for other key shares and, when they collected a sufficient number of them, broadcast the aggregated decryption key.

### Interfaces with

- Key Broadcast Contract: To broadcast eon key
- Keyper Set Manager: To check membership
- Validator: To provide decryption keys

### Interface

Keypers provide decryption keys to interested parties via a [libp2p gossipsub network](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/README.md). The relevant topics are `decryptionKeyShare` and `decryptionKey`. On the former, keypers broadcast decryption key shares, on the latter the corresponding aggregated decryption keys. Listeners should subscribe to at least the `decryptionKey` topic and may additionally, for improved latency, subscribe to `decryptionKeyShare` and aggregate by themselves.

Messages are encoded according to the following protocol buffer declarations:

```jsx
message DecryptionKeyShare {
    uint64 instanceID = 1;
    uint64 eon = 2;
    bytes epochID = 3;
    uint64 keyperIndex = 4;
    bytes share = 5;
}

message DecryptionKey {
    uint64 instanceID = 1;
    uint64 eon = 2;
    bytes epochID = 3;
    bytes key = 4;
}
```

- `instanceID` is `101`.
- `eon` is the index of the corresponding eon key. It is equal to the index of the keyper set that is generating the key as defined in the Keyper Set Manager.
- `epochID` identifies the epoch for which the key has been generated. It is the big endian-encoded slot number.
- `keyperIndex` is the index of the keyper in the keyper set.
- `share` is the encoded decryption key share.
- `key` is the encoded decryption key.

Participants in the gossip network should apply the following message validation logic in order to prevent propagation of invalid messages:

- Check that `instanceID` is correct.
- Check that `epochID` corresponds to the number of a slot in the near future.
- Check that `eon` is equal to the keyper set index defined in the Key Broadcast Contract for the slot given by `epochID`.
- For `DecryptionKeyShare`:
  - Check that `keyperIndex` is a valid index for the set defined in the Keyper Set Manager and identified by `eon`.
  - Check that `share` is the valid decryption key share by the keyper `keyperIndex` for epoch `epochID`, given the eon key for `eon` broadcast in the Key Broadcast Contract.
- For `DecryptionKey`:
  - Check that `key` is the valid decryption key for epoch `epochID` given the eon key for `eon` broadcast in the Key Broadcast Contract.

Peers can be found via the discovery protocol of [Kademlia DHT](https://github.com/libp2p/specs/blob/master/kad-dht/README.md) with dedicated bootstrap nodes.

## Validator

Responsible: Nethermind

### Functionality

On startup, validators check if they are registered in the Validator Registry. If they are and a keyper set is active, they listen on the gossip network sourced by keypers for decryption keys. Decryption keys can be discarded immediately, unless the validator is selected to propose the next block. In this case, they keep it in memory and follow the following modified block production strategy:

1. Fetch all encrypted transactions for the block’s slot from the Sequencer Contract.
2. Decrypt these transactions using the decryption key.
3. Build the block using all valid decrypted transactions at the front in the order they appeared in the Sequencer Contract. The rest of the block can be built at will.

### Interfaces with

- Key Broadcast Contract: To get eon key
- Keypers: To receive decryption keys
- Sequencer Contract: To get encrypted transactions
- Validator Registry: To register and check registration

### Interface

No interface needed.

## Sequencer Contract

Responsible: Gnosis

### Functionality

The Sequencer Contract allows anyone to submit encrypted transactions with a slot number in which they are supposed to be decrypted. For gas efficiency, the contract should not store the transaction data in storage. Validators are expected to retrieve it from the raw transactions in the block.

Submitting the transaction for the current or past slots should fail.

Successfully submitting a transaction should emit an event.

### Interfaces with

- Encrypting RPC Server: To receive encrypted transactions
- Validator: To provide encrypted transactions

### Interface

- `function submitEncryptedTransaction(uint64 slot, bytes calldata encryptedTransaction) external`
- `event SubmitTransaction(uint64 indexed slot)`

## Validator Registry

Responsible: Gnosis

### Functionality

The Validator Registry allows validators to register and deregister, indicating that they participate in the protocol or not. Validators authenticate themselves using a signature created with their validator key. The contract does not verify these signatures, this is left to off-chain observers.

### Interfaces with

- Validator: To allow registration
- Encrypting RPC Server: To provide registration checks

### Interface

- `function register(bytes memory registrationSignature) external`
- `function deregister(bytes memory deregistrationSignature) external`
- `event Registration(bytes registrationSignature)`
- `event Deregistration(bytes deregistrationSignature)`

## Key Broadcast Contract

Responsible: Shutter (Gnosis?)

### Functionality

The Key Broadcast Contract allows the keyper sets to announce new eon keys to the public. Each keyper set can broadcast exactly one eon key, with the eon index being the keyper set index. Calls are authenticated through the Keyper Set Manager, i.e., they must come from the keyper safe defined in the manager with index `eon`.

The Key Broadcast Contract provides a function to query the eon key for each eon.

### Interfaces with

- Keypers: To receive eon key
- Keyper Set Manager: To authenticate eon keys
- Validator: To provide eon key
- Encrypting RPC Server: To provide eon keys

### Interface

- `function broadcastEonKey(uint64 eon, bytes memory key) external`
- `event eonKeyBroadcast(uint64 eon, bytes key)`
- `function getEonKey(uint64 eon) external view returns (bytes memory)`

## Keyper Set Manager

Responsible: Shutter (Gnosis?)

### Functionality

Keyper sets, consisting of an ordered list of addresses as well as a threshold parameter, are defined in the form of a Gnosis Safe contract. The Keyper Set Manager defines the active keyper set over time by referencing keyper safes and labeling each of them with an activation slot number. The keyper set active at a particular slot `s` is the one with the most recent activation block number `s_i <= s`.

The Keyper Set Manager has an owner. The owner is allowed to add keyper sets for the future at the end, i.e., with activation slot numbers greater or equal to the previously added one and greater than the current slot. They may not change or remove already added keyper sets. Adding a new keyper set emits an event.

The Keyper Set Manager allows querying the keyper sets by index. It also allows finding the index of the keyper set active at a particular slot.

### Interfaces with

- Keypers: To provide keyper set
- Key Broadcast Contract: To provide keyper set

### Interface

- `function getNumKeyperSets() external view returns (uint64)`
- `function getKeyperSetIndexBySlot(uint64 slot) external view returns (address, uint64)`
- `function getKeyperSetAddress(uint64 index) external view returns (address, uint64)`
- `function getKeyperSetActivationSlot(uint64 index) external view returns (uint64)`

## Encrypting RPC Server

Responsible: ?

### Functionality

The Encrypting RPC Server exposes the standard Ethereum RPC API. Whenever a user submits a transaction via `eth_sendRawTransaction`, the server will attempt to encrypt it. To this end, it keeps track of the eon keys from the Eon Key Broadcast Contract as well as the set of participating validators from the Validator Registry. It selects a slot in the near future whose proposer is registered and encrypts the transaction for this slot. It then submits it to the Sequencer Contract.

### Interfaces with

- Key Broadcast Contract: To receive eon keys
- Sequencer Contract: To provide encrypted transactions
- Validator Registry: To check registered validators

### Interface

See [https://ethereum.github.io/execution-apis/api-documentation/](https://ethereum.github.io/execution-apis/api-documentation/).
