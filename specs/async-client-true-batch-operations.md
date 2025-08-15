# Async Mandoline Client with True Batch Operations

## Overview

Create an async Mandoline client that provides true concurrent batch operations by reusing existing infrastructure and only adding async capabilities.

## Implementation Approach

### 1. Reuse Existing Infrastructure

The async client will hook into existing components:
- `MandolineRequestConfig` for timeout and URL configuration
- Existing Pydantic models (`Metric`, `Evaluation`, etc.)
- Same auth header logic
- Same error handling from `mandoline.errors`
- Same URL processing and request body logic

### 2. New Async Components

#### `AsyncMandoline` Client
- Same constructor signature as sync client
- Reuses `MandolineRequestConfig` for configuration
- Async versions of all CRUD operations
- True concurrent batch operations

#### Async Connection Manager
- Create async version of `make_request()` using `httpx.AsyncClient`
- Reuse existing `process_url()`, `process_request_body()`, `process_response()`
- Use same timeout configuration from `MandolineRequestConfig`

### 3. True Batch Operations

Replace the sync client's pseudo-batch methods with real concurrent operations:

```python
async def batch_create_metrics(
    self, *, metrics: List[MetricCreate]
) -> List[Metric]:
    """Creates multiple metrics concurrently."""

async def batch_create_evaluations(
    self, *, evaluations: List[EvaluationCreate]  
) -> List[Evaluation]:
    """Creates multiple evaluations concurrently."""
```

### 4. Sync Client Cleanup

Remove misleading batch methods from sync client:
- Remove `batch_create_metrics()`
- Remove `batch_create_evaluations()`

## Files to Create/Modify

### New Files:
- `mandoline/async_client.py` - AsyncMandoline class
- `mandoline/async_connection_manager.py` - Async request handling

### Modified Files:
- `mandoline/client.py` - Remove batch methods
- `mandoline/__init__.py` - Export AsyncMandoline

## Key Benefits

1. **True Concurrency**: Uses `asyncio.gather()` for parallel API calls
2. **Minimal Code**: Reuses 90% of existing infrastructure 
3. **Consistent API**: Same method signatures with async/await
4. **Proper Configuration**: Uses existing timeout and config system
5. **Clean Separation**: Sync for simple use, async for performance