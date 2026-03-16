# ADR-002: Use Apollo Gateway for GraphQL Federation

## Status
Accepted

## Context
The challenge requires GraphQL Federation and a gateway.

## Decision
Use Apollo Gateway in a small Node service.

## Consequences
Pros:
- standard federation story
- easy frontend integration
- clear composition layer
Cons:
- mixed-language stack
- additional service to run
