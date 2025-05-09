import os
import json
import markdown
from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)

def parse_markdown_file(file_path):
    """Parse markdown file and extract prompts."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert markdown to HTML
    html = markdown.markdown(content)
    
    # Extract prompts from markdown
    prompts = []
    current_prompt = {}
    
    for line in content.split('\n'):
        if line.startswith('# '):
            if current_prompt:
                prompts.append(current_prompt)
            current_prompt = {
                'name': line[2:].strip(),
                'description': '',
                'template': ''
            }
        elif line.startswith('## '):
            current_prompt['description'] = line[3:].strip()
        elif line.strip() and not line.startswith('#'):
            current_prompt['template'] += line + '\n'
    
    if current_prompt:
        prompts.append(current_prompt)
    
    return prompts

def parse_json_file(file_path):
    """Parse JSON file and extract prompts."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('prompts', [])

def load_prompts_from_directory(directory):
    """Load all prompts from a directory."""
    prompts = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                category = os.path.basename(root)
                file_path = os.path.join(root, file)
                category_prompts = parse_markdown_file(file_path)
                if category_prompts:
                    if category not in prompts:
                        prompts[category] = {
                            'icon': '📝',
                            'description': f'Prompts from {category}',
                            'prompts': []
                        }
                    prompts[category]['prompts'].extend(category_prompts)
            
            elif file.endswith('.json'):
                category = os.path.basename(root)
                file_path = os.path.join(root, file)
                category_prompts = parse_json_file(file_path)
                if category_prompts:
                    if category not in prompts:
                        prompts[category] = {
                            'icon': '📝',
                            'description': f'Prompts from {category}',
                            'prompts': []
                        }
                    prompts[category]['prompts'].extend(category_prompts)
    
    return prompts

@app.route('/load-prompts')
def load_prompts():
    """API endpoint to load prompts."""
    try:
        data_dir = Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data'))
        if not data_dir.exists():
            return jsonify({'error': 'Data directory not found'}), 404
            
        prompts = load_prompts_from_directory(data_dir)
        if not prompts:
            return jsonify({'error': 'No prompts found'}), 404
            
        return jsonify(prompts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add error handler for 404 Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

if __name__ == '__main__':
    app.run(port=5000)