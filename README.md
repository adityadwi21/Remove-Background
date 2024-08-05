# Background Removal App

![image](https://github.com/user-attachments/assets/e34583e9-7090-4253-8d24-40aa96afae5c)


## Overview

This Tkinter-based application provides a user-friendly interface for removing backgrounds from images using the `rembg` library. Users can upload images, view processed results, and manage the result folder from within the application.

## Features

- Upload multiple images for background removal.
- Progress bar to show the processing status.
- View results in a dedicated section.
- Manage and view processed images in a listbox.
- Access the result folder directly from the application.

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- `Pillow` library
- `rembg` library
- `tkinter` (usually comes pre-installed with Python)

You can install the necessary Python libraries using `pip`:

```bash
pip install pillow rembg
```

## Getting Started

Follow these steps to set up and run the Background Removal App on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/adityadwi21/Remove-Background.git
cd Remove-Background
```

### 2. Run the Application

Execute the `app.py` script to launch the application:

```bash
python app.py
```

### 3. Using the Application

- **Upload Images**: Click the "Upload Images" button to select and upload images. Only images under 10 MB will be processed.
- **View Result Folder**: Click the "View Result Folder" button to open the folder where processed images are saved.
- **Progress Bar**: Observe the progress of image processing through the progress bar.
- **Image Listbox**: Select an image from the listbox to display it in the results section.

### 4. Stopping the Application

To close the application, simply close the Tkinter window.

## Code Explanation

Here's a brief overview of the main components:

- **UI Setup**: Configures the main window, control buttons, progress bar, and result display.
- **Image Upload**: Handles image selection, size validation, and initiates background removal processing.
- **Background Removal**: Uses the `rembg` library to remove the background from images.
- **Progress Tracking**: Updates the progress bar and displays messages about the processing status.
- **Error Handling**: Logs errors and displays error messages through popups.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. Ensure that your changes adhere to the project's coding standards and include appropriate tests.
