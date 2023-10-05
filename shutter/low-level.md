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

Each keyper has a private key `keyper_private_key` to an Ethereum address `keyper_address`. During a setup phase, they have generated `eon_secret_key_share` and a sequence of `eon_public_key_shares`.

#### Chain Monitoring

At all times, the keyper monitors the chain. They keep track of the current slot `s`. They also watch the `keyperSetManager = IKeyperSetManager(KEYPER_SET_MANAGER_ADDRESS)` for

- the current eon `eon = keyperSetManager.getKeyperSetIndexBySlot(s)`,
- the active keyper set contract `keyperSetContract = IKeyperSet(keyperSetManager.getKeyperSetAddress(eon))`,
- the active keyper set `keypers = keyperSetContract.getMembers()`, and
- the threshold `threshold = keyperSetContract.getThreshold()`.

Lastly, they monitor the `validatorRegistry = IValidatorRegistry(VALIDATOR_REGISTRY_ADDRESS)` for the set of indices of the participating validators `participating_validator_indices = get_participating_validators(state)` where `state` refers to the chain state.

#### Slot Processing

At the beginning of each slot `s`, the keyper checks if `keyper_address` is an element of `keypers`. If not, they suspend slot processing until the start of the next slot.

Otherwise, they check if the block proposer of slot `s` is registered in the Validator Registry, i.e., if their validator index is an element of `participating_validator_indices`. If they are not, they suspend slot processing until the start of the next slot.

