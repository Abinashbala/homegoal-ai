import sys
sys.stdout.reconfigure(encoding="utf-8")
for lib in ["sklearn", "prophet", "xgboost", "scipy", "statsmodels"]:
    try:
        m = __import__(lib)
        ver = getattr(m, "__version__", "?")
        print(f"  [OK]  {lib} {ver}")
    except ImportError as e:
        print(f"  [MISSING]  {lib}  -> {e}")
