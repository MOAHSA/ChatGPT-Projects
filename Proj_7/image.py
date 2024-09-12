import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageOps,ImageTk
import os

class IMAGE:
    def __init__(self, image_path, slice_method, frame_width=None, frame_height=None, rows=None, columns=None, filters_transfer=None,x_padding =0,y_padding=0):
        self.image_path = image_path
        self.slice_method = slice_method  # Either "by_size" or "by_grid"
        self.image = Image.open(self.image_path)
        self.width, self.height = self.image.size
        self.extension = self.image_path.split('.')[-1]
        self.frames = []

        # Process based on slicing method
        if self.slice_method == "by_size" and frame_width and frame_height:
            self.make_frames_by_size(self.image, self.width, self.height, frame_width, frame_height,x_padding,y_padding, filters_transfer)
        elif self.slice_method == "by_grid" and rows and columns:
            self.make_frames_by_grid(self.image, self.width, self.height, rows, columns,x_padding,y_padding, filters_transfer)
        else:
            raise ValueError("Invalid parameters for slicing. Ensure correct slice method and parameters are provided.")
        
        

    def make_frames_by_size(self, image, width, height, frame_width, frame_height, x_padding, y_padding, filters_transfer):
        """Slices image into frames based on frame width and height with padding."""
        index = 0
        self.frames = []
        
        # Adjust frame dimensions to include padding
        frame_width += x_padding
        frame_height += y_padding

        # Calculate number of frames based on padded dimensions
        columns, rows = (width + x_padding) // frame_width, (height + y_padding) // frame_height

        for r in range(rows):
            for c in range(columns):
                # Calculate the box with padding
                left = c * frame_width
                top = r * frame_height
                right = left + frame_width
                bottom = top + frame_height
                
                # Ensure the box is within image bounds
                right = min(right, width)
                bottom = min(bottom, height)

                box = (left, top, right, bottom)
                frame_image = image.crop(box)
                frame = Frame(frame_image, filters_transfer, f"{index}.{self.extension}")
                self.frames.append(frame)
                index += 1
    def make_frames_by_grid(self, image, width, height, rows, columns, x_padding, y_padding, filters_transfer):
        """Slices image into frames based on the number of rows and columns with padding."""
        index = 0
        self.frames = []
        
        # Calculate frame dimensions with padding
        frame_width, frame_height = (width + x_padding) // columns, (height + y_padding) // rows

        for r in range(rows):
            for c in range(columns):
                # Calculate the box with padding
                left = c * frame_width
                top = r * frame_height
                right = left + frame_width
                bottom = top + frame_height

                # Ensure the box is within image bounds
                right = min(right, width)
                bottom = min(bottom, height)

                box = (left, top, right, bottom)
                frame_image = image.crop(box)
                frame = Frame(frame_image, filters_transfer, f"{index}.{self.extension}")
                self.frames.append(frame)
                index += 1


    def save_frames(self,path):
        # Create new output path if it doesn't exist

        for frame in range(len(self.frames)):
            
            self.frames[frame].save(f"{path}/{frame}.{self.extension}")

class Frame:
    def __init__(self, image, filters_transfer,name):
        self.name = name 
        self.im = image
        self.width, self.height = self.im.size
        self.editit(filters_transfer)


    def editit(self, filters_transfer):
        if filters_transfer is None:
            return
        if filters_transfer.get('rotate'):
            self.rotate(filters_transfer['rotate'])
        if filters_transfer.get('flip'):
            self.flip(filters_transfer['flip']['x'], filters_transfer['flip']['y'])
        if filters_transfer.get('gray'):
            self.gray()
        if filters_transfer.get('pixel_enhancer'):
            self.pixel_enhancer()
        if filters_transfer.get('scale') and filters_transfer['scale']['x'] > 0 :
            self.scalex(filters_transfer['scale']['x'])
        if filters_transfer.get('scale') and filters_transfer['scale']['y'] > 0 :
            self.scaley(filters_transfer['scale']['y'])
        if filters_transfer.get('transparent_pixel_filter'):
            self.transparent_pixel_filter(filters_transfer['transparent_pixel_filter'])

    def rotate(self, angle):
        self.im = self.im.rotate(angle)

    def flip(self, x, y):
        if x:
            self.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        if y:
            self.im = self.im.transpose(Image.FLIP_TOP_BOTTOM)

    def gray(self):
        self.im = ImageOps.grayscale(self.im)

    def pixel_enhancer(self):
        # Ensure the image is in RGB mode for autocontrast to work
        if self.im.mode == 'RGBA':
            self.im = self.im.convert('RGB')
        self.im = ImageOps.autocontrast(self.im)

    def transparent_pixel_filter(self, color=(255, 255, 255, 0)):
        """
        Modify transparent pixels (alpha = 0) by setting them to a specified color.
        Default color is white with zero opacity.
        """
        if self.im.mode == 'RGBA':
            data = np.array(self.im)
            # Extract the alpha channel
            r, g, b, a = data.T
            # Replace transparent pixels with the specified color
            transparent_areas = (a == 0)
            data[..., :-1][transparent_areas.T] = color[:3]  # Apply color (R, G, B)
            self.im = Image.fromarray(data, mode='RGBA')

    def scalex(self, x):
        self.im = self.im.resize((x, self.height))
        self.width = x
    def scaley(self,y):
        self.im = self.im.resize((self.width, y))
        self.height = y
    def show(self):
        self.im.show()

    def save(self, path):
        self.im.save(path)
