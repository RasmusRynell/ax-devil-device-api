import sys
from pathlib import Path

# The generator lives in the repo root (not in the wheel); make it importable for these tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
