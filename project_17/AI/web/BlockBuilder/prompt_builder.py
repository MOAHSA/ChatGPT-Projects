import os
import re
from typing import Dict, List, Optional, Union

class PromptBuilder:
    def __init__(self):
        self.blocks = []
        self.parameters = {}
        self.focus_message = ""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data')
    
    def clear(self):
        """Clear all blocks and parameters"""
        self.blocks = []
        self.parameters = {}
        self.focus_message = ""
    
    def add_block(self, category, block_name):
        """Add a block from a specific category"""
        self.blocks.append({
            'category': category,
            'name': block_name
        })
    
    def add_parameter(self, block_name, param_name, param_value):
        """Add a parameter for a specific block"""
        if block_name not in self.parameters:
            self.parameters[block_name] = {}
        self.parameters[block_name][param_name] = param_value
    
    def get_block_preview(self, category, block_name):
        """Get a preview of a block's content"""
        try:
            content = self.load_block(category, block_name)
            # Get first 200 characters for preview
            return content[:200] + "..." if len(content) > 200 else content
        except Exception as e:
            return f"Error loading block: {str(e)}"
    
    def load_block(self, category, block_name):
        """Load a block's content from file"""
        file_path = os.path.join(self.data_dir, category, f"{block_name}.md")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            raise Exception(f"Error loading block {block_name} from {category}: {str(e)}")
    
    def get_block_parameters(self, category, block_name):
        """Get default parameters from a block's content"""
        try:
            content = self.load_block(category, block_name)
            # Find all parameters in square brackets
            parameters = re.findall(r'\[([^\]]+)\]', content)
            return parameters
        except Exception as e:
            return []
    
    def build_preview(self, focus_message=""):
        """Build a preview of the complete prompt"""
        self.focus_message = focus_message
        return self._build_prompt()
    
    def build(self, focus_message=""):
        """Build the complete prompt"""
        self.focus_message = focus_message
        return self._build_prompt()
    
    def _resolve_parameter_value(self, value: Union[str, Dict]) -> str:
        """Resolve a parameter value, which can be either a direct string or a block reference"""
        if isinstance(value, dict):
            # This is a block reference
            try:
                return self.load_block(value['category'], value['name'])
            except Exception as e:
                return f"[Error loading block: {str(e)}]"
        return str(value)
    
    def _build_prompt(self):
        """Internal method to build the prompt"""
        if not self.blocks:
            return "No blocks added"
        
        prompt_parts = []
        
        # Add focus message if provided
        if self.focus_message:
            prompt_parts.append(f"""
                                تعليمات هامة:
1. الرسالة الرئيسية أدناه هي محور تركيزك الأساسي
2. استخدم السياق الإضافي فقط لتعزيز فهمك
3. لا تدع السياق الإضافي يشتتك عن المهمة الأساسية
4. أعطِ الأولوية دائمًا لمتطلبات الرسالة الرئيسية
================================================================================
🔴 الرسالة الرئيسية (المهمة الأساسية) 🔴
--------------------------------------------------
{self.focus_message}\n
""")
        
        # Add each block's content
        for block in self.blocks:
            content = self.load_block(block['category'], block['name'])
            
            # Replace parameters in the content
            if block['name'] in self.parameters:
                for param_name, param_value in self.parameters[block['name']].items():
                    resolved_value = self._resolve_parameter_value(param_value)
                    content = content.replace(f"[{param_name}]", resolved_value)
            
            prompt_parts.append(content)
        prompt_parts.append(f"""
                ================================================================================
            تذكير: ارجع إلى الرسالة الرئيسية أعلاه وتأكد من أن ردك يتناول هذه المتطلبات بشكل أساسي.
            =============================================================================================
            """)
        # Join all parts with double newlines
        return "\n\n".join(prompt_parts)

    def get_available_blocks(self) -> Dict[str, List[str]]:
        """Get all available blocks organized by category"""
        blocks = {}
        
        # Get all directories in the data folder
        for item in os.listdir(self.data_dir):
            item_path = os.path.join(self.data_dir, item)
            if os.path.isdir(item_path):
                # Get all markdown files in this directory
                md_files = [f for f in os.listdir(item_path) if f.endswith('.md')]
                if md_files:
                    blocks[item] = md_files
                    
        return blocks

# Example usage
if __name__ == "__main__":
    builder = PromptBuilder()
    
    # Add some blocks
    builder.add_block("engineer", "الحبوب/حبة مهندس النماذج اللغوية.md")
    
    # Set parameters
    builder.add_parameter("engineer", "model_name", "GPT-4")
    builder.add_parameter("engineer", "task", "تحليل النصوص")
    
    # Set focus message
    builder.focus_message = "تحليل نص طويل عن الذكاء الاصطناعي"
    
    # Build the prompt
    final_prompt = builder.build()
    print(final_prompt)