import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ================= DATABASE =================

conn = sqlite3.connect("employee_leave.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
    emp_id TEXT PRIMARY KEY,
    name TEXT,
    department TEXT,
    leave_balance INTEGER DEFAULT 30
)
""")
conn.commit()
# ================= FUNCTIONS =================

def add_employee():
    emp_id = entry_id.get().strip()
    name = entry_name.get().strip()
    dept = entry_dept.get().strip()

    if not emp_id or not name or not dept:
        messagebox.showerror("Error", "Fill all fields")
        return

    try:
        cursor.execute(
            "INSERT INTO employees VALUES(?,?,?,?)",
            (emp_id, name, dept, 20)
        )
        conn.commit()

        messagebox.showinfo("Success", "Employee Added Successfully")

        entry_id.delete(0, tk.END)
        entry_name.delete(0, tk.END)
        entry_dept.delete(0, tk.END)

        view_all()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Employee ID Already Exists")


def search_employee():
    emp_id = search_id.get().strip()

    if not emp_id:
        messagebox.showerror("Error", "Enter Employee ID")
        return

    cursor.execute(
        "SELECT * FROM employees WHERE emp_id=?",
        (emp_id,)
    )

    record = cursor.fetchone()

    details.delete(1.0, tk.END)

    if record:
        details.insert(
            tk.END,
            f"Employee ID      : {record[0]}\n"
            f"Employee Name    : {record[1]}\n"
            f"Department       : {record[2]}\n"
            f"Leave Balance    : {record[3]} Days"
        )

        leave_days.config(state="normal")
        apply_btn.config(state="normal")

    else:
        details.insert(tk.END, "Employee Not Found")
        leave_days.config(state="disabled")
        apply_btn.config(state="disabled")


def apply_leave():
    emp_id = search_id.get().strip()

    try:
        days = int(leave_days.get())
    except:
        messagebox.showerror("Error", "Enter Valid Leave Days")
        return

    cursor.execute(
        "SELECT leave_balance FROM employees WHERE emp_id=?",
        (emp_id,)
    )

    result = cursor.fetchone()

    if result is None:
        messagebox.showerror("Error", "Employee Not Found")
        return

    balance = result[0]

    if days <= 0:
        messagebox.showerror("Error", "Leave Days Must Be Greater Than 0")
        return

    if days > balance:
        messagebox.showwarning(
            "Warning",
            "Insufficient Leave Balance"
        )
        return

    new_balance = balance - days

    cursor.execute(
        "UPDATE employees SET leave_balance=? WHERE emp_id=?",
        (new_balance, emp_id)
    )

    conn.commit()

    messagebox.showinfo(
        "Success",
        f"Leave Approved\nRemaining Balance: {new_balance}"
    )

    leave_days.delete(0, tk.END)

    search_employee()
    view_all()


def view_all():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM employees")

    records = cursor.fetchall()

    for row in records:
        tree.insert("", tk.END, values=row)


# ================= GUI =================

root = tk.Tk()
root.title("Employee Leave Management System")
root.geometry("950x650")
root.configure(bg="#ECF0F1")
root.resizable(False, False)

# ================= TITLE =================

title = tk.Label(
    root,
    text="EMPLOYEE LEAVE MANAGEMENT SYSTEM",
    font=("Arial", 20, "bold"),
    bg="#ECF0F1"
)
title.pack(pady=10)

# ================= REGISTRATION =================

reg_frame = tk.LabelFrame(
    root,
    text="Employee Registration",
    padx=10,
    pady=10
)
reg_frame.pack(fill="x", padx=20, pady=10)

tk.Label(reg_frame, text="Employee ID").grid(row=0, column=0, padx=5)

entry_id = tk.Entry(reg_frame)
entry_id.grid(row=0, column=1, padx=5)

tk.Label(reg_frame, text="Employee Name").grid(row=0, column=2, padx=5)

entry_name = tk.Entry(reg_frame)
entry_name.grid(row=0, column=3, padx=5)

tk.Label(reg_frame, text="Department").grid(row=0, column=4, padx=5)

entry_dept = tk.Entry(reg_frame)
entry_dept.grid(row=0, column=5, padx=5)

tk.Button(
    reg_frame,
    text="Register Employee",
    command=add_employee
).grid(row=0, column=6, padx=10)

# ================= SEARCH =================

search_frame = tk.LabelFrame(
    root,
    text="Search & Leave Management",
    padx=10,
    pady=10
)
search_frame.pack(fill="x", padx=20, pady=10)

tk.Label(search_frame, text="Employee ID").grid(row=0, column=0)

search_id = tk.Entry(search_frame)
search_id.grid(row=0, column=1, padx=5)

tk.Button(
    search_frame,
    text="Search",
    command=search_employee
).grid(row=0, column=2, padx=10)

tk.Label(search_frame, text="Leave Days").grid(row=0, column=3)

leave_days = tk.Entry(
    search_frame,
    state="disabled"
)
leave_days.grid(row=0, column=4, padx=5)

apply_btn = tk.Button(
    search_frame,
    text="Apply Leave",
    state="disabled",
    command=apply_leave
)
apply_btn.grid(row=0, column=5, padx=10)

# ================= DETAILS =================

details_frame = tk.LabelFrame(
    root,
    text="Employee Details",
    padx=10,
    pady=10
)
details_frame.pack(fill="x", padx=20, pady=10)

details = tk.Text(
    details_frame,
    height=6,
    width=70
)
details.pack()

# ================= TABLE =================

table_frame = tk.LabelFrame(
    root,
    text="Employee Records",
    padx=10,
    pady=10
)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = (
    "Employee ID",
    "Name",
    "Department",
    "Leave Balance"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

for col in columns:
    tree.heading(col, text=col)

tree.column("Employee ID", width=150)
tree.column("Name", width=250)
tree.column("Department", width=200)
tree.column("Leave Balance", width=150)

tree.pack(fill="both", expand=True)

root.mainloop()

conn.close()