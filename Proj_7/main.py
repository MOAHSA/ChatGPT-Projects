import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename,askdirectory
from image import IMAGE ,ImageTk
class CutFramesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Frames Cutter")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        self.BACKGROUND_COLOR = "#16423C"
        self.root.config(bg=self.BACKGROUND_COLOR)
        self.filters = {}
        self.image = None
        self.create_widgets()
        self.selected_items = None
    def create_widgets(self):
        # Canvas for file operations
        self.files_canvas = tk.Canvas(self.root, width=200, height=640, background='#6a9c89', borderwidth=0, highlightthickness=0)
        self.files_canvas.place(x=42, y=115)

        self.open_image_button = tk.Button(self.files_canvas, text="Open Image", font=('Arial', 15), bg='#6a9c89', activebackground='#6a9c89', activeforeground='white', borderwidth=0, highlightthickness=0, fg='white', command=self.open_image)
        self.open_image_button.place(x=20, y=20, width=160, height=60)
        self.save_frames_button = tk.Button(self.files_canvas, text="Save Frames", font=('Arial', 15), bg='#6a9c89', activebackground='#6a9c89', activeforeground='white', borderwidth=0, highlightthickness=0, fg='white', command=self.save_frames)
        self.save_frames_button.place(x=20, y=100, width=160, height=60)

        #creat_frames_widgets
        self.create_frames_widgets()

        # Canvas for advanced options
        self.advanced_canvas = tk.Canvas(self.root, width=200, height=640, background='#6a9c89', borderwidth=0, highlightthickness=0)
        self.advanced_canvas.place(x=748, y=115)

        self.advanced_title = tk.Label(self.advanced_canvas, text="Advanced Options", font=('Arial', 15), bg='#6a9c89', fg='white')
        self.advanced_title.place(x=20, y=20)

        # Filter settings on advanced_canvas
        self.create_filter_widgets()

        # Canvas for preview
        self.preview_canvas = tk.Canvas(self.root, width=220, height=220, background='#c4dad2', borderwidth=0, highlightthickness=0)
        self.preview_canvas.place(x=385, y=23)
        self.preview_canvas.bind("<Button-1>", lambda mouse : self.on_preview_canvas_click(mouse))
        self.sleected_items = None
        # Treeview for frames
        columns = ['Name', 'Size']
        self.frames_tree = ttk.Treeview(self.root, columns=columns)
        self.frames_tree.heading('#0', text="Frames")
        self.frames_tree.heading('Name', text="Name")
        self.frames_tree.heading('Size', text="Size")
        self.frames_tree.column("#0", width=50, stretch=tk.NO)
        self.frames_tree.column("Name", width=250 ,stretch=tk.NO)
        self.frames_tree.column("Size", width=170, stretch=tk.NO)
        self.frames_tree.place(x=260, y=260, width=470, height=440)
        self.frames_tree.bind('<<TreeviewSelect>>', self.on_selection_change)


        # Vertical scrollbar
        self.scroll = tk.Scrollbar(self.root, orient="vertical", command=self.frames_tree.yview)
        self.scroll.place(x=710, y=260, height=440)
        self.frames_tree.configure(yscrollcommand=self.scroll.set)

        # Frame it button
        self.frame_it_button = tk.Button(self.root, text="Frame it", font=('Arial', 15), background='#6a9c89', activebackground='#6a9c89', activeforeground='white', borderwidth=0, highlightthickness=0, fg='white', command=self.frame_it)
        self.frame_it_button.place(x=425, y=720, width=150, height=50)
        self.apply_filters()

    def on_preview_canvas_click(self,mouse):
        #open imshow 
        if self.selected_items:
            self.image.frames[int(self.selected_items[0])-1].show()

    def on_selection_change(self, event):
        self.selected_items = self.frames_tree.selection()
        self.preview_canvas.delete("all")
        if self.selected_items:
            self.preview_frame(self.image.frames[int(self.selected_items[0])-1])
    def create_frames_widgets(self):
        #slice methode > Either "by_size" or "by_grid" combobox
        
        self.create_label(self.files_canvas, "Slice Method:", 0, 250)
        self.slice_method_value = tk.StringVar(value="by_size")
        self.slice_method_combobox = ttk.Combobox(self.files_canvas, textvariable=self.slice_method_value, values=["by_size", "by_grid"])
        self.slice_method_combobox.place(x=100, y=250, width=100, height=20)
        
        self.create_label(self.files_canvas,"rows/width", 0, 280)
        self.row_width_value = tk.IntVar(value=10)
        self.row_width_entry = tk.Entry(self.files_canvas, textvariable=self.row_width_value)
        self.row_width_entry.place(x=120, y=280, width=50, height=20)
        
        self.create_label(self.files_canvas,"columns/height", 0, 310)
        self.column_height_value = tk.IntVar(value=10)
        self.column_height_entry = tk.Entry(self.files_canvas, textvariable=self.column_height_value)
        self.column_height_entry.place(x=120, y=310, width=50, height=20)

        self.create_label(self.files_canvas,"x_padding", 0, 340)
        self.x_padding_value = tk.IntVar(value=0)
        self.x_padding_entry = tk.Entry(self.files_canvas, textvariable=self.x_padding_value)
        self.x_padding_entry.place(x=120, y=340, width=50, height=20)

        self.create_label(self.files_canvas,"y_padding", 0, 370)
        self.y_padding_value = tk.IntVar(value=0)
        self.y_padding_entry = tk.Entry(self.files_canvas, textvariable=self.y_padding_value)
        self.y_padding_entry.place(x=120, y=370, width=50, height=20)

    def create_filter_widgets(self):
        # Filter settings
        self.create_label(self.advanced_canvas, "Rotate (degrees):", 0, 90)
        self.rotate_value = tk.IntVar(value=0)
        self.rotate_entry = tk.Entry(self.advanced_canvas, textvariable=self.rotate_value)
        self.rotate_entry.place(x=120, y=90,width=60, height=20)

        self.create_label(self.advanced_canvas, "Flip X:", 1, 120)
        self.flip_x_value = tk.BooleanVar(value=False)
        self.flip_x_checkbox = tk.Checkbutton(self.advanced_canvas, variable=self.flip_x_value,bd=0,bg='#6a9c89')
        self.flip_x_checkbox.place(x=60, y=120)

        self.create_label(self.advanced_canvas, "Flip Y:", 2, 120,x_pos=100)
        self.flip_y_value = tk.BooleanVar(value=False)
        self.flip_y_checkbox = tk.Checkbutton(self.advanced_canvas, variable=self.flip_y_value,bd=0,bg='#6a9c89')
        self.flip_y_checkbox.place(x=140, y=120)

        self.create_label(self.advanced_canvas, "Gray Scale:", 3, 150)
        self.gray_value = tk.BooleanVar(value=False)
        self.gray_checkbox = tk.Checkbutton(self.advanced_canvas, variable=self.gray_value,bd=0,bg='#6a9c89')
        self.gray_checkbox.place(x=100, y=150)

        self.create_label(self.advanced_canvas, "Pixel Enhancer:", 4, 180)
        self.pixel_enhancer_value = tk.BooleanVar(value=False)
        self.pixel_enhancer_checkbox = tk.Checkbutton(self.advanced_canvas, variable=self.pixel_enhancer_value,bd=0,bg='#6a9c89')
        self.pixel_enhancer_checkbox.place(x=100, y=180)

        self.create_label(self.advanced_canvas, "Scale X (pixels):", 5, 210)
        self.scale_x_value = tk.IntVar(value=0)
        self.scale_x_entry = tk.Entry(self.advanced_canvas, textvariable=self.scale_x_value, width=10)
        self.scale_x_entry.place(x=110, y=210)

        self.create_label(self.advanced_canvas, "Scale Y (pixels):", 6, 240)
        self.scale_y_value = tk.IntVar(value=0)
        self.scale_y_entry = tk.Entry(self.advanced_canvas, textvariable=self.scale_y_value, width=10)
        self.scale_y_entry.place(x=110, y=240)

        self.create_label(self.advanced_canvas, "Transparent Pixel Color (R,G,B,A):", 7, 270)
        self.trans_color_r = tk.IntVar(value=0)
        self.trans_color_g = tk.IntVar(value=0)
        self.trans_color_b = tk.IntVar(value=0)
        self.trans_color_a = tk.IntVar(value=0)

        self.create_color_entry(self.advanced_canvas, "R", self.trans_color_r, 8, 300,x_pos=10)
        self.create_color_entry(self.advanced_canvas, "G", self.trans_color_g, 9, 300,x_pos=50)
        self.create_color_entry(self.advanced_canvas, "B", self.trans_color_b, 10, 300,x_pos=90)
        self.create_color_entry(self.advanced_canvas, "A", self.trans_color_a, 11, 300,x_pos=130)


    def create_label(self, canvas, text, row, y_pos,x_pos=20):
        label = tk.Label(canvas, text=text, bg='#6a9c89', fg='white')
        label.place(x=x_pos, y=y_pos)

    def create_color_entry(self, canvas, color, var, row, y_pos,x_pos):
        frame = tk.Frame(canvas, bg='#6a9c89')
        frame.place(x=x_pos, y=y_pos)
        tk.Label(frame, text=f"{color}:", bg='#6a9c89', fg='white').pack(side=tk.LEFT)
        entry = tk.Entry(frame, textvariable=var, width=5)
        entry.pack(side=tk.LEFT)

    def open_image(self):
        self.image_path = askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        # Here you would typically add code to handle the image file.
        

    def save_frames(self):
        # Implement the functionality for the "Save Frames" button here.
        path = askdirectory()
        self.image.save_frames(path)
    
    def frame_it(self):
        self.apply_filters()
        # Implement the functionality for the "Frame it" button here.
        if self.slice_method_value.get() == "by_grid"  :
            self.image = IMAGE(self.image_path,self.slice_method_value.get(),rows=self.row_width_value.get(),columns=self.column_height_value.get(),filters_transfer=self.filters,x_padding=self.x_padding_value.get(),y_padding=self.y_padding_value.get())
        elif self.slice_method_value.get() == "by_size":
            self.image = IMAGE(self.image_path,self.slice_method_value.get(),frame_width=self.row_width_value.get(),frame_height=self.column_height_value.get(),filters_transfer=self.filters,x_padding=self.x_padding_value.get(),y_padding=self.y_padding_value.get())
        self.load_to_frames_tree(self.image.frames)
        self.preview_frame(self.image.frames[0])
    def load_to_frames_tree(self,frames):
        #clear the tree
        self.frames_tree.delete(*self.frames_tree.get_children())
        # Load the frames into the Treeview
        for index, frame in enumerate(frames, start=1):
                    # Use index as the ID and insert into Treeview
                    self.frames_tree.insert("", "end", iid=index, text=index, values=(frame.name, f"{frame.width}x{frame.height}"))

    def preview_frame(self,frame):
        #drw frame in preview canvas
        image = ImageTk.PhotoImage(frame.im)
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.preview_canvas.image = image
    def apply_filters(self):

        self.filters = {
            'rotate': self.rotate_value.get(),
            'flip': {'x': self.flip_x_value.get(), 'y': self.flip_y_value.get()},
            'gray': self.gray_value.get(),
            'pixel_enhancer': self.pixel_enhancer_value.get(),
            'scale': {'x': self.scale_x_value.get(), 'y': self.scale_y_value.get()},
            'transparent_pixel_filter': (
                self.trans_color_r.get(),
                self.trans_color_g.get(),
                self.trans_color_b.get(),
                self.trans_color_a.get()
            )
        }


# Create the main window
root = tk.Tk()
app = CutFramesApp(root)
root.mainloop()
try:
    app.image.close()
except:
    pass