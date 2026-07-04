from src.config import (
    PRINTING_VALUE_1, PRINTING_VALUE_2, 
    BINDING_VALUE_3, BINDING_VALUE_4, 
    COST_PER_PAGE, BINDING_HARD_COST
)

def calculate_thesis_costs(pages, thesis_quantity, printing_choice, binding_choice):
    """Calculates granular volume allocations, page distributions, and base costs."""
    printing_rate = PRINTING_VALUE_1 if printing_choice == 1 else PRINTING_VALUE_2
    binding_rate = BINDING_VALUE_3 if binding_choice == 3 else BINDING_VALUE_4

    total_pages = pages * thesis_quantity + thesis_quantity
    binding_cost = binding_rate * thesis_quantity
    total_cost = ((pages * printing_rate + binding_rate) * thesis_quantity) + (thesis_quantity * 10) 
    
    return total_pages, binding_cost, total_cost

def process_financial_metrics(students, expenses):
    """Executes running calculations across entire ledger frameworks."""
    total_revenue_collected = 0.0
    total_binding_expense = 0.0
    total_pages_consumed = 0      
    
    for info in students.values():
        discounted = float(info.get("discounted_value", 0.0))
        pending = float(info.get("pending_amount", 0.0))
        total_revenue_collected += max(0.0, discounted - pending)
        
        quantity = int(info.get("quantity", 0))
        total_binding_expense += (quantity * BINDING_HARD_COST)
        total_pages_consumed += int(info.get("total_pages", 0))

    # Calculate exact material usage breakdowns
    cartons = total_pages_consumed // 2500
    remaining_after_cartons = total_pages_consumed % 2500
    rims = remaining_after_cartons // 500
    leftover_pages = remaining_after_cartons % 500

    consumption_str = ""
    if cartons > 0:
        consumption_str += f"{cartons} Carton(s), "
    consumption_str += f"{rims} Rim(s) and {leftover_pages} Page(s)"

    total_paper_expense = total_pages_consumed * COST_PER_PAGE
    total_misc_expenses = sum(expenses.values())
    combined_expenses = total_misc_expenses + total_binding_expense + total_paper_expense
    net_profit = total_revenue_collected - combined_expenses
    
    return {
        "total_revenue_collected": total_revenue_collected,
        "total_binding_expense": total_binding_expense,
        "total_pages_consumed": total_pages_consumed,
        "consumption_str": consumption_str,
        "total_paper_expense": total_paper_expense,
        "total_misc_expenses": total_misc_expenses,
        "combined_expenses": combined_expenses,
        "net_profit": net_profit
    }