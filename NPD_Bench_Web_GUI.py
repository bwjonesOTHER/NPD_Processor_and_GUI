"""
Author: Brannon Jones
Date Modified: 07/08/2026

This provides test personel with an easy-to-use GUI for uploading NPD test data to SharePoint
while performing the data processing immediately for engineer review. This is also being used
as a proof of concept for using python to pull/push files from and to sharepoint.
"""

# ---- Libraries ---- #

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import sys
import Macallan_PMA_NPDxoverTemp_GT_MPedits_V3
import Macallan_PMA_BenchtopNPD_PlotData_v2
import Macallan_PMA_Array_BenchtopNPD_PlotData_v2
import threading
import shutil
import time
import traceback


################################################################################
# ---- User Credentials Input ---- #

def process_input():
    """Retrieve and process the text from both Entry widgets."""
    first = first_entry.get().strip().lower()
    last = last_entry.get().strip().lower()
    password = password_entry.get().strip()

    # TEST 1 → Over Temp
    if test == 1:
        path = os.path.join(
            r"File Path for Inputs"
        )

    # TEST 2 → Single Tile Bench NPD
    elif test == 2:
        path = os.path.join(
            r"File Path for Inputs"
        )

    # TEST 3 → Full PMA Array Bench NPD
    elif test == 3:
        # IMPORTANT: For test 3 the base folder is Test Hat
        path = os.path.join(
            r"File Path for Inputs"
        )

    # Write the base path into path.txt
    with open("path.txt", "w") as f:
        f.write(path)

    # Save credentials
    user = f"{first}.{last}@webarea.com"
    with open("user_credentials.txt", "w") as f:
        f.write(user)
        f.write("\n")
        f.write(password)



################################################################################


################################################################################
# ---- Uploads Data from User Input to Host Files ---- #



def upload_data():
    global PATH

    LMO_number = LMO_number_entry.get().strip()
    first = first_entry.get().strip().lower()
    last = last_entry.get().strip().lower()
    if test == 1:
        run_number = run_number_entry.get().strip()
        cap_number = cap_number_entry.get().strip()
        upload_path = os.path.join(r"File Path for Inputs")
    elif test == 2:
        PMA_area = PMA_number_entry.get().strip()
        print(PMA_area)
        if PMA_area != 'L110173C' and PMA_area != 'L110172E':
            print("Wrong PMA Area Value Entered. Please try again!")
        SN = SN_entry.get().strip()
        upload_path = os.path.join(
            rf"File Path for Inputs")

        with open("PMA_Area.txt", "w") as f:
            f.write(PMA_area)
        with open("SN.txt", "w") as f:
            f.write(SN)
        PATH = upload_path


    elif test == 3:

        SN = SN_entry.get().strip()
        LMO_number = LMO_number_entry.get().strip()
        SN_folder = f"SN{int(SN):04d}_LMO{LMO_number}"

        base_path = rf"File Path for Inputs"

        upload_path = os.path.join(base_path, SN_folder)
        os.makedirs(upload_path, exist_ok=True)

        with open("SN.txt", "w") as f:
            f.write(SN)

        with open("path.txt", "w") as f:
            f.write(upload_path)
        PATH = upload_path


###############################################################################


################################################################################
# ---- Allows User to Select and Move Files ---- #

def select_files(allow_multiple=True):
    try:
        filetypes = [
            ("All supported files (.csv, .s2p)", "*.csv *.s2p")

        ]

        if allow_multiple:
            # Returns a tuple of file paths
            files = filedialog.askopenfilenames(
                title="Select File(s)",
                filetypes=filetypes
            )
            if files:
                messagebox.showinfo("Files Selected", "\n".join(files))

            else:
                messagebox.showinfo("No Selection", "No files were selected.")
        else:
            # Returns a single file path
            file = filedialog.askopenfilename(
                title="Select a File",
                filetypes=filetypes
            )

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    selected_files = list(files)
    print(selected_files)

    # Example: list of selected files (full paths)

    # Destination folder
    with open("upload_path.txt", "r") as f:
        dest_folder = f.read().strip()

    # Create the folder if it doesn't exist
    os.makedirs(dest_folder, exist_ok=True)

    # Move each file
    for file_path in selected_files:
        if os.path.isfile(file_path):
            try:
                shutil.move(file_path, dest_folder)
                print(f"Moved: {file_path}")
            except Exception as e:
                print(f"Error moving {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")


