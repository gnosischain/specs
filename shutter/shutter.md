# Shutterized Gnosis Chain — Specification

> :construction: :construction: :construction:
>
> This specification is a work in progress and not yet in effect.
>
> :construction: :construction: :construction:

This document is a specification of the first implementation phase of the Shutterized Beacon Chain proposal. It is intended to be implemented on Gnosis Chain.

## Applications

This section specifies the responsibilities that the various applications .

### Keyper

> :construction: :construction: :construction:
>
> - Describe eon key generation process, at least from the outside.
> - Refer to networking doc once it exists
> - Update message types and sending conditions if we decide to go with individually encrypted transactions.
> - Define how keyper index is found (requires specification of keyper set contract)
> - Use canonical topic naming scheme
>
> :construction: :construction: :construction:

The keyper node is configured with the following parameters:

- `instanceID` (a `uint64`)
- `address` (an Ethereum address)

For each slot `s`, the keyper queries the `keyperSetManager = IKeyperSetManager(KEYPER_SET_MANAGER_ADDRESS)` for the keyper set `keyperSet = keyperSetManager.getKeyperSetAddress(eon)` with argument `eon = keyperSetManager.getKeyperSetIndexBySlot(s)`. The keyper then queries the index `keyperIndex` of `address` in `keyperSet`. If no keyper set is defined for slot `s` or the keyper is not part of the keyper set, it is inactive in slot `s`.

At the start of each slot `s`, if they are not inactive, the keyper generates its encryption key share `share` and broadcasts the following message on topic `decryptionKeyTopicShare`:

```jsx
message DecryptionKeyShare {
    uint64 instanceID = 1;
    uint64 eon = 2;
    bytes epochID = 3;
    uint64 keyperIndex = 4;
    bytes share = 5;
}
```

with

- `message.instanceID = instanceID`
- `message.eon = eon`
- `message.epochID = encode_g1(compute_epoch_id(s))`
- `message.keyperIndex = keyperIndex`
- `message.share = encode_decryption_key_share(share)`

Active keypers also listen to `DecryptionKeyShare` messages from other keypers. Once they have received enough of them to be able to generate the decryption key `key`, they do so and broadcast the following message on topic `decryptionKey`, unless they have already received it from a peer:

```jsx
message DecryptionKey {
    uint64 instanceID = 1;
    uint64 eon = 2;
    bytes epochID = 3;
    bytes key = 4;
}
```

with

- `message.instanceID = instanceID`
- `message.eon = eon`
- `message.epochID = encode_g1(compute_epoch_id(s))`
- `message.key = encode_decryption_key(key)`

### Validator

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

### Encrypting RPC Server

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

### Decryption Key Relay

The Decryption Key Relay is configured with the parameter `instanceID` of type `uint64`. It subscribes to the topics `decryptionKey` and `decryptionKeyShare` and stores all received messages.

The relay provides the following HTTP GET endpoints:

- `/v1/decryption_keys`
- `/v1/decryption_keys/{slot}`

Both endpoints require the query parameter `instance_id`, expected to be a decimal encoded instance ID. If this value differs from the value given as the configuration parameter `instanceID`, the relay responds with HTTP status code `404`.

The first endpoint (without the `slot` parameter) opens an SSE stream that yields items of the following format whenever the relay learns about a new decryption key:

```jsx
event: decryption_key;
data: data;
```

