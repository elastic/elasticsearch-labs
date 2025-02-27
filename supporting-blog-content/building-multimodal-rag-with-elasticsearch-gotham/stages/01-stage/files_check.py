import os

# Base directory for clues
data_dir = "data"

# List of expected files
evidences = {
    "images": ["crime_scene1.jpg", "crime_scene1.jpg", "joker_alley.jpg"],
    "audios": ["joker_laugh.wav"],
    "texts": ["riddle.txt", "note2.txt"],
    "depths": ["depth_suspect.png"],
}

# Create directories if they don't exist
for category, files in evidences.items():
    category_path = os.path.join(data_dir, category)
    os.makedirs(category_path, exist_ok=True)

    for file in files:
        file_path = os.path.join(category_path, file)
        if not os.path.exists(file_path):
            print(f"Warning: {file} not found in {category_path}.")

print("All files are correctly organized!")
