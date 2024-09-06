from typing import List

from mandoline import Mandoline, Metric

mandoline = Mandoline()


def get_personality_metrics() -> None:
    try:
        metrics: List[Metric] = mandoline.get_metrics(tags=["personality"])
        print("Personality metrics:", metrics)
    except Exception as error:
        print("An error occurred:", error)


def main() -> None:
    get_personality_metrics()


if __name__ == "__main__":
    main()
