import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font as tkFont
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

class WebScrapingApp(tk.Tk):
    def __init__(self, width=800, height=600, title="Web Scraping Application"):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.urls = []
        self.element_map = {}
        self.font_name = tkFont.Font(family="Arial").cget("family")
        self.font_size = 12
        self._setup_ui()

    def _setup_ui(self):
        # Title
        title_label = tk.Label(self, text="Web Scraping Application", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Button Frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        load_button = tk.Button(button_frame, text="Load URLs from File", command=self.load_urls_from_file, width=20)
        load_button.grid(row=0, column=0, padx=5, pady=5)

        enter_button = tk.Button(button_frame, text="Enter URL Manually", command=self.enter_url_manually, width=20)
        enter_button.grid(row=0, column=1, padx=5, pady=5)

        scrape_button = tk.Button(button_frame, text="Scrape Data", command=self.scrape_data, width=20)
        scrape_button.grid(row=1, column=0, padx=5, pady=5)

        save_button = tk.Button(button_frame, text="Save to Excel", command=self.save_to_excel, width=20)
        save_button.grid(row=1, column=1, padx=5, pady=5)

        # Font Settings
        font_frame = tk.Frame(self)
        font_frame.pack(pady=10)

        tk.Label(font_frame, text="Font Name:").grid(row=0, column=0, padx=5)
        self.font_entry = tk.Entry(font_frame)
        self.font_entry.grid(row=0, column=1, padx=5)
        self.font_entry.insert(0, self.font_name)

        tk.Label(font_frame, text="Font Size:").grid(row=0, column=2, padx=5)
        self.font_size_entry = tk.Entry(font_frame, width=5)
        self.font_size_entry.grid(row=0, column=3, padx=5)
        self.font_size_entry.insert(0, str(self.font_size))

        # Scrollable Frame for Elements
        self.elements_frame = tk.Frame(self)
        self.elements_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.canvas = tk.Canvas(self.elements_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.elements_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def load_urls_from_file(self):
        file_path = filedialog.askopenfilename(title="Select URL File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.urls = [line.strip() for line in file.readlines() if line.strip()]
            messagebox.showinfo("Success", f"Loaded {len(self.urls)} URLs.")

    def enter_url_manually(self):
        url = simpledialog.askstring("Input", "Please enter the URL:")
        if url:
            self.urls.append(url)
            messagebox.showinfo("Success", "URL added successfully.")

    def scrape_data(self):
        self.element_map.clear()
        self.clear_sublist()

        for url in self.urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Check for request errors
                soup = BeautifulSoup(response.content, 'html.parser')
                self._extract_classes_and_ids(soup)
            except requests.RequestException as e:
                messagebox.showerror("Error", f"Failed to fetch data from {url}: {e}")

        if not self.element_map:
            messagebox.showwarning("No Data", "No classes or IDs were found on the provided URLs.")
        else:
            self._display_elements()

    def _extract_classes_and_ids(self, soup):
        for element in soup.find_all(class_=True):
            class_names = element.get("class", [])
            for class_name in class_names:
                if class_name:
                    if class_name not in self.element_map:
                        self.element_map[class_name] = []
                    self.element_map[class_name].append((element.name, element.get_text(strip=True)))

        for element in soup.find_all(id=True):
            element_id = element.get("id")
            if element_id:
                if element_id not in self.element_map:
                    self.element_map[element_id] = []
                self.element_map[element_id].append((element.name, element.get_text(strip=True)))

    def _display_elements(self):
        for element_type, elements in self.element_map.items():
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(fill="x", padx=10, pady=5)

            tk.Label(frame, text=f"{element_type}:", font=("Arial", 14, "bold")).pack(anchor="w")

            

            
            

            self._create_checkbuttons(frame, elements, element_type)

    def _create_checkbuttons(self, frame, elements, element_type):
        for element_name, value in sorted(set(elements)):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(frame, text=f"{element_name}: {value}", variable=var)
            cb.pack(anchor="w", padx=20)
            self.element_map[element_type] = [(element_name, value, var)]

    def _search_items(self, search_text, frame, elements):
        filtered_elements = [(name, val) for name, val in elements if search_text.lower() in name.lower()]
        self.clear_sublist()
        self._create_checkbuttons(frame, filtered_elements, frame.cget("text"))

    def save_to_excel(self):
        try:
            self.font_name = self.font_entry.get()
            if not tkFont.Font(family=self.font_name).actual():
                self.font_name = "Arial"
            self.font_size = int(self.font_size_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid font size.")
            return

        data = []
        for element_type, elements in self.element_map.items():
            for item in elements:
                if isinstance(item, tuple) and len(item) == 3:
                    element_name, value, var = item
                    if var.get():
                        data.append((element_type, element_name, value))

        if data:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                self._create_excel_file(file_path, data)
                messagebox.showinfo("Success", f"Data saved to {file_path}.")
        else:
            messagebox.showwarning("No Data", "No data selected to save.")

    def _create_excel_file(self, file_path, data):
        wb = Workbook()
        ws = wb.active
        ws.title = "Scraped Data"

        ws.append(["Element Type", "Element Name", "Value"])

        for element_type, element_name, value in data:
            ws.append([element_type, element_name, value])

        self._format_excel_table(ws)
        wb.save(file_path)

    def _format_excel_table(self, ws):
        for row in ws.iter_rows():
            for cell in row:
                cell.font = Font(name=self.font_name, size=self.font_size)
                cell.alignment = Alignment(horizontal="center", vertical="center")

        for column in ws.columns:
            max_length = max(len(str(cell.value)) for cell in column)
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

    def clear_sublist(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = WebScrapingApp()
    app.mainloop()
