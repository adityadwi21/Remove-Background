import tkinter as tk
from tkinter import filedialog, Label, Button, Listbox, Scrollbar, messagebox
from tkinter.ttk import Progressbar, Frame
from PIL import Image, ImageTk, UnidentifiedImageError
from rembg import remove
import os
import concurrent.futures
import threading
import logging
import subprocess
import platform

# Konfigurasi logging
logging.basicConfig(filename='process_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Konstanta ukuran file maksimum (10 MB)
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Buat folder 'assets' jika belum ada
assets_folder = 'assets'
os.makedirs(assets_folder, exist_ok=True)

class BackgroundRemovalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Removal App")
        self.root.geometry("800x600")

        self.setup_ui()

    def setup_ui(self):
        # Frame untuk tombol upload, view folder, dan progress bar
        control_frame = Frame(self.root)
        control_frame.pack(fill=tk.X, pady=10)

        self.upload_button = Button(control_frame, text="Upload Images", command=self.upload_images)
        self.upload_button.pack(pady=5)

        self.view_folder_button = Button(control_frame, text="View Result Folder", command=self.view_result_folder)
        self.view_folder_button.pack(pady=5)

        self.progress = Progressbar(control_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Frame untuk hasil gambar
        self.result_frame = Frame(self.root)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_label = Label(self.result_frame, text="")
        self.result_label.pack(pady=10)

        self.image_label = Label(self.result_frame)
        self.image_label.pack(pady=10)

        # Frame untuk daftar gambar
        self.listbox_frame = Frame(self.root)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.image_listbox = Listbox(self.listbox_frame, selectmode=tk.SINGLE)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(self.listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.image_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.image_listbox.yview)

        self.image_listbox.bind('<<ListboxSelect>>', self.display_result_from_list)

    def upload_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.tiff *.bmp *.gif")])
        if file_paths:
            valid_paths = [path for path in file_paths if self.is_valid_file_size(path)]
            if not valid_paths:
                messagebox.showerror("Error", "All selected files are too large to process.")
                return

            self.prepare_for_processing()
            threading.Thread(target=self.process_images, args=(valid_paths,), daemon=True).start()

    def is_valid_file_size(self, file_path):
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE_BYTES:
                logging.warning(f"File {file_path} is too large ({file_size} bytes). Max size is {MAX_FILE_SIZE_BYTES} bytes.")
                messagebox.showwarning("File Too Large", f"{os.path.basename(file_path)} exceeds the maximum file size of {MAX_FILE_SIZE_MB} MB.")
                return False
            return True
        except Exception as e:
            logging.error(f"Error checking file size for {file_path}: {e}")
            self.show_error_popup(f"Error checking file size for {file_path}: {e}")
            return False

    def prepare_for_processing(self):
        self.progress['value'] = 0
        self.result_label.config(text="")
        self.image_label.config(image='')

    def process_images(self, input_image_paths):
        total_files = len(input_image_paths)
        self.update_progress(0, total_files)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.remove_background, path): path for path in input_image_paths}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error processing image: {e}")
                    self.show_error_popup(f"Error processing image: {e}")

                self.update_progress(i + 1, total_files)

        self.result_label.config(text=f"Processed {total_files} images successfully!")
        logging.info(f"Processed {total_files} images successfully.")
        self.update_image_list()

    def remove_background(self, input_image_path):
        try:
            logging.info(f"Processing image {input_image_path}.")
            with open(input_image_path, 'rb') as inp_file:
                input_image = inp_file.read()

            output_image = remove(input_image)
            output_image_path = self.get_output_image_path(input_image_path)
            with open(output_image_path, 'wb') as out_file:
                out_file.write(output_image)

            logging.info(f"Saved image to {output_image_path}.")

        except (IOError, UnidentifiedImageError) as e:
            logging.error(f"Error processing image {input_image_path}: {e}")
            self.show_error_popup(f"Error processing image {input_image_path}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            self.show_error_popup(f"An unexpected error occurred: {e}")

    def get_output_image_path(self, input_image_path):
        file_name = os.path.basename(input_image_path)
        name, _ = os.path.splitext(file_name)
        return os.path.join(assets_folder, f"{name}_rembg.png")

    def update_progress(self, current, total):
        self.progress['value'] = (current / total) * 100
        self.root.update_idletasks()

    def display_result_from_list(self, event):
        selected_index = self.image_listbox.curselection()
        if selected_index:
            file_name = self.image_listbox.get(selected_index[0])
            output_image_path = os.path.join(assets_folder, file_name)
            self.display_result(output_image_path)

    def display_result(self, output_image_path):
        try:
            image = Image.open(output_image_path)
            image = image.resize((250, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.photo = photo
        except (UnidentifiedImageError, IOError) as e:
            logging.error(f"Error displaying image: {e}")
            self.show_error_popup(f"Error displaying image: {e}")

    def update_image_list(self):
        self.image_listbox.delete(0, tk.END)
        try:
            for file_name in os.listdir(assets_folder):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    self.image_listbox.insert(tk.END, file_name)
        except Exception as e:
            logging.error(f"Error updating image list: {e}")
            self.show_error_popup(f"Error updating image list: {e}")

    def show_error_popup(self, message):
        messagebox.showerror("Error", message)

    def view_result_folder(self):
        try:
            folder_path = os.path.abspath(assets_folder)
            if platform.system() == 'Windows':
                os.startfile(folder_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', folder_path])
            elif platform.system() == 'Linux':
                subprocess.run(['xdg-open', folder_path])
            else:
                raise OSError("Unsupported operating system")
        except Exception as e:
            logging.error(f"Error opening result folder: {e}")
            self.show_error_popup(f"Error opening result folder: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemovalApp(root)
    root.mainloop()
