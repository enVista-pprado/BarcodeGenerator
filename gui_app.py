import tkinter as tk
from tkinter import filedialog, messagebox
from barcode_generator import generate_pdf_from_csv

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )

    if not file_path:
        return

    try:
        output_path = "output.pdf"
        generate_pdf_from_csv(file_path, output_path)
        messagebox.showinfo("Success", f"PDF generated:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

# --- GUI ---
root = tk.Tk()
root.title("Barcode PDF Generator")
root.geometry("400x200")

label = tk.Label(root, text="Upload a CSV to generate barcode PDF", font=("Arial", 12))
label.pack(pady=20)

button = tk.Button(root, text="Select CSV", command=select_file, font=("Arial", 12))
button.pack(pady=10)

root.mainloop()
