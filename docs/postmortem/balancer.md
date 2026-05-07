# Balancer exploit (Nov 3, 2025) — Gnosis Chain post‑mortem

## Abstract

On Nov 3, 2025 the Balancer V2 exploit affected composable stable pools across multiple chains, including Gnosis Chain.

On Gnosis Chain, the attacker controlled funds through externally owned accounts (EOAs). A majority of validators deployed a soft‑fork level censorship rule to prevent attacker-driven fund movement while a recovery plan was designed.

Recovery and redistribution required a protocol-level intervention: a hardfork with an irregular state transition that replaced the attacker EOA code with a restricted forwarding contract, enabling controlled recovery transfers while preventing further attacker-initiated transactions.

This post‑mortem focuses exclusively on the **Gnosis Chain mitigation, coordination, and recovery hardfork execution**.

## Motivation

The immediate goals on Gnosis were:

1. Prevent unilateral movement of stolen funds on Gnosis Chain.
2. Enable safe, coordinated recovery and redistribution to affected parties.
3. Minimize blast radius: modify as little state as possible while keeping the mechanism reproducible across clients.

Censorship alone can freeze attacker activity, but cannot redistribute funds. Therefore a recovery hardfork was required.

## Timeline

- **2025-11-03** — Balancer V2 exploit. Impacted composable stable pools across multiple chains, including Gnosis Chain.

- **2025-11-05** — Emergency mitigation deployed on Gnosis: a validator/client-level soft‑fork censorship schedule to prevent transactions from known attacker EOAs to known destination contracts.

- **2025-11-06** — Censorship schedule updated (second phase), enabling the `is7702PatchEnabled` configuration change. The configuration (as shared publicly later) was:

  - `censoringSchedule[0]` at `timestamp: 0x690b5158`
    - `senders`:
      - `0x506d1f9efe24f0d47853adca907eb8d89ae03207`
      - `0x491837cc85bbeab5f9b3110ad61f39d87f8ec618`
    - `to`:
      - `0x5e7fa86cfdd10de6129e53377335b78bb34eabd3`
      - `0x234490fa3cd6c899681c8e93ba88e97183a71fe4`
      - `0x49b5ce67b22b1d596842ca071ac3da93ee593e11`
      - `0x7b23c07a0bbbe652bf7069c9c4143a2c85132166`
      - `0x1bdc1febebf92bffab3a2e49c5cf3b7e35a9e81e`
    - `is7702PatchEnabled: false`

  - `censoringSchedule[1]` at `timestamp: 0x690cfe40`
    - same `senders` / `to`
    - `is7702PatchEnabled: true`

- **2025-11-21** — Recovery hardfork spec shared with client teams (HackMD). Explicit requirements:
  - implement a way to set code on an EOA on the hardfork slot
  - disable censoring on the hardfork slot
  - start implementation ASAP to enable devnets and cut releases.

- **2025-12-12** — Client releases cut across the execution client ecosystem (Gnosis-specific forks/patches) and validation/testing continued. Reference spec (reviewed internally) landed in `gnosischain/specs` PR #87.

- **2025-12-22** — Recovery completed; approximately **$9m** sent back to affected parties. Follow-up governance work started:
  https://forum.gnosis.io/t/a-framework-for-the-future/11914

## Mitigation: validator/client-level censorship schedule

Prior to the recovery hardfork, a majority of Gnosis Chain validators deployed a soft‑fork censorship rule to prevent inclusion of transactions matching the attacker sender set and known destination contracts.

This mitigation reduced immediate risk by preventing unilateral attacker movement, and bought time for a coordinated recovery plan. However, it was not sufficient on its own to recover or redistribute funds.

A critical operational requirement for recovery was to ensure censoring would not block the recovery execution. Client teams coordinated to **disable censoring on the hardfork slot** to ensure recovery transactions could be included.

## Recovery hardfork: irregular state transition

Recovery required a hardfork implementing an irregular state transition (full specification in `gnosischain/specs` PR #87, `execution/balancer_recovery.md`).

In summary:

- During block processing of the first block whose timestamp crosses `BALANCER_HARDFORK_TIMESTAMP`, the bytecode of `BALANCER_ATTACKER_ADDRESS` is replaced with a fixed restricted forwarding contract (`BALANCER_RESCUE_BYTECODE`) controlled by `BALANCER_RESCUE_ADDRESS`.
- Only bytecode is modified. Balance, nonce and storage are not changed.
- Post-fork, attacker-signed transactions from that address cannot be included due to EIP-3607.

## Outcome

The recovery hardfork executed successfully after ~1.5 months of coordination and client releases. Approximately **$9m** was recovered and redistributed to affected parties.

A follow-up effort to develop a better framework for future incidents was initiated:
https://forum.gnosis.io/t/a-framework-for-the-future/11914
