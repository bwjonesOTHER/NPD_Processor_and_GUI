import os
def get_files():
    runs = []
    if os.path.exists("SelectedRuns.txt"):
        with open("SelectedRuns.txt", "r") as f:
            runs = [line.strip() for line in f if line.strip()]
    if runs:
        print(f"Checking directory: {runs[0]}")
        try:
            for root, dirs, files in os.walk(runs[0]):
                for f in files:
                    print(os.path.join(root, f))
        except Exception as e:
            print("Error walking directory:", e)
    else:
        print("No runs selected.")
get_files()
