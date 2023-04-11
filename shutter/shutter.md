# Shutterized Gnosis Chain — Specification

This is a specification of the Shutterized Beacon Chain proposal intended to be implemented on Gnosis Chain. The focus is on the interfaces between the individual components that make up the system as well as high-level functionality. Internals on the other hand are left relatively open.

# Definitions

Definitions from Ethereum's [consensus](https://github.com/ethereum/consensus-specs) and [execution](https://github.com/ethereum/execution-specs) specs are inherited.

- Keyper set: A set of nodes responsible for generating one eon key and many decryption keys. Its members are identified by Ethereum addresses.
- Eon: The time period measured in slots in which a particular keyper set is active. Enumerated by a zero-based, incremental index. Eons don't overlap. Eons may be tentatively open ended.
- Eon key: A key produced by the keyper set for their eon and used by users to encrypt transactions.
- Decryption key: A key produced by the keyper set for each slot that decrypts transactions.
- Instance ID: A unique identifier distinguishing between the various instantiations of Shutter. For Gnosis Chain it is `100001`, for Chiado it is `200001`.

To illustrate some of these definitions, see the following example with eon boundaries at slot 0, 100, and 150:

```
slot:           | 0 | 1 | 2 | ... | 100 | 101 | 102 | ... | 150 | 151 |
eon:            | 0               | 1                     | 2
decryption key: | 0 | 1 | 2 | ... | 100 | 101 | 101 | ... | 150 | 151 | ...
eon key:        | 0               | 1                     | 2
keyper set:     | 0               | 1                     | 2
```

# Components

This section describes the various components of the system and how they interact with each other.

| Component              | Responsible Team |
| ---------------------- | ---------------- |
| Keypers                | Shutter          |
| Validator              | Nethermind       |
| Sequencer Contract     | Gnosis           |
| Validator Registry     | Gnosis           |
| Key Broadcast Contract | Shutter          |
| Keyper Set Manager     | Shutter          |
| Encrypting RPC Server  | Tbd              |
| Decryption Key Relay   | Shutter          |

## Keypers

Keypers watch the Keyper Set Manager and detect at which slot they become part of a keyper set. Some time well before this slot, they start generating an eon key with an index given by the keyper set index in the Keyper Set Manager. The key generation process is out of scope of this document.

Once the eon key is generated, they broadcast it via the Key Broadcast Contract.

During the time the keyper set is active, the keypers continuously generate decryption keys. To this end, they listen for Gnosis Chain blocks. As soon as they see a new block, they broadcast their decryption key share for the following slot on a p2p network. In addition, keypers listen for key shares from other keypers and, when they collected a sufficient number of them, broadcast the aggregated decryption key.

### Interfaces with

- Key Broadcast Contract: To broadcast eon key
- Keyper Set Manager: To check membership
- Validator: To provide decryption keys to

### Interface

For each slot, active keypers provide keys to interested parties via a [libp2p gossipsub network](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/README.md). The relevant topics are `decryptionKeyShare` and `decryptionKey`. On the former, keypers broadcast decryption key shares, on the latter the corresponding aggregated decryption keys, in the form of the protocol buffers `DecryptionKeyShare` and `DecryptionKey`:

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

- `instanceID`: The instance ID of the network.
- `eon`: The eon index of the key.
- `epochID`: The slot number of the key, in big-endian encoding (note that this field is unrelated to the epochs of the beacon chain).
- Only present in decryption key share messages:
  - `keyperIndex`: The zero-based index of the keyper in the keyper set who generated the key share.
  - `share`: A decryption key share encoded as described in the _Encoding_ section.
- Only present in decryption key messages:
  - `key`: The decryption key encoded as described in the _Encoding_ section.

Participants in the gossip network should apply the following message validation logic in order to prevent propagation of invalid messages:

- Check that `instanceID` is correct.
- Check that `epochID` corresponds to the number of a slot in the near future.
- Check that `eon` is equal to the keyper set index defined in the Key Broadcast Contract for the slot given by `epochID`.
- For `DecryptionKeyShare`:
  - Check that `keyperIndex` is a valid index for the set defined in the Keyper Set Manager and identified by `eon`.
  - Check that `share` is the valid decryption key share by the keyper `keyperIndex` for epoch `epochID`, given the eon key for `eon` broadcast in the Key Broadcast Contract.
- For `DecryptionKey`:
  - Check that `key` is the valid decryption key for epoch `epochID` given the eon key for `eon` broadcast in the Key Broadcast Contract.

