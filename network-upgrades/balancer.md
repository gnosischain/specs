# Balancer Upgrade Specification

## Included changes

This hard fork introduces an irregular state change to recover the stolen funds of the Balancer V2 hack on November 2025.

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


