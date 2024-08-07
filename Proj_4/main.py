import tkinter as tk
from tkinter import messagebox, font
from tkinter import simpledialog
from tkinter import ttk
from sympy import symbols, Eq, solve, Rational, lcm

def parse_formula(formula):
    from collections import defaultdict
    import re
    
    element_pattern = re.compile(r'([A-Z][a-z]*)(\d*)')
    counts = defaultdict(int)
    
    for elem, count in element_pattern.findall(formula):
        counts[elem] += int(count) if count else 1
    
    return counts

def balance_equation():
    input_eq = entry.get().strip()
    try:
        if '=' not in input_eq:
            raise ValueError("The equation must contain an '=' sign.")
        
        reactants, products = input_eq.split('=')
        reactants = reactants.strip().split('+')
        products = products.strip().split('+')
        
        # Define symbols for coefficients
        num_reactants = len(reactants)
        num_products = len(products)
        coeffs = symbols(' '.join([f'a{i}' for i in range(num_reactants + num_products)]))
        
        # Build equations based on element counts
        equations = []
        elements = set()
        reactant_counts = [parse_formula(r.strip()) for r in reactants]
        product_counts = [parse_formula(p.strip()) for p in products]
        
        for counts in reactant_counts + product_counts:
            elements.update(counts.keys())
        
        for element in elements:
            lhs = sum(reactant_counts[i].get(element, 0) * coeffs[i] for i in range(num_reactants))
            rhs = sum(product_counts[i].get(element, 0) * coeffs[num_reactants + i] for i in range(num_products))
            equations.append(Eq(lhs, rhs))
        
        # Add normalization constraint (sum of coefficients should be non-zero)
        equations.append(Eq(sum(coeffs), 1))
        
        # Solve equations
        solutions = solve(equations, coeffs)
        
        if not solutions:
            raise ValueError("No solution found.")
        
        # Extract coefficients and find the least common multiple of denominators
        coeff_values = [solutions.get(coeff, 0) for coeff in coeffs]
        denominators = [coeff.as_numer_denom()[1] for coeff in coeff_values if coeff != 0]
        if denominators:
            factor = lcm(denominators)
            coeff_values = [factor * coeff for coeff in coeff_values]
        
        # Format the balanced equation
        balanced_eq = ' + '.join([f"{int(coeff_values[i])} {reactants[i].strip()}" for i in range(num_reactants) if coeff_values[i] > 0]) + " = " + \
                      ' + '.join([f"{int(coeff_values[num_reactants + i])} {products[i].strip()}" for i in range(num_products) if coeff_values[num_reactants + i] > 0])
        result_text.config(text=balanced_eq)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to balance equation: {e}")

def change_font_type():
    global selected_font,font_combobox

    # Create a new top-level window for font selection
    font_window = tk.Toplevel(root)
    font_window.title("Select Font Type")
    
    # Create a label and combobox for font selection
    label = tk.Label(font_window, text="Select Font Type:")
    label.pack(pady=10)

    font_combobox = ttk.Combobox(font_window, values=list(font.families()))
    font_combobox.set(selected_font)
    font_combobox.pack(pady=10)
    
    def on_select():
        global selected_font
        font_choice = font_combobox.get()
        if font_choice:
            selected_font = font_choice
            update_font()
        font_window.destroy()
    
    # Create a button to confirm selection
    ok_button = tk.Button(font_window, text="OK", command=on_select)
    ok_button.pack(pady=10)

def set_font_type(event):
    global selected_font
    selected_font = font_combobox.get()
    update_font()


def change_font_size():
    global font_size
    try:
        size_choice = int(simpledialog.askstring("Font Size", "Enter font size (e.g., 12, 14):", initialvalue=str(font_size)))
        if size_choice > 0:
            font_size = size_choice
            update_font()
    except ValueError:
        pass

def update_font():
    custom_font = font.Font(family=selected_font, size=font_size)
    entry.config(font=custom_font)
    balance_button.config(font=custom_font)
    result_label.config(font=custom_font)
    result_text.config(font=custom_font)

# Initialize default settings
selected_font = "Arial"
font_size = 12

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Chemical Equation Balancer")

# Create Menu
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

# Font Type Menu Item
settings_menu.add_command(label="Change Font Type", command=change_font_type)

# Font Size Menu Item
settings_menu.add_command(label="Change Font Size", command=change_font_size)

tk.Label(root, text="Enter Chemical Equation (e.g., H2 + O2 = H2O):").pack(pady=10)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

balance_button = tk.Button(root, text="Balance Equation", command=balance_equation)
balance_button.pack(pady=10)

result_label = tk.Label(root, text="Balanced Equation:")
result_label.pack(pady=5)

result_text = tk.Label(root, text="")
result_text.pack(pady=5)

update_font()

root.mainloop()
