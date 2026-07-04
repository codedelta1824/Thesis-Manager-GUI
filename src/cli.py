import os
import sys
import csv
from datetime import datetime
from src.config import (
    PRINTING_VALUE_1, PRINTING_VALUE_2, 
    BINDING_VALUE_3, BINDING_VALUE_4, TXT_FILE
)
from src.storage import load_json_data, save_json_data, sync_json_to_txt
from src.core import calculate_thesis_costs, process_financial_metrics
from src.exporter import export_students_to_csv, export_financial_report_csv

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_return():
    """
    Anti-Spam Input Guard: Freezes the terminal display. 
    Will not drop out to parent menus until 'q' is explicitly entered.
    """
    while True:
        choice = input("\n➔ Type 'q' (or 'Q') to go back: ").strip().lower()
        if choice == 'q':
            break
        print("⚠️  Screen Locked: You must explicitly type 'q' to exit this view.")

def export_to_csv(filename_prefix, headers, rows):
    """Safely handles generic CSV writes inside the designated exports directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_dir = os.path.join(base_dir, "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = os.path.join(export_dir, filename)
    
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"\n📊 Export Complete!")
        print(f"📂 CSV Location: {filepath}")
    except Exception as e:
        print(f"\n❌ Error printing spreadsheet matrix: {e}")

def add_thesis_data():
    while True:
        clear_screen()
        print('======== Adding Student Data Ledger ========')
        try:
            raw_input = input("\nHow many thesis data entries do you want to add? (or type 'q' to go back): ").strip().lower()
            if raw_input == 'q':
                clear_screen()
                return
            num_entries = int(raw_input)
            if num_entries <= 0:
                print('Please enter a number greater than 0.')
                wait_for_return()
                continue
            break
        except ValueError:
            print("\nInvalid input. Please enter a valid number or 'q'.")
            wait_for_return()

    for i in range(num_entries):
        clear_screen()
        print(f'======== Adding Student {i + 1} of {num_entries} ========')
        print('\n1) Per Page Print 10rs/80grms Paper')
        print('2) Per page Print 8rs/70grms Paper')
        
        try:
            printing_choice = int(input('\nEnter Printing Choice (1 or 2): '))
            if printing_choice not in [1, 2]:
                print('\nInvalid Number. Skipping this student entry!')
                wait_for_return()
                continue
                
            print('\n3) Thesis Binding Rs.600')
            print('4) Spiral Binding Rs.200')

            binding_choice = int(input('\nEnter Binding Choice (3 or 4): '))
            if binding_choice not in [3, 4]:
                print('\nInvalid Number. Skipping this student entry!')
                wait_for_return()
                continue
                
            clear_screen()
            
            name = input('Enter Your Name: ').lower().strip()
            if not name:
                print("Name cannot be empty. Skipping this student entry!")
                wait_for_return()
                continue
                
            thesis_quantity = int(input('Enter Thesis Quantity: '))
            pages = int(input('Enter Pages Per Book: '))

            total_pages, binding_cost, total_cost = calculate_thesis_costs(
                pages, thesis_quantity, printing_choice, binding_choice
            )

            print('\n ======== Costing Data Of Thesis ========')
            print(f'Name: {name}')
            print(f'Total Thesis Quantity: {thesis_quantity}')
            print(f'Pages Per Book: {int(pages) + 1}')
            print(f'Total Pages: {total_pages}')
            print(f'Total Binding Cost: Rs.{binding_cost}')
            print(f"Total Cost: Rs.{total_cost}💰")

            discount = int(input('Enter Thesis Discount: '))
            final_cost = total_cost - discount

            print(f"Final Cost After Discount: Rs.{final_cost}💰")

            db = load_json_data()
            db["students"][name] = {
                "name": name,
                "quantity": thesis_quantity,
                "pages_per_book": int(pages) + 1,
                "total_pages": total_pages,
                "binding_cost": binding_cost,
                "total_cost": total_cost,
                "discounted_value": final_cost,
                "pending_amount": float(final_cost),
                "status": "unknown"
            }
            save_json_data(db)
            sync_json_to_txt()

            print(f'\nStudent Data for "{name}" Saved Successfully ✅\n')
            if i < num_entries - 1:
                print("Press Enter context cleared. Moving to next record prompt setup.")
                wait_for_return()
                
        except ValueError:
            print("\nInvalid input type. Skipping this student entry.")
            wait_for_return()
            
    print("\nAll database updates finished successfully.")
    wait_for_return()
    clear_screen()

def view_thesis_data():
    clear_screen()
    try:
        sync_json_to_txt()
        if not os.path.exists(TXT_FILE):
            print('\nNo Such File Exists.')
            wait_for_return()
            clear_screen()
            return

        with open(TXT_FILE, "r", encoding='utf-8') as f:
            data = f.read()
        if data.strip():
            print('======= Saved Thesis Data =======')
            print(data)
            
            # Interactive CSV Export Prompt
            export_choice = input("Would you like to export this raw text breakdown to CSV? (y/n): ").strip().lower()
            if export_choice == 'y':
                db = load_json_data()
                headers = ["Student ID", "Quantity Ordered", "Page Length", "Aggregated Pages", "Total Cost Ledger"]
                rows = [[k, v.get("quantity"), v.get("pages_per_book"), v.get("total_pages"), v.get("total_cost")] for k, v in db.get("students", {}).items()]
                export_to_csv("raw_thesis_manifest", headers, rows)
            
            wait_for_return()
            clear_screen()
        else:
            print('\nNo Thesis Data Found 📂\n')
            wait_for_return()
            clear_screen()
            
    except Exception as e:
        print(f"An error occurred: {e}")
        wait_for_return()

def delete_specific_student_thesis_data():
    clear_screen()
    name_to_delete = input("\nEnter the name of the student to delete (or type 'q' to cancel): ").lower().strip()
    if name_to_delete == 'q':
        clear_screen()
        return
        
    db = load_json_data()

    if name_to_delete in db["students"]:
        del db["students"][name_to_delete]
        save_json_data(db)
        sync_json_to_txt()
        print(f"\nStudent named '{name_to_delete}' has been deleted ✅\n")
    else:
        print(f"\nNo student found with the name '{name_to_delete}' ❌")
    
    wait_for_return()
    clear_screen()

def delete_all_thesis_data():
    clear_screen()
    print("=========================================================")
    print("⚠️  WARNING: YOU ARE ABOUT TO DELETE ALL THESIS RECORDS  ⚠️")
    print("=========================================================")
    print("\nThis action is PERMANENT and will wipe out the entire database.")
    print("Type 'DELETE' in all caps to confirm, or 'q' to abort.")
    
    confirm = input("\nConfirm destructive action: ").strip()
    
    if confirm == "DELETE":
        db = load_json_data()
        db["students"] = {}
        save_json_data(db)
        sync_json_to_txt()
        print('\n[SUCCESS] All Student Thesis Data Has Been Safely Deleted ✅')
    else:
        print("\n[CANCELLED] Action aborted. Your data remains perfectly intact.")
        
    wait_for_return()
    clear_screen()

def view_overall_cost():
    clear_screen()
    db = load_json_data()
    students = db.get("students", {})
    
    if not students:
        print("\nNo thesis data found to calculate cost.\n")
        wait_for_return()
        clear_screen()
        return

    all_orig = all_disc = all_pend = all_recv = 0
    all_count = len(students)

    del_orig = del_disc = del_pend = del_recv = 0
    del_count = 0

    ndel_orig = ndel_disc = ndel_pend = ndel_recv = 0
    ndel_count = 0

    def clean_float(val):
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        cleaned = str(val).replace("Rs.", "").replace("💰", "").replace(",", "").strip()
        try: return float(cleaned)
        except ValueError: return 0.0

    for info in students.values():
        original = clean_float(info.get("total_cost", 0))
        discounted = clean_float(info.get("discounted_value", 0))
        pending = clean_float(info.get("pending_amount", 0.0))
        received = max(0.0, discounted - pending)

        all_orig += original; all_disc += discounted; all_pend += pending; all_recv += received
        is_delivered = info.get("thesis_delivered", False)

        if is_delivered:
            del_count += 1; del_orig += original; del_disc += discounted; del_pend += pending; del_recv += received
        else:
            ndel_count += 1; ndel_orig += original; ndel_disc += discounted; ndel_pend += pending; ndel_recv += received

    print("\n" + "="*115)
    print(f"{'THREE-WAY THESIS FINANCIAL SUMMARY':^115}")
    print("="*115)
    print(f"{'Metric / Category':<27} | {'OVERALL (All)':<25} | {'DELIVERED':<25} | {'NOT DELIVERED':<25}")
    print("-" * 115)
    print(f"{'Student Count':<27} | {all_count:<25} | {del_count:<25} | {ndel_count:<25}")
    print(f"{'Thesis Items Check':<27} | {all_count * 4:<25} | {del_count * 4:<25} | {ndel_count * 4:<25}")
    print(f"{'Combined Original Cost':<27} | Rs.{all_orig:<21.2f} | Rs.{del_orig:<21.2f} | Rs.{ndel_orig:<21.2f}")
    print(f"{'Combined Discounted Cost':<27} | Rs.{all_disc:<21.2f} | Rs.{del_disc:<21.2f} | Rs.{ndel_disc:<21.2f}")
    print("-" * 115)
    print(f"{'Total Received Amount':<27} | Rs.{all_recv:<21.2f} | Rs.{del_recv:<21.2f} | Rs.{ndel_recv:<21.2f}")
    print(f"{'Total Pending Amount':<27} | Rs.{all_pend:<21.2f} | Rs.{del_pend:<21.2f} | Rs.{ndel_pend:<21.2f}")
    print("="*115 + "\n")
    
    export_choice = input("Would you like to export this financial matrix breakdown to CSV? (y/n): ").strip().lower()
    if export_choice == 'y':
        headers = ["Financial Metric Description", "Overall Combined Sums", "Delivered Dispatches", "Pending Active Deposits"]
        rows = [
            ["Active Client Count", all_count, del_count, ndel_count],
            ["Total Volume Matrix Item Multiplier", all_count * 4, del_count * 4, ndel_count * 4],
            ["Base Valuation Costing", all_orig, del_orig, ndel_orig],
            ["Contractual Realized Pricing", all_disc, del_disc, ndel_disc],
            ["Liquid Cash Balance Received", all_recv, del_recv, ndel_recv],
            ["Outstanding Invoice Deficits", all_pend, del_pend, ndel_pend] 
        ]
        export_to_csv("three_way_financial_summary", headers, rows)
        
    wait_for_return()
    clear_screen()

def combine_student_by_name():
    clear_screen()
    print("======== 🔄 Combine / Merge Student Records ========\n")
    db = load_json_data()
    students = db.get("students", {})
    
    if len(students) < 2:
        print("At least two active student records are required to perform a merge action.")
        wait_for_return()
        clear_screen()
        return

    print("Active Students Ledger:")
    print("-" * 65)
    for idx, (student_id, s) in enumerate(students.items(), start=1):
        print(f"{idx:2}) Name: {student_id.title():<12} | Qty: {s.get('quantity', 0):<3} | Total: Rs.{s.get('total_cost', 0):<5} | Pending: Rs.{s.get('pending_amount', 0.0)}")
    print("-" * 65)

    source_name = input("\nEnter name to merge FROM (or type 'q' to go back): ").lower().strip()
    if source_name == 'q': return
    if source_name not in students:
        print(f"\nNo valid record found for '{source_name}' ❌")
        wait_for_return()
        return

    target_name = input("Enter name to merge INTO: ").lower().strip()
    if target_name not in students:
        print(f"\nNo valid record found for '{target_name}' ❌")
        wait_for_return()
        return

    if source_name == target_name:
        print("\n❌ Error: Cannot merge a student record into itself.")
        wait_for_return()
        return

    src_data = students[source_name]
    tgt_data = students[target_name]

    combined_quantity = src_data.get("quantity", 0) + tgt_data.get("quantity", 0)
    combined_total_pages = src_data.get("total_pages", 0) + tgt_data.get("total_pages", 0)
    combined_binding_cost = src_data.get("binding_cost", 0) + tgt_data.get("binding_cost", 0)
    combined_total_cost = src_data.get("total_cost", 0) + tgt_data.get("total_cost", 0)
    combined_discounted_value = src_data.get("discounted_value", 0) + tgt_data.get("discounted_value", 0)
    combined_pending_amount = float(src_data.get("pending_amount", 0.0)) + float(tgt_data.get("pending_amount", 0.0))
    combined_pages_per_book = max(src_data.get("pages_per_book", 0), tgt_data.get("pages_per_book", 0))
    
    combined_status = tgt_data.get("status", "unknown")

    print("\n================= ACCOUNT MERGE PREVIEW =================")
    print(f"Merging data from '{source_name}' into master record '{target_name}'")
    print("-" * 57)
    print(f"• Total Book Quantity : {tgt_data.get('quantity', 0)} + {src_data.get('quantity', 0)} ➔ {combined_quantity}")
    print(f"• Consolidated Cost   : Rs.{tgt_data.get('total_cost', 0)} + Rs.{src_data.get('total_cost', 0)} ➔ Rs.{combined_total_cost}💰")
    print(f"• Outstanding Balance : Rs.{tgt_data.get('pending_amount', 0.0)} + Rs.{src_data.get('pending_amount', 0.0)} ➔ Rs.{combined_pending_amount:.2f}💰")
    print("=========================================================")
    
    confirm = input(f"\nAre you sure you want to merge these accounts? '{source_name}' will be permanently deleted (Y/N): ").strip().lower()
    
    if confirm == 'y':
        tgt_data["quantity"] = combined_quantity
        tgt_data["pages_per_book"] = combined_pages_per_book
        tgt_data["total_pages"] = combined_total_pages
        tgt_data["binding_cost"] = combined_binding_cost
        tgt_data["total_cost"] = combined_total_cost
        tgt_data["discounted_value"] = combined_discounted_value
        tgt_data["pending_amount"] = combined_pending_amount
        
        del db["students"][source_name]
        save_json_data(db)
        sync_json_to_txt()
        print(f"\nRecords successfully unified into '{target_name}'! ✅")
        
        export_choice = input("Export updated unified client metadata profile matrix to CSV? (y/n): ").strip().lower()
        if export_choice == 'y':
            export_to_csv(f"merged_{target_name}_profile", ["Metric Keys", "Values"], list(tgt_data.items()))
    else:
        print("\n[CANCELLED] Merge operation aborted.")
        
    wait_for_return()
    clear_screen()

def discount_specific_student():
    clear_screen()
    print("======== 🏷️  Apply Student Discount  ========\n")
    db = load_json_data()
    students = db.get("students", {})

    if not students:
        print("No student records found to apply a discount.")
        wait_for_return()
        clear_screen()
        return

    print("Available Students Ledger:")
    print("-" * 40)
    for idx, (student_id, s) in enumerate(students.items(), start=1):
        print(f"{idx}) Name: {student_id.title():<12} | Total Cost: Rs.{s.get('total_cost', 0):<10} | Current Pending: Rs.{s.get('pending_amount', 0.0):<10} | Discounted Value: Rs.{s.get('discounted_value', 0):<10}")
    print("-" * 40)

    name = input("\nEnter Name (or type 'q' to go back): ").lower().strip()
    if name == 'q' or name == "":
        clear_screen()
        return

    if name in students:
        student_data = students[name]
        original_total_cost = student_data["total_cost"]
        old_discounted_value = student_data["discounted_value"]
        current_pending = float(student_data.get("pending_amount", 0.0))
        amount_already_paid = max(0.0, float(old_discounted_value) - current_pending)

        try:
            new_discount = int(input(f"Enter new discount total for {name}: "))
            new_discounted_val = max(original_total_cost - new_discount, 0)
            new_pending_val = max(0.0, float(new_discounted_val) - amount_already_paid)
            
            student_data["discounted_value"] = new_discounted_val
            student_data["pending_amount"] = new_pending_val
            
            save_json_data(db)
            sync_json_to_txt()
            print(f"\nDiscount updated for '{name}' ✅")
            
            export_choice = input("Export modified invoice sheet row items to CSV? (y/n): ").strip().lower()
            if export_choice == 'y':
                export_to_csv(f"discount_{name}_invoice", ["Account Target", "Initial Bill", "Applied Deductible Balance", "Net Invoice Due"], [[name, original_total_cost, new_discount, new_pending_val]])
        except ValueError:
            print("\n❌ Invalid discount amount.")
    else:
        print(f"\nNo student found with the name '{name}' ❌")
        
    wait_for_return()
    clear_screen()

def view_cost_of_specific_students():
    clear_screen()
    names_input = input("\nEnter comma-separated names to query (or type 'q' to abort): ").lower().strip()
    if names_input == 'q': return
    names_to_check = [n.strip() for n in names_input.split(",") if n.strip()]

    db = load_json_data()
    students = db.get("students", {})
    rows_collected = []

    for name in names_to_check:
        if name in students:
            info = students[name]
            print("\n" + "=" * 40)
            print(f"Name: {name}\n"
                f"Thesis Quantity: {info['quantity']}\n"
                f"Pages Per Book: {info['pages_per_book']}\n"
                f"Total Pages: {info['total_pages']}\n"
                f"Total Binding Cost: Rs.{info['binding_cost']}\n"
                f"Total Cost: Rs.{info['total_cost']}💰\n"
                f"Discounted Value: Rs.{info['discounted_value']}💰\n"
                f"Pending Amount: Rs.{info['pending_amount']}💰")
            print("=" * 40)
            rows_collected.append([name, info['quantity'], info['total_pages'], info['total_cost'], info['pending_amount']])
        else:
            print(f"\nNo data found for '{name}' ❌")

    if rows_collected:
        export_choice = input("\nExport these matched student queries to a separate CSV? (y/n): ").strip().lower()
        if export_choice == 'y':
            export_to_csv("filtered_students_lookup", ["Name ID", "Units", "Gross Vol Pages", "Base Invoiced Total", "Outstanding Balance"], rows_collected)

    wait_for_return()
    clear_screen()

def calculate_profit():
    while True:
        clear_screen()
        print('======== 📈 ADVANCED FINANCIAL CALCULATOR ========')
        print("\n1) Add Miscellaneous Expense")
        print("2) View Detailed Expense Breakdown")
        print("3) Generate Full Profit & Loss Statement")
        print("4) Check Account Balance (Cash in Account)")
        print("5) Clear Miscellaneous Expenses")
        print("6) Export Financial Report to CSV")
        print("7) Return to Main Menu")
        print("=========================================================")

        user_choice = input("\nChoose an option (1-7): ").strip()
        db = load_json_data()
        students = db.get("students", {})
        expenses = db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)

        if user_choice == "1":
            try:
                raw_amt = input("\nHow many expenses do you want to add? (or 'q' to go back): ").strip().lower()
                if raw_amt == 'q': continue
                choice = int(raw_amt)
                for i in range(choice):
                    expense_name = input(f"Enter description for expense #{i+1}: ").strip().lower()
                    if not expense_name: continue
                    amount = float(input(f"Enter amount for '{expense_name}': Rs."))
                    db["expenses"][expense_name] = db["expenses"].get(expense_name, 0.0) + amount
                
                save_json_data(db)
                sync_json_to_txt()
                print("\nExpenses logged successfully! ✅")
            except ValueError:
                print("\n❌ Invalid data entry numerical parsing failure.")
            wait_for_return()

        elif user_choice == "2":
            print("\n================= EXPENSE BREAKDOWN =================")
            print(f"1. Automated Thesis Binding Costs : Rs.{metrics['total_binding_expense']:.2f}")
            print(f"2. Automated Paper Stock Costs    : Rs.{metrics['total_paper_expense']:.2f}")
            print(f"   (Total Consumption: {metrics['consumption_str']})")
            print("-" * 53)
            for name, amount in expenses.items():
                print(f"   • {name}: Rs.{amount:.2f}")
            print("=" * 53)
            print(f"TOTAL RUNNING EXPENDITURES         : Rs.{metrics['combined_expenses']:.2f}💰\n")
            
            export_choice = input("Export complete operating expense matrix logs to CSV? (y/n): ").strip().lower()
            if export_choice == 'y':
                headers = ["Expenditure Core Items", "Outflow Valuation (Rs.)"]
                rows = [["Automated Binding Machine Surcharges", metrics['total_binding_expense']], ["Raw Inventory Paper Medium Consumed", metrics['total_paper_expense']]]
                for k, v in expenses.items(): rows.append([f"Misc - {k}", v])
                export_to_csv("itemized_operating_expenses", headers, rows)
            wait_for_return()

        elif user_choice == "3":
            print("\n================ PROFIT & LOSS STATEMENT ================")
            print(f" Gross Revenue (Actual Cash Collected) : Rs.{metrics['total_revenue_collected']:.2f}")
            print(f" Total Hard Costs (Binding Costs)     : Rs.{metrics['total_binding_expense']:.2f}")
            print(f" Raw Material Costs (Paper Usage)      : Rs.{metrics['total_paper_expense']:.2f}")
            print(f" Operational Expenses (Shop/Misc)      : Rs.{metrics['total_misc_expenses']:.2f}")
            print("-" * 57)
            print(f" NET SYSTEM P&L RESULT                : Rs.{metrics['net_profit']:.2f}")
            print("=========================================================")
            
            export_choice = input("Export full P&L balance sheet ledger data to CSV? (y/n): ").strip().lower()
            if export_choice == 'y':
                export_financial_report_csv(metrics)
            wait_for_return()

        elif user_choice == "4":
            print("\n=================== CASH ACCOUNT LEDGER ===================")
            print(f" Cash Received on Orders :  Rs.{metrics['total_revenue_collected']:.2f}")
            print(f" Outgoing Cash Outlays   : -Rs.{metrics['combined_expenses']:.2f}")
            print("-" * 59)
            print(f" CURRENT CASH IN ACCOUNT :  Rs.{metrics['net_profit']:.2f} 💰")
            print("===========================================================")
            
            export_choice = input("Export liquid cash reconciliation report ledger to CSV? (y/n): ").strip().lower()
            if export_choice == 'y':
                export_to_csv("cash_reserve_statement", ["Ledger Account Line Item", "Liquid Asset Valuation"], [["Aggregated Incoming Cash Revenue Receipts", metrics['total_revenue_collected']], ["Debited Expenditures Liquid Value Outflows", metrics['combined_expenses']], ["Net Dynamic Working Liquidity Reserves", metrics['net_profit']]])
            wait_for_return()

        elif user_choice == "5":
            confirm = input("\n⚠️ Delete all misc shop expenses? (Y/N): ").strip().lower()
            if confirm == 'y':
                db["expenses"] = {}
                save_json_data(db)
                sync_json_to_txt()
                print("\nMiscellaneous shop expenses cleared. ✅")
            wait_for_return()

        elif user_choice == "6":
            csv_path = export_financial_report_csv(metrics)
            print(f"\nFinancial ledger report exported successfully to: {csv_path} ✅")
            wait_for_return()

        elif user_choice == "7":
            break
        else:
            print("\n❌ Selection out of bounds.")
            wait_for_return()

def payment_stats():
    while True:
        clear_screen()
        print('======== Payment Statistics System ========')
        print('\n1) Cash Received (Subtracts from Balance Owed)')
        print('2) Pending Amount (Add/Override Balance Owed)')
        print('3) Remove Student (Delete Record)')
        print('4) Show Stats (View All Pending Balance)')
        print('5) Return to Main Menu')

        choice = input('\nChoose Any Number From (1-5): ').strip()
        db = load_json_data()

        if choice == '1':
            show_all = input("Show all students with pending balances before processing payment? (y/n): ").strip().lower()
            if show_all == 'y':
                print("\nCurrent Students with Pending Balances:")
                for s_name, info in db.get("students", {}).items():
                    pending = info.get("pending_amount", 0.0)
                    if pending > 0:
                        print(f" - {s_name:<14}: Rs.{pending:<10.2f} pending")
                print("-" * 40)

            name = input("Enter Student Name (or 'q' to go back): ").lower().strip()
            if name == 'q': continue
            try:
                amount_given = float(input('Enter Received Amount: '))
                if name in db["students"]:
                    current_val = db["students"][name].get("pending_amount", 0.0)
                    new_val = max(0.0, current_val - amount_given)
                    db["students"][name]["pending_amount"] = new_val
                    save_json_data(db)
                    sync_json_to_txt()
                    print(f'\nPayment updated! Rs.{amount_given} processed for {name}. ✅')
                    
                    export_choice = input("Export receipt confirmation transaction line to CSV? (y/n): ").strip().lower()
                    if export_choice == 'y':
                        export_to_csv(f"payment_receipt_{name}", ["Client", "Transaction Payment Processed", "Remaining Outstanding Credit"], [[name, amount_given, new_val]])
                else:
                    print(f'\nStudent "{name}" not found. ❌')
            except ValueError:
                print("\nInvalid input formats.")
            wait_for_return()

        elif choice == '2':
            name = input('Enter Student Name: ').lower().strip()
            try:
                pending_amount = float(input('Enter Total Balance Owed Amount: '))
                if name not in db["students"]:
                    db["students"][name] = {
                        "name": name, "quantity": 0, "pages_per_book": 0, "total_pages": 0,
                        "binding_cost": 0, "total_cost": 0, "discounted_value": pending_amount,
                        "pending_amount": pending_amount, "status": "unknown"
                    }
                else:
                    db["students"][name]["pending_amount"] = pending_amount
                    
                save_json_data(db)
                sync_json_to_txt()
                print('\nPayment Data Balance Injection Complete ✅')
            except ValueError:
                print("\nInvalid calculation string formats.")
            wait_for_return()

        elif choice == '3':
            name_to_remove = input('Enter Student Name to Remove: ').lower().strip()
            if name_to_remove in db["students"]:
                del db["students"][name_to_remove]
                save_json_data(db)
                sync_json_to_txt()
                print(f'\nStudent "{name_to_remove}" removed from payments ✅')
            else:
                print(f'\nStudent "{name_to_remove}" not found. ❌')
            wait_for_return()

        elif choice == '4':
            students = db.get("students", {})
            if students:
                print('\n======= Current Payment Stats =======')
                rows = []
                for s_name, info in students.items():
                    print(f"Student Name: {s_name:<14} | Remaining Balance: Rs.{info.get('pending_amount', 0.0):<10.2f}💰")
                    rows.append([s_name, info.get('pending_amount', 0.0)])
                
                export_choice = input("\nExport current outstanding account deficits listing to CSV? (y/n): ").strip().lower()
                if export_choice == 'y':
                    export_to_csv("credit_deficit_rallies", ["Client Identity Name Tag", "Outstanding Invoiced Inactive Arrears"], rows)
            else:
                print('\nNo Payment Data Found 📂')
            wait_for_return()

        elif choice == '5':
            break
        else:
            print("\nInvalid sequence parameters mapping index chosen.")
            wait_for_return()
            clear_screen()

def show_status():
    while True:
        clear_screen()
        print("======== System Status Interface ========\n")
        db = load_json_data()
        students = db.get("students", {})

        if not students:
            print("No student records found.")
            wait_for_return()
            return

        student_mapping = {}
        rows = []
        for idx, (student_id, s) in enumerate(students.items(), start=1):
            student_mapping[str(idx)] = student_id 
            print(f"{idx}) Name: {s.get('name', student_id):<15} | Status: {s.get('status', 'unknown'):<10}")
            rows.append([s.get('name', student_id), s.get('status', 'unknown')])
        
        print("\n===============================")
        choice_num = input("Enter Num Of Student To Update Status (or 'e' to export list, 'q' to quit): ").strip().lower()
        
        if choice_num == 'q':
            break
        elif choice_num == 'e':
            export_to_csv("student_structural_status_report", ["Client Reference Key", "Production Milestone Tag"], rows)
            wait_for_return()
            continue
        
        if choice_num in student_mapping:
            target_id = student_mapping[choice_num]
            student_data = students[target_id]
            
            print(f"\nUpdating status for {student_data.get('name', target_id)}:")
            print("1) checked\n2) unchecked\n3) pending")
            choice_status = input("Choose an option (1-3): ").strip()
            
            status_opts = {"1": "checked", "2": "unchecked", "3": "pending"}
            if choice_status in status_opts:
                student_data["status"] = status_opts[choice_status]
                save_json_data(db)
                print(f"\nStatus updated to '{status_opts[choice_status]}' for {student_data.get('name')}!")
            else:
                print("\nInvalid status modification parameters.")
            wait_for_return()
        else:
            print(f"\nInvalid selection key index mapping sequence.")
            wait_for_return()
            clear_screen()

def add_cash():
    while True:
        clear_screen()
        print("======== Fine / Append Cash Surcharges ========\n")
        db = load_json_data()
        students = db.get("students", {})
        
        if not students:
            print("No student records found.")
            wait_for_return()
            return
        
        student_mapping = {}
        for idx, (student_id, s) in enumerate(students.items(), start=1):
            student_mapping[str(idx)] = student_id
            print(f"{idx}) Name: {s.get('name', student_id):<15} | Pending Owed: Rs.{s.get('pending_amount', 0.0):<10}💰")
            
        print("\n===============================")
        choice_num = input("Enter Num Of Student To Add Cash Or Q To Quit: ").strip().lower()
        if choice_num == 'q':
            break
            
        if choice_num in student_mapping:
            target_id = student_mapping[choice_num]
            student_data = students[target_id]
            
            try:
                amount_to_add = float(input(f"Enter invoice fine amount to add to {student_data.get('name', target_id)}: Rs."))
                student_data["total_cost"] = float(student_data.get("total_cost", 0.0)) + amount_to_add
                student_data["discounted_value"] = float(student_data.get("discounted_value", 0.0)) + amount_to_add
                student_data["pending_amount"] = max(0.0, float(student_data.get("pending_amount", 0.0)) + amount_to_add)
                
                save_json_data(db)
                print(f"\nAdded Rs.{amount_to_add} to balance ledger successfully. ✅")
                
                export_choice = input("Export modified fine balance log event index item to CSV? (y/n): ").strip().lower()
                if export_choice == 'y':
                    export_to_csv(f"fine_surcharge_{target_id}", ["Target Profile Account", "Surcharge Processing Amount Debited"], [[target_id, amount_to_add]])
            except ValueError:
                print("\nInvalid numerical values processed.")
            wait_for_return()
        else:
            print(f"\nInvalid student row selection entry point.")        
            wait_for_return()
            clear_screen()

def given_pending_amount(): 
    clear_screen()
    print("======== Given/Pending Amounts Ledger ========\n")
    db = load_json_data()
    students = db.get("students", {})
    
    if not students:
        print("No student records found.")
        wait_for_return()
        clear_screen()
        return
    
    rows = []
    for name, info in students.items():
        total = float(info.get("total_cost", 0.0))
        discounted = float(info.get("discounted_value", 0.0))
        pending = float(info.get("pending_amount", 0.0))
        given = max(0.0, discounted - pending)
        print(f"Name:{name:<14} | Given:{given:<10.2f} | Pending:{pending:<14.2f} | Total:{total:<10.2f}")
        rows.append([name, given, pending, total])
    
    export_choice = input("\nExport entire system liquidity status ledger checklist metrics array to CSV? (y/n): ").strip().lower()
    if export_choice == 'y':
        export_to_csv("general_accounts_receivable_roster", ["Account Name ID", "Actual Liquid Assets Gathered", "Outstanding Liquidity Invoiced Unpaid", "Gross Aggregated Asset Valuation"], rows)
        
    wait_for_return()
    clear_screen()

def export_csv():
    clear_screen()
    print("======== Master Core Roster File Export System ========\n")
    db = load_json_data()
    students = db.get("students", {})
    
    if not students:
        print("No student records found to export.")
        wait_for_return()
        clear_screen()
        return
        
    target_path = export_students_to_csv(students)
    print(f"Data successfully exported to master dump target directory line: {target_path} ✅")
    wait_for_return()
    clear_screen()

def thesis_status_manager():
    while True:
        clear_screen()
        print("======== Thesis Status Manager ========\n")
        db = load_json_data()
        students = db.get("students", {})

        if not students:
            print("No student records found in the database system.")
            wait_for_return()
            return

        print(f"    {'Name':<14} | {'Delivered':<10} | {'Not Delivered':<14} | {'Pending Amount':<15} | {'Given Amount':<13} | {'Total Cost':<11}")
        print("    " + "-" * 95)
        student_mapping = {}

        for idx, (student_id, s) in enumerate(students.items(), start=1):
            student_mapping[str(idx)] = student_id 
            name_str = s.get("name", student_id).title()
            is_delivered = s.get("thesis_delivered", False)
            delivered_emoji = "✅" if is_delivered else "❌"
            print(f"{idx:2}) {name_str:<14} | {delivered_emoji:<10} | {'Yes' if is_delivered else 'No':<14} | Rs.{s.get('pending_amount', 0.0):<14.2f} | Rs.{max(0.0, float(s.get('discounted_value', 0.0)) - float(s.get('pending_amount', 0.0))):<12.2f} | Rs.{s.get('discounted_value', 0.0):<10.2f} | {s.get('total_cost', 0.0):<10.2f}")
        print("==============================================")
        choice_num = input("Enter Student Num To Toggle Delivery Status (or 'e' to export list, 'q' to return): ").strip().lower()
        if choice_num == 'q':
            clear_screen()
            return
        elif choice_num == 'e':
            export_to_csv("thesis_delivery_status_report", ["Student Name", "Thesis Delivered"], [[s.get("name", sid), "Yes" if s.get("thesis_delivered", False) else "No"] for sid, s in students.items()])
            wait_for_return()
            continue
        if choice_num in student_mapping:
            target_id = student_mapping[choice_num]
            current_state = db["students"][target_id].get("thesis_delivered", False)
            db["students"][target_id]["thesis_delivered"] = not current_state
            save_json_data(db)
            sync_json_to_txt()
        else:
            print(f"\nInvalid selection index mapping reference.")
            wait_for_return()

        clear_screen()    

def thesis_delivery_manager():
    while True:
        clear_screen()
        print("======== Thesis Delivery & Payment Status Matrix ========\n")
        db = load_json_data()
        students = db.get("students", {})

        if not students:
            print("No student records found in the database system.")
            wait_for_return()
            return

        print(f"    {'Name':<14} | {'Total':<7} | {'Given':<7} | {'Pending':<8} | {'Thesis Delivered':<16} | {'Status':<10}")
        print("    " + "-" * 73)
        
        student_mapping = {}
        delivered_count = 0
        pending_count = 0
        rows = []
        
        for idx, (student_id, s) in enumerate(students.items(), start=1):
            student_mapping[str(idx)] = student_id 
            name_str = s.get("name", student_id).title()
            total_val = float(s.get("total_amount", 0.0))
            pending_val = float(s.get("pending_amount", 0.0))
            given_val = max(0.0, float(total_val) - float(pending_val))
            
            is_delivered = s.get("thesis_delivered", False)
            if is_delivered: delivered_count += 1
            else: pending_count += 1
                
            delivered_emoji = "✅" if is_delivered else "❌"
            print(f"{idx:2}) {name_str:<14} | {int(total_val):<7} | {int(given_val):<7} | {int(pending_val):<8} | {delivered_emoji:<16} | {s.get('status', 'unknown'):<10}")
            rows.append([name_str, total_val, given_val, pending_val, "Yes" if is_delivered else "No", s.get('status', 'unknown')])
            
        print(f"\nDelivered To: {delivered_count} | Pending Delivery: {pending_count}")
        print("=========================================================================")
        choice_num = input("Enter Student Num To Toggle (or 'e' to export summary list, 'q' to return): ").strip().lower()
        
        if choice_num == 'q':
            clear_screen()
            return
        elif choice_num == 'e':
            export_to_csv("logistics_and_delivery_schedule", ["Profile Identity", "Contract Pricing Metric", "Capital Capital Gathered", "Outstanding Invoice Accounts", "Delivery Dispatch Matrix Marker", "Milestone Progress Status"], rows)
            wait_for_return()
            continue
        
        if choice_num in student_mapping:
            target_id = student_mapping[choice_num]
            current_state = db["students"][target_id].get("thesis_delivered", False)
            db["students"][target_id]["thesis_delivered"] = not current_state
            save_json_data(db)
            sync_json_to_txt()
        else:
            print(f"\nInvalid collection mapping reference grid coordinate.")
            wait_for_return()

def exit_program():
    print('\nSynchronizing tracking structures... Exiting safely. GoodBye! 👋')
    sys.exit()

def main_function():
    sync_json_to_txt()
    while True:
        try:
            print(f"{'='*110:^110}")
            print(f"{'======================= Student Thesis Manager Engine =======================':^110}")
            print(f'\n1) {'Add Data':<24} | 2) {'View Data':<24}  | 3) {'Delete Specific':<24} | 4) {'Delete All':<24}')
            print(f'5) {'View Overall Cost':<24} | 6) {'Combine Students':<24}  | 7) {'Apply Discount':<24} | 8) {'View Specific Costs':<24}')
            print(f'9) {'Calculate Profit':<24} | 10) {'Payment Stats':<24} | 11) {'Show Status':<24}| 12) {'Add Cash':<24}')
            print(f"13) {'Given/Pending Amounts':<24}| 14) {'Export CSV':<24} | 15) {'TD Manager':<24}")
            print(f"16) {'Thesis Status Manager':<24}| 17) {'Exit Program':<24}")
            print(f"{'='*110:^110}")
            
            choice = input('\nChoose Configuration Entry Point Target (1-16): ').strip()
            menu_actions = {
                '1': add_thesis_data, '2': view_thesis_data,
                '3': delete_specific_student_thesis_data, '4': delete_all_thesis_data,
                '5': view_overall_cost, '6': combine_student_by_name,
                '7': discount_specific_student, '8': view_cost_of_specific_students,
                '9': calculate_profit, '10': payment_stats, '11': show_status,
                '12': add_cash, '13': given_pending_amount, '14': export_csv,
                '15': thesis_delivery_manager, '16': thesis_status_manager, '17': exit_program
            }

            if choice in menu_actions:
                menu_actions[choice]()
            else:
                print("\n❌ System Selection Index Range Mismatch. Enter valid parameters (1-16).")
                # Main menu invalid action trap requires deliberate action to cycle screen layout loop cleanly
                input("Press Enter to refresh main screen options display console panel matrix...")
                clear_screen()
        except Exception as e:
            print(f"An unexpected loop breakdown error occurred: {e}")
            input("Press Enter to continue layout cycle reboot routines...")
            clear_screen()

if __name__ == '__main__':
    main_function()            