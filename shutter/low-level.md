# Opt-in Shutterized Gnosis Chain -- Low Level Specification

> :construction: :construction: :construction:
>
> This specification is a work in progress and not yet in effect.
>
> :construction: :construction: :construction:

This document is a specification of the first implementation phase of the Shutterized Beacon Chain proposal. It is intended to be implemented on Gnosis Chain.

For an overview over the protocol, rationale, and security discussion, checkout the [high-level document](shutter/high-level.md).

## Applications

This section describes the functionality of the applications involved in the protocol.

### Keyper

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

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

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

## Smart Contracts

This section specifies the interfaces and behavior of the smart contracts in the protocol.

### Sequencer

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

### Validator Registry

The Validator Registry is a contract deployed at address `VALIDATOR_REGISTRY_ADDRESS`. It implements the following interface:

```
interface IValidatorRegistry {
    function register(bytes memory registrationMessage, bytes memory registrationSignature) external;
    function deregister(bytes memory deregistrationMessage, bytes memory deregistrationSignature) external;

    event Registration(bytes registrationMessage, bytes registrationSignature);
    event Deregistration(bytes deregistrationMessage, bytes deregistrationSignature);
}
```

`register(registrationMessage, registrationSignature)` emits the event `Registration(registrationMessage, registrationSignature)`.

`deregister(deregistrationMessage, deregistrationSignature)` emits the event `Deregistration(deregistrationMessage, deregistrationSignature)`.

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

Otherwise, it stores `key` in a way that it is indexable by `eon` and emits the event `EonKeyBroadcast(eon, key)`.

`getEonKey(eon)` returns the key stored for `eon`, or an empty bytes value if no key for `eon` is stored.

### Keyper Set Manager

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

### Keyper Set Contract

> :construction: :construction: :construction:
>
> Todo
>
> :construction: :construction: :construction:

## Cryptography

This section defines the cryptographic primitives used in the protocol.

### Definitions

| Type                                            | Description                                                                                                                      |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| G1                                              | An element of the BN256-group G1 as defined in [EIP-197](https://eips.ethereum.org/EIPS/eip-197#definition-of-the-groups)        |
| G2                                              | An element of the BN256-group G2 as defined in [EIP-197](https://eips.ethereum.org/EIPS/eip-197#definition-of-the-groups)        |
| GT                                              | An element of the BN256-group GT, the range of the pairing function defined in [EIP-197](https://eips.ethereum.org/EIPS/eip-197) |
| Block                                           | A 32-byte block                                                                                                                  |
| EncryptedMessage = (G2, Block, Sequence[Block]) | An encrypted message                                                                                                             |

| Constant | Description                   | Value                                                                         |
| -------- | ----------------------------- | ----------------------------------------------------------------------------- |
| ORDER    | The order of groups G1 and G2 | 21888242871839275222246405745257275088548364400416034343698204186575808495617 |

The following functions are considered prerequisites:

| Function                       | Description                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| keccak256(bytes) -> Block      | The keccak-256 hash function                                                                    |
| pairing(G1, G2) -> GT          | The pairing function specified in [EIP-197](https://eips.ethereum.org/EIPS/eip-197)             |
| g1_scalar_base_mult(int) -> G1 | Multiply the generator of G1 by a scalar                                                        |
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

def encode_gt(value: GT) -> bytes:
    pass  # TODO

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

def compute_block_keys(sigma: Block, n: int) -> Sequence[Block]:
    suffix_length = max(n.bit_length() + 7) // 8, 1)
    suffixes = [n.to_bytes(suffix_length, "big")]
    preimages = [sigma + suffix for suffix in suffixes]
    keys = [hash_bytes_to_block(preimage) for preimage in preimages]
    return keys
```

### Encryption and Decryption

```Python
def encrypt(message: bytes, identity: G1, eon_key: G2, sigma: Block) -> EncryptedMessage:
    message_blocks = pad_and_split(message)
    r = compute_r(sigma)
    return (
        compute_c1(r),
        compute_c2(sigma, r, identity, eon_key),
        compute_c3(message_blocks, sigma),
    )

def compute_r(sigma: Block) -> int:
    return hash_block_to_int(sigma)

def compute_c1(r: int) -> G2:
    return g2_scalar_base_mult(r)

def compute_c2(sigma: Block, r: int, identity: G1, eon_key: G2) -> Block:
    p = pairing(identity, eon_key)
    preimage = gt_scalar_mult(p, r)
    key = hash_gt_to_block(preimage)
    return xor_blocks(sigma, key)

def compute_c3(message_blocks: Sequence[Block], sigma: Block) -> Sequence[Block]:
    keys = compute_block_keys(sigma, len(message_blocks))
    return [xor_blocks(key, block) for key, block in zip(keys, blocks)]

def compute_identity(prefix: bytes, sender: bytes) -> G1:
    h = keccak256(prefix + sender)
    i = int.from_bytes(h, "big")
    return g1_scalar_base_mult(i)
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

```Python
def encode_decryption_key(decryption_key: G1) -> bytes:
    return encode_g1(decryption_key)

def encode_decryption_key_share(decryption_key_share: G1) -> bytes:
    return encode_g1(k)

def encode_encrypted_message(encrypted_message: EncryptedMessage) -> bytes:
    c1, c2, c3 = encrypted_message
    return encode_g2(c1) + c2 + b"".join(c3)
```
