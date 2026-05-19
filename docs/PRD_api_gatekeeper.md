# PRD API Gatekeeper

## Purpose
Centralize all external API execution, rate limiting, queueing, retries, and logging.

## Requirements
- Enforce requests per minute, requests per hour, and concurrent max from `config/rate_limits.json`.
- Queue requests FIFO when limits are reached.
- Apply exponential backoff on transient exceptions.
- Raise backpressure errors when the queue is full.
- Log each completed or failed API call.

## Interface
- `ApiGatekeeper.execute(service, api_call, *args, **kwargs)`
- `ApiGatekeeper.get_queue_status(service)`

## Acceptance
- Unit tests cover limits, FIFO ordering, retry backoff, logging, and backpressure.
