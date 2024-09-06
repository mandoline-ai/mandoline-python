from typing import Any, Dict, List
from uuid import UUID

from anthropic import Anthropic
from openai import OpenAI

from mandoline import Evaluation, Mandoline, Metric

# Step 1: Set Up Your Experiment
mandoline = Mandoline()
openai_client = OpenAI()
anthropic_client = Anthropic()


# Step 2: Define Metrics
def create_metrics() -> List[Metric]:
    metric_definitions: List[tuple[str, str]] = [
        (
            "Conceptual Leap",
            "Assesses the model's ability to generate unconventional ideas.",
        ),
        (
            "Contextual Reframing",
            "Measures how the model approaches problems from different perspectives.",
        ),
        (
            "Idea Synthesis",
            "Evaluates the model's capacity to connect disparate concepts.",
        ),
        (
            "Constraint Navigation",
            "Examines how the model handles limitations creatively.",
        ),
        (
            "Metaphorical Thinking",
            "Looks at the model's use of figurative language to explore ideas.",
        ),
    ]

    return [
        mandoline.create_metric(name=name, description=description)
        for name, description in metric_definitions
    ]


# Step 3: Generate Responses
def generate_ideas(*, prompt: str, model: str) -> str:
    if model == "gpt-4":
        completion = openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content or ""
    elif model == "claude":
        msg = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    raise ValueError("Unsupported model")


# Step 4: Evaluate Responses
def evaluate_response(
    *, metric: Metric, prompt: str, response: str, model: str
) -> Evaluation:
    return mandoline.create_evaluation(
        metric_id=metric.id,
        prompt=prompt,
        response=response,
        properties={"model": model},
    )


# Step 5: Run Experiments
def run_experiment(*, prompt: str, metrics: List[Metric]) -> Dict[str, Dict[str, Any]]:
    models: List[str] = ["gpt-4", "claude"]
    results: Dict[str, Dict[str, Any]] = {}

    for model in models:
        response = generate_ideas(prompt=prompt, model=model)
        results[model] = {
            "response": response,
            "evaluations": [
                evaluate_response(
                    metric=metric, prompt=prompt, response=response, model=model
                )
                for metric in metrics
            ],
        }

    return results


# Step 6: Analyze Results
def analyze_results(*, metric_id: UUID) -> None:
    # Fetch evaluations for the given metric
    evaluations = mandoline.get_evaluations(metric_id=metric_id)

    # Group evaluations by model
    grouped_by_model: Dict[str, List[Evaluation]] = {}
    for eval in evaluations:
        model = eval.properties["model"]
        if model not in grouped_by_model:
            grouped_by_model[model] = []
        grouped_by_model[model].append(eval)

    # Calculate and print average scores for each model
    for model, evals in grouped_by_model.items():
        avg_score = sum(eval.score for eval in evals) / len(evals)
        print(f"Average score for {model}: {avg_score:.2f}")


# Main function to run the experiment
def main() -> None:
    try:
        metrics = create_metrics()
        prompt = "If humans could photosynthesize like plants, how would our daily lives and global systems be different?"

        print("Running experiment...")
        experiment_results = run_experiment(prompt=prompt, metrics=metrics)
        print(experiment_results)

        print("\nAnalyzing results...")
        for metric in metrics:
            print(f"\nResults for {metric.name}:")
            analyze_results(metric_id=metric.id)

        print(
            "\nExperiment complete. Use these insights to inform your model selection."
        )
    except Exception as error:
        print("An error occurred:", error)


if __name__ == "__main__":
    main()
