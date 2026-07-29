import sys
sys.path.append('backend')
from app import app
from backend.plot_generator import generate_plots

with app.app_context():
    params = {
        'testType': '1',
        'benchPath': '',
        'calPath': '',
        'tempCalPath': ''
    }
    try:
        plots = generate_plots(params)
        print("Generated plots!")
        with open('backend/debug_log.txt', 'r') as f:
            lines = f.readlines()
            for line in lines[-20:]:
                print(line.strip())
    except Exception as e:
        print(f"Error: {e}")
