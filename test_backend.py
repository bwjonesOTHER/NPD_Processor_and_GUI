import sys
sys.path.insert(0, 'backend')
import plot_generator
try:
    print("Testing plot_generator backend structure...")
    # Just checking imports and basic structure without actual data (because we don't have mock data)
    print("Success: modules load correctly")
except Exception as e:
    print("Error:", e)
