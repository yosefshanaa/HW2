# PRD Logging Pipeline

## Purpose
Provide asynchronous FIFO logging into rotating files.

## Requirements
- Log path and limits come from configuration.
- Raw events are written to a FIFO.
- A background consumer formats events as `[ISO8601] [LEVEL] [COMPONENT] Message`.
- Rotating storage uses a circular set of files with configured max file and line counts.

## Interface
- `FifoLogger.log(level, component, message)`
- `LogConsumer.start()` and `stop()`
- `RotatingWriter.write(entry)`

## Acceptance
- Tests verify FIFO creation, formatting, line limits, circular overwrite, and concurrent no-loss pipeline behavior.
