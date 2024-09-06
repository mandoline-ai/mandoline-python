import itertools
from typing import Callable, Dict, List, Tuple

from mandoline import Evaluation, Mandoline, Metric

# Step 1: Set Up Your Experiment
mandoline = Mandoline()


# This will mock out the LLM
class YourLLM:
    @staticmethod
    def generate(*, prompt: str) -> str:
        return f'Mock response to: "{prompt}"'


your_llm = YourLLM()


# Step 2: Create a Use-Case Specific Metric
def create_metric() -> Metric:
    return mandoline.create_metric(
        name="Moralistic Tendency",
        description="Assesses how frequently the model adopts a moralistic tone or attempts to lecture users on ethical matters.",
        tags=["tone", "personality", "user_experience"],
    )


# Step 3: Test Different Prompts
def test_prompts(*, metric: Metric) -> List[Evaluation]:
    events: List[str] = [
        "The use of atomic bombs in World War II",
        "The Industrial Revolution",
        # Add more events...
    ]

    prompt_templates: List[str] = [
        "Discuss the historical event: {event}",
        "Provide an objective overview of: {event}",
        "Describe the facts surrounding: {event}",
        "Outline key points of: {event} without moral judgment",
        # Add more templates...
    ]

    def test_prompt(*, template: str, event: str) -> Evaluation:
        prompt = template.replace("{event}", event)
        response = your_llm.generate(prompt=prompt)
        return mandoline.create_evaluation(
            metric_id=metric.id,
            prompt=prompt,
            response=response,
            properties={"template": template, "event": event},
        )

    return [
        test_prompt(template=template, event=event)
        for event in events
        for template in prompt_templates
    ]


# Step 4: Analyze the Results
def analyze_results(*, results: List[Evaluation]) -> None:
    # Overall moralistic tendency
    avg_score = sum(r.score for r in results) / len(results)
    print(f"Average Moralistic Tendency: {avg_score:.2f}")

    # Helper function for grouping
    def group_by(items: List[Evaluation], key: Callable) -> Dict[str, List[Evaluation]]:
        return {
            k: list(v) for k, v in itertools.groupby(sorted(items, key=key), key=key)
        }

    # Moralistic tendency by event
    event_scores = group_by(results, lambda r: r.properties["event"])
    for event, evals in event_scores.items():
        event_avg = sum(e.score for e in evals) / len(evals)
        print(f"{event}: {event_avg:.2f}")

    # Best prompt structure
    prompt_scores = group_by(results, lambda r: r.properties["template"])
    best_prompt: Tuple[str, float] = min(
        (
            (template, sum(e.score for e in evals) / len(evals))
            for template, evals in prompt_scores.items()
        ),
        key=lambda x: x[1],
    )
    print(f"Best prompt: {best_prompt[0]}")


# Main function to run the experiment
def main() -> None:
    try:
        metric = create_metric()
        results = test_prompts(metric=metric)
        analyze_results(results=results)

        print(
            "Next steps: Use these insights to refine your prompts and improve your LLM application."
        )
    except Exception as error:
        print("An error occurred:", error)


if __name__ == "__main__":
    main()
