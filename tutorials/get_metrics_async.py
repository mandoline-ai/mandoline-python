import asyncio
from typing import List

from mandoline import AsyncMandoline, Metric


async def get_personality_metrics_direct() -> None:
    """Example using direct instantiation (original pattern)."""
    async_mandoline = AsyncMandoline()
    try:
        metrics: List[Metric] = await async_mandoline.get_metrics(tags=["personality"])
        print("Personality metrics (direct):", metrics)
    except Exception as error:
        print("An error occurred:", error)


async def get_personality_metrics_context_manager() -> None:
    """Example using async context manager (recommended pattern)."""
    try:
        async with AsyncMandoline() as client:
            metrics: List[Metric] = await client.get_metrics(tags=["personality"])
            print("Personality metrics (context manager):", metrics)
    except Exception as error:
        print("An error occurred:", error)


async def main() -> None:
    print("Demonstrating both usage patterns:")
    await get_personality_metrics_direct()
    await get_personality_metrics_context_manager()


if __name__ == "__main__":
    asyncio.run(main())