import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from embedding_generator import EmbeddingGenerator

# Initialize the generator
generator = EmbeddingGenerator()

# Generate embedding for the image
image_embedding = generator.generate_embedding(["data/images/crime_scene1.jpg"], "vision")

# Print the shape
print(image_embedding.shape)
# Expected Output: (1024,)