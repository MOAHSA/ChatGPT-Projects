import pygame
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog

class PygameApp:
    def __init__(self, width=800, height=600, title="Web Scraping Application"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font_name = 'Arial'
        self.font_size = 16  # Set the default font size to 16
        self.update_font()
        self.urls = []
        self.element_map = {}
        self.running = True

        # Create UI elements
        self.setup_ui()

    def update_font(self):
        """ Update the fonts based on the current font name and size """
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.small_font = pygame.font.SysFont(self.font_name, self.font_size - 6)

    def setup_ui(self):
        self.buttons = {
            "load_urls": pygame.Rect(50, 50, 200, 50),
            "enter_url": pygame.Rect(50, 120, 200, 50),
            "scrape_data": pygame.Rect(50, 190, 200, 50),
            "save_to_excel": pygame.Rect(50, 260, 200, 50),
            "clear_scrap": pygame.Rect(50, 330, 200, 50)
        }
        self.input_boxes = {
            "font_name": pygame.Rect(300, 50, 150, 30),
            "font_size": pygame.Rect(300, 100, 50, 30)
        }
        self.text_inputs = {
            "font_name": self.font_name,
            "font_size": str(self.font_size)
        }
        self.scroll_offset = 0
        self.scroll_speed = 5
        self.elements = []
        self.create_scrollable_area()

    def create_scrollable_area(self):
        self.scrollable_area = pygame.Rect(300, 150, 450, 400)
        self.scrollable_content = []

    def draw_ui(self):
        self.screen.fill((30, 30, 30))

        # Draw buttons
        for text, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (0, 128, 255), rect)
            text_surf = self.font.render(text.replace('_', ' ').title(), True, (255, 255, 255))
            self.screen.blit(text_surf, rect.topleft)

        # Draw input boxes
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_boxes["font_name"], 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_boxes["font_size"], 2)
        font_name_surf = self.small_font.render(f"Font: {self.text_inputs['font_name']}", True, (255, 255, 255))
        font_size_surf = self.small_font.render(f"Size: {self.text_inputs['font_size']}", True, (255, 255, 255))
        self.screen.blit(font_name_surf, (self.input_boxes["font_name"].x + 5, self.input_boxes["font_name"].y + 5))
        self.screen.blit(font_size_surf, (self.input_boxes["font_size"].x + 5, self.input_boxes["font_size"].y + 5))

        # Draw scrollable area content
        pygame.draw.rect(self.screen, (200, 200, 200), self.scrollable_area)
        for i, text in enumerate(self.scrollable_content):
            text_surf = self.small_font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surf, (self.scrollable_area.x + 5, self.scrollable_area.y + 5 + i * 30 - self.scroll_offset))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.buttons["load_urls"].collidepoint(pos):
                self.load_urls_from_file()
            elif self.buttons["enter_url"].collidepoint(pos):
                self.enter_url_manually()
            elif self.buttons["scrape_data"].collidepoint(pos):
                self.scrape_data()
            elif self.buttons["save_to_excel"].collidepoint(pos):
                self.save_to_excel()
            elif self.buttons["clear_scrap"].collidepoint(pos):
                self.clear_scrap()
            elif self.input_boxes["font_name"].collidepoint(pos):
                self.text_inputs["font_name"] = simpledialog.askstring("Input", "Enter font name:", initialvalue=self.text_inputs["font_name"])
                self.update_font()
            elif self.input_boxes["font_size"].collidepoint(pos):
                size_str = simpledialog.askstring("Input", "Enter font size:", initialvalue=self.text_inputs["font_size"])
                if size_str and size_str.isdigit():
                    self.text_inputs["font_size"] = size_str
                    self.font_size = int(size_str)
                    self.update_font()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.scroll_offset + self.scroll_speed, len(self.scrollable_content) * 30 - self.scrollable_area.height)
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)

    def load_urls_from_file(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select URL File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.urls = [line.strip() for line in file.readlines() if line.strip()]
            self.display_message(f"Loaded {len(self.urls)} URLs.")

    def enter_url_manually(self):
        root = tk.Tk()
        root.withdraw()
        url = simpledialog.askstring("Input", "Please enter the URL:")
        if url:
            self.urls.append(url)
            self.display_message("URL added successfully.")

    def scrape_data(self):
        self.element_map.clear()
        self.scrollable_content.clear()
        for url in self.urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                self._extract_classes_and_ids(soup)
            except requests.RequestException as e:
                self.display_message(f"Failed to fetch data from {url}: {e}")
        if not self.element_map:
            self.display_message("No classes or IDs were found.")
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
        self.scrollable_content.clear()
        for element_type, elements in self.element_map.items():
            self.scrollable_content.append(f"{element_type}:")
            for element_name, value in sorted(set(elements)):
                self.scrollable_content.append(f"  {element_name}: {value}")

    def save_to_excel(self):
        data = [(element_type, element_name, value) for element_type, elements in self.element_map.items() for element_name, value in elements]
        if data:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                self._create_excel_file(file_path, data)
                self.display_message(f"Data saved to {file_path}.")
        else:
            self.display_message("No data selected to save.")

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

    def clear_scrap(self):
        self.element_map.clear()
        self.scrollable_content.clear()

    def display_message(self, message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showinfo("Info", message)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PygameApp()
    app.run()