`data` is the `0x`-prefixed, hex encoded decryption key protocol buffer defined under [Keyper](#keyper).

The second endpoint takes a decimal slot number as parameter and returns the corresponding decryption key protocol buffer in `0x`-prefixed, hex-encoded format. If the relay does not know the key for the requested slot, it sends a response with status code `404`. The relay should be able to respond to requests for the current and the most recent slots if they observed the corresponding keys on the network. They may prune keys when they become too old and do not have to persist them across restarts of the application.

## Smart Contracts

This section specifies the functionality and interfaces of the smart contracts involved in the system.

### Sequencer

The Sequencer is a contract deployed at address `SEQUENCER_ADDRESS`. It implements the following interface:

```Solidity
interface ISequencer {
    function submitEncryptedTransaction(uint64 eon, bytes32 identityPrefix, bytes calldata encryptedTransaction, uint256 gasLimit) external;

    event TransactionSubmitted(uint64 eon, bytes32 identityPrefix, uint256 gasLimit);
}
```

`submitEncryptedTransaction(eon, identityPrefix, encryptedTransaction, gasLimit)` emits the event `TransactionSubmitted(eon, identityPrefix, gasLimit)`.

> :construction: :construction: :construction:
>
> ELements should be removed from the front of the queue after they have been executed to let the keypers know at which transaction to start decryption next.
>
> :construction: :construction: :construction:

### Validator Registry

The Validator Registry is a contract deployed at address `VALIDATOR_REGISTRY_ADDRESS`. It implements the following interface:

```
interface IValidatorRegistry {
    function register(bytes memory registrationSignature) external;
    function deregister(bytes memory deregistrationSignature) external;

    event Registration(bytes registrationSignature);
    event Deregistration(bytes deregistrationSignature);
}
```

`register(registrationSignature)` emits the event `Registration(registrationSignature)`.

`deregister(deregistrationSignature)` emits the event `Deregistration(deregistrationSignature)`.

### Key Broadcast Contract

The Key Broadcast Contract is deployed at address `KEY_BROADCAST_CONTRACT_ADDRESS`. It implements the following interface:

```
interface IKeyBroadcastContract {
    function broadcastEonKey(uint64 eon, bytes memory key) external;
    function getEonKey(uint64 eon) external view returns (bytes memory);

    event EonKeyBroadcast(uint64 eon, bytes key)
}
```

`broadcastEonKey(eon, key)` reverts if any of the following conditions is met at the time of the call:

1. The contract has already stored a key for the given eon.
2. `key` is empty.
3. `IKeyperSetManager(KEYPER_SET_MANAGER_MANAGER_ADDRESS).getKeyperSetAddress(eon)` reverts or returns an address different from `msg.sender`.

Otherwise, it stores `key` such that it is accessible by `eon` and emits the event `EonKeyBroadcast(eon, key)`.

`getEonKey(eon)` returns the key stored for `eon`, or an empty bytes value if no key for `eon` is stored.

### Keyper Set Manager

The Keyper Set Manager is a contract deployed at address `KEYPER_SET_MANAGER_ADDRESS`. It implements the following interface:

```
interface IKeyperSetManager {
    function addKeyperSet(uint64 activationSlot, address keyperSetContract) external;
    function getNumKeyperSets() external view returns (uint64);
    function getKeyperSetIndexBySlot(uint64 slot) external view returns (address, uint64);
    function getKeyperSetAddress(uint64 index) external view returns (address, uint64);
    function getKeyperSetActivationSlot(uint64 index) external view returns (uint64);

    event KeyperSetAdded(uint64 activationSlot, address keyperSetContract);
}
```

In addition, the contract implements the [Contract Ownership Standard (ERC-173)](https://eips.ethereum.org/EIPS/eip-173).

`addKeyperSet(activationSlot, keyperSetContract)` reverts if any one of the following conditions is met at the time of the call:

1. `msg.sender != owner()`
2. `getNumKeyperSets() > 0 && activationSlot < getKeyperSetActivationSlot(getNumKeyperSets() - 1)`
3. `activationSlot` is smaller or equal than the current slot number

> :construction: :construction: :construction:
>
> Is 3 necessary? Should the activation slot be required to be a certain amount of slots in the future?
>
> :construction: :construction: :construction:

Otherwise, `addKeyperSet` saves `keyperSetContract` and the corresponding `activationSlot` to storage. Finally, it emits the event `KeyperSetAdded(activationSlot, keyperSetContract)`.

Define `n` as the number of added keyper sets, `k_0 ... k_(n - 1)` as the keyper sets in the order they were added, and `s_0 ... s_(n - 1)` as the corresponding activation slot numbers. Then, there are `n` eons `e_i` starting at slot `s_i` (inclusive). Eon `e_i` for `i = 0 ... n - 2` ends at slot `s_(i + 1)` (exclusive), eon `e_(n - 1)` is tentatively open ended. The keyper set for any slot in `e_i` is `k_i`.

`getNumKeyperSets()` returns `n`.

`getKeyperSetIndexBySlot(s)` reverts if `n == 0` or `s < s_0`. Otherwise, it returns `k_i` where `i` is the index of the eon that contains slot `s`.

`getKeyperSetAddress(i)` reverts if `i >= n`. Otherwise, it returns `k_i`.

`getKeyperSetActivationSlot(i)` reverts if `i >= n`. Otherwise, it returns `s_i`.

### Keyper Set Contract

> :construction: :construction: :construction:
>
> Define the interface which should allow initializing and retrieving the members of one keyper set, its size, and the threshold. Deployments of this contract will be referenced by the keyper set manager.
>
> :construction: :construction: :construction:

## Cryptography

This section defines the functions `encrypt` and `decrypt` that are used to encrypt and decrypt the users' transactions and some corresponding types. The cryptographic functions are based on the bilinear group BN256 as used in [EIP-196](https://eips.ethereum.org/EIPS/eip-196) and [EIP-197](https://eips.ethereum.org/EIPS/eip-197).

### Definitions

We define the following types and constants:

| Type                                            | Description                      |
| ----------------------------------------------- | -------------------------------- |
| G1                                              | An element of the BN256-curve G1 |
| G2                                              | An element of the BN256-curve G2 |
| GT                                              | An element of the BN256-curve GT |
| Block                                           | A 32-byte block                  |
| EncryptedMessage = (G2, Block, Sequence[Block]) | An encrypted message             |

| Constant | Description                   | Value                                                                         |
| -------- | ----------------------------- | ----------------------------------------------------------------------------- |
| ORDER    | The order of groups G1 and G2 | 21888242871839275222246405745257275088548364400416034343698204186575808495617 |

The following functions are considered prerequisites:

| Function                       | Description                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| keccak256(bytes) -> Block      | The keccak-256 hash function                                                                    |
| pairing(G1, G2) -> GT          | The BN256-defined pairing function                                                              |
| g2_scalar_base_mult(int) -> G2 | Multiply the generator of G2 by a scalar                                                        |
| gt_scalar_mult(GT, int)        | Multiply an element of GT by a scalar                                                           |
| encode_g1(G1) -> bytes         | Encode an element of G1 according to [EIP-197](https://eips.ethereum.org/EIPS/eip-197#encoding) |
| encode_g2(G2) -> bytes         | Encode an element of G2 according to [EIP-197](https://eips.ethereum.org/EIPS/eip-197#encoding) |

### Helper Functions

```Python
def hash_block_to_int(block: Block) -> int:
    h = keccak256(block)
    i = int.from_bytes(h, "big")
    return i % ORDER

def hash_gt_to_block(preimage: GT) -> Block:
    b = encode_gt(preimage)
    return hash_bytes_to_block(b)

def hash_bytes_to_block(preimage: bytes) -> Block:
    return keccak256(preimage)

def xor_blocks(block1: Block, block2: Block) -> Block:
    return Block(bytes(b1 ^ b2 for b1, b2 in zip(block1, block2)))

def pad_and_split(b: bytes) -> Sequence[Block]:
    # pad according to PKCS #7
    n = 32 - len(b) % 32
    padded = b + n * bytes([n])
    return [padded[i:i + 32] for i in range(0, len(padded), 32)]

def unpad_and_join(blocks: Sequence[Block]) -> bytes:
    # unpad according to PKCS #7
    if len(blocks) == 0:
        return b""
    last_block = blocks[-1]
    n = last_block[-1]
    assert 0 < n <= 32, "invalid padding length"
    return b"".join(blocks)[:-n]

def encode_gt(value: GT) -> bytes:
    pass  # TODO

def compute_block_keys(sigma: Block, n: int) -> Sequence[Block]:
    suffix_length = max(n.bit_length() + 7) // 8, 1)
    suffixes = [n.to_bytes(suffix_length, "big")]
    preimages = [sigma + suffix for suffix in suffixes]
    keys = [hash_bytes_to_block(preimage) for preimage in preimages]
    return keys
```

### Encryption and Decryption

The following code defines the function `encrypt` and `decrypt`. The former encrypts a given message for a particular slot given an eon key. The latter decrypts an encrypted message using a decryption key.

```Python
def encrypt(message: bytes, slot: int, eon_key: G2, sigma: Block) -> EncryptedMessage:
    message_blocks = pad_and_split(message)
    r = compute_r(sigma)
    epoch_id = compute_epoch_id(slot)
    return (
        compute_c1(r),
        compute_c2(sigma, r, epoch_id, eon_key),
        compute_c3(message_blocks, sigma),
    )

def compute_r(sigma: Block) -> int:
    return hash_block_to_int(sigma)

def compute_c1(r: int) -> G2:
    return g2_scalar_base_mult(r)

def compute_c2(sigma: Block, r: int, epoch_id: G1, eon_key: G2) -> Block:
    p = pairing(epoch_id, eon_key)
    preimage = gt_scalar_mult(p, r)
    key = hash_gt_to_block(preimage)
    return xor_blocks(sigma, key)

def compute_c3(message_blocks: Sequence[Block], sigma: Block) -> Sequence[Block]:
    keys = compute_block_keys(sigma, len(message_blocks))
    return [xor_blocks(key, block) for key, block in zip(keys, blocks)]

def compute_epoch_id(slot: int) -> G1:
    pass  # TODO
```

```Python
def decrypt(encrypted_message: EncryptedMessage, decryption_key: G1) -> bytes:
    sigma = recover_sigma(encrypted_message, decryption_key)
    _, _, c3 = encrypted_message
    keys = compute_block_keys(sigma, len(blocks))
    decrypted_blocks = [xor_blocks(key, block) for key, block in zip(keys, blocks)]
    return unpad_and_join(decrypted_blocks)

def recover_sigma(encrypted_message: EncryptedMessage, decryption_key: G1) -> Block:
    c1, c2, _ = encrypted_message
    p = pairing(decryption_key, c1)
    key = hash_gt_to_block(p)
    sigma = xor_blocks(c2, decryption_key)
    return sigma
```

### Encoding

The following functions define how some of the cryptographic objects are encoded into bytes.

```Python
def encode_decryption_key(decryption_key: G1) -> bytes:
    return encode_g1(decryption_key)

def encode_decryption_key_share(decryption_key_share: G1) -> bytes:
    return encode_g1(k)

def encode_encrypted_message(encrypted_message: EncryptedMessage) -> bytes:
    c1, c2, c3 = encrypted_message
    return encode_g2(c1) + c2 + b"".join(c3)
```
