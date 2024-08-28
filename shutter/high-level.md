# Opt-in Shutterized Gnosis Chain -- High Level Overview

This document gives a high level overview over the Opt-in Shutterized Gnosis Chain proposal.

## Introduction

The goal of this proposal is to give users of Gnosis Chain the ability to submit transactions in a censorship and frontrunning resistant manner. This is achieved by enabling users to encrypt their transactions. The protocol decrypts and executes them only once it has decided to include them and once the order of all ancestor transactions has been finalized. Thus, a potential third party with the goal to censor or frontrun has to perform their attack without knowledge of the transaction content, rendering it ineffective.

Instead of trusting a single entity or the user to decrypt the transaction at the right time, the protocol relies on threshold cryptography. As long as a tunable majority of a reasonably sized committee acts honestly, transactions are guaranteed to be decrypted neither early nor late, either of which would break the security guarantees of the protocol.

In order to minimize risks, the proposal is designed in a way such that it does not require any changes to the underlying protocol, i.e., without requiring Gnosis Chain to hard fork. Only participation by a subset of all validators is necessary, and they can freely opt-in and out.

## Protocol

The protocol involves the validators of Gnosis Chain in their capacity as _block proposers_, a set of nodes called _keypers_, and the _users_ of the chain who seek to send transactions.

