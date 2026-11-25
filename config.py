from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

SOIL_DIR = DATA_DIR / "soil"
BOUNDARIES_DIR = DATA_DIR / "boundaries"
FOREST_DIR = DATA_DIR / "tree_species"

EE_PROJECT_ID = "omela-geo-tools"

POINTS_FILE = DATA_DIR / 'points.xlsx'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)