from flask import Flask, render_template, jsonify, request
import os
from prompt_builder import PromptBuilder

app = Flask(__name__)
prompt_builder = PromptBuilder()

@app.route('/')
def index():
    # Get all categories and their blocks
    blocks = {}
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data')
    
    for category in os.listdir(data_dir):
        category_path = os.path.join(data_dir, category)
        if os.path.isdir(category_path):
            blocks[category] = []
            for file in os.listdir(category_path):
                if file.endswith('.md'):
                    blocks[category].append(file[:-3])  # Remove .md extension
    
    return render_template('index.html', blocks=blocks)

@app.route('/preview/<category>/<block_name>')
def preview_block(category, block_name):
    try:
        preview = prompt_builder.get_block_preview(category, block_name)
        parameters = prompt_builder.get_block_parameters(category, block_name)
        return jsonify({
            'preview': preview,
            'parameters': parameters
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/preview', methods=['POST'])
def preview_prompt():
    try:
        data = request.get_json()
        blocks = data.get('blocks', [])
        focus_message = data.get('focus_message', '')
        
        # Clear previous blocks and parameters
        prompt_builder.clear()
        
        # Add blocks in order
        for block in blocks:
            prompt_builder.add_block(block['category'], block['name'])
            # Add parameters for this block
            for param_name, param_value in block['parameters'].items():
                prompt_builder.add_parameter(block['name'], param_name, param_value)
        
        # Build the prompt with focus message
        preview = prompt_builder.build_preview(focus_message)
        return jsonify({'preview': preview})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/build', methods=['POST'])
def build_prompt():
    try:
        data = request.get_json()
        blocks = data.get('blocks', [])
        focus_message = data.get('focus_message', '')
        
        # Clear previous blocks and parameters
        prompt_builder.clear()
        
        # Add blocks in order
        for block in blocks:
            prompt_builder.add_block(block['category'], block['name'])
            # Add parameters for this block
            for param_name, param_value in block['parameters'].items():
                prompt_builder.add_parameter(block['name'], param_name, param_value)
        
        # Build the prompt with focus message
        prompt = prompt_builder.build(focus_message)
        return jsonify({'prompt': prompt})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)