# Fix Tutorial Version Mismatch

## Problem

The tutorials directory contains `get_metrics_async.py` which uses `AsyncMandoline` class, but `tutorials/requirements.txt` still pins `mandoline==0.4.0`. The `AsyncMandoline` class was added in version 0.5.0, causing import errors for users following the tutorial.

## Current State

- Package version: 0.5.0 (mandoline/__init__.py)
- Tutorial requirements: mandoline==0.4.0 (tutorials/requirements.txt)
- Tutorial script: get_metrics_async.py imports AsyncMandoline

## Solution

1. Update `tutorials/requirements.txt` to pin `mandoline==0.5.0` to match the current package version
2. Create isolated virtual environment in `tutorials/.venv` to test actual user experience
3. Install requirements in isolated environment and verify all tutorial scripts work

## Files to Change

- `tutorials/requirements.txt`: Update version from 0.4.0 to 0.5.0
- `tutorials/.venv/`: Create isolated virtual environment for testing

## Testing

- Create fresh virtual environment in tutorials directory
- Install from updated requirements.txt (which pulls from PyPI)
- Verify tutorial scripts can import AsyncMandoline after version update
- Run get_metrics_async.py to ensure no import errors
- Test represents actual user experience, not development environment

## Success Criteria

- tutorials/requirements.txt specifies mandoline==0.5.0
- get_metrics_async.py can successfully import AsyncMandoline
- No breaking changes to other tutorial dependencies