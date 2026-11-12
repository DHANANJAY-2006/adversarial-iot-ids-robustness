import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
MODELS_DIR = os.path.join(PROJECT_ROOT, "results", "models")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")

os.makedirs(DATA_RAW_DIR, exist_ok=True)
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

BENIGN_LABEL = "BenignTraffic"
TARGET_COLUMN = "label"

MAX_ROWS = 500000 
TEST_SIZE = 0.2
RANDOM_SEED = 42

MUTABLE_FEATURES = [
    "Duration",
    "Tot size of bckwd packet",
    "Tot size of fwd packet",
    "Fwd Packet Length Max",
    "Bckwd Packet Length Max",
    "Flow IAT Mean",
    "Bckwd IAT Mean"
]

IMMUTABLE_FEATURES = [
    "Protocol",
    "Port",
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count"
]
