import os
import json

base_path = "."
pma = "TestArea"
lmo_num = "123"

pma_path = os.path.join(base_path, "BenchNPD", pma)
if not os.path.exists(pma_path):
    pma_path = os.path.join(base_path, pma)

print(f"pma_path: {pma_path}")
if os.path.exists(pma_path):
    all_dirs = [d for d in os.listdir(pma_path) if os.path.isdir(os.path.join(pma_path, d))]
    matches = [d for d in all_dirs if lmo_num in d]
    print(f"matches: {matches}")
