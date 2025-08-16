# Spec: Add Async Context Manager Support to AsyncMandoline

## Problem Statement

AsyncMandoline currently requires direct instantiation and doesn't support Python's `async with` pattern, which is the standard convention for async HTTP clients. This creates a suboptimal developer experience and deviates from established Python async patterns.

## Current State

```python
# Current usage
async_mandoline = AsyncMandoline()
metrics = await async_mandoline.get_metrics()
```

## Proposed Solution

Add `__aenter__` and `__aexit__` methods to AsyncMandoline to support:

```python
# Proposed usage
async with AsyncMandoline() as client:
    metrics = await client.get_metrics()
```

## Implementation Details

### AsyncMandoline Changes

1. Add `__aenter__()` method that returns `self`
2. Add `__aexit__()` method for proper cleanup protocol
3. Maintain backward compatibility - direct instantiation still works

### Technical Considerations

- Current architecture creates/closes AsyncClient per request, so no persistent resources need cleanup
- Implementation should be minimal and not change existing behavior
- Future-proofs for potential connection pooling additions

## Testing Requirements

1. Verify `async with` pattern works correctly
2. Ensure backward compatibility with existing direct instantiation
3. Test proper resource cleanup (even if currently no-op)
4. Update tutorial examples to demonstrate both patterns

## Success Criteria

- AsyncMandoline supports `async with` pattern
- All existing code continues to work unchanged
- Tutorial demonstrates both usage patterns
- Tests pass for both instantiation methods