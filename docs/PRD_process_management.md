# PRD Process Management

## Purpose
Run agents in isolated subprocesses and recover from hangs or crashes.

## Requirements
- Each agent turn can run in a subprocess.
- Timeouts kill the child process and return a penalized fallback response.
- Watchdog pings expose process liveness.
- JSON FIFO transports structured IPC payloads.

## Interface
- `ProcessManager.spawn_agent(target, *args)`
- `ProcessManager.run_with_timeout(target, agent)`
- `ProcessManager.watchdog_ping(process)`
- `JsonFifo.write(payload)` and `read()`

## Acceptance
- Tests verify timeout kill/penalty, normal child response, stopped-process detection, and JSON FIFO round trip.
