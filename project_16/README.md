# Modern Recipe Manager

A clean, modern Python GUI application for managing your favorite recipes, built with Tkinter.

## Features

- **Three-column layout** for easy navigation and organization
- **Category Management**: Add, edit, and delete recipe categories
- **Recipe Management**: Add, edit, and delete recipes with detailed descriptions
- **Modern UI**: Clean design with a pleasant color scheme
- **Automatic saving**: All changes are saved to a local JSON file

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)
- Pillow (PIL Fork)
- ttkthemes (for modern UI appearance)

## Installation

1. Clone or download this repository
2. Install required packages:

```
pip install -r requirements.txt
```

## Usage

Run the application:

```
python main.py
```

### Working with Categories

1. **Add a Category**: Click the "Add Category" button and enter a name
2. **Edit a Category**: Select a category and click "Edit"
3. **Delete a Category**: Select a category and click "Delete"

### Working with Recipes

1. **Select a Category**: Click on a category in the first column
2. **Add a Recipe**: Click "Add Recipe" button, enter a name and description
3. **Edit a Recipe**: Select a recipe and click "Edit" 
4. **Delete a Recipe**: Select a recipe and click "Delete"
5. **View Recipe Details**: Click on a recipe card to view its details in the third column

## Data Storage

All your recipes are stored in a `recipes.json` file in the same directory as the application. 