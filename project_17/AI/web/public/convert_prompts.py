import os
import json
from pathlib import Path

def convert_prompts_to_json():
    # Get the Data directory path - using absolute path
    data_dir = Path('E:/AI/Data')
    prompts = []

    # Walk through all directories and files
    for category in data_dir.iterdir():
        if category.is_dir():
            for file in category.glob('*.md'):
                try:
                    # Read the markdown file
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create prompt object
                    prompt = {
                        'id': f"{category.name}-{file.stem}",
                        'category': category.name,
                        'title': file.stem,
                        'content': content
                    }
                    prompts.append(prompt)
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    # Write to JSON file
    output_file = Path('E:/AI/web/public/Data/prompts.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    convert_prompts_to_json() 