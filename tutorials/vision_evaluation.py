import base64
import os

from mandoline import Mandoline


def create_data_uri(image_path: str) -> str:
    """
    Convert image file to data URI

    Args:
        image_path: Path to the image file

    Returns:
        Data URI string
    """
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Get file extension and determine MIME type
    _, ext = os.path.splitext(image_path)
    ext = ext.lower().lstrip(".")

    # Convert jpg to jpeg for MIME type
    if ext == "jpg":
        ext = "jpeg"

    mime_type = f"image/{ext}"
    base64_data = base64.b64encode(image_data).decode("utf-8")

    return f"data:{mime_type};base64,{base64_data}"


def evaluate_vector_design():
    try:
        mandoline = Mandoline()

        # Create a metric for evaluating visual design quality
        metric = mandoline.create_metric(
            name="Visual Asset Design",
            description="Evaluates design quality of minimalist vector illustrations, focusing on composition, line work, and dimensionality",
            tags=["design", "vector-art", "minimalist"],
        )

        # Load and convert image to data URI
        response_image = create_data_uri("./mandoline.png")

        # Create evaluation
        evaluation = mandoline.create_evaluation(
            metric_id=metric.id,
            prompt="Create a minimalist vector illustration of a mandoline slicer with strong dimensionality. Use black strokes and include key features like the blade, ridged surface, and feet.",
            response_image=response_image,
            properties={"style": "vector-illustration", "perspective": "isometric"},
        )

        print(f"Evaluation score: {evaluation.score}")

    except Exception as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    # Run the demo
    evaluate_vector_design()