################################################################################


################################################################################
# ---- Error Detection in Terminal ---- #

def run_with_error_detection(target_function, timeout=60):
    error_info = {"exception": None, "done": False}

    def wrapper():
        try:
            target_function()
        except Exception as e:
            import traceback
            error_info["exception"] = traceback.format_exc()
        finally:
            error_info["done"] = True

    worker = threading.Thread(target=wrapper, daemon=True)
    worker.start()

    start_time = time.time()
    while time.time() - start_time < timeout:
        if error_info["done"]:
            break
        time.sleep(0.2)

    # Error handling
    if error_info["exception"]:
        status_label.config(text="Error detected!", fg="red")
        print("ERROR in processing:\n" + error_info["exception"], file=sys.stderr)
        return False

    if not error_info["done"]:
        status_label.config(text="Processing timeout!", fg="red")
        print(f"ERROR: Function timed out after {timeout} seconds.", file=sys.stderr)
        return False

    # Success
    status_label.config(text="Processed!", fg="green")
    return True


################################################################################


################################################################################
# ---- Starts Processing Scripts while checking for errors ---- #

def macallan_NPD_Processing():
    if test == 1:
        success = run_with_error_detection(Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.main, timeout=90)
    elif test == 2:
        success = run_with_error_detection(Macallan_PMA_BenchtopNPD_PlotData_v2.main, timeout=90)
    else:
        success = run_with_error_detection(Macallan_PMA_Array_BenchtopNPD_PlotData_v2.main, timeout=90)

    if success:
        root.after(0, lambda: status_label.config(text="Processed!", fg="green"))
    else:
        root.after(0, lambda: status_label.config(text="Stopped Processing Due to Error!", fg="red"))


################################################################################


################################################################################
# ---- Button for Running Processing Scripts ---- #

def on_processing_button_click():
    status_label.config(text="Processing...", fg="orange")
    threading.Thread(target=macallan_NPD_Processing, daemon=True).start()


################################################################################


################################################################################
# ---- Place Holder Sharepoint Function Until IT Access ---- #

def connect_to_sharepoint_fake():
    # Test_Sharepoint_Access()
    root.after(1000, lambda: connectstatus_label.config(text="Connected to Sharepoint!", fg="green"))


################################################################################


################################################################################
# ---- Uses Sharepoint Function When User Submits Credentials ---- #

def on_submit_click():
    process_input()
    if test == 1:
        global PATH
        PATH = get_saved_path()
    connectstatus_label.config(text="Connecting to SharePoint...", fg="orange")
    threading.Thread(target=connect_to_sharepoint_fake, daemon=True).start()


################################################################################


################################################################################
# ---- Sets Test Type ---- #

def set_test(value):
    global test
    test = value
    root.destroy()  # Close the window after selection


################################################################################


################################################################################
# ---- Initial Test Selection GUI ---- #
################################################################################

root = tk.Tk()
root.title("NPD GUI")
root.geometry("400x200")

tk.Label(root, text="Please Select the Test Type", font=("Arial", 9)).grid(padx=120, pady=10)



tk.Button(root, text="Single Tile Bench NPD", command=lambda: set_test(2)).grid(
    row=1, column=0, columnspan=2, pady=25
)
tk.Button(root, text="Full PMA Array Bench NPD", command=lambda: set_test(3)).grid(
    row=2, column=0, columnspan=2, pady=25
)

root.mainloop()


################################################################################
# ---- Main GUI Window ---- #
################################################################################

root = tk.Tk()
root.title("NPD GUI")
root.geometry("1200x700")


