import asyncio
from typing import List

from mandoline import AsyncMandoline, Metric

async_mandoline = AsyncMandoline()


async def get_personality_metrics() -> None:
    try:
        metrics: List[Metric] = await async_mandoline.get_metrics(tags=["personality"])
        print("Personality metrics:", metrics)
    except Exception as error:
        print("An error occurred:", error)


async def main() -> None:
    await get_personality_metrics()


if __name__ == "__main__":
    asyncio.run(main())