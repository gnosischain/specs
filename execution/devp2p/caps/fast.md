# Ethereum fast sync 

The `fast` protocol runs on top of [RLPx], facilitating fast-sync algorithm. The protocol is an optional extension.

The current version is `fast/1`.

## Overview

The `fast` protocol is meant to run side-by-side with `eth` protocol.

## Protocol Messages

- GetNodeData (0x0d) `[request-id: P, [hash₁: B_32, hash₂: B_32, ...]]`
- NodeData (0x0e) `[request-id: P, [value₁: B, value₂: B, ...]]`

## Change Log

### fast/1 (September 2023)

Version 1 introduces the fast protocol.

