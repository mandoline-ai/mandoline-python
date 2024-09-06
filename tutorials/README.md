# Mandoline Python Tutorials

This directory contains tutorials and examples for using the Mandoline Python client.

## Contents

1. `quick_start.py`: A basic introduction to using the Mandoline client.
2. `prompt_engineering.py`: An example of using Mandoline for prompt engineering tasks.
3. `model_selection.py`: A tutorial on comparing different language models using Mandoline.
4. `get_metrics.py`: A simple demo that fetches all metrics with a "personality" tag.

## Setup

1. Ensure you're in the tutorials directory:

   ```bash
   cd tutorials
   ```

2. Install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in this directory with your API keys:

   ```
   export MANDOLINE_API_KEY=your_mandoline_api_key
   export OPENAI_API_KEY=your_openai_api_key
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Running the Tutorials

To run a specific tutorial, use the following commands:

1. Source the environment variables:

   ```bash
   source .env
   ```

2. Run the desired script:

   ```bash
   python quick_start.py
   # or
   python prompt_engineering.py
   # or
   python model_selection.py
   # or
   python get_metrics.py
   ```

## Modifying the Tutorials

Feel free to modify these scripts to experiment with different prompts, metrics, or models. The tutorials are designed to be starting points for your own experiments with Mandoline.

## Additional Resources

- For more information on the Mandoline API, visit the [official documentation](https://mandoline.ai/docs).
- If you encounter any issues or have questions, please [open an issue](https://github.com/mandoline-ai/mandoline-python/issues) or contact Mandoline support at [support@mandoline.ai](mailto:support@mandoline.ai).