Peers for the gossipsub topics can be found via bootstrap nodes that immediately PRUNE connection attempts with additional [gossipsub v1.1 PX](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#prune-backoff-and-peer-exchange) metadata.

Listeners not involved in key generation should subscribe to at least the `decryptionKey` topic and may additionally, for improved latency, subscribe to `decryptionKeyShare` and aggregate by themselves.

## Validator

On startup, validators check if they are registered in the Validator Registry. If they are and a keyper set is active for the next slot, they listen on the gossip network sourced by keypers for decryption keys. Decryption keys can be discarded immediately, unless the validator is selected to propose the next block. In this case, they keep it in memory and follow the following modified block production strategy:

1. Fetch all encrypted transactions for the block’s slot from the Sequencer Contract.
2. Decrypt these transactions using the decryption key.
3. Build the block using all valid decrypted transactions at the front in the order they appeared in the Sequencer Contract. The rest of the block can be built at will.

### Interfaces with

- Key Broadcast Contract: To get eon key
- Sequencer Contract: To get encrypted transactions
- Validator Registry: To register and check registration

And one of:

- Keypers: To receive decryption keys
- Decryption Key Relay: To receive keys from

### Interface

No interface needed.

## Sequencer Contract

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

The Key Broadcast Contract allows the keyper sets to announce new eon keys to the public. Each keyper set can broadcast exactly one eon key, with the eon index being the keyper set index. Calls are authenticated through the Keyper Set Manager, i.e., they must come from the keyper safe defined in the manager with index `eon`.

The Key Broadcast Contract provides a function to query the eon key for each eon.

### Interfaces with

- Keypers: To receive eon key
- Keyper Set Manager: To authenticate eon keys
- Validator: To provide eon key
- Encrypting RPC Server: To provide eon keys to

### Interface

- `function broadcastEonKey(uint64 eon, bytes memory key) external`
- `event eonKeyBroadcast(uint64 eon, bytes key)`
- `function getEonKey(uint64 eon) external view returns (bytes memory)`

## Keyper Set Manager

Keyper sets, consisting of an ordered list of addresses as well as a threshold parameter, are defined in the form of a Gnosis Safe contract. The Keyper Set Manager defines the active keyper set over time by referencing keyper safes and labeling each of them with an activation slot number. The keyper set active at a particular slot `s` is the one with the most recent activation block number `s_i <= s`.

The keyper set implicitly defines the eons and their indices. Given the ordered set of activation block numbers `s_i`, eon `j` starts at slot `s_j` and ends at `s_(j + 1)` (if `s_(j+1)` exists, otherwise the eon is tentatively open ended).

The Keyper Set Manager has an owner. The owner is allowed to add keyper sets for the future at the end, i.e., with activation slot numbers greater or equal to the previously added one and greater than the current slot. They may not change or remove already added keyper sets. Adding a new keyper set emits an event.

The Keyper Set Manager allows querying the keyper sets by index. It also allows finding the index of the keyper set active at a particular slot.

### Interfaces with

- Keypers: To provide keyper set to
- Key Broadcast Contract: To provide keyper set to

### Interface

- `function getNumKeyperSets() external view returns (uint64)`
- `function getKeyperSetIndexBySlot(uint64 slot) external view returns (address, uint64)`
- `function getKeyperSetAddress(uint64 index) external view returns (address, uint64)`
- `function getKeyperSetActivationSlot(uint64 index) external view returns (uint64)`

## Encrypting RPC Server

The Encrypting RPC Server exposes the standard Ethereum RPC API. Whenever a user submits a transaction via `eth_sendRawTransaction`, the server will attempt to encrypt it. To this end, it keeps track of the eon keys from the Eon Key Broadcast Contract as well as the set of participating validators from the Validator Registry. It selects a slot in the near future whose proposer is registered and encrypts the transaction for this slot. It then submits it to the Sequencer Contract.

### Interfaces with

- Key Broadcast Contract: To receive eon keys
- Sequencer Contract: To provide encrypted transactions to
- Validator Registry: To check registered validators

### Interface

See [https://ethereum.github.io/execution-apis/api-documentation/](https://ethereum.github.io/execution-apis/api-documentation/).

## Decryption Key Relay

The Decryption Key Relay allows users to listen to decryption keys without having to join the libp2p gossip network themselves. It subscribes to both the `decryptionKey` and `decryptionKeyShare` topics. It applies the filtering logic described in the Keyper-section. It relays the remaining messages to the clients that suscribed to the interface described below.

### Interfaces with

- Keypers: To receive keys from
- Validators: To send keys to

### Interface

The relay provides an HTTP GET endpoint at path `/v1/decryption_keys` with the following required query parameters:

- `instance_id`: A decimal encoded instance ID

If the relay is connected to a gossip network with different instance ID, it responds with status code `404`. Otherwise, an SSE stream is opened that yields items of the following format:

```jsx
event: decryption_key;
data: data;
```

`data` is the `0x`-prefixed, hex encoded decryption key protocol buffer defined under “Keypers”.

## Encodings

This section describes how various data types used above are canonically encoded.

### P2P Messages

Gossiped p2p messages are encoded as protocol buffers and are wrapped in the following envelope:

```jsx
message Envelope {
    uint32 version = 1 ;
    google.protobuf.Any message = 2;
}
```

- `version`: `0`, to be incremented with future incompatible protocol changes.
- `message`: Any of the above defined message types.

### Cryptographic Objects

The cryptographic objects described below are composed of elements of the bilinear group BN256. Consequently, their encoding functions are composed of the encoding functions of these primitives.

The relevant primitives are points on the curves G1 and G2. They are encoded according to [EIP-197](https://eips.ethereum.org/EIPS/eip-197#encoding). The encoding functions are denoted `encode_g1` and `encode_g2`, respectively.

#### Decryption Keys

Decryption keys are points on G1 and are encoded accordingly:

```Python
def encode_decryption_key(k):
    return encode_g1(k)
```

#### Decryption Key Shares

Decryption key shares are points on G1 and are encoded accordingly:

```Python
def encode_decryption_key_share(k):
    return encode_g1(k)
```

#### Encrypted Messages

Encrypted messages are tuples `(C1, C2, C3)` where

- `C1` is a point on G2,
- `C2` is a 32 bytes block, and
- `C3` is a sequence of one or more 32 bytes blocks.

Its encoding is the concatenation of its part, i.e. `encode_g2(C1) | C2 | C3[0] | ... | C3[n]` where `|` denotes concatenation and .

```Python
def encode_encrypted_message(m):
    c1, c2, c3 = m
    return encode_g2(c1) + c2 + b"".join(c3)
```
