import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import pytesseract
import re
import csv
from PIL import Image, ImageTk
import os

class BillGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bill Analyzer")
        self.root.geometry("400x600")

        self.upload_frame = tk.Frame(self.root)
        self.upload_frame.pack(fill="x")

        self.camera_frame = tk.Frame(self.root)
        self.camera_frame.pack(fill="x")

        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(fill="both", expand=True)

        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill="both", expand=True)

        self.upload_button = tk.Button(self.upload_frame, text="Upload Bill Image", command=self.upload_bill)
        self.upload_button.pack(side="left", padx=10, pady=10)

        self.camera_button = tk.Button(self.camera_frame, text="Take Bill Photo", command=self.take_photo)
        self.camera_button.pack(side="left", padx=10, pady=10)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(fill="both", expand=True)

        self.output_label = tk.Label(self.output_frame, text="", wraplength=400)
        self.output_label.pack(fill="both", expand=True)

        # CSV file initialization
        self.csv_file = "bill_analysis.csv"
        self.initialize_csv()

    def initialize_csv(self):
        # Check if the CSV file exists, if not create it and add headers
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Category", "Total Amount"])

    def upload_bill(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.display_image(file_path)
            self.analyze_bill(file_path)

    def take_photo(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Unable to access the camera")
            return
        
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("bill_image.jpg", frame)
            cap.release()
            cv2.destroyAllWindows()
            self.display_image("bill_image.jpg")
            self.analyze_bill("bill_image.jpg")
        else:
            messagebox.showerror("Error", "Failed to capture the image")
            cap.release()

    def display_image(self, image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((300, 300))  # Adjust the size while maintaining the aspect ratio
            image_tk = ImageTk.PhotoImage(image)
            self.image_label.config(image=image_tk)
            self.image_label.image = image_tk
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display the image: {e}")

    def analyze_bill(self, path):
        try:
            text = extract_text(path)
            category = business_classifier(text)
            total_value = total(text)
            output = f"Category: {category}\nTotal: {total_value}"
            self.output_label.config(text=output)

            # Write the results to the CSV file
            self.write_to_csv(category, total_value)
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing the bill: {e}")

    def write_to_csv(self, category, total_value):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([category, total_value])


def extract_text(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(image_rgb)
    return text

def business_classifier(text):
    type_directory = {
        "Utility Bills": ["electricity", "water", "gas", "internet", "cable"],
        "Retail Receipts": ["sale", "gift", "shop", "receipt","mart"],
        "Medical Bills": ["hospital", "pharmacy"],
        "Dining and Hospitality Bills": ["restaurant", "hotel","barbecue","grill"],
        "Transportation and Travel Receipts": ["uber", "ola", "ride", "airline", "parking"]
    }
    for category, keywords in type_directory.items():
        if any(keyword in text.lower() for keyword in keywords):
            return category
    return "Unknown category"

def total(text):
    total_value = 0
    lines = text.split('\n')
    for i in lines:
        line = i.lower()
        if 'total' in line:
            pattern = r"[+-]? *(?:\$? *(?:\d{1,3}(?:,\d{3})*|\d*)(?:\.\d+)?|\b\d+(?:\.\d+)?\b)"
            numerical_values = re.findall(pattern, line)
            for val in numerical_values:
                try:
                    total_value += float(val.replace(',', '').replace('$', ''))
                except ValueError:
                    pass
    return '{:,.2f}'.format(total_value)

root = tk.Tk()
gui = BillGUI(root)
root.mainloop()