Otherwise, they fetch the transactions `txs = get_next_transactions(state, eon, tx_pointer)` where `tx_pointer` is a local variable. `tx_pointer` is `0` for the start slot of eon `eon` as defined in the [Keyper Set Manager section](#keyper-set-manager). `tx_pointer` is updated as described in the [Decryption Keys Processing section](#decryption-keys-processing).

Based on `txs`, the keyper generates and broadcasts a `DecryptionKeyShares` message `make_decryption_key_shares_message(eon, s, keyper_index, tx_pointer, txs, eon_secret_key_share, keyper_private_key)` with `keyper_index = keypers.index(keyper_address)` as follows:

```protobuf
message DecryptionKeyShares {
    uint64 instanceID = 1;
    uint64 eon = 2;
    uint64 keyperIndex = 3;
    uint64 slot = 4;
    uint64 txPointer = 5;
    repeated KeyShare shares = 6;
    bytes signature = 7;
}

message KeyShare {
    bytes identity = 1;
    bytes share = 2;
}
```

```python
def make_decryption_key_shares_message(
    eon: uint64,
    slot: uint64,
    keyper_index: uint64,
    tx_pointer: uint64,
    txs: Sequence[SequencedTransaction],
    eon_secret_key_share: int,
    keyper_private_key: ECDSAPrivkey,
) -> DecryptionKeyShares:
    shares = [
        KeyShare(
            identity=tx.identity,
            share=compute_decryption_key_share(
                eon_secret_key_share,
                tx.identity
            ),
        )
        for tx in txs
    ]
    signature = compute_slot_decryption_identities_signature(
        instance_id=INSTANCE_ID,
        eon=eon,
        slot=slot,
        identities=[tx.identity for tx in txs],
        keyper_private_key=keyper_private_key,
    )
    return DecryptionKeyShares(
        instanceID=INSTANCE_ID,
        eon=eon,
        keyperIndex=keyper_index,
        slot=s,
        txPointer=tx_pointer + len(txs),
        shares=shares,
        signature=signature,
    )
```

#### Message Processing

##### Decryption Key Shares Processing

The keyper processes `DecryptionKeyShares` messages that they receive from the p2p network as well as those that they produce themselves. They ignore messages that are not valid according to `check_decryption_key_shares_message(key_shares_message, eon, keypers, eon_public_key_shares)`:

```python
def check_decryption_key_shares_message(
    key_shares_message: DecryptionKeyShares,
    eon: uint64,
    keypers: Sequence[Address],
    eon_public_key_shares: Sequence[G2],
) -> bool:
    if (
        key_shares_message.instanceID != INSTANCE_ID or
        key_shares_message.eon != eon
    ):
        return False

    if key_shares_message.keyperIndex >= len(keypers):
        return False

    if not all(
        check_decryption_key_share(
            share.share,
            eon_public_key_shares[key_shares_message.keyperIndex],
            share.identity,
        ) for share in key_shares_message.shares
    ):
        return False

    return check_slot_decryption_identities_signature(
        instance_id=key_shares_message.instanceID,
        eon=key_shares_message.eon,
        slot=key_shares_message.slot,
        identities=[share.identity for share in key_shares_message.shares],
        signature=key_shares_message.signature,
        keyper_address=keypers[key_shares_message.keyperIndex],
    )
```

Once the keyper has processed `threshold` valid messages `share_messages` with distinct `keyperIndex` as well as equal `slot`, `txPointer`, `len(shares)`, and `shares[j].identity` for all `j`, they generate a `DecryptionKeys` message `make_keys_message(share_messages)` as follows:

```protobuf
message DecryptionKeys {
    uint64 instanceID = 1;
    uint64 eon = 2;
    uint64 slot = 3;
    uint64 txPointer = 4;
    repeated Key keys = 5;
    repeated uint64 signerIndices = 6;
    repeated bytes signatures = 7;
}

message Key {
    bytes identity = 1;
    bytes key = 2;
}
```

```python
def make_keys_message(share_messages: Sequence[DecryptionKeyShares]) -> DecryptionKeys:
    keyper_indices = [m.keyperIndex for m in share_messages]
    identities = [share.identity for share in share_messages[0].shares]
    raw_keys = [
        compute_decryption_key(
            keyper_indices,
            [m.shares[key_index].share for m in share_messages],
        )
        for key_index, identity in enumerate(identities)
    ]
    keys = [
        Key(identity=identity, key=raw_key)
        for identity, raw_key in zip(identities, raw_keys)
    ]


    signer_indices_and_signatures = sorted([
        (m.keyperIndex, m.signature) for m in share_messages
    ])
    signer_indices = [i for i, _ in signer_indices_and_signatures]
    signatures = [s for _, s in signer_indices_and_signatures]

    return DecryptionKeys(
        instanceID=share_messages[0].instanceID,
        eon=share_messages[0].eon,
        slot=share_messages[0].slot,
        txPointer=share_messages[0].txPointer,
        keys=keys,
        signerIndices=signer_indices,
        signatures=signatures,
    )
```

They broadcast the message, unless they have already received a valid `DecryptionKeys` message with equal `instanceID`, `eon`, `slot`, and `keys`.

##### Decryption Keys Processing

The keyper processes the following `DecryptionKeys` messages:

- Messages they received on the p2p network.
- Messages they produced and broadcast themselves.
- Messages they received as the `message` argument of `DecryptionProgressSubmitted` events emitted by the sequencer contract at `SEQUENCER_ADDRESS`.

If a message `keys_message` is not valid according to `check_decryption_keys_message(keys_message, eon)` it is ignored:

```python
def check_decryption_keys_message(keys_message: DecryptionKeys, eon: uint64, threshold: uint64) -> bool:
    if keys_message.instanceID != INSTANCE_ID or keys_message.eon != eon:
        return False

    if not all(
        check_decryption_key(key_message.key, eon_public_key, key.identity)
        for key in keys.keys
    ):
        return False

    unique_signer_indices = set(keys_message.signerIndices)
    if len(keys_message.signerIndices) != unique_signer_indices:
        return False
    if len(keys_message.signatures) != len(keys_message.signerIndices):
        return False
    if len(keys_message.signatures) != threshold:
        return False

    return all(
        check_slot_decryption_identities_signature(
            instance_id=keys_message.instanceID,
            eon=keys_message.eon,
            slot=keys_message.slot,
            identities=[key.identity for key in keys_message.keys],
            signature=signature,
            keyper_address=keypers[signer_index],
        )
        for signer_index, signature in zip(keys_message.signerIndices, keys_message.signatures)
    )
```

Otherwise, the keyper updates its local `tx_pointer` to `max(tx_pointer, keys_message.txPointer)`.

### Validator

Validators keep track if they are registered in the Validator Registry, i.e., `validator_index in get_participating_validators(state)` where

- `validator_index` is the index of the validator in the Beacon Chain,
- `state` is the current Beacon Chain state, and

Registered validators subscribe to `DecryptionKeys` messages from keypers on the topic `tbd` and validate them as described under [Decryption Keys Processing](#decryption-keys-processing).

If a registered validator is selected as the block proposer for slot `s`, they hold off on producing a block until they receive a valid `DecryptionKeys` message `keys_message` where `keys_message.slot == s`. If no such message is received up until the end of `s`, the proposer proposes no block.

Once `keys_message` is received, the validator fetches those `TransactionSubmitted` events `e` from the sequencer contract that, for any `k` in `keys_message.keys`, fulfill

- `e.args.eon == keys_message.eon` and
- `compute_identity(e.args.identityPrefix, keys_message.sender) == k.identity`.

The events are fetched in the order the events were emitted. For each `e` with corresponding `k`, the validator first computes `encrypted_transaction = decode_encrypted_message(e.args.encryptedTransaction)` and then `decrypted_transaction = decrypt(encrypted_transaction, k.key)`. If any of the functions fails, they skip `e`. The decrypted transactions are appended to a list `decrypted_transactions` in the same order the events are fetched.

With the set of decrypted transactions `decrypted_transactions`, the validator constructs a block `b` with transactions `txs`. `txs[0]` makes the contract at `SEQUENCER_ADDRESS` to emit the event `DecryptionProgressSubmitted` exactly once with argument `message = keys_message`.

Transactions `txs[j]` for `j >= 1` are a subset of `decrypted_transactions`. The transactions are in the correct order, i.e., taking any two decrypted transactions `txs[i1]` and `txs[i2]` with `i2 > i1`, the corresponding indices in `decrypted_transactions` `j1` and `j2` fulfill `j2 > j1`. Furthermore, for any decrypted transaction that is missing in the block one or both of the following conditions holds:

- Inserting it in accordance with the ordering property and removing all following transactions would make the block invalid.
- Its gas limit is different from the gas limit specified by the corresponding `TransactionSubmitted` event `e` in the argument `e.args.gasLimit`.

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

This section specifies the interfaces and behavior of the smart contracts in the protocol. The id of the chain on which they are deployed is `CHAIN_ID`.

### Sequencer

The Sequencer is a contract deployed at address `SEQUENCER_ADDRESS`. It implements the following interface:

```solidity
interface ISequencer {
    function submitEncryptedTransaction(uint64 eon, bytes32 identityPrefix, address sender, bytes memory encryptedTransaction, uint256 gasLimit) external;
    function submitDecryptionProgress(bytes memory message) external;

    event TransactionSubmitted(uint64 eon, bytes32 identityPrefix, address sender, bytes encryptedTransaction, uint256 gasLimit);
    event DecryptionProgressSubmitted(bytes message);
}
```

`submitEncryptedTransaction(eon, identityPrefix, encryptedTransaction, gasLimit)` reverts if `msg.value < block.baseFee * gasLimit`. Otherwise, it emits the event `TransactionSubmitted(eon, msg.sender, identityPrefix, encryptedTransaction, gasLimit)`.

`submitDecryptionProgress(message)` emits `DecryptionProgressSubmitted(message)`.

The constant `ENCRYPTED_GAS_LIMIT` defines how much gas is earmarked for encrypted transactions. The function `get_next_transactions` retrieves a set of transactions from the queue:

```python
import dataclasses

@dataclasses.dataclass
class SequencedTransaction:
    eon: uint64
    encrypted_transaction: bytes
    gas_limit: int
    identity: G1

def get_next_transactions(state: BeaconState, eon: int, tx_pointer: int) -> Sequence[SequencedTransaction]:
    events = get_events(state, SEQUENCER_ADDRESS)
    events = [
        event for event in events
        if event.name == "TransactionSubmitted" and event.args.eon == eon
    ]
    events = events[tx_pointer:]

    txs = []
    total_gas = 0
    for event in events:
        if total_gas + event.args.gasLimit > ENCRYPTED_GAS_LIMIT:
            break
        tx = SequencedTransaction(
            eon=event.args.eon,
            encrypted_transaction=event.args.encryptedTransaction,
            gas_limit=event.args.gasLimit,
            identity=compute_identity(event.args.identityPrefix, event.args.sender),
        )
        txs.append(tx)
        total_gas += event.args.gasLimit
    return txs

@dataclasses.dataclass
class Event:
    name: str
    args: Any  # an object with attributes according to the event type

def get_events(state: BeaconState, address: Address) -> Sequence[Event]:
    """Return a list of events emitted by the contract at `address` according to `state`.

    The list is in the order in which the events were emitted.
    """
    pass
```

### Validator Registry

The Validator Registry is a contract deployed at address `VALIDATOR_REGISTRY_ADDRESS`. It implements the following interface:

```solidity
interface IValidatorRegistry {
    struct Update {
        bytes message;
        bytes signature;
    }

    function getNumUpdates() external view returns (uint256);
    function getUpdate(uint256 i) external view returns (Update memory);

    function update(
        bytes memory message,
        bytes memory signature
    ) external;

    event Updated(bytes message, bytes signature);
}
```

The contract maintains a zero-indexed sequence of `Update`s. `getNumUpdates()` returns the length of the sequence `n`, `getUpdate(i)` returns the `i`th element if `i < n` and reverts otherwise. The sequence is initially empty. `update(message, signature)` appends the element `Update(message, signature)`. It also emits the event `Updated(message, signature)`.

Validators are expected to announce their intent to start or stop participating in the protocol by calling `update(message, signature)`. `message` is computed by `compute_registration_message` or `compute_deregistration_message`, respectively:

```python
def compute_registration_message(validator_index: uint64, nonce: uint64):
    return compute_registry_message_prefix(validator_index, nonce) + b"\x01"

def compute_deregistration_message(validator_index: uint64, nonce: uint64):
    return compute_registry_message_prefix(validator_index, nonce) + b"\x00"

def compute_registry_message_prefix(validator_index: uint64, nonce: uint64):
    return VALIDATOR_REGISTRY_MESSAGE_VERSION + CHAIN_ID.to_bytes(8, "big") + VALIDATOR_REGISTRY_ADDRESS + validator_index.to_bytes(8, "big") + nonce.to_bytes(8, "big")
```

The parameters are as follows:

- `validator_index` is the Beacon Chain index of the registering or deregistering validator.
- `nonce` is a `uint64` greater than the nonce used in any previously published registration or deregistration message by the registering validator.
- `VALIDATOR_REGISTRY_MESSAGE_VERSION = b"\x00"`

`signature = bls.Sign(validator_privkey, keccak256(message))` where `validator_privkey` is the private key of the validator.

The list of indices of all participating validators is `get_participating_validators(state)` given the beacon chain state `state`:

```python
def get_participating_validators(state) -> Sequence[ValidatorIndex]:
    registry = IValidatorRegistry(VALIDATOR_REGISTRY_ADDRESS)
    indices = set()
    prev_nonces = {}

    n = registry.getNumUpdates()
    updates = [registry.getUpdate(i) for i in range(n)]
    for update in updates:
        try:
            (
                version,
                chain_id,
                validator_registry_address,
                validator_index,
                nonce,
                is_registration,
            ) = extract_message_parts(update.message)
        except:
            continue

        if version != VALIDATOR_REGISTRY_MESSAGE_VERSION:
            continue
        if chain_id != CHAIN_ID:
            continue
        if validator_registry_address != VALIDATOR_REGISTRY_ADDRESS:
            continue

        if validator_index >= len(state.validators):
            continue
        if nonce <= prev_nonces.get(validator_index, -1):
            continue

        validator_pubkey = state.validators[validator_index].pubkey
        if not bls.Verify(validator_pubkey, keccak256(message), signature):
            continue

        prev_nonces[validator_index] = nonce
        if is_registration:
            indices.add(validator_index)
        else:
            indices.remove(validator_index)

    return sorted(indices)

def extract_message_parts(message: bytes) -> tuple[bytes, uint64, Address, uint64, uint64, bool]:
    suffix = message[-1:]
    is_registration = bool(int.from_bytes(suffix, "big"))

    prefix = message[:-1]
    assert len(prefix) == 1 + 8 + 20 + 8 + 8
    version = prefix[0:1]
    chain_id_bytes = prefix[1:9]
    registry_address = prefix[9:29]
    index_bytes = prefix[29:37]
    nonce_bytes = prefix[37:45]

    chain_id = int.from_bytes(chain_id_bytes, "big")
    index = int.from_bytes(index_bytes, "big")
    nonce = int.from_bytes(nonce_bytes, "big")

    return version, chain_id, registry_address, index, nonce, is_registration
```

### Key Broadcast Contract

The Key Broadcast Contract is deployed at address `KEY_BROADCAST_CONTRACT_ADDRESS`. It implements the following interface:

```solidity
interface IKeyBroadcastContract {
    function broadcastEonKey(uint64 eon, bytes memory key) external;
    function getEonKey(uint64 eon) external view returns (bytes memory);

    event EonKeyBroadcast(uint64 eon, bytes key)
}
```

`broadcastEonKey(eon, key)` reverts if any of the following conditions is met at the time of the call:

1. The contract has already stored a key for the given eon.
2. `key` is empty.
3. `IKeyperSetManager(KEYPER_SET_MANAGER_ADDRESS).getKeyperSetAddress(eon)` reverts or returns an address different from `msg.sender`.

Otherwise, it stores `key` in a way that it is indexable by `eon` and emits the event `EonKeyBroadcast(eon, key)`.

`getEonKey(eon)` returns the key stored for `eon`, or an empty bytes value if no key for `eon` is stored.

### Keyper Set Manager

The Keyper Set Manager is a contract deployed at address `KEYPER_SET_MANAGER_ADDRESS`. It implements the following interface:

```solidity
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

Otherwise, `addKeyperSet` saves `keyperSetContract` and the corresponding `activationSlot` to storage. Finally, it emits the event `KeyperSetAdded(activationSlot, keyperSetContract)`.

Define

- `n` as the number of added keyper sets,
- `k_0 ... k_(n - 1)` as the keyper sets in the order they were added, and
- `s_0 ... s_(n - 1)` as the corresponding activation slot numbers.

Then, there are `n` eons `e_i` starting at slot `s_i` (inclusive). Eon `e_i` for `i = 0 ... n - 2` ends at slot `s_(i + 1)` (exclusive), eon `e_(n - 1)` is tentatively open ended. The keyper set for any slot in `e_i` is `k_i`.

`getNumKeyperSets()` returns `n`.

`getKeyperSetIndexBySlot(s)` reverts if `n == 0` or `s < s_0`. Otherwise, it returns `k_i` where `i` is the index of the eon that contains slot `s`.

`getKeyperSetAddress(i)` reverts if `i >= n`. Otherwise, it returns `k_i`.

`getKeyperSetActivationSlot(i)` reverts if `i >= n`. Otherwise, it returns `s_i`.

### Keyper Set Contract

Keyper set contracts are contracts which fulfill the following interface:

```solidity
interface IKeyperSet {
    function isFinalized() external view returns (bool);
    function getNumMembers() external view returns (uint64);
    function getMember(uint64 index) external view returns (address);
    function getMembers() external view returns (address[] memory);
    function getThreshold() external view returns (uint64);
}
```

If `isFinalized` returns `false`, the behavior of the contract is unspecified. If `isFinalized()` returns `true`:

- `getNumMembers()` returns a number `n` that is greater than or equal to `1`.
- `getMembers()` returns an array of `n` non-zero addresses.
- `getMember(i)` returns `getMembers()[i]` for `0 <= i < n` and the zero address for `i >= n`.
- `getThreshold()` returns a number `t` with `1 <= t <= n`.
- The return values of `isFinalized`, `getNumMembers`, `getMember`, `getMembers`, and `getThreshold` will not change in the future.

## Cryptography

This section defines the cryptographic primitives used in the protocol.

### Definitions

| Type                                              | Description                                                                                                                      |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `G1`                                              | An element of the BN256-group G1 as defined in [EIP-197](https://eips.ethereum.org/EIPS/eip-197#definition-of-the-groups)        |
| `G2`                                              | An element of the BN256-group G2 as defined in [EIP-197](https://eips.ethereum.org/EIPS/eip-197#definition-of-the-groups)        |
| `GT`                                              | An element of the BN256-group GT, the range of the pairing function defined in [EIP-197](https://eips.ethereum.org/EIPS/eip-197) |
| `Block`                                           | A 32-byte block                                                                                                                  |
| `EncryptedMessage` = (G2, Block, Sequence[Block]) | An encrypted message                                                                                                             |
| `ECDSAPrivkey`                                    | A secp256k1 ECDSA private key                                                                                                    |
| `ECDSASignature`                                  | A secp256k1 ECDSA signature encoded in format `R ++ S ++ V` where `V` is `0` or `1`                                              |
| `Address`                                         | An Ethereum address                                                                                                              |
| `uint64`                                          | An unsigned 64 bit integer                                                                                                       |

| Constant | Description                   | Value                                                                         |
| -------- | ----------------------------- | ----------------------------------------------------------------------------- |
| ORDER    | The order of groups G1 and G2 | 21888242871839275222246405745257275088548364400416034343698204186575808495617 |

The following functions are considered prerequisites:

| Function                       | Description                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| keccak256(bytes) -> Block      | The keccak-256 hash function                                                                    |
| pairing(G1, G2) -> GT          | The pairing function specified in [EIP-197](https://eips.ethereum.org/EIPS/eip-197)             |
| g1_add(G1, G1) -> G1           | Add two elements of G1                                                                          |
| g1_scalar_mult(G1, int) -> G1  | Multiply an element of G1 by a scalar                                                           |
| g1_scalar_base_mult(int) -> G1 | Multiply the generator of G1 by a scalar                                                        |
| g2_scalar_base_mult(int) -> G2 | Multiply the generator of G2 by a scalar                                                        |
| gt_scalar_mult(GT, int) -> GT  | Multiply an element of GT by a scalar                                                           |
| encode_g1(G1) -> bytes         | Encode an element of G1 according to [EIP-197](https://eips.ethereum.org/EIPS/eip-197#encoding) |
| encode_g2(G2) -> bytes         | Encode an element of G2 according to [EIP-197](https://eips.ethereum.org/EIPS/eip-197#encoding) |
| decode_g2(bytes) -> G2         | Decode an element of G2 according to [EIP-197](https://eips.ethereum.org/EIPS/eip-197#encoding) |

### Helper Functions

```python
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
    suffix_length = max((n.bit_length() + 7) // 8, 1)
    suffixes = [n.to_bytes(suffix_length, "big")]
    preimages = [sigma + suffix for suffix in suffixes]
    keys = [hash_bytes_to_block(preimage) for preimage in preimages]
    return keys

def compute_lagrange_coefficients(indices: Sequence[int]) -> Sequence[int]:
    return [compute_lagrange_coefficient(indices, i) for i in indices]

def compute_lagrange_coefficient(indices: Sequence[int], i: int) -> int:
    l = 1
    for k in indices:
        if k == i:
            continue
        l_k = compute_lagrange_coefficient_factor(k, i)
        l *= l_k
        l %= ORDER
    return l

def compute_lagrange_coefficient_factor(k: int, i: int) -> int:
    x_k = k + 1
    x_i = i + 1
    dx = (x_k - x_i) % ORDER
    dx_inv = invert(dx)
    l_k = (x_k * dx_inv) % ORDER
    return l_k

def invert(x: int) -> int:
    return x**(ORDER - 2) % ORDER
```

### Key Generation

```python
def compute_decryption_key_share(eon_secret_key_share: int, identity: G1) -> G1:
    return g1_scalar_mult(identity, eon_secret_key_share)

def compute_decryption_key(keyper_indices: Sequence[int], shares: Sequence[G1]) -> G1:
    assert len(keyper_indices) == len(shares)
    assert len(set(keyper_indices)) == len(keyper_indices)
    assert all(i >= 0 for i in keyper_indices)

    lagrange_coefficients = compute_lagrange_coefficients(keyper_indices)
    key = g1_scalar_base_mult(0)
    for lambda_, share in zip(lagrange_coefficients, shares):
        q_times_lambda = g1_scalar_mult(share, lambda_)
        key = g1_add(key, q_times_lambda)
    return key
```

### Encryption and Decryption

```python
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
    return [xor_blocks(key, block) for key, block in zip(keys, message_blocks)]

def compute_identity(prefix: bytes, sender: bytes) -> G1:
    h = keccak256(prefix + sender)
    i = int.from_bytes(h, "big")
    return g1_scalar_base_mult(i)
```

```python
def decrypt(encrypted_message: EncryptedMessage, decryption_key: G1) -> bytes:
    sigma = recover_sigma(encrypted_message, decryption_key)
    _, _, blocks = encrypted_message
    keys = compute_block_keys(sigma, len(blocks))
    decrypted_blocks = [xor_blocks(key, block) for key, block in zip(keys, blocks)]
    return unpad_and_join(decrypted_blocks)

def recover_sigma(encrypted_message: EncryptedMessage, decryption_key: G1) -> Block:
    c1, c2, _ = encrypted_message
    p = pairing(decryption_key, c1)
    key = hash_gt_to_block(p)
    sigma = xor_blocks(c2, key)
    return sigma
```

### Validation

```python
import secrets

def check_decryption_key_share(decryption_key_share: G1, eon_public_key_share: G2, identity: G1) -> bool:
    return pairing(decryption_key_share, g2_scalar_base_mult(1)) == pairing(identity, eon_public_key_share)

def check_decryption_key(decryption_key: G1, eon_public_key: G2, identity: G1) -> bool:
    message = secrets.token_bytes(32)
    sigma = secrets.token_bytes(32)
    encrypted_message = encrypt(message, identity, eon_public_key, sigma)
    try:
        decrypted_message = decrypt(encrypted_message, decryption_key)
    except:
        return False
    return message == decrypted_message
```

### Encoding

```python
def encode_decryption_key(decryption_key: G1) -> bytes:
    return encode_g1(decryption_key)

def encode_decryption_key_share(decryption_key_share: G1) -> bytes:
    return encode_g1(decryption_key_share)

def encode_encrypted_message(encrypted_message: EncryptedMessage) -> bytes:
    c1, c2, c3 = encrypted_message
    return encode_g2(c1) + c2 + b"".join(c3)

def decode_encrypted_message(b: bytes) -> EncryptedMessage:
    assert len(b) > 4 * 32 + 32 + 32
    c1_bytes = b[:4 * 32]
    c2 = b[4 * 32: 5 * 32]
    c3_bytes = b[5 * 32:]
    c1 = decode_g2(c1_bytes)
    assert len(c3_bytes) % 32 == 0
    c3 = [c3_bytes[i:i + 32] for i in range(0, len(c3_bytes), 32)]
    return (c1, c2, c3)
```

### Decryption Identities Signing

The following describes the signing for constructing the `DecryptionKeyShares` messages and the signature validation relevant for `DecryptionKeys` message. It uses the [SimpleSerialize (SSZ)](https://github.com/ethereum/consensus-specs/blob/v1.3.0/ssz/simple-serialize.md) container `SlotDecryptionIdentities`:

```python
class SlotDecryptionIdentities(Container):
    instance_id: uint64
    eon: uint64
    keyper_index: uint64
    slot: uint64
    txPointer: uint64
    identities: List[Bytes64, ceil(ENCRYPTED_GAS_LIMIT / 21000)]

def generate_hash(
    instance_id: uint64,
    eon: uint64,
    slot: uint64,
    identities: Sequence[G1],
) -> Bytes32:
    sdi = SlotDecryptionIdentities(
        instance_id=instance_id,
        eon=eon,
        slot=slot,
        identities=[encode_g1(identity) for identity for identities],
    )
    return ssz.hash_tree_root(sdi)

def compute_slot_decryption_identities_signature(
    instance_id: uint64,
    eon: uint64,
    slot: uint64,
    identities: Sequence[G1],
    keyper_private_key: ECDSAPrivkey,
) -> ECDSASignature:
    h = generate_hash(
        instance_id,
        eon,
        slot,
        identities,
    )
    return ecdsa.sign(keyper_private_key, h)

def check_slot_decryption_identities_signature(
    instance_id: uint64,
    eon: uint64,
    slot: uint64,
    identities: Sequence[G1],
    signature: ECDSASignature,
    keyper_address: Address,
) -> bool:
    h = generate_hash(
        instance_id,
        eon,
        slot,
        identities,
    )
    expected_pubkey = ecdsa.recover(h, signature)
    return keyper_address == eth.pubkey_to_address(expected_pubkey)
```