![System overview](https://knowhow.brainbot.com/uploads/9e39e260-f67b-4c7e-a989-a6125e2fde0c.png)

### Preparation

A smart contract defines the threshold committee called _keyper set_ and the _threshold_, a parameter representing the minimum number of members that is assumed to be honest. To set up, the keyper set runs a distributed key generation protocol, outputting a _secret share_ for each member and the shared _eon key_. They publish the eon key by sending it to the _eon key broadcast contract_ and vote on it. If a key collects votes from at least `threshold` keypers, the eon key is accepted.

Infrequently and according to the rules defined by the smart contract, the keyper set may change. In this case, new secret shares and a new eon key is generated. The time span, measured in Gnosis Chain blocks, in which one particular keyper set is in charge is called an _eon_. Eons are numbered by the _eon index_.

Validators can opt into participating in the protocol by registering in the _validator registry contract_. By doing so, they commit themselves to follow a more constrained block production process described below.

### Transaction Submission

Instead of sending a transaction in plaintext, users may encrypt it. The encrypted blob has to be annotated with the transaction hash, the gas limit, and the current eon. The resulting tuple is wrapped in an envelope transaction that submits it to the _sequencer contract_. Users can also encrypt "bundles" of transactions all at once.

The encryption function takes the eon key and an identity value as parameters. The identity value is derived from a user defined random value and the sender address of the envelope transaction. Note that the identity value can be reconstructed from the envelope transaction, but cannot be forged without control over the sender account.

The sequencer contract manages a set of transaction queues, one for each eon. Upon submission, encrypted transactions are appended to the end of the queue corresponding to the given eon. Submitting a transaction requires burning the specified amount of gas at the current base fee price.

### Block Production

At the start of a slot whose assigned block producer has registered in the validator registration contract, the keyper set generates the decryption keys for a slice of encrypted transactions in the sequencer contract's transaction queue for the current eon. The slice starts with the first transaction in the queue that has not been decrypted for an earlier slot. The length of the slice is as long as possible without the sum of the transactions' gas limits exceeding the _encrypted gas limit_, a system parameter.

![Transaction Queue](https://knowhow.brainbot.com/uploads/7f2ab108-60e3-4e2b-9e20-28853026cf32.png)

Each keyper derives the _decryption key shares_ from their secret share and the identity values of the transactions in the slice. The shares are broadcast and anyone, once they received them from at least _threshold_ keypers, can aggregate them to derive the decryption keys for all transactions in the slice.

In addition, the keypers also generate an aggregate signature of the start and the end of the slice of transactions to decrypt, i.e., for which transactions the decryption keys are for. Both key (shares) and (individual) signatures can be sent in one message, resulting in no additional round trip.

Upon receiving the decryption keys and the aggregate signature from the keypers, the block producer fetches the transactions to decrypt from the sequencer contract and decrypts them. Subsequently, it builds the block by adding transactions one by one in the order given by the decryption key message. Transactions that fail to be decrypted, that have a different hash or gas limit from what was specified, or that would make the block invalid are not included. The rest of the block can be filled at will.

## Security Analysis

The system makes the following security assumptions:

1. Participating proposers are honest and online.
2. At least _threshold_ keypers are honest and online.
3. The decryption key generation and broadcast is fast enough so that the proposer can decrypt and propose in time.
4. There are no reorgs.
5. Priority fees are not needed to incentivize validators.

In particular assumption (1) is strong. Future versions can loosen it considerably by introducing slashing conditions for falsely constructed blocks or by making them invalid (the latter would require a hard fork).

Assumption (2) can be justified by choosing a large, diverse, and a keyper set that is incentivized for the long-term.

Assumption (4) is usually met in practice. Many MEV protection and extraction protocols rely on it as well. Single-slot finality would guarantee it.

Assumption (5) is met in practice on Gnosis Chain, where the majority of validator revenue comes from the protocol instead from priority fees.

### Scenarios

##### A user submits bad data.

Bad data could be

- undecryptable data
- encrypted data whose plaintext is not a valid transaction
- an encrypted transaction whose plaintext cannot be included, for instance because the nonce is wrong
- an encrypted transaction whose gas limit or hash does not match the values given in the envelope

In these cases, the proposer would not include the transaction in the "encrypted" section of the block according to the block construction rules. If the transaction is valid, they or a future proposer may include it in the "plaintext" section of a block. This allows for frontrunning, but in most cases it is due to a fault of the sender. A potential exception is a low maximum base fee in situations of rapidly rising block base fee. The chance of this happening can be reduced by using high values for the maximum base fee. This issue could be fixed with a protocol change.

##### The queue contains more transactions than fit into a block.

In this case, the keypers would only decrypt transactions who are guaranteed to fit into the next block, according to the user specified gas limits. The remaining transactions would be decrypted and included in future blocks.

##### A user spams the queue by submitting many transactions that use up huge amounts of gas each.

This is possible, but the user has to pay for the gas they consume. Similar attacks are possible with plaintext transactions today. The main difference is that using up all gas earmarked for encrypted transactions does not necessarily lead to an increase in the block base fee which is based on the total gas usage. Thus, it is possible that spamming the encrypted queue is relatively cheap.

One possible solution is to allow all block gas to be used by encrypted transactions. Another, more complicated solution would be to setup a separate fee market and/or base fee mechanism specifically for encrypted transactions.

##### The keypers decrypt transactions too early.

This would allow them to put a frontrunning transaction at the end of the previous block and a backrunning transaction after it in the sequencer queue (unless it is full for the current block already). Note that this would require a threshold of keypers to collude and break security assumption (2).

##### The keypers decrypt transactions too late.

In this case, the proposer would be unable to produce a block according to the rules of the protocol and require them to skip. At this stage, the keypers still have the option to not generate the decryption keys for this block at all, preventing further harm. If they do, a future proposer can frontrun and sandwich these transactions however they choose.

It is therefore vital to ensure sufficient performance of the decryption key generation and broadcast protocol.

##### A block proposer is offline.

If a block proposer is offline and they thus fail to produce a block, the decryption keys for the transactions become public and the producer of the next block can frontrun them. Note that this would break security assumption (1).

One possible solution is to enforce the block production rules in the protocol, thus requiring future block producers to abide by the determined transaction order as well. However, this would require a hard fork. Under the assumption that the proposer's behavior is merely accidental and not malicious, other options are to decrypt the decryption key shares for the proposer's public key so that only they have access to it, or to make the keypers only release the key if they have assurance that the validator is online (e.g. by observing recently sent attestations).

##### A keyper is offline and becomes online. How do they determine where in the transaction queue to start at?

One option is to passively observe the network for decryption keys generated by the rest of the set. This works well if only few keypers are offline, but not if the whole set is disfunctional. A safer, more involved option is to reconstruct when and which keys should have been produced so far based on the history of the transaction queue (in particular, when and which transactions have been added). This can be supported by regularly persisting the decryption key messages or making them available on the p2p layer.

##### A block proposer builds a block that does not include some of the transactions from the queue or includes them in a different order.

This is malicious behavior which would break security assumption (2). It can be prevented by enforcing the block production rules in-protocol, i.e., making differently constructed blocks invalid. However, this would require a hard fork. In the mean time, it is possible to introduce a slashing mechanism that punishes this behavior.

##### User A submits an encrypted transaction, and B frontruns the submission with another one that uses the same identity value.

As there is exactly one decryption key for each identity value (given an eon key), this would lead to A's transaction to be decrypted early and thus make it susceptible for frontrunning. However, since the identity value is derived from the address that submitted the transaction, only A can do this (or whoever A delegates this task to).
