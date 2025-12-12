# Balancer Upgrade Specification

## Included changes

This hard fork specification introduces an irregular state change intended to recover funds stolen in the Balancer V2 hack in November 2025. Whether and when this specification is activated on Gnosis Chain depends on validator adoption and client configuration.

| EIP | Scope |  |
| - | - | - |
| TBD: Balancer recovery | EL 

### Balancer recovery

This change is unique to Gnosis. Full specification in [`/execution/balancer_recovery.md`](../execution/balancer_recovery.md)

## Upgrade schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash  | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | ---------- | ------------------ |
| Chiado  | -            | -                             | -          | -                  |
| Mainnet | -            | -                             | -          | -                  |

### Readiness Checklist

**List of outstanding items before deployment.**

- [ ] Client Integration Testing
  - [ ] Deploy a Client Integration Testnet
  - [ ] Integration Tests
- [ ] Select Fork Triggers
  - [ ] Chiado
  - [ ] Mainnet
- [ ] Deploy Clients
- [ ] Activate Fork


