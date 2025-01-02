import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import rawpy
from PIL import Image
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_image(file_path, output_folder):
    """Process a single image and save it as JPEG."""
    try:
        # Open the RAW file with rawpy
        with rawpy.imread(file_path) as raw:
            # Process the RAW image
            rgb_array = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
            rgb_image = Image.fromarray(rgb_array)

            # Save to the output folder with high quality
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_folder, f"{base_name}.jpg")
            rgb_image.save(output_path, "JPEG", quality=95)  # High-quality setting
        return True, file_path
    except Exception as e:
        return False, (file_path, str(e))

def convert_images():
    # Get the selected files
    files = filedialog.askopenfilenames(title="Select RAW Image Files", 
                                        filetypes=[("RAW Files", "*.raw *.nef *.cr2 *.arw"), ("All Files", "*.*")])
    if not files:
        messagebox.showinfo("No Files Selected", "Please select at least one RAW image file.")
        return

    # Output folder selection
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        messagebox.showinfo("No Output Folder", "Please select an output folder.")
        return

    # Initialize the progress bar
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(files)

    # List to track failed files
    failed_files = []

    # Use ProcessPoolExecutor for multi-processing
    with ProcessPoolExecutor() as executor:
        # Submit tasks to the process pool
        futures = {executor.submit(process_image, file_path, output_folder): file_path for file_path in files}

        for future in as_completed(futures):
            # Update progress bar
            progress_bar["value"] += 1
            root.update_idletasks()

            # Process results
            result, info = future.result()
            if not result:
                failed_files.append(info)

    # Show completion message
    if failed_files:
        error_msg = "\n".join([f"{file}: {error}" for file, error in failed_files])
        messagebox.showerror("Conversion Errors", f"Some files failed to convert:\n{error_msg}")
    else:
        messagebox.showinfo("Conversion Complete", "All selected images have been converted to JPEG.")

# GUI setup
root = tk.Tk()
root.title("RAW to JPEG Converter (Multi-Core)")

# Instruction label
label = tk.Label(root, text="Click 'Convert' to select and convert RAW images to JPEG.", wraplength=400, justify="center")
label.pack(pady=10)

# Progress bar
progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

# Convert button
convert_button = tk.Button(root, text="Convert", command=convert_images)
convert_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
