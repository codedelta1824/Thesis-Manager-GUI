import json
import os
from src.config import JSON_FILE, TXT_FILE, EXPENSE_FILE

def load_json_data():
    if not os.path.exists(JSON_FILE):
        return {"students": {}, "expenses": {}}
    try:
        with open(JSON_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"students": {}, "expenses": {}}

def save_json_data(data):
    with open(JSON_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def sync_json_to_txt():
    db = load_json_data()
    
    # 1. Synchronize Student Text Database
    with open(TXT_FILE, "w", encoding='utf-8') as f:
        for name, details in db.get("students", {}).items():
            f.write(
                f'Name: {name}\n'
                f'Thesis Quantity: {details.get("quantity", 0)}\n'
                f'Pages Per Book: {details.get("pages_per_book", 0)}\n'
                f'Total Pages: {details.get("total_pages", 0)}\n'
                f'Total Binding Cost: Rs.{details.get("binding_cost", 0)}\n'
                f'Total Cost: Rs.{details.get("total_cost", 0)}💰\n'
                f'Discounted Value: Rs.{details.get("discounted_value", 0)}💰\n'
                f'Pending Amount: Rs.{float(details.get("pending_amount", 0.0))}💰\n\n'
            )
            
    # 2. Synchronize Operating Expense Text Trackers
    with open(EXPENSE_FILE, "w", encoding='utf-8') as f:
        for exp_name, exp_amount in db.get("expenses", {}).items():
            f.write(f"{exp_name}: {exp_amount}\n")