import os
from src.config import EXPORTS_DIR

def export_students_to_csv(students, filename="thesis_data_export.csv"):
    csv_file = os.path.join(EXPORTS_DIR, filename)
    
    with open(csv_file, "w", encoding='utf-8') as f:
        f.write("Name,Thesis Quantity,Pages Per Book,Total Pages,Binding Cost,Total Cost,Discounted Value,Pending Amount,Status\n")
        for name, info in students.items():
            f.write(f"{name},{info.get('quantity', 0)},{info.get('pages_per_book', 0)},{info.get('total_pages', 0)},"
                    f"{info.get('binding_cost', 0)},{info.get('total_cost', 0)},{info.get('discounted_value', 0)},"
                    f"{info.get('pending_amount', 0.0)},{info.get('status', 'unknown')}\n")
    return csv_file

def export_financial_report_csv(metrics, filename="financial_report.csv"):
    csv_file = os.path.join(EXPORTS_DIR, filename)
    
    with open(csv_file, "w", encoding='utf-8') as f:
        f.write("Metric,Value (Rs.)\n")
        f.write(f"Gross Revenue Collected,{metrics['total_revenue_collected']:.2f}\n")
        f.write(f"Total Automated Binding Expenses,{metrics['total_binding_expense']:.2f}\n")
        f.write(f"Paper Material Stock Costs,{metrics['total_paper_expense']:.2f}\n")
        f.write(f"Operational Miscellaneous Expenses,{metrics['total_misc_expenses']:.2f}\n")
        f.write(f"Combined Running Expenditures,{metrics['combined_expenses']:.2f}\n")
        f.write(f"Net System Calculation Result,{metrics['net_profit']:.2f}\n")
    return csv_file