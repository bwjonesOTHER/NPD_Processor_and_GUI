with open('backend/app.py', 'r') as f:
    content = f.read()

old_generate = """    # Gather paths based on the test type for backward compatibility with existing text file logic
    if test == 1:
        runs = []
        # If in Upload mode, the runs are in uploads/Test1. The frontend passes dataSource as the path if we used Access mode.
        # But wait! For Test 1, the user uploads runs via Step 3 "Select Runs", which puts them in uploads/Test1!
        # So we should just read the directories from uploads/Test1!
        test1_dir = os.path.join(os.getcwd(), 'uploads', 'Test1')
        if os.path.exists(test1_dir):
            runs = [os.path.join(test1_dir, d) for d in os.listdir(test1_dir) if os.path.isdir(os.path.join(test1_dir, d))]
        params['runs'] = sorted(runs)"""

new_generate = """    # Gather paths based on the test type for backward compatibility with existing text file logic
    if test == 1:
        runs = []
        if os.path.exists("SelectedRuns.txt"):
            with open("SelectedRuns.txt", "r") as f:
                runs = [line.strip() for line in f if line.strip()]
        else:
            run_a = read_txt("RunA_Path.txt")
            run_b = read_txt("RunB_Path.txt")
            runs = [run for run in [run_a, run_b] if run]
        params['runs'] = runs"""

content = content.replace(old_generate, new_generate)

with open('backend/app.py', 'w') as f:
    f.write(content)
