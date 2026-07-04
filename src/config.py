import os

# Core Directory Resolution
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')

# Ensure isolated directories exist seamlessly
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# System File Paths
JSON_FILE = os.path.join(DATA_DIR, 'thesis_data.json')
TXT_FILE = os.path.join(DATA_DIR, 'Thesis Info.txt')
EXPENSE_FILE = os.path.join(DATA_DIR, 'Expenses.txt')

# Pricing Strategy & Constants
PRINTING_VALUE_1 = 10 
PRINTING_VALUE_2 = 8 

BINDING_VALUE_3 = 600  
BINDING_VALUE_4 = 200 

COST_PER_PAGE = 1.68
BINDING_HARD_COST = 300.0