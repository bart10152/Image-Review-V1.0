import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import pandas as pd
import sqlite3
import random

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('answers.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        image_id TEXT PRIMARY KEY,
        folder TEXT,
        answer TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Clear the SQLite database
def clear_db():
    conn = sqlite3.connect('answers.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM answers')
    conn.commit()
    conn.close()
    # Also clear the CSV file
    with open('answers.csv', 'w') as f:
        f.write('')

# Save answer to database and CSV
def save_answer(image_id, folder, answer):
    conn = sqlite3.connect('answers.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO answers (image_id, folder, answer)
    VALUES (?, ?, ?)
    ''', (image_id, folder, answer))
    conn.commit()
    conn.close()

    # Append the new data directly to the CSV file
    with open('answers.csv', 'a') as f:
        if os.stat('answers.csv').st_size == 0:  # Check if the file is empty
            f.write('image_id,folder,answer\n')  # Write the header if the file is empty
        f.write(f'{image_id},{folder},{answer}\n')

# Function to handle the yes/no button click
def on_button_click(answer):
    global current_image, image_label, image_list, folder_label

    if current_image:
        folder_name, image_file = os.path.split(current_image)
        save_answer(image_file, os.path.basename(folder_name), answer)

    if image_list:
        current_image = image_list.pop(0)
        update_image()
    else:
        messagebox.showinfo("End", "You have completed all the images.")
        root.quit()

# Function to update the displayed image
def update_image():
    global current_image, image_label, folder_label

    if current_image:
        try:
            img = Image.open(current_image)
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk

            folder_name = os.path.basename(os.path.dirname(current_image))
            folder_label.config(text=f"Is this: {folder_name} ?", font=("Arial", 20))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
            on_button_click("Error")

# Function to start the app
def start_app():
    global image_list, current_image

    # Get the absolute path to the images folder
    main_folder = os.path.abspath('images')
    image_list = []
    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                image_list.append(os.path.join(root, file))

    # Shuffle images globally
    random.shuffle(image_list)
    if image_list:
        current_image = image_list.pop(0)
    else:
        current_image = None

    start_button.pack_forget()
    reset_button.pack_forget()
    question_label.pack(pady=10)
    image_label.pack()
    folder_label.pack(pady=10)
    button_frame.pack(side=tk.BOTTOM, pady=20)
    yes_button.pack(side=tk.LEFT, padx=20)
    no_button.pack(side=tk.RIGHT, padx=20)
    update_image()

# Initialize the main application window
root = tk.Tk()
root.title("Image Answer App")
root.geometry("1024x1024")

# Initialize database
init_db()

# Setup UI elements
start_button = tk.Button(root, text="Press Start to Begin", command=start_app, font=("Arial", 16))
start_button.pack(expand=True)

reset_button = tk.Button(root, text="Reset Data", command=clear_db, font=("Arial", 16))
reset_button.pack(expand=True)

question_label = tk.Label(root, text="Rate the below image based on general representation.", font=("Arial", 20))
image_label = tk.Label(root)
folder_label = tk.Label(root, text="", font=("Arial", 20))
button_frame = tk.Frame(root)
yes_button = tk.Button(button_frame, text="Yes", command=lambda: on_button_click("Yes"), font=("Arial", 16), width=10, height=2)
no_button = tk.Button(button_frame, text="No", command=lambda: on_button_click("No"), font=("Arial", 16), width=10, height=2)

# Bind ESC key to close the app
root.bind('<Escape>', lambda e: root.quit())

# Run the application
root.mainloop()
