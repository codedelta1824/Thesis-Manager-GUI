import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from src.config import EXPORTS_DIR
from src.core import calculate_thesis_costs, process_financial_metrics
from src.exporter import export_financial_report_csv, export_students_to_csv
from src.storage import load_json_data, save_json_data, sync_json_to_txt


class ThesisManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thesis Manager Pro")
        self.root.geometry("1580x920")
        self.root.minsize(1420, 860)
        self.root.configure(bg="#000001")

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._configure_styles()

        self.db = load_json_data()
        self._build_ui()
        self._show_view("add_data")
        self._start_clock()

    def _configure_styles(self):
        self.style.configure("TFrame", background="#000000")
        self.style.configure("Card.TFrame", background="#111827", relief="flat")
        self.style.configure("Sidebar.TFrame", background="#0b1220")
        self.style.configure("TLabelframe", background="#111827", foreground="#f8fafc")
        self.style.configure("TLabelframe.Label", background="#111827", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.configure("TLabel", background="#111827", foreground="#f8fafc")
        self.style.configure("Heading.TLabel", background="#111827", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        self.style.configure("Subheading.TLabel", background="#111827", foreground="#707c8e", font=("Segoe UI", 10, "bold"))
        self.style.configure("Body.TLabel", background="#111827", foreground="#e2e8f0", font=("Segoe UI", 13, "bold"))
        self.style.configure("Metric.TLabel", background="#111827", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.configure("Value.TLabel", background="#111827", foreground="#27ad58", font=("Segoe UI", 18, "bold"))
        self.style.configure("Warning.TLabel", background="#111827", foreground="#fbbf24", font=("Segoe UI", 18, "bold"))
        self.style.configure("Danger.TLabel", background="#111827", foreground="#fb7185", font=("Segoe UI", 18, "bold"))
        self.style.configure("Accent.TLabel", background="#111827", foreground="#0e88bc", font=("Segoe UI", 18, "bold"))
        self.style.configure("TButton", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.map("TButton", background=[("active", "#334155")])
        self.style.configure("Primary.TButton", background="#2563eb", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.map("Primary.TButton", background=[("active", "#1d4ed8")])
        self.style.configure("Success.TButton", background="#16a34a", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.map("Success.TButton", background=[("active", "#15803d")])
        self.style.configure("Danger.TButton", background="#dc2626", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.map("Danger.TButton", background=[("active", "#b91c1c")])
        self.style.configure("Sidebar.TButton", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.map("Sidebar.TButton", background=[("active", "#1e293b"), ("selected", "#2563eb")])
        self.style.configure("Treeview", rowheight=30, background="#0f172a", fieldbackground="#0f172a", foreground="#e2e8f0", font=("Segoe UI", 10))
        self.style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])
        self.style.configure("Treeview.Heading", background="#111827", foreground="#f8fafc", relief="flat", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview.Heading", background=[("active", "#1e293b")])

    def _build_ui(self):
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", padding=16)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(1, weight=1)

        ttk.Label(sidebar, text="Thesis Manager", style="Heading.TLabel", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(sidebar, text="Professional operations hub", style="Subheading.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 16))

        self.clock_label = ttk.Label(sidebar, text="--", style="Metric.TLabel", font=("Segoe UI", 13, "bold"))
        self.clock_label.grid(row=2, column=0, sticky="w", pady=(0, 12))

        self.menu_canvas = tk.Canvas(sidebar, bg="#0b1220", highlightthickness=0, height=620)
        self.menu_canvas.grid(row=3, column=0, sticky="nsew")
        self.menu_scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=self.menu_canvas.yview)
        self.menu_scrollbar.grid(row=3, column=1, sticky="ns")
        self.menu_canvas.configure(yscrollcommand=self.menu_scrollbar.set)

        self.menu_frame = ttk.Frame(self.menu_canvas, style="Sidebar.TFrame")
        self.menu_canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.menu_frame.bind("<Configure>", lambda event: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all")))

        self.menu_buttons = {}
        menu_items = [
            ("Add Data", "add_data"),
            ("View Data", "view_data"),
            ("Delete Specific", "delete_specific"),
            ("Delete All", "delete_all"),
            ("View Overall Cost", "view_overall_cost"),
            ("Combine Students", "combine_students"),
            ("Apply Discount", "apply_discount"),
            ("View Specific Costs", "view_specific_costs"),
            ("Calculate Profit", "calculate_profit"),
            ("Payment Stats", "payment_stats"),
            ("Show Status", "show_status"),
            ("Add Cash", "add_cash"),
            ("Given/Pending Amounts", "pending_amounts"),
            ("Export CSV", "export_csv"),
            ("TD Manager", "td_manager"),
            ("Thesis Status Manager", "thesis_status_manager"),
            ("Exit Program", "exit_program"),
        ]

        for index, (label, value) in enumerate(menu_items):
            button = ttk.Button(self.menu_frame, text=label, style="Sidebar.TButton", command=lambda v=value: self._show_view(v))
            button.grid(row=index, column=0, sticky="ew", pady=2)
            self.menu_buttons[value] = button

        main = ttk.Frame(self.root, style="Card.TFrame", padding=18)
        main.grid(row=0, column=1, sticky="nsew", padx=(10, 12), pady=12)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        self.header_label = ttk.Label(main, text="Operations Center", style="Heading.TLabel")
        self.header_label.grid(row=0, column=0, sticky="w")
        self.subheader_label = ttk.Label(main, text="Manage thesis work with a polished dark interface", style="Subheading.TLabel")
        self.subheader_label.grid(row=1, column=0, sticky="w", pady=(4, 10))

        self.content_frame = ttk.Frame(main, style="Card.TFrame")
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

    def _start_clock(self):
        self._update_clock()

    def _update_clock(self):
        now = datetime.now().strftime("%A, %d %b %Y  •  %H:%M:%S")
        self.clock_label.configure(text=now)
        self.root.after(1000, self._update_clock)

    def _show_view(self, view_name):
        self.db = load_json_data()
        for key, button in self.menu_buttons.items():
            button.state(["!selected"])
        if view_name in self.menu_buttons:
            self.menu_buttons[view_name].state(["selected"])

        for child in self.content_frame.winfo_children():
            child.destroy()

        titles = {
            "add_data": ("Add Thesis Record", "Capture a new thesis request with pricing and discount logic."),
            "view_data": ("Student Ledger Viewer", "Inspect all stored records and export the raw data."),
            "delete_specific": ("Delete a Student Record", "Remove one thesis entry cleanly from the workspace."),
            "delete_all": ("Delete All Records", "Clear the full thesis registry with a confirmation guard."),
            "view_overall_cost": ("Financial Overview", "Review totals, pending amounts, and delivered status at a glance."),
            "combine_students": ("Combine Student Accounts", "Merge two student profiles into one unified record."),
            "apply_discount": ("Apply Discount", "Adjust the discounted value and remaining balance for a student."),
            "view_specific_costs": ("Specific Student Cost Inquiry", "Inspect selected students in a focused ledger view."),
            "calculate_profit": ("Profit and Expense Engine", "Track expenses, calculate profit, and export financial reports."),
            "payment_stats": ("Payment Statistics", "Log payments, set pending balances, and review cash flow."),
            "show_status": ("Status Manager", "Update each thesis status with a clear production state."),
            "add_cash": ("Add Fine / Cash Adjustment", "Increase a student balance with an additional surcharge."),
            "pending_amounts": ("Given and Pending Amounts", "Monitor collected funds and open balances by student."),
            "export_csv": ("CSV Export Center", "Export student and financial data into spreadsheet-ready files."),
            "td_manager": ("Delivery Manager", "Toggle thesis delivery status and review delivery progress."),
            "thesis_status_manager": ("Thesis Status Manager", "Manage milestone progression with professional status controls."),
            "exit_program": ("System Exit", "Close the thesis manager safely."),
        }
        title, subtitle = titles.get(view_name, ("Operations Center", ""))
        self.header_label.configure(text=title)
        self.subheader_label.configure(text=subtitle)

        builder = getattr(self, f"_build_{view_name}_view", None)
        if builder is None:
            self._build_overview_view(self.content_frame)
        else:
            builder(self.content_frame)

    def _build_overview_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)

        summary = ttk.Frame(body, style="Card.TFrame", padding=14)
        summary.pack(fill="x", pady=(0, 12))
        summary.columnconfigure((0, 1, 2, 3), weight=1)

        metric_specs = [
            ("Students", "0", "#38bdf8"),
            ("Revenue", "Rs.0", "#4ade80"),
            ("Pending", "Rs.0", "#fbbf24"),
            ("Profit", "Rs.0", "#fb7185"),
        ]
        self.metrics = {}
        for index, (title, default, color) in enumerate(metric_specs):
            card = ttk.Frame(summary, style="Card.TFrame", padding=12)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 0))
            ttk.Label(card, text=title, style="Metric.TLabel").grid(row=0, column=0, sticky="w")
            value_label = ttk.Label(card, text=default, foreground=color, font=("Segoe UI", 20, "bold"))
            value_label.grid(row=1, column=0, sticky="w", pady=(6, 0))
            self.metrics[title] = value_label

        mid = ttk.Frame(body, style="Card.TFrame")
        mid.pack(fill="both", expand=True)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        mid.rowconfigure(0, weight=1)

        ledger_frame = ttk.LabelFrame(mid, text="Student Ledger", padding=12)
        ledger_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ledger_frame.columnconfigure(0, weight=1)
        ledger_frame.rowconfigure(0, weight=1)

        columns = ("name", "quantity", "pages", "total", "pending", "status")
        self.tree = ttk.Treeview(ledger_frame, columns=columns, show="headings", height=14)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.heading("name", text="Student")
        self.tree.heading("quantity", text="Qty")
        self.tree.heading("pages", text="Pages")
        self.tree.heading("total", text="Total")
        self.tree.heading("pending", text="Pending")
        self.tree.heading("status", text="Status")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("quantity", width=80, anchor="center")
        self.tree.column("pages", width=90, anchor="center")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("pending", width=120, anchor="e")
        self.tree.column("status", width=120, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_student)

        xscroll = ttk.Scrollbar(ledger_frame, orient="horizontal", command=self.tree.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=xscroll.set)
        yscroll = ttk.Scrollbar(ledger_frame, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        right = ttk.Frame(mid, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        detail_frame = ttk.LabelFrame(right, text="Selected Record", padding=12)
        detail_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        self.detail_text = tk.Text(detail_frame, height=10, bg="#0f172a", fg="#e2e8f0", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 11))
        self.detail_text.grid(row=0, column=0, sticky="nsew")
        self.detail_text.configure(state="disabled")

        chart_frame = ttk.LabelFrame(right, text="Revenue Overview", padding=12)
        chart_frame.grid(row=1, column=0, sticky="nsew")
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        self.chart_canvas = tk.Canvas(chart_frame, bg="#0f172a", highlightthickness=0)
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")

        self.refresh_dashboard()

    def _build_add_data_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)

        form = ttk.LabelFrame(body, text="New Thesis Entry", padding=16)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        self.add_form_vars = {}
        fields = [
            ("Student Name", "name"),
            ("Thesis Quantity", "quantity"),
            ("Pages Per Book", "pages"),
            ("Printing Choice", "printing"),
            ("Binding Choice", "binding"),
            ("Discount", "discount"),
        ]
        row = 0
        for label_text, key in fields:
            ttk.Label(form, text=label_text, style="Body.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 12), pady=8)
            if key == "printing":
                var = tk.StringVar(value="10rs / 80gsm")
                combo = ttk.Combobox(form, textvariable=var, state="readonly", values=["10rs / 80gsm", "8rs / 70gsm"], width=28)
                combo.grid(row=row, column=1, sticky="ew", pady=8)
                self.add_form_vars[key] = var
            elif key == "binding":
                var = tk.StringVar(value="Thesis Binding")
                combo = ttk.Combobox(form, textvariable=var, state="readonly", values=["Thesis Binding", "Spiral Binding"], width=28)
                combo.grid(row=row, column=1, sticky="ew", pady=8)
                self.add_form_vars[key] = var
            else:
                var = tk.StringVar()
                ttk.Entry(form, textvariable=var, width=30, font=("Segoe UI", 11)).grid(row=row, column=1, sticky="ew", pady=8)
                self.add_form_vars[key] = var
            row += 1

        ttk.Button(form, text="Save Thesis Record", style="Primary.TButton", command=self._save_record_gui).grid(row=row, column=0, columnspan=2, sticky="ew", pady=(14, 0))

    def _build_view_data_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Stored Thesis Data", padding=14)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        self.view_text = tk.Text(panel, bg="#0f172a", fg="#e2e8f0", relief="flat", font=("Segoe UI", 11))
        self.view_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.view_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.view_text.configure(yscrollcommand=scrollbar.set)
        ttk.Button(panel, text="Refresh Ledger", style="Success.TButton", command=self._refresh_view_data).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self._refresh_view_data()

    def _build_delete_specific_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Remove One Student Record", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text="Student Name", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)
        self.delete_name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.delete_name_var, width=35, font=("Segoe UI", 11)).grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Button(panel, text="Delete Record", style="Danger.TButton", command=self._delete_specific_record).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(14, 0))

    def _build_delete_all_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Danger Zone", padding=20)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="This action permanently removes all thesis records and supporting data from the system.", style="Body.TLabel", wraplength=650, justify="left").pack(anchor="w", pady=(0, 16))
        ttk.Label(panel, text="Use this only when you want a full reset.", style="Warning.TLabel").pack(anchor="w", pady=(0, 16))
        ttk.Button(panel, text="Delete All Records", style="Danger.TButton", command=self._delete_all_records).pack(fill="x")

    def _build_view_overall_cost_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Financial Summary", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure((0, 1, 2, 3), weight=1)

        self.overall_cards = {}
        for index, (title, value, color) in enumerate([("Students", "0", "#38bdf8"), ("Revenue", "Rs.0", "#4ade80"), ("Pending", "Rs.0", "#fbbf24"), ("Profit", "Rs.0", "#fb7185")]):
            card = ttk.Frame(panel, style="Card.TFrame", padding=12)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 0))
            ttk.Label(card, text=title, style="Metric.TLabel").grid(row=0, column=0, sticky="w")
            label = ttk.Label(card, text=value, foreground=color, font=("Segoe UI", 18, "bold"))
            label.grid(row=1, column=0, sticky="w", pady=(6, 0))
            self.overall_cards[title] = label

        details = tk.Text(panel, height=14, bg="#0f172a", fg="#e2e8f0", relief="flat", font=("Segoe UI", 11))
        details.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        panel.rowconfigure(1, weight=1)
        ttk.Button(panel, text="Export Financial Report", style="Primary.TButton", command=self._export_financial_report).grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self._refresh_overall_cost_view(details)

    def _build_combine_students_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Merge Student Records", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text="Merge From", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)
        self.combine_from_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.combine_from_var, width=35, font=("Segoe UI", 11)).grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Label(panel, text="Merge Into", style="Body.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=8)
        self.combine_into_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.combine_into_var, width=35, font=("Segoe UI", 11)).grid(row=1, column=1, sticky="ew", pady=8)
        ttk.Button(panel, text="Merge Records", style="Primary.TButton", command=self._combine_students).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))

    def _build_apply_discount_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Discount Adjustment", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text="Student", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)
        self.discount_student_var = tk.StringVar()
        self.discount_student_combo = ttk.Combobox(panel, textvariable=self.discount_student_var, state="readonly", width=28)
        self.discount_student_combo.grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Label(panel, text="Discount Amount", style="Body.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=8)
        self.discount_amount_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.discount_amount_var, width=35, font=("Segoe UI", 11)).grid(row=1, column=1, sticky="ew", pady=8)
        ttk.Button(panel, text="Apply Discount", style="Primary.TButton", command=self._apply_discount).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self._populate_student_combo(self.discount_student_combo)

    def _build_view_specific_costs_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Targeted Cost Review", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text="Student Names", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)
        self.specific_names_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.specific_names_var, width=45, font=("Segoe UI", 11)).grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Button(panel, text="Show Student Costs", style="Success.TButton", command=self._show_specific_costs).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.specific_result = tk.Text(panel, height=16, bg="#0f172a", fg="#e2e8f0", relief="flat", font=("Segoe UI", 11))
        self.specific_result.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        panel.rowconfigure(2, weight=1)

    def _build_calculate_profit_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Finance Operations", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        buttons = ttk.Frame(panel, style="Card.TFrame")
        buttons.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for text, cmd in [
            ("Add Expense", self._add_misc_expense),
            ("View Breakdown", self._show_expense_breakdown),
            ("P&L Statement", self._show_profit_statement),
            ("Cash Account", self._show_cash_account),
            ("Clear Expenses", self._clear_expenses),
            ("Export Report", self._export_financial_report),
        ]:
            ttk.Button(buttons, text=text, style="Primary.TButton", command=cmd).pack(side="left", padx=4)

        self.profit_output = tk.Text(panel, bg="#0f172a", fg="#e2e8f0", relief="flat", font=("Segoe UI", 11))
        self.profit_output.grid(row=1, column=0, sticky="nsew")
        self._show_expense_breakdown()

    def _build_payment_stats_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Payment Operations", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        action_bar = ttk.Frame(panel, style="Card.TFrame")
        action_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for text, cmd in [
            ("Record Payment", self._record_payment),
            ("Set Pending", self._set_pending),
            ("Remove Student", self._remove_student_payment),
            ("View Stats", self._show_payment_stats),
        ]:
            ttk.Button(action_bar, text=text, style="Primary.TButton", command=cmd).pack(side="left", padx=4)

        self.payment_output = tk.Text(panel, bg="#0f172a", fg="#e2e8f0", relief="flat", font=("Segoe UI", 11))
        self.payment_output.grid(row=1, column=0, sticky="nsew")
        self._show_payment_stats()

    def _build_show_status_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Status Control", padding=14)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        columns = ("student", "status")
        self.status_tree = ttk.Treeview(panel, columns=columns, show="headings", height=13)
        self.status_tree.grid(row=0, column=0, sticky="nsew")
        self.status_tree.heading("student", text="Student")
        self.status_tree.heading("status", text="Status")
        self.status_tree.column("student", width=220, anchor="w")
        self.status_tree.column("status", width=140, anchor="center")

        controls = ttk.Frame(panel, style="Card.TFrame", padding=8)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="New Status", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.status_choice_var = tk.StringVar(value="pending")
        ttk.Combobox(controls, textvariable=self.status_choice_var, state="readonly", values=["checked", "unchecked", "pending"], width=18).grid(row=0, column=1, sticky="ew")
        ttk.Button(controls, text="Update Status", style="Success.TButton", command=self._update_status).grid(row=0, column=2, padx=(8, 0))
        self._refresh_status_tree()

    def _build_add_cash_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Cash Adjustment", padding=16)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text="Student", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)
        self.cash_student_var = tk.StringVar()
        self.cash_student_combo = ttk.Combobox(panel, textvariable=self.cash_student_var, state="readonly", width=28)
        self.cash_student_combo.grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Label(panel, text="Amount", style="Body.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=8)
        self.cash_amount_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.cash_amount_var, width=35, font=("Segoe UI", 11)).grid(row=1, column=1, sticky="ew", pady=8)
        ttk.Button(panel, text="Add Cash Adjustment", style="Primary.TButton", command=self._add_cash_adjustment).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self._populate_student_combo(self.cash_student_combo)

    def _build_pending_amounts_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Collected vs Pending", padding=14)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        columns = ("student", "given", "pending", "total")
        self.pending_tree = ttk.Treeview(panel, columns=columns, show="headings", height=15)
        self.pending_tree.grid(row=0, column=0, sticky="nsew")
        for heading, width in [("student", 220), ("given", 140), ("pending", 140), ("total", 140)]:
            self.pending_tree.heading(heading, text=heading.title())
            self.pending_tree.column(heading, width=width, anchor="e")
        ttk.Button(panel, text="Export Ledger", style="Success.TButton", command=self._export_pending_ledger).grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self._refresh_pending_tree()

    def _build_export_csv_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Spreadsheet Export", padding=20)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="Export the student roster and financial summary into CSV files for bookkeeping and reporting.", style="Body.TLabel", wraplength=700, justify="left").pack(anchor="w", pady=(0, 16))
        ttk.Button(panel, text="Export Student CSV", style="Primary.TButton", command=self._export_data).pack(fill="x", pady=6)
        ttk.Button(panel, text="Export Financial CSV", style="Success.TButton", command=self._export_financial_report).pack(fill="x", pady=6)

    def _build_td_manager_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Delivery Manager", padding=14)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        columns = ("student", "delivered", "pending", "status")
        self.td_tree = ttk.Treeview(panel, columns=columns, show="headings", height=15)
        self.td_tree.grid(row=0, column=0, sticky="nsew")
        self.td_tree.heading("student", text="Student")
        self.td_tree.heading("delivered", text="Delivered")
        self.td_tree.heading("pending", text="Pending")
        self.td_tree.heading("status", text="Status")
        self.td_tree.column("student", width=220, anchor="w")
        self.td_tree.column("delivered", width=120, anchor="center")
        self.td_tree.column("pending", width=120, anchor="center")
        self.td_tree.column("status", width=140, anchor="center")
        ttk.Button(panel, text="Toggle Selected Delivery", style="Success.TButton", command=self._toggle_delivery).grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self._refresh_td_tree()

    def _build_thesis_status_manager_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Thesis Milestones", padding=14)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        columns = ("student", "status")
        self.milestone_tree = ttk.Treeview(panel, columns=columns, show="headings", height=15)
        self.milestone_tree.grid(row=0, column=0, sticky="nsew")
        self.milestone_tree.heading("student", text="Student")
        self.milestone_tree.heading("status", text="Status")
        self.milestone_tree.column("student", width=240, anchor="w")
        self.milestone_tree.column("status", width=160, anchor="center")
        controls = ttk.Frame(panel, style="Card.TFrame", padding=8)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Status", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.milestone_status_var = tk.StringVar(value="pending")
        ttk.Combobox(controls, textvariable=self.milestone_status_var, state="readonly", values=["checked", "unchecked", "pending"], width=18).grid(row=0, column=1, sticky="ew")
        ttk.Button(controls, text="Update Milestone", style="Success.TButton", command=self._update_milestone).grid(row=0, column=2, padx=(8, 0))
        self._refresh_milestone_tree()

    def _build_exit_program_view(self, parent):
        body = ttk.Frame(parent, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        panel = ttk.LabelFrame(body, text="Exit", padding=20)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="Close the thesis manager safely when you are done.", style="Body.TLabel", wraplength=700, justify="left").pack(anchor="w", pady=(0, 16))
        ttk.Button(panel, text="Exit Application", style="Danger.TButton", command=self.root.destroy).pack(fill="x")

    def refresh_dashboard(self):
        self.db = load_json_data()
        self._populate_tree()
        self._update_metrics()
        self._draw_chart()

    def _populate_tree(self):
        if not hasattr(self, "tree"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        students = self.db.get("students", {})
        for name, info in sorted(students.items()):
            self.tree.insert("", "end", values=(
                name.title(),
                info.get("quantity", 0),
                info.get("pages_per_book", 0),
                f"Rs.{float(info.get('total_cost', 0)):.2f}",
                f"Rs.{float(info.get('pending_amount', 0.0)):.2f}",
                str(info.get("status", "unknown")).title(),
            ))

    def _update_metrics(self):
        students = self.db.get("students", {})
        expenses = self.db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)
        if hasattr(self, "metrics"):
            self.metrics["Students"].configure(text=str(len(students)))
            self.metrics["Revenue"].configure(text=f"Rs.{metrics['total_revenue_collected']:.2f}", foreground="#4ade80")
            self.metrics["Pending"].configure(text=f"Rs.{metrics['combined_expenses']:.2f}", foreground="#fbbf24")
            self.metrics["Profit"].configure(text=f"Rs.{metrics['net_profit']:.2f}", foreground="#fb7185")
        if hasattr(self, "overall_cards"):
            self.overall_cards["Students"].configure(text=str(len(students)))
            self.overall_cards["Revenue"].configure(text=f"Rs.{metrics['total_revenue_collected']:.2f}", foreground="#4ade80")
            self.overall_cards["Pending"].configure(text=f"Rs.{metrics['combined_expenses']:.2f}", foreground="#fbbf24")
            self.overall_cards["Profit"].configure(text=f"Rs.{metrics['net_profit']:.2f}", foreground="#fb7185")

    def _draw_chart(self):
        if not hasattr(self, "chart_canvas"):
            return
        canvas = self.chart_canvas
        canvas.delete("all")
        students = self.db.get("students", {})
        if not students:
            canvas.create_text(280, 140, text="No thesis records yet", fill="#8da0bc", font=("Segoe UI", 12))
            return
        values = [float(info.get("total_cost", 0)) for info in students.values()]
        max_value = max(values) if values else 1
        width = 540
        height = 250
        left_margin = 40
        bottom_margin = 34
        gap = 16
        bar_width = 30
        canvas.create_line(left_margin, height - bottom_margin, width + left_margin - 10, height - bottom_margin, fill="#334155", width=2)
        canvas.create_line(left_margin, 20, left_margin, height - bottom_margin, fill="#334155", width=2)
        for idx, value in enumerate(values):
            bar_height = max(8, (value / max_value) * (height - bottom_margin - 14))
            x = left_margin + 18 + idx * (gap + bar_width)
            y = height - bottom_margin - bar_height
            canvas.create_rectangle(x, y, x + bar_width, height - bottom_margin, fill="#38bdf8", outline="#8b5cf6")
            canvas.create_text(x + bar_width / 2, y - 8, text=f"Rs.{value:.0f}", fill="#f8fafc", font=("Segoe UI", 8, "bold"))
        for idx, label in enumerate(list(students.keys())[:len(values)]):
            x = left_margin + 18 + idx * (gap + bar_width)
            canvas.create_text(x + bar_width / 2, height - 10, text=label[:8].title(), fill="#8da0bc", font=("Segoe UI", 8))

    def _on_select_student(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0], "values")
        name = item[0].lower()
        student_info = self.db.get("students", {}).get(name)
        if not student_info:
            return
        content = (
            f"Name: {student_info.get('name', name).title()}\n"
            f"Quantity: {student_info.get('quantity', 0)}\n"
            f"Pages Per Book: {student_info.get('pages_per_book', 0)}\n"
            f"Total Pages: {student_info.get('total_pages', 0)}\n"
            f"Binding Cost: Rs.{student_info.get('binding_cost', 0)}\n"
            f"Total Cost: Rs.{student_info.get('total_cost', 0)}\n"
            f"Discounted Value: Rs.{student_info.get('discounted_value', 0)}\n"
            f"Pending Amount: Rs.{student_info.get('pending_amount', 0.0)}\n"
            f"Status: {student_info.get('status', 'unknown').title()}"
        )
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", content)
        self.detail_text.configure(state="disabled")

    def _save_record_gui(self):
        try:
            name = self.add_form_vars["name"].get().strip().lower()
            quantity = int(self.add_form_vars["quantity"].get())
            pages = int(self.add_form_vars["pages"].get())
            discount = int(self.add_form_vars["discount"].get() or 0)
            printing_choice = 1 if self.add_form_vars["printing"].get() == "10rs / 80gsm" else 2
            binding_choice = 3 if self.add_form_vars["binding"].get() == "Thesis Binding" else 4
            if not name:
                raise ValueError("Student name cannot be empty")
            total_pages, binding_cost, total_cost = calculate_thesis_costs(pages, quantity, printing_choice, binding_choice)
            final_cost = total_cost - discount
            self.db = load_json_data()
            self.db["students"][name] = {
                "name": name,
                "quantity": quantity,
                "pages_per_book": pages + 1,
                "total_pages": total_pages,
                "binding_cost": binding_cost,
                "total_cost": total_cost,
                "discounted_value": final_cost,
                "pending_amount": float(final_cost),
                "status": "unknown",
            }
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            messagebox.showinfo("Saved", f"Record for {name.title()} saved successfully")
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to save thesis record: {exc}")

    def _refresh_view_data(self):
        self.db = load_json_data()
        sync_json_to_txt()
        if hasattr(self, "view_text"):
            self.view_text.delete("1.0", "end")
            self.view_text.insert("1.0", self._render_student_text())

    def _render_student_text(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        if not students:
            return "No thesis student data saved yet."
        lines = []
        for name, info in sorted(students.items()):
            lines.append(f"Name: {name.title()}")
            lines.append(f"Quantity: {info.get('quantity', 0)}")
            lines.append(f"Pages Per Book: {info.get('pages_per_book', 0)}")
            lines.append(f"Total Pages: {info.get('total_pages', 0)}")
            lines.append(f"Binding Cost: Rs.{info.get('binding_cost', 0)}")
            lines.append(f"Total Cost: Rs.{info.get('total_cost', 0)}")
            lines.append(f"Discounted Value: Rs.{info.get('discounted_value', 0)}")
            lines.append(f"Pending Amount: Rs.{info.get('pending_amount', 0.0)}")
            lines.append(f"Status: {info.get('status', 'unknown').title()}\n")
        return "\n".join(lines)

    def _delete_specific_record(self):
        name = self.delete_name_var.get().strip().lower()
        if not name:
            messagebox.showwarning("Input Required", "Please enter a student name.")
            return
        self.db = load_json_data()
        if name in self.db.get("students", {}):
            self.db["students"].pop(name)
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            messagebox.showinfo("Deleted", f"{name.title()} was removed.")
        else:
            messagebox.showwarning("Not Found", f"No record found for {name.title()}.")

    def _delete_all_records(self):
        if messagebox.askyesno("Confirm Reset", "Delete every thesis record permanently?"):
            self.db = load_json_data()
            self.db["students"] = {}
            self.db["expenses"] = {}
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            messagebox.showinfo("Reset Complete", "The thesis database has been cleared.")

    def _refresh_overall_cost_view(self, text_widget):
        self.db = load_json_data()
        students = self.db.get("students", {})
        expenses = self.db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)
        summary = [
            f"Total Students: {len(students)}",
            f"Revenue Collected: Rs.{metrics['total_revenue_collected']:.2f}",
            f"Binding Expense: Rs.{metrics['total_binding_expense']:.2f}",
            f"Paper Expense: Rs.{metrics['total_paper_expense']:.2f}",
            f"Miscellaneous Expenses: Rs.{metrics['total_misc_expenses']:.2f}",
            f"Combined Expenses: Rs.{metrics['combined_expenses']:.2f}",
            f"Net Profit: Rs.{metrics['net_profit']:.2f}",
            f"Material Usage: {metrics['consumption_str']}",
        ]
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", "\n".join(summary))

    def _combine_students(self):
        source = self.combine_from_var.get().strip().lower()
        target = self.combine_into_var.get().strip().lower()
        if not source or not target:
            messagebox.showwarning("Input Required", "Enter both source and target names.")
            return
        self.db = load_json_data()
        students = self.db.get("students", {})
        if source not in students or target not in students:
            messagebox.showwarning("Not Found", "Both student names must already exist.")
            return
        if source == target:
            messagebox.showwarning("Invalid Merge", "Source and target cannot be the same.")
            return
        source_data = students[source]
        target_data = students[target]
        target_data["quantity"] = int(source_data.get("quantity", 0)) + int(target_data.get("quantity", 0))
        target_data["total_pages"] = int(source_data.get("total_pages", 0)) + int(target_data.get("total_pages", 0))
        target_data["binding_cost"] = float(source_data.get("binding_cost", 0)) + float(target_data.get("binding_cost", 0))
        target_data["total_cost"] = float(source_data.get("total_cost", 0)) + float(target_data.get("total_cost", 0))
        target_data["discounted_value"] = float(source_data.get("discounted_value", 0)) + float(target_data.get("discounted_value", 0))
        target_data["pending_amount"] = float(source_data.get("pending_amount", 0)) + float(target_data.get("pending_amount", 0))
        students.pop(source)
        save_json_data(self.db)
        sync_json_to_txt()
        self.refresh_dashboard()
        messagebox.showinfo("Merge Complete", f"Records merged into {target.title()}.")

    def _apply_discount(self):
        student = self.discount_student_var.get().strip().lower()
        try:
            amount = float(self.discount_amount_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Value", "Please enter a numeric discount.")
            return
        self.db = load_json_data()
        if student not in self.db.get("students", {}):
            messagebox.showwarning("Not Found", "Student not found.")
            return
        student_data = self.db["students"][student]
        original_total = float(student_data.get("total_cost", 0.0))
        new_discounted = max(0.0, original_total - amount)
        student_data["discounted_value"] = new_discounted
        student_data["pending_amount"] = max(0.0, new_discounted)
        save_json_data(self.db)
        sync_json_to_txt()
        self.refresh_dashboard()
        messagebox.showinfo("Discount Applied", f"Discount applied for {student.title()}.")

    def _show_specific_costs(self):
        names = [item.strip().lower() for item in self.specific_names_var.get().split(",") if item.strip()]
        if not names:
            messagebox.showwarning("Input Required", "Enter one or more names separated by commas.")
            return
        self.db = load_json_data()
        students = self.db.get("students", {})
        lines = []
        for name in names:
            info = students.get(name)
            if info:
                lines.append(f"{name.title()} -> Total: Rs.{info.get('total_cost', 0)} | Pending: Rs.{info.get('pending_amount', 0.0)}")
            else:
                lines.append(f"{name.title()} -> No record found")
        self.specific_result.delete("1.0", "end")
        self.specific_result.insert("1.0", "\n".join(lines))

    def _add_misc_expense(self):
        try:
            name = simpledialog("Expense Name", "Enter an expense label")
            amount = float(simpledialog("Expense Amount", "Enter amount"))
            if name and amount:
                self.db = load_json_data()
                self.db.setdefault("expenses", {})[name] = self.db["expenses"].get(name, 0.0) + amount
                save_json_data(self.db)
                sync_json_to_txt()
                self.refresh_dashboard()
                self._show_expense_breakdown()
                messagebox.showinfo("Expense Added", f"{name} saved.")
        except Exception:
            pass

    def _show_expense_breakdown(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        expenses = self.db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)
        text = [
            f"Binding Costs: Rs.{metrics['total_binding_expense']:.2f}",
            f"Paper Costs: Rs.{metrics['total_paper_expense']:.2f}",
            f"Miscellaneous Expenses: Rs.{metrics['total_misc_expenses']:.2f}",
            f"Combined Expenditures: Rs.{metrics['combined_expenses']:.2f}",
            f"Material Consumption: {metrics['consumption_str']}",
            "",
            "Expense List:",
        ]
        for name, amount in expenses.items():
            text.append(f"- {name}: Rs.{amount:.2f}")
        if hasattr(self, "profit_output"):
            self.profit_output.delete("1.0", "end")
            self.profit_output.insert("1.0", "\n".join(text))

    def _show_profit_statement(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        expenses = self.db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)
        text = [
            "Profit and Loss Statement",
            f"Revenue Collected: Rs.{metrics['total_revenue_collected']:.2f}",
            f"Binding Expenses: Rs.{metrics['total_binding_expense']:.2f}",
            f"Paper Costs: Rs.{metrics['total_paper_expense']:.2f}",
            f"Operational Expenses: Rs.{metrics['total_misc_expenses']:.2f}",
            f"Net Profit: Rs.{metrics['net_profit']:.2f}",
        ]
        if hasattr(self, "profit_output"):
            self.profit_output.delete("1.0", "end")
            self.profit_output.insert("1.0", "\n".join(text))

    def _show_cash_account(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        expenses = self.db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)
        text = [
            "Cash Account Ledger",
            f"Receipts: Rs.{metrics['total_revenue_collected']:.2f}",
            f"Outgoings: Rs.{metrics['combined_expenses']:.2f}",
            f"Net Cash Balance: Rs.{metrics['net_profit']:.2f}",
        ]
        if hasattr(self, "profit_output"):
            self.profit_output.delete("1.0", "end")
            self.profit_output.insert("1.0", "\n".join(text))

    def _clear_expenses(self):
        if messagebox.askyesno("Clear Expenses", "Remove all recorded misc expenses?"):
            self.db = load_json_data()
            self.db["expenses"] = {}
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            self._show_expense_breakdown()
            messagebox.showinfo("Cleared", "Expenses cleared.")

    def _record_payment(self):
        name = self._prompt_for_name("Student Name")
        if not name:
            return
        try:
            amount = float(self._prompt_for_value("Received Amount"))
        except Exception:
            return
        self.db = load_json_data()
        if name in self.db.get("students", {}):
            current = float(self.db["students"][name].get("pending_amount", 0.0))
            self.db["students"][name]["pending_amount"] = max(0.0, current - amount)
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            self._show_payment_stats()
            messagebox.showinfo("Payment Logged", f"Rs.{amount:.2f} applied to {name.title()}.")
        else:
            messagebox.showwarning("Not Found", "Student was not found.")

    def _set_pending(self):
        name = self._prompt_for_name("Student Name")
        if not name:
            return
        try:
            amount = float(self._prompt_for_value("Pending Amount"))
        except Exception:
            return
        self.db = load_json_data()
        if name not in self.db.get("students", {}):
            self.db["students"][name] = {"name": name, "quantity": 0, "pages_per_book": 0, "total_pages": 0, "binding_cost": 0, "total_cost": 0, "discounted_value": amount, "pending_amount": amount, "status": "unknown"}
        else:
            self.db["students"][name]["pending_amount"] = amount
        save_json_data(self.db)
        sync_json_to_txt()
        self.refresh_dashboard()
        self._show_payment_stats()

    def _remove_student_payment(self):
        name = self._prompt_for_name("Student Name")
        if not name:
            return
        self.db = load_json_data()
        if name in self.db.get("students", {}):
            self.db["students"].pop(name)
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            self._show_payment_stats()
        else:
            messagebox.showwarning("Not Found", "Student not found.")

    def _show_payment_stats(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        lines = ["Current Payment Overview"]
        for name, info in sorted(students.items()):
            lines.append(f"- {name.title()}: Pending Rs.{float(info.get('pending_amount', 0.0)):.2f}")
        if hasattr(self, "payment_output"):
            self.payment_output.delete("1.0", "end")
            self.payment_output.insert("1.0", "\n".join(lines))

    def _refresh_status_tree(self):
        if not hasattr(self, "status_tree"):
            return
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        students = self.db.get("students", {})
        for name, info in sorted(students.items()):
            self.status_tree.insert("", "end", values=(name.title(), str(info.get("status", "unknown")).title()))

    def _update_status(self):
        selection = self.status_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Required", "Choose a student first.")
            return
        name = self.status_tree.item(selection[0], "values")[0].lower()
        self.db = load_json_data()
        if name in self.db.get("students", {}):
            self.db["students"][name]["status"] = self.status_choice_var.get()
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            self._refresh_status_tree()
            messagebox.showinfo("Updated", f"Status updated for {name.title()}.")

    def _populate_student_combo(self, combo):
        self.db = load_json_data()
        names = [name.title() for name in self.db.get("students", {}).keys()]
        combo["values"] = names

    def _add_cash_adjustment(self):
        name = self.cash_student_var.get().strip().lower()
        if not name:
            messagebox.showwarning("Input Required", "Choose a student first.")
            return
        try:
            amount = float(self.cash_amount_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Value", "Enter a valid amount.")
            return
        self.db = load_json_data()
        if name not in self.db.get("students", {}):
            messagebox.showwarning("Not Found", "Student not found.")
            return
        student_data = self.db["students"][name]
        student_data["total_cost"] = float(student_data.get("total_cost", 0.0)) + amount
        student_data["discounted_value"] = float(student_data.get("discounted_value", 0.0)) + amount
        student_data["pending_amount"] = max(0.0, float(student_data.get("pending_amount", 0.0)) + amount)
        save_json_data(self.db)
        sync_json_to_txt()
        self.refresh_dashboard()
        messagebox.showinfo("Adjusted", f"Rs.{amount:.2f} added to {name.title()}.")

    def _refresh_pending_tree(self):
        if not hasattr(self, "pending_tree"):
            return
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        students = self.db.get("students", {})
        for name, info in sorted(students.items()):
            total = float(info.get("total_cost", 0.0))
            discounted = float(info.get("discounted_value", 0.0))
            pending = float(info.get("pending_amount", 0.0))
            given = max(0.0, discounted - pending)
            self.pending_tree.insert("", "end", values=(name.title(), f"Rs.{given:.2f}", f"Rs.{pending:.2f}", f"Rs.{total:.2f}"))

    def _export_pending_ledger(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        rows = []
        for name, info in sorted(students.items()):
            total = float(info.get("total_cost", 0.0))
            discounted = float(info.get("discounted_value", 0.0))
            pending = float(info.get("pending_amount", 0.0))
            given = max(0.0, discounted - pending)
            rows.append([name, given, pending, total])
        export_path = export_students_to_csv(students, filename="pending_amounts_export.csv")
        messagebox.showinfo("Exported", f"Pending ledger exported to {export_path}")

    def _refresh_td_tree(self):
        if not hasattr(self, "td_tree"):
            return
        for item in self.td_tree.get_children():
            self.td_tree.delete(item)
        students = self.db.get("students", {})
        for name, info in sorted(students.items()):
            delivered = info.get("thesis_delivered", False)
            self.td_tree.insert("", "end", values=(name.title(), "Yes" if delivered else "No", "No" if delivered else "Yes", info.get("status", "unknown").title()))

    def _toggle_delivery(self):
        selection = self.td_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Required", "Choose a student first.")
            return
        name = self.td_tree.item(selection[0], "values")[0].lower()
        self.db = load_json_data()
        if name in self.db.get("students", {}):
            self.db["students"][name]["thesis_delivered"] = not self.db["students"][name].get("thesis_delivered", False)
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            self._refresh_td_tree()
            messagebox.showinfo("Updated", f"Delivery status updated for {name.title()}.")

    def _refresh_milestone_tree(self):
        if not hasattr(self, "milestone_tree"):
            return
        for item in self.milestone_tree.get_children():
            self.milestone_tree.delete(item)
        students = self.db.get("students", {})
        for name, info in sorted(students.items()):
            self.milestone_tree.insert("", "end", values=(name.title(), str(info.get("status", "unknown")).title()))

    def _update_milestone(self):
        selection = self.milestone_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Required", "Choose a student first.")
            return
        name = self.milestone_tree.item(selection[0], "values")[0].lower()
        self.db = load_json_data()
        if name in self.db.get("students", {}):
            self.db["students"][name]["status"] = self.milestone_status_var.get()
            save_json_data(self.db)
            sync_json_to_txt()
            self.refresh_dashboard()
            self._refresh_milestone_tree()
            messagebox.showinfo("Updated", f"Milestone updated for {name.title()}.")

    def _export_financial_report(self):
        self.db = load_json_data()
        students = self.db.get("students", {})
        expenses = self.db.get("expenses", {})
        metrics = process_financial_metrics(students, expenses)
        export_path = export_financial_report_csv(metrics, filename="financial_report_gui.csv")
        messagebox.showinfo("Export Completed", f"Financial report saved to {export_path}")

    def _prompt_for_name(self, title):
        return simpledialog(title, f"Enter {title.lower()}").strip().lower()

    def _prompt_for_value(self, title):
        return simpledialog(title, f"Enter {title.lower()}")


def create_thesis_manager_window(parent=None):
    if parent is None:
        root = tk.Tk()
    else:
        root = parent
    app = ThesisManagerGUI(root)
    return app


def launch_thesis_manager(parent=None):
    app = create_thesis_manager_window(parent=parent)
    if parent is None:
        root = app.root
        root.mainloop()
    return app


def run_thesis_manager_app():
    launch_thesis_manager()
