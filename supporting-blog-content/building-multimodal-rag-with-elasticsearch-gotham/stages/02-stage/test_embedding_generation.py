import sys
import os
import base64

# Add the src directory to Python path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
)

from elastic_manager import ElasticsearchManager

INFERENCE_ID = ".jina-embeddings-v5-omni-small"

# Initialize the ES manager
es = ElasticsearchManager.connect_elasticsearch()

# Generate embedding for text
text_response = es.inference.embedding(
    inference_id=INFERENCE_ID,
    embedding={
        "input": [
            {
                "content": {
                    "type": "text",
                    "format": "text",
                    "value": "Why so serious?",
                }
            }
        ],
        "input_type": "search",
    },
)
text_embedding = text_response["embeddings"][0]["embedding"]
print(f"Text embedding dims: {len(text_embedding)}")

# Generate embedding for the image
with open("data/images/crime_scene1.jpg", "rb") as file:
    encoded = base64.b64encode(file.read()).decode("utf-8")
image_content = f"data:image/jpeg;base64,{encoded}"

image_response = es.inference.embedding(
    inference_id=INFERENCE_ID,
    embedding={
        "input": [
            {
                "content": {
                    "type": "image",
                    "format": "base64",
                    "value": image_content,
                }
            }
        ],
        "input_type": "search",
    },
)
image_embedding = image_response["embeddings"][0]["embedding"]
print(f"Image embedding dims: {len(image_embedding)}")

# Generate embedding for audio
with open("data/audios/joker_laugh.wav", "rb") as file:
    encoded = base64.b64encode(file.read()).decode("utf-8")
audio_content = f"data:audio/wav;base64,{encoded}"


audio_response = es.inference.embedding(
    inference_id=INFERENCE_ID,
    embedding={
        "input": [
            {
                "content": {
                    "type": "audio",
                    "format": "base64",
                    "value": audio_content,
                }
            }
        ],
        "input_type": "search",
    },
)
audio_embedding = audio_response["embeddings"][0]["embedding"]
print(f"Audio embedding dims: {len(audio_embedding)}")
