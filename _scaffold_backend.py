import os, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8")

dirs = [
    "backend",
    "backend/schemas",
    "backend/engines",
    "backend/routers",
    "backend/tests",
]
BASE = r"C:\Users\DELL\Desktop\HomeGoal AI"
for d in dirs:
    pathlib.Path(os.path.join(BASE, d)).mkdir(parents=True, exist_ok=True)
    init = os.path.join(BASE, d, "__init__.py")
    if not os.path.exists(init):
        open(init, "w").close()
    print(f"  [OK]  {d}/")

print("\nDirectory scaffold complete.")
