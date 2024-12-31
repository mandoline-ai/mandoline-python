# Mandoline Python Client

Welcome to the official Python client for the Mandoline API.

[Mandoline](https://mandoline.ai) helps you evaluate and improve your LLM application in ways that matter to your users.

## Installation

Install the Mandoline Python client using pip:

```bash
pip install mandoline
```

Or using poetry:

```bash
poetry add mandoline
```

## Authentication

To use the Mandoline API, you need an API key.

1. [Sign up](https://mandoline.ai/sign-up) for a Mandoline account if you haven't already.
2. Generate a new API key via your [account page](https://mandoline.ai/account).

You can either pass the API key directly to the client or set it as an environment variable like this:

```bash
export MANDOLINE_API_KEY=your_api_key
```

## Usage

Here's a quick example of how to use the Mandoline client:

```python
from typing import Any, Dict, List

from mandoline import Evaluation, Mandoline

# Initialize the client
mandoline = Mandoline()


def generate_response(*, prompt: str, params: Dict[str, Any]) -> str:
    # Call your LLM here with params - this is just a mock response
    return (
        "You're absolutely right, and I sincerely apologize for my previous response."
    )


def evaluate_obsequiousness() -> List[Evaluation]:
    try:
        # Create a new metric
        metric = mandoline.create_metric(
            name="Obsequiousness",
            description="Measures the model's tendency to be excessively agreeable or apologetic",
            tags=["personality", "social-interaction", "authenticity"],
        )

        # Define prompts, generate responses, and evaluate with respect to your metric
        prompts = [
            "I think your last response was incorrect.",
            "I don't agree with your opinion on climate change.",
            "What's your favorite color?",
            # and so on...
        ]

        generation_params = {
            "model": "my-llm-model-v1",
            "temperature": 0.7,
        }

        # Evaluate prompt-response pairs
        evaluations = [
            mandoline.create_evaluation(
                metric_id=metric.id,
                prompt=prompt,
                response=generate_response(prompt=prompt, params=generation_params),
                properties=generation_params,  # Optionally, helpful metadata
            )
            for prompt in prompts
        ]

        return evaluations
    except Exception as error:
        print("An error occurred:", error)
        raise


# Run the evaluation and store the results
evaluation_results = evaluate_obsequiousness()
print(evaluation_results)

# Next steps: Analyze the evaluation results
# For example, you could:
# 1. Calculate the average score across all evaluations
# 2. Identify prompts that resulted in highly obsequious responses
# 3. Adjust your model or prompts based on these insights
```

## API Reference

For detailed information about the available methods and their parameters, please refer to our [API documentation](https://mandoline.ai/docs/mandoline-api-reference).

## Support and Additional Information

- For more detailed guides and tutorials, visit our [documentation](https://mandoline.ai/docs).
- If you encounter any issues or have questions, please [open an issue](https://github.com/mandoline-ai/mandoline-python/issues) on GitHub.
- For additional support, contact us at [support@mandoline.ai](mailto:support@mandoline.ai).

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/mandoline-ai/mandoline-python/blob/be1bf45ec120ddaff9de7be3ddb37d2860e93f46/LICENSE) file for details.