################################################################################
# ---- Terminal Window ---- #
################################################################################

console_frame = tk.Frame(root)
console_frame.grid(row=0, column=5, rowspan=1000, padx=10, pady=10, sticky="ns")

tk.Label(console_frame, text="Live Output:", font=("Arial", 9)).pack(anchor="w")

output_box = ScrolledText(console_frame, height=32, width=100, state="disabled", font=("Consolas", 9))
output_box.pack(pady=5)

output_box.tag_config("stdout", foreground="black")
output_box.tag_config("stderr", foreground="red")

class TextRedirector:
    def __init__(self, widget, tag):
        self.widget = widget
        self.tag = tag

    def write(self, message):
        self.widget.configure(state="normal")
        self.widget.insert("end", message, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass

sys.stdout = TextRedirector(output_box, "stdout")
sys.stderr = TextRedirector(output_box, "stderr")

def clear_output():
    output_box.configure(state="normal")
    output_box.delete("1.0", "end")
    output_box.configure(state="disabled")

tk.Button(console_frame, text="Clear Output", command=clear_output).pack(pady=5)

print("Welcome to the NPD GUI. Please follow the steps to ensure proper file management/processing.")

################################################################################
# ---- Helpers ---- #
################################################################################

def get_saved_path():
    try:
        with open("path.txt", "r") as f:
            return f.read().strip()
    except:
        return None

PATH = get_saved_path()

def get_folders():
    try:
        return [f for f in os.listdir(PATH) if os.path.isdir(os.path.join(PATH, f))]
    except:
        return []

################################################################################
# ---- STEP 1: User Credentials ---- #
################################################################################

row = 0

tk.Label(root, text="1. Enter your name and SharePoint password:", font=("Arial", 9)).grid(
    row=row, column=0, columnspan=2, sticky="w", pady=10
)

row += 1
tk.Label(root, text="First Name:", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
first_entry = tk.Entry(root, width=25)
first_entry.grid(row=row, column=1)

row += 1
tk.Label(root, text="Last Name:", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
last_entry = tk.Entry(root, width=25)
last_entry.grid(row=row, column=1)

row += 1
tk.Label(root, text="SharePoint Password:", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
password_entry = tk.Entry(root, show="*", width=25)
password_entry.grid(row=row, column=1)

row += 1
tk.Button(root, text="Submit Credentials", command=on_submit_click).grid(
    row=row, column=0, columnspan=2, pady=5
)

row += 1
connectstatus_label = tk.Label(root, text="Not Connected", fg="red")
connectstatus_label.grid(row=row, column=0, columnspan=2)

row += 2


################################################################################
# ---- STEP 2: File Info Input ---- #
################################################################################

# Header
if test == 1:
    tk.Label(root, text="2. Enter Run Number, LMO Number, and Cap Number.", font=("Arial", 9)).grid(
        row=row, column=0, columnspan=2, sticky="w"
    )
elif test == 2:
    tk.Label(root, text="2. Enter LMO Number, Serial Number, and PMA Area.", font=("Arial", 9)).grid(
        row=row, column=0, columnspan=2, sticky="w"
    )
else:
    tk.Label(root, text="2. Enter LMO Number, Serial Number, and Run Entry.", font=("Arial", 9)).grid(
        row=row, column=0, columnspan=2, sticky="w"
    )

row += 1

# LMO
tk.Label(root, text="LMO Number (####-##):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
LMO_number_entry = tk.Entry(root, width=25)
LMO_number_entry.grid(row=row, column=1)

# ------------------------------------------------------------------------
# Test 1 fields
# ------------------------------------------------------------------------
if test == 1:
    row += 1
    tk.Label(root, text="Run Number (#):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    run_number_entry = tk.Entry(root, width=25)
    run_number_entry.grid(row=row, column=1)

    row += 1
    tk.Label(root, text="Cap Number (##):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    cap_number_entry = tk.Entry(root, width=25)
    cap_number_entry.grid(row=row, column=1)

# ------------------------------------------------------------------------
# Test 2 fields
# ------------------------------------------------------------------------
if test == 2:
    row += 1
    tk.Label(root, text="Serial Number (####):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    SN_entry = tk.Entry(root, width=25)
    SN_entry.grid(row=row, column=1)

    row += 1
    tk.Label(root, text="PMA Area (L110173C or L110172E):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    PMA_number_entry = tk.Entry(root, width=25)
    PMA_number_entry.grid(row=row, column=1)

# ------------------------------------------------------------------------
# Test 3 fields (cleaned + fixed)
# ------------------------------------------------------------------------
if test == 3:
    row += 1
    tk.Label(root, text="Serial Number (####):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    SN_entry = tk.Entry(root, width=25)
    SN_entry.grid(row=row, column=1)

    row += 1
    tk.Label(root, text="Run Entry (Run_#_#.###A):", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    run_entry_entry = tk.Entry(root, width=25)
    run_entry_entry.grid(row=row, column=1)

# ------------------------------------------------------------------------

row += 1
tk.Button(root, text="Submit File Info", command=upload_data).grid(
    row=row, column=0, columnspan=2, pady=10
)

row += 2


################################################################################
# ---- STEP 3: Select Files ---- #
################################################################################

tk.Label(root, text="3. Select all relevant data files (.csv + .s2p).", font=("Arial", 9)).grid(
    row=row, column=0, columnspan=2, sticky="w"
)

row += 1
tk.Button(root, text="Select Data Files", command=select_files).grid(
    row=row, column=0, columnspan=2
)

row += 2


################################################################################
# ---- STEP 4: Run Selection (Test 1 & 3 only) ---- #
################################################################################

if test in [1, 3]:
    tk.Label(root, text="4. Select Run A and Run B folders to process.", font=("Arial", 9)).grid(
        row=row, column=0, columnspan=2, sticky="w"
    )

    row += 1
    selected_folder = tk.StringVar(value="Select a folder")
    selected_folder1 = tk.StringVar(value="Select a folder")

    def update_paths_runs(*args):
        if selected_folder.get() not in ["", "Select a folder"]:
            with open("RunA_Path.txt", "w") as f:
                f.write(selected_folder.get())
        if selected_folder1.get() not in ["", "Select a folder"]:
            with open("RunB_Path.txt", "w") as f:
                f.write(selected_folder1.get())

    selected_folder.trace_add("write", update_paths_runs)
    selected_folder1.trace_add("write", update_paths_runs)

    tk.Label(root, text="Run A:", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    folder_combobox = ttk.Combobox(root, textvariable=selected_folder, values=get_folders(),
                                   state="readonly", width=30)
    folder_combobox.grid(row=row, column=1)

    row += 1
    tk.Label(root, text="Run B:", font=("Arial", 9)).grid(row=row, column=0, sticky="e")
    folder_combobox1 = ttk.Combobox(root, textvariable=selected_folder1, values=get_folders(),
                                    state="readonly", width=30)
    folder_combobox1.grid(row=row, column=1)

    # Auto-refresh dropdowns every 2 seconds
    def refresh_dropdowns():
        try:
            folders = [""] + get_folders()
            folder_combobox["values"] = folders
            folder_combobox1["values"] = folders
        except:
            pass
        root.after(2000, refresh_dropdowns)

    refresh_dropdowns()

    row += 2


################################################################################
# ---- STEP 5: Process ---- #
################################################################################

step_num = 5 if test == 1 else 4

tk.Label(root, text=f"{step_num}. Process the data files.", font=("Arial", 9)).grid(
    row=row, column=0, columnspan=2, sticky="w"
)

row += 1
tk.Button(root, text="Process Data Files", command=on_processing_button_click).grid(
    row=row, column=0, sticky="w"
)

status_label = tk.Label(root, text="Idle", fg="red")
status_label.grid(row=row, column=1, sticky="w")


root.mainloop()

# ---- End of Code ---- #
################################################################################