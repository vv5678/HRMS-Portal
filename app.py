import io
import json
import os
import sqlite3
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hrms.db"
SMTP_CONFIG_PATH = BASE_DIR / "smtp_config.json"

MENU_OPTIONS = [
    "Employee Dashboard",
    "Employee Profiles",
    "Employee Edit",
    "Attendance",
    "WFH / WFO",
    "Project Timesheets",
    "Comp-Off",
    "Leave Management",
    "Leave Calendar",
    "Expense Claims",
    "Resignation alerts",
    "Exit Workflow",
    "Onboarding",
    "Date of Joining",
    "Onboarding Checklist",
    "Learning Management",
    "Professional Certifications",
    "Employee Contributions",
    "Recruitment",
    "Payroll",
    "Payroll Summary",
    "Payslips",
    "Performance",
    "Analytics",
    "Announcements",
    "Asset Requests",
    "Employee Documents",
    "Recruiter Interviews",
    "Schedule Interviews",
    "Background Verification",
    "HR Letter Templates",
    "Pending approvals",
    "Approval History",
]


MENU_GROUPS = {
    # new tabs added below
    "👥 People": ["Employee Dashboard", "Employee Profiles", "Employee Edit", "Employee Documents"],
    "⏰ Time & Work": ["Attendance", "WFH / WFO", "Project Timesheets", "Comp-Off"],
    "🌴 Leave & Approvals": ["Leave Management", "Leave Calendar", "Expense Claims", "Pending approvals", "Approval History"],
    "💰 Payroll & Finance": ["Payroll", "Payroll Summary", "Payslips"],
    "📈 Growth & Performance": ["Performance", "Analytics", "Learning Management", "Professional Certifications", "Employee Contributions"],
    "💼 Talent & Operations": ["Recruitment", "Recruiter Interviews", "Background Verification", "Onboarding", "Onboarding Checklist"],
    "⚙️ Admin & Records": ["Admin Profile", "Resignation alerts", "Exit Workflow", "Asset Requests", "Announcements", "HR Letter Templates"],
    "📅 Events & People": ["Company Calendar", "Birthday Wishes", "Schedule Interviews"],
}


def get_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            department TEXT,
            role TEXT,
            status TEXT,
            work_mode TEXT,
            manager TEXT,
            salary REAL,
            phone TEXT,
            address TEXT,
            date_joined TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            date TEXT,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS wfh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            mode TEXT,
            reason TEXT,
            date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS timesheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            project TEXT,
            hours REAL,
            date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS comp_off (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            reason TEXT,
            hours INTEGER,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resignations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            reason TEXT,
            status TEXT,
            date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS onboarding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            role TEXT,
            stage TEXT,
            date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS onboarding_checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            checklist_item TEXT,
            status TEXT,
            due_date TEXT,
            assigned_to TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS exit_workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            resignation_date TEXT,
            last_working_day TEXT,
            exit_status TEXT,
            reason TEXT,
            notes TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT,
            employee TEXT,
            progress INTEGER,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT,
            certification TEXT,
            expiry TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT,
            contribution TEXT,
            impact TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            leave_type TEXT,
            start_date TEXT,
            end_date TEXT,
            days INTEGER,
            reason TEXT,
            status TEXT,
            requested_by TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expense_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            category TEXT,
            amount REAL,
            description TEXT,
            status TEXT,
            submitted_on TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            created_by TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS asset_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            asset_type TEXT,
            reason TEXT,
            status TEXT,
            requested_on TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS recruitment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            location TEXT,
            openings INTEGER,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            basic_salary REAL,
            bonus REAL,
            net_pay REAL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT,
            score INTEGER,
            rating TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            to_email TEXT,
            subject TEXT,
            message TEXT,
            sent_at TEXT,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS approval_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_type TEXT,
            employee_name TEXT,
            employee_id TEXT,
            approver TEXT,
            requested_by TEXT,
            status TEXT,
            details TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employee_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            file_name TEXT,
            file_path TEXT,
            uploaded_at TEXT,
            document_type TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payslips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            month TEXT,
            basic_salary REAL,
            bonus REAL,
            net_pay REAL,
            generated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS recruiter_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            role TEXT,
            interviewer TEXT,
            interview_date TEXT,
            stage TEXT,
            status TEXT,
            notes TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS background_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            check_type TEXT,
            status TEXT,
            check_date TEXT,
            notes TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scheduled_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            role TEXT,
            interview_date TEXT,
            interview_time TEXT,
            mode TEXT,
            interviewer TEXT,
            status TEXT,
            notes TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS company_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            event_date TEXT,
            event_type TEXT,
            description TEXT
        )
        """
    )
    # add date_of_birth column if missing
    emp_cols = [r[1] for r in cur.execute("PRAGMA table_info(employees)").fetchall()]
    if "date_of_birth" not in emp_cols:
        cur.execute("ALTER TABLE employees ADD COLUMN date_of_birth TEXT")
    # backfill birthdays + a few calendar events for existing data
    emp_rows = cur.execute("SELECT employee_id FROM employees").fetchall()
    for idx, erow in enumerate(emp_rows):
        dob_month = (idx % 12) + 1
        dob_day = (idx % 27) + 1
        cur.execute(
            "UPDATE employees SET date_of_birth = ? WHERE employee_id = ? AND (date_of_birth IS NULL OR date_of_birth = '')",
            (f"19{90 + (idx % 10)}-{dob_month:02d}-{dob_day:02d}", erow["employee_id"]),
        )
    if cur.execute("SELECT COUNT(*) FROM company_calendar").fetchone()[0] == 0:
        cal_events = [
            ("Annual Day", f"{datetime.now().year}-12-15", "Celebration", "Company annual day celebration"),
            ("Quarterly Town Hall", f"{datetime.now().year}-{datetime.now().month:02d}-28", "Meeting", "All-hands quarterly town hall"),
            ("Diwali Holiday", f"{datetime.now().year}-11-01", "Holiday", "Company holiday"),
            ("New Year", f"{datetime.now().year + 1}-01-01", "Holiday", "New year holiday"),
        ]
        cur.executemany("INSERT INTO company_calendar (title, event_date, event_type, description) VALUES (?, ?, ?, ?)", cal_events)
    conn.commit()


def fetch_all(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def load_smtp_config():
    if SMTP_CONFIG_PATH.exists():
        try:
            return json.loads(SMTP_CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_smtp_config(config):
    SMTP_CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_smtp_settings():
    config = load_smtp_config()
    merged = {
        "SMTP_HOST": os.getenv("SMTP_HOST") or config.get("SMTP_HOST", ""),
        "SMTP_PORT": os.getenv("SMTP_PORT") or config.get("SMTP_PORT", "587"),
        "SMTP_USER": os.getenv("SMTP_USER") or config.get("SMTP_USER", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD") or config.get("SMTP_PASSWORD", ""),
        "SMTP_USE_TLS": os.getenv("SMTP_USE_TLS") or config.get("SMTP_USE_TLS", "true"),
    }
    return merged


def execute_query(query, params=()):
    conn = get_connection()
    conn.execute(query, params)
    conn.commit()


def record_approval_history(request_type, employee_name, employee_id, approver, requested_by, status, details):
    execute_query(
        "INSERT INTO approval_history (request_type, employee_name, employee_id, approver, requested_by, status, details, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            request_type,
            employee_name,
            employee_id,
            approver,
            requested_by,
            status,
            details,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )


def generate_seed_employees():
    first_names = [
        "Aarav","Vivaan","Aditya","Vihaan","Ananya","Diya","Meher","Ishaan","Naina","Kabir","Riya","Arjun","Saanvi","Aditi","Pranav","Kavya",
        "Reyansh","Sara","Yash","Mira","Rohan","Tanya","Dhruv","Pooja","Neil","Aisha","Rahul","Simran","Karan","Ira","Rishabh","Nandini","Harsh",
        "Sofia","Dev","Anika","Kunal","Charvi","Manav","Tanvi","Aryan","Zoya","Jay","Kiara","Abhinav","Aanya","Parth","Esha","Ved","Krisha",
        "Mohit","Shruti","Uday","Jiya","Ashish","Mitali","Nikhil","Shreya","Ritvik","Anvi","Tarun","Bhavna","Sahil","Rhea","Vansh","Gargi",
        "Ojas","Sakshi","Aman","Vaishnavi","Adwait","Nikita","Himanshu","Palak","Naman","Khushi","Rudra","Ishita","Chetan","Disha","Varun","Jasmine",
        "Tejas","Samaira","Kartik","Aarohi","Yuvraj","Arihant","Manya","Vikram","Pallavi","Malhar","Suhani","Rajan","Ayesha","Rudransh","Prerna","Siddharth",
        "Sneha","Deepak","Janhvi","Devansh","Aditi","Keshav","Anushka","Amanpreet","Mrunal","Akash","Nisha","Chirag","Ira","Samar","Ritika","Tanush","Divya"
    ]
    last_names = [
        "Sharma","Verma","Patel","Reddy","Nair","Iyer","Singh","Khan","Kapoor","Gupta","Roy","Das","Jain","Saxena","Mehta","Chopra","Joshi","Malhotra","Rao","Bose",
        "Sen","Kulkarni","Murthy","Agarwal","Nadkarni","Thakur","Saini","Mishra","Yadav","Arora","Bhatt","Tiwari","Pandey","Shah","Desai","Gandhi","Bhardwaj",
        "Sethi","Pillai","Narang","Venkatesh","Suri","Menon","Batra","Vora","Kukreja","Dutta","Mohan","Sathya","Mangal","Purohit","Lal","Bhatia","Kaur","Ahuja"
    ]
    departments = ["Engineering", "HR", "Finance", "Sales", "Operations", "Marketing", "Support"]
    roles = {
        "Engineering": ["Software Engineer", "Senior Developer", "QA Analyst", "Tech Lead", "Platform Engineer"],
        "HR": ["HR Executive", "HR Manager", "Recruitment Specialist", "People Partner"],
        "Finance": ["Finance Analyst", "Accountant", "Payroll Specialist", "Finance Manager"],
        "Sales": ["Sales Executive", "Account Manager", "Business Development Manager", "Sales Lead"],
        "Operations": ["Operations Analyst", "Operations Manager", "Project Coordinator", "Logistics Lead"],
        "Marketing": ["Marketing Executive", "Content Strategist", "Brand Manager", "Growth Analyst"],
        "Support": ["Support Engineer", "Customer Success Manager", "IT Support Specialist", "Service Desk Analyst"],
    }
    cities = [
        ("Bengaluru", "Karnataka"), ("Hyderabad", "Telangana"), ("Pune", "Maharashtra"),
        ("New Delhi", "Delhi"), ("Chennai", "Tamil Nadu"), ("Mumbai", "Maharashtra"),
        ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
        ("Noida", "Uttar Pradesh"), ("Kochi", "Kerala"), ("Indore", "Madhya Pradesh"),
        ("Chandigarh", "Punjab"), ("Bhubaneswar", "Odisha"), ("Guwahati", "Assam"),
        ("Coimbatore", "Tamil Nadu"), ("Nagpur", "Maharashtra"), ("Lucknow", "Uttar Pradesh"),
        ("Patna", "Bihar"), ("Visakhapatnam", "Andhra Pradesh"), ("Dehradun", "Uttarakhand"),
        ("Raipur", "Chhattisgarh"), ("Surat", "Gujarat"), ("Bhopal", "Madhya Pradesh"),
        ("Mangaluru", "Karnataka"), ("Thrissur", "Kerala"), ("Jodhpur", "Rajasthan"),
        ("Varanasi", "Uttar Pradesh"), ("Amritsar", "Punjab"), ("Ranchi", "Jharkhand"),
    ]
    employees = []
    for i in range(500):
        first = first_names[i % len(first_names)]
        last = last_names[(i * 3) % len(last_names)]
        full_name = f"{first} {last}"
        dept = departments[i % len(departments)]
        role = roles[dept][i % len(roles[dept])]
        employee_id = f"EMP-{1000 + i}"
        email = f"{first.lower()}.{last.lower()}{i}@company.com"
        work_mode = ["WFH", "Office", "Hybrid"][i % 3]
        salary = 55000 + ((i * 2475) % 145000)
        manager = f"Manager {departments[(i + 1) % len(departments)]}"
        phone = f"+91 9{(100000000 + i * 12345) % 900000000:09d}"
        city, state = cities[i % len(cities)]
        address = f"{city}, {state}, India"
        joined = f"20{22 + (i % 5)}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
        employees.append((employee_id, full_name, email, dept, role, "Active", work_mode, manager, round(salary, 2), phone, address, joined))
    return employees


def seed_data():
    conn = get_connection()
    cur = conn.cursor()
    emp_count = cur.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if emp_count == 0:
        employees = generate_seed_employees()
        cur.executemany(
            "INSERT INTO employees (employee_id, name, email, department, role, status, work_mode, manager, salary, phone, address, date_joined) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            employees,
        )

        attendance = [
            ("EMP-1001", "Aisha Khan", "2026-09-06", "Present"),
            ("EMP-1002", "Rohit Verma", "2026-09-06", "Present"),
            ("EMP-1003", "Meera Iyer", "2026-09-06", "WFH"),
            ("EMP-1004", "Karan Sethi", "2026-09-06", "Absent"),
        ]
        cur.executemany("INSERT INTO attendance (employee_id, name, date, status) VALUES (?, ?, ?, ?)", attendance)

        wfh = [
            ("EMP-1001", "Aisha Khan", "WFH", "Design review", "2026-09-06"),
            ("EMP-1003", "Meera Iyer", "WFH", "Client meetings", "2026-09-06"),
        ]
        cur.executemany("INSERT INTO wfh (employee_id, name, mode, reason, date) VALUES (?, ?, ?, ?, ?)", wfh)

        timesheets = [
            ("EMP-1001", "Aisha Khan", "ERP Revamp", 8.5, "2026-09-06"),
            ("EMP-1004", "Karan Sethi", "New Client Onboarding", 7.0, "2026-09-06"),
        ]
        cur.executemany("INSERT INTO timesheets (employee_id, name, project, hours, date) VALUES (?, ?, ?, ?, ?)", timesheets)

        compoff = [
            ("EMP-1001", "Aisha Khan", "Extended sprint support", 6, "Pending"),
        ]
        cur.executemany("INSERT INTO comp_off (employee_id, name, reason, hours, status) VALUES (?, ?, ?, ?, ?)", compoff)

        resignations = [
            ("EMP-1004", "Karan Sethi", "Career growth", "Pending", "2026-09-05"),
        ]
        cur.executemany("INSERT INTO resignations (employee_id, name, reason, status, date) VALUES (?, ?, ?, ?, ?)", resignations)

        onboarding = [
            ("EMP-1005", "Ishita Roy", "Associate Analyst", "Offer Letter Sent", "2026-09-06"),
        ]
        cur.executemany("INSERT INTO onboarding (employee_id, name, role, stage, date) VALUES (?, ?, ?, ?, ?)", onboarding)

        onboarding_checklists = [
            ("EMP-1005", "Ishita Roy", "Submit identity proof", "Pending", "2026-09-08", "HR Team"),
            ("EMP-1005", "Ishita Roy", "Laptop and access setup", "In Progress", "2026-09-09", "IT Team"),
            ("EMP-1005", "Ishita Roy", "Manager introduction call", "Pending", "2026-09-10", "Reporting Manager"),
        ]
        cur.executemany(
            "INSERT INTO onboarding_checklists (employee_id, employee_name, checklist_item, status, due_date, assigned_to) VALUES (?, ?, ?, ?, ?, ?)",
            onboarding_checklists,
        )

        exit_workflows = [
            ("EMP-1004", "Karan Sethi", "2026-09-05", "2026-09-30", "Pending", "Career growth", "Notice period in progress"),
        ]
        cur.executemany(
            "INSERT INTO exit_workflows (employee_id, employee_name, resignation_date, last_working_day, exit_status, reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            exit_workflows,
        )

        learning = [
            ("Data Privacy Essentials", "Aisha Khan", 80, "In Progress"),
            ("Leadership Skills", "Rohit Verma", 100, "Completed"),
        ]
        cur.executemany("INSERT INTO learning (course, employee, progress, status) VALUES (?, ?, ?, ?)", learning)

        certs = [
            ("Aisha Khan", "AWS Solutions Architect", "2027-09-06"),
            ("Meera Iyer", "Microsoft Power BI", "2027-03-10"),
        ]
        cur.executemany("INSERT INTO certifications (employee, certification, expiry) VALUES (?, ?, ?)", certs)

        contributions = [
            ("Aisha Khan", "Built automated onboarding dashboard", "High"),
            ("Meera Iyer", "Reduced monthly reconciliation cycle", "Medium"),
        ]
        cur.executemany("INSERT INTO contributions (employee, contribution, impact) VALUES (?, ?, ?)", contributions)

        leave_requests = [
            ("EMP-1001", "Aisha Khan", "Annual Leave", "2026-09-10", "2026-09-12", 3, "Family trip", "Approved", "Aisha Khan"),
            ("EMP-1004", "Karan Sethi", "Casual Leave", "2026-09-15", "2026-09-15", 1, "Personal work", "Pending", "Karan Sethi"),
        ]
        cur.executemany(
            "INSERT INTO leave_requests (employee_id, name, leave_type, start_date, end_date, days, reason, status, requested_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            leave_requests,
        )

        expense_claims = [
            ("EMP-1002", "Rohit Verma", "Travel", 4500.0, "Client travel and lodging", "Pending", "2026-09-06"),
            ("EMP-1003", "Meera Iyer", "Conference", 2200.0, "Finance summit registration", "Approved", "2026-09-02"),
        ]
        cur.executemany(
            "INSERT INTO expense_claims (employee_id, name, category, amount, description, status, submitted_on) VALUES (?, ?, ?, ?, ?, ?, ?)",
            expense_claims,
        )

        announcements = [
            ("Quarterly Town Hall", "Please join the quarterly town hall meeting on Friday at 4:00 PM.", "HR Admin", "2026-09-06 09:00:00"),
            ("Policy Update", "Remote work policy has been updated for Q4 compliance review.", "HR Admin", "2026-09-05 15:30:00"),
        ]
        cur.executemany("INSERT INTO announcements (title, message, created_by, created_at) VALUES (?, ?, ?, ?)", announcements)

        asset_requests = [
            ("EMP-1001", "Aisha Khan", "Laptop Upgrade", "Need a better performance machine for development work", "Pending", "2026-09-06"),
            ("EMP-1002", "Rohit Verma", "Monitor", "Need second display for analytics work", "Approved", "2026-09-05"),
        ]
        cur.executemany(
            "INSERT INTO asset_requests (employee_id, name, asset_type, reason, status, requested_on) VALUES (?, ?, ?, ?, ?, ?)",
            asset_requests,
        )

        recruitment = [
            ("Senior Backend Engineer", "Remote", 2, "Open"),
            ("HR Executive", "Bengaluru", 1, "Open"),
        ]
        cur.executemany("INSERT INTO recruitment (title, location, openings, status) VALUES (?, ?, ?, ?)", recruitment)

        payroll = [
            ("EMP-1001", "Aisha Khan", 120000, 15000, 135000),
            ("EMP-1002", "Rohit Verma", 90000, 12000, 102000),
        ]
        cur.executemany("INSERT INTO payroll (employee_id, name, basic_salary, bonus, net_pay) VALUES (?, ?, ?, ?, ?)", payroll)

        performance = [
            ("Aisha Khan", 92, "Excellent"),
            ("Rohit Verma", 88, "Very Good"),
        ]
        cur.executemany("INSERT INTO performance (employee, score, rating) VALUES (?, ?, ?)", performance)

    conn.commit()


def load_employees():
    return pd.DataFrame(fetch_all("SELECT * FROM employees ORDER BY name ASC"))


def generate_payslip_pdf(employee_name, employee_id, basic_salary, bonus, month_label):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate(io.BytesIO(), pagesize=A4)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    net_pay = float(basic_salary) + float(bonus)
    elements = []
    elements.append(Paragraph("Company Payslip", styles['Title']))
    elements.append(Spacer(1, 18))
    info = [
        ["Employee", employee_name],
        ["Employee ID", employee_id],
        ["Month", month_label],
        ["Basic Salary", f"₹{float(basic_salary):,.2f}"],
        ["Bonus", f"₹{float(bonus):,.2f}"],
        ["Net Pay", f"₹{net_pay:,.2f}"],
    ]
    table = Table(info, colWidths=[180, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#123d6d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def send_email(to_email: str, subject: str, message: str):
    settings = get_smtp_settings()
    smtp_host = settings.get("SMTP_HOST", "")
    smtp_port = settings.get("SMTP_PORT", "587")
    smtp_user = settings.get("SMTP_USER", "")
    smtp_password = settings.get("SMTP_PASSWORD", "")
    use_tls = str(settings.get("SMTP_USE_TLS", "true")).lower() == "true"

    if not all([smtp_host, smtp_port, smtp_user, smtp_password]):
        execute_query(
            "INSERT INTO email_log (to_email, subject, message, sent_at, status) VALUES (?, ?, ?, ?, ?)",
            (to_email, subject, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "queued"),
        )
        return False, "SMTP not configured. Email queued locally only."

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg.set_content(message)

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        execute_query(
            "INSERT INTO email_log (to_email, subject, message, sent_at, status) VALUES (?, ?, ?, ?, ?)",
            (to_email, subject, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sent"),
        )
        return True, "Email sent successfully."
    except Exception as exc:
        execute_query(
            "INSERT INTO email_log (to_email, subject, message, sent_at, status) VALUES (?, ?, ?, ?, ?)",
            (to_email, subject, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"failed:{exc}"),
        )
        return False, f"SMTP send failed: {exc}"


def render_css():
    st.markdown(
        """
        <style>
            :root {
                --bg: #f4f7fb;
                --card: #ffffff;
                --brand: #6d28d9;
                --brand-2: #ec4899;
                --accent-1: #f59e0b;
                --accent-2: #10b981;
                --accent-3: #3b82f6;
                --accent-4: #ef4444;
                --text: #1f2937;
                --muted: #6b7280;
                --line: #e5e7eb;
            }
            .stApp {
                background: linear-gradient(120deg, #fdf2f8 0%, #eef2ff 35%, #ecfeff 70%, #fefce8 100%);
            }
            h1, .stApp h1 {
                background: linear-gradient(90deg, #7c3aed, #ec4899, #f59e0b, #10b981);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent !important;
                -webkit-text-fill-color: transparent;
            }
            h2, .stApp h2 { color: #7c3aed; }
            h3, .stApp h3 { color: #0ea5e9; }
            hr { border-color: #f0abfc; }
            .block-container {
                padding-top: 1.2rem;
                padding-left: 1.2rem;
                padding-right: 1.2rem;
            }
            .card {
                background: var(--card);
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: 0 8px 24px rgba(13, 32, 56, 0.05);
                margin-bottom: 1rem;
            }
            .profile-box {
                background: linear-gradient(120deg, #7c3aed 0%, #ec4899 50%, #f59e0b 100%);
                border-radius: 20px;
                padding: 1.1rem 1.2rem;
                color: white;
                margin-bottom: 1rem;
            }
            .metric-box {
                padding: 1rem;
                border-radius: 14px;
                border: none;
                border-top: 5px solid transparent;
                height: 100%;
                color: #ffffff;
                box-shadow: 0 6px 18px rgba(0,0,0,0.10);
                transition: transform 0.15s ease;
            }
            .metric-box:hover { transform: translateY(-3px); }
            .metric-box .label, .metric-box span {
                color: rgba(255,255,255,0.9) !important;
            }
            .metric-box:nth-child(5n+1) {
                background: linear-gradient(135deg, #7c3aed, #a855f7);
                border-top-color: #fbbf24;
            }
            .metric-box:nth-child(5n+2) {
                background: linear-gradient(135deg, #ec4899, #f472b6);
                border-top-color: #fef08a;
            }
            .metric-box:nth-child(5n+3) {
                background: linear-gradient(135deg, #0ea5e9, #38bdf8);
                border-top-color: #fde68a;
            }
            .metric-box:nth-child(5n+4) {
                background: linear-gradient(135deg, #10b981, #34d399);
                border-top-color: #fcd34d;
            }
            .metric-box:nth-child(5n+5) {
                background: linear-gradient(135deg, #f97316, #fb923c);
                border-top-color: #fde047;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 6px;
                background: #ffffff;
                border-radius: 12px;
                padding: 6px;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px;
                color: #7c3aed;
                font-weight: 600;
            }
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #7c3aed, #ec4899);
                color: #ffffff !important;
            }
            .letter-box {
                background: white;
                border: 1px solid #dbe3ef;
                border-radius: 14px;
                padding: 1.2rem;
                box-shadow: 0 8px 20px rgba(17,24,39,0.04);
                line-height: 1.7;
                color: #1f2937;
                white-space: pre-wrap;
                font-family: Arial, sans-serif;
            }
            .sidebar .stRadio {
                margin-top: 10px;
            }
            section[data-testid="stSidebar"] {
                background:
                    radial-gradient(circle at 20% 8%, rgba(236,72,153,0.35), transparent 45%),
                    radial-gradient(circle at 85% 30%, rgba(14,165,233,0.30), transparent 40%),
                    radial-gradient(circle at 50% 95%, rgba(245,158,11,0.30), transparent 45%),
                    linear-gradient(180deg, #1e1040 0%, #3b1366 40%, #4c1d95 70%, #701a4d 100%);
            }
            section[data-testid="stSidebar"] .stRadio label:hover {
                background: rgba(255,255,255,0.15);
                border-radius: 8px;
            }
            section[data-testid="stSidebar"] * {
                color: #ffffff !important;
            }
            section[data-testid="stSidebar"] hr {
                border: none;
                height: 2px;
                background: linear-gradient(90deg, transparent, #ec4899, #0ea5e9, transparent);
                opacity: 0.8;
            }
            .side-user-card {
                background: rgba(255,255,255,0.12);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 18px;
                padding: 14px;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 8px 22px rgba(0,0,0,0.25);
                margin-bottom: 10px;
            }
            .side-avatar {
                width: 54px;
                height: 54px;
                border-radius: 50%;
                background: linear-gradient(135deg, #f59e0b, #ec4899, #7c3aed);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 26px;
                font-weight: 800;
                color: #fff !important;
                box-shadow: 0 4px 12px rgba(236,72,153,0.5);
                flex-shrink: 0;
            }
            .side-user-card .role-chip {
                display: inline-block;
                font-size: 11px;
                font-weight: 700;
                padding: 2px 10px;
                border-radius: 999px;
                margin-top: 3px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .role-admin { background: linear-gradient(90deg, #f59e0b, #ef4444); }
            .role-manager { background: linear-gradient(90deg, #0ea5e9, #10b981); }
            .role-employee { background: linear-gradient(90deg, #8b5cf6, #ec4899); }
            .side-stat {
                background: rgba(255,255,255,0.10);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 14px;
                padding: 10px 12px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background 0.2s ease, transform 0.2s ease;
            }
            .side-stat:hover {
                background: rgba(255,255,255,0.20);
                transform: translateX(4px);
            }
            .side-stat .num {
                font-size: 20px;
                font-weight: 800;
                background: linear-gradient(90deg, #fbbf24, #f472b6, #38bdf8);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent !important;
                -webkit-text-fill-color: transparent;
            }
            .side-alert {
                background: linear-gradient(120deg, rgba(239,68,68,0.35), rgba(245,158,11,0.30));
                border: 1px solid rgba(251,191,36,0.5);
                border-radius: 14px;
                padding: 10px 12px;
                margin-bottom: 10px;
                font-size: 13px;
                animation: sidePulse 2.5s ease-in-out infinite;
            }
            .side-ok {
                background: linear-gradient(120deg, rgba(16,185,129,0.30), rgba(14,165,233,0.25));
                border: 1px solid rgba(52,211,153,0.45);
                border-radius: 14px;
                padding: 10px 12px;
                margin-bottom: 10px;
                font-size: 13px;
            }
            @keyframes sidePulse {
                0%, 100% { box-shadow: 0 0 0 rgba(251,191,36,0.0); }
                50% { box-shadow: 0 0 18px rgba(251,191,36,0.45); }
            }
            .side-clock {
                text-align: center;
                background: rgba(0,0,0,0.25);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 14px;
                padding: 10px;
                margin-bottom: 12px;
                font-variant-numeric: tabular-nums;
            }
            .side-clock .time {
                font-size: 26px;
                font-weight: 800;
                letter-spacing: 1px;
                background: linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent !important;
                -webkit-text-fill-color: transparent;
            }
            .side-clock .date { font-size: 12px; opacity: 0.85; margin-top: 2px; }
            .side-footer {
                margin-top: 14px;
                text-align: center;
                font-size: 11px;
                opacity: 0.7;
                line-height: 1.6;
            }
            .stButton > button {
                border-radius: 10px;
                background: linear-gradient(120deg, #7c3aed, #ec4899, #f97316);
                background-size: 200% auto;
                color: white;
                font-weight: 700;
                border: none;
                transition: background-position 0.3s ease;
            }
            .stButton > button[data-baseweb="button"] { width: 100%; }
            section[data-testid="stSidebar"] .stButton > button {
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.20);
                color: #ffffff !important;
                text-align: left;
                font-weight: 600;
                border-radius: 12px;
            }
            section[data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(255,255,255,0.22);
                transform: translateX(3px);
            }
            section[data-testid="stSidebar"] .stButton > button[kind="primary"],
            section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
                background: linear-gradient(120deg, #ec4899, #8b5cf6, #0ea5e9) !important;
                border: none !important;
                box-shadow: 0 4px 14px rgba(236,72,153,0.45);
                font-weight: 800;
            }
            .stButton > button:hover {
                background-position: right center;
                box-shadow: 0 4px 14px rgba(236, 72, 153, 0.4);
            }
            .stDownloadButton > button {
                border-radius: 10px;
                background: linear-gradient(120deg, #10b981, #0ea5e9);
                color: white;
                font-weight: 700;
                border: none;
            }
            .stAlert {
                border-radius: 12px;
            }
            /* ================= AURORA GLASS PREMIUM THEME ================= */
            .stApp {
                background:
                    radial-gradient(ellipse 80% 50% at 10% -10%, rgba(124,58,237,0.28), transparent),
                    radial-gradient(ellipse 70% 45% at 95% 5%, rgba(14,165,233,0.22), transparent),
                    radial-gradient(ellipse 60% 40% at 50% 110%, rgba(236,72,153,0.20), transparent),
                    linear-gradient(160deg, #070714 0%, #0d0d24 45%, #120b2e 100%) !important;
                background-attachment: fixed;
            }
            .stApp, .stApp p, .stApp label, .stApp span, .stApp div {
                color: #e7e9f5;
            }
            h1, .stApp h1 {
                background: linear-gradient(90deg, #a78bfa, #f472b6, #38bdf8) !important;
                -webkit-background-clip: text !important;
                background-clip: text !important;
            }
            h2, .stApp h2 { color: #c4b5fd !important; }
            h3, .stApp h3 { color: #7dd3fc !important; }
            .stApp .stCaption, .stApp small, .stApp .stMarkdownContainer em { color: #9aa0c3 !important; }
            .card, .letter-box {
                background: rgba(255,255,255,0.05) !important;
                border: 1px solid rgba(255,255,255,0.12) !important;
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.35) !important;
                color: #e7e9f5 !important;
            }
            .stDataFrame, [data-testid="stDataFrame"] {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 14px;
                overflow: hidden;
            }
            [data-testid="stDataFrame"] iframe { filter: invert(0.92) hue-rotate(180deg); border-radius: 14px; }
            .stTextInput input, .stTextArea textarea, .stNumberInput input,
            .stSelectbox > div > div, .stMultiSelect > div > div,
            [data-baseweb="select"] > div, [data-baseweb="input"] > div {
                background: rgba(255,255,255,0.06) !important;
                border: 1px solid rgba(255,255,255,0.14) !important;
                border-radius: 10px !important;
                color: #e7e9f5 !important;
            }
            [data-baseweb="popover"] *, [role="listbox"] * { background: #14142e !important; color: #e7e9f5 !important; }
            .stDateInput input, .stTimeInput input {
                background: rgba(255,255,255,0.06) !important;
                color: #e7e9f5 !important;
                border: 1px solid rgba(255,255,255,0.14) !important;
            }
            [data-testid="stExpander"] {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 14px;
            }
            [data-testid="stExpanderDetails"] { color: #e7e9f5; }
            .stTabs [data-baseweb="tab-list"] {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.10);
            }
            .stTabs [data-baseweb="tab"] { color: #c4b5fd !important; }
            .stSlider > div { color: #e7e9f5; }
            .stButton > button {
                background: linear-gradient(120deg, #7c3aed, #db2777, #f59e0b) !important;
                background-size: 220% auto !important;
                box-shadow: 0 6px 20px rgba(124,58,237,0.4);
            }
            .stDownloadButton > button {
                background: linear-gradient(120deg, #059669, #0ea5e9) !important;
                box-shadow: 0 6px 20px rgba(5,150,105,0.35);
            }
            .stForm { border: none !important; }
            ::-webkit-scrollbar { width: 10px; height: 10px; }
            ::-webkit-scrollbar-track { background: #0d0d24; }
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #7c3aed, #ec4899);
                border-radius: 6px;
            }
            ::selection { background: rgba(236,72,153,0.4); }
            .hero-banner {
                background:
                    radial-gradient(circle at 15% 20%, rgba(56,189,248,0.35), transparent 40%),
                    radial-gradient(circle at 85% 30%, rgba(236,72,153,0.35), transparent 40%),
                    linear-gradient(120deg, rgba(124,58,237,0.85), rgba(219,39,119,0.75) 55%, rgba(245,158,11,0.7));
                border-radius: 24px;
                padding: 26px 30px;
                color: #fff !important;
                box-shadow: 0 14px 40px rgba(124,58,237,0.45);
                margin-bottom: 18px;
                border: 1px solid rgba(255,255,255,0.25);
            }
            .hero-banner h1 { color: #fff !important; -webkit-text-fill-color: #fff !important; background: none !important; margin: 0; }
            .hero-banner p { color: rgba(255,255,255,0.92) !important; margin: 6px 0 0; }
            .glass-panel {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.12);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border-radius: 18px;
                padding: 18px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35);
            }
            @keyframes floatGlow {
                0%,100% { box-shadow: 0 10px 30px rgba(124,58,237,0.35); }
                50% { box-shadow: 0 14px 44px rgba(236,72,153,0.5); }
            }
            .metric-box { animation: floatGlow 4s ease-in-out infinite; }
            [data-testid="stHeader"] {
                background: transparent;
            }
            [data-testid="stDecoration"] { display: none; }
            #MainMenu { visibility: hidden; }
            section[data-testid="stSidebar"] .side-clock .time {
                font-variant-numeric: tabular-nums;
            }
            .stApp a { color: #7dd3fc !important; }
            .stApp code { background: rgba(255,255,255,0.08) !important; color: #fbbf24 !important; }
            /* ================= SIMPLE CLEAN WEBSITE THEME (final layer) ================= */
            .stApp {
                background: #f5f7fb !important;
                background-attachment: scroll;
            }
            .stApp, .stApp p, .stApp label, .stApp span, .stApp div {
                color: #1f2937;
            }
            h1, .stApp h1 {
                background: none !important;
                -webkit-text-fill-color: #111827 !important;
                color: #111827 !important;
                font-weight: 800;
            }
            h2, .stApp h2 { color: #111827 !important; font-weight: 700; }
            h3, .stApp h3 { color: #1d4ed8 !important; }
            .card, .letter-box, [data-testid="stExpander"], .glass-panel {
                background: #ffffff !important;
                border: 1px solid #e5e7eb !important;
                backdrop-filter: none;
                box-shadow: 0 2px 10px rgba(16,24,40,0.06) !important;
                color: #1f2937 !important;
            }
            .metric-box {
                animation: none !important;
                background: #ffffff !important;
                border: 1px solid #e5e7eb !important;
                border-left: 6px solid #2563eb !important;
                box-shadow: 0 2px 10px rgba(16,24,40,0.06) !important;
                color: #1f2937 !important;
                border-radius: 14px;
                padding: 1.1rem !important;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .metric-box:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(37,99,235,0.15) !important; }
            .metric-box .label, .metric-box span, .metric-box div { color: #1f2937 !important; }
            .metric-box .label { font-size: 13px !important; color: #6b7280 !important; }
            .metric-box div[style*="font-size:2rem"], .metric-box div[style*="font-size:2.2rem"] { color: #111827 !important; }
            .metric-box:nth-child(5n+1) { border-left-color: #2563eb; background: #ffffff !important; }
            .metric-box:nth-child(5n+2) { border-left-color: #059669; background: #ffffff !important; }
            .metric-box:nth-child(5n+3) { border-left-color: #d97706; background: #ffffff !important; }
            .metric-box:nth-child(5n+4) { border-left-color: #7c3aed; background: #ffffff !important; }
            .metric-box:nth-child(5n+5) { border-left-color: #dc2626; background: #ffffff !important; }
            /* ---- BIG website-style tabs with pointer cursor ---- */
            .stTabs [data-baseweb="tab-list"] {
                gap: 4px;
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                padding: 8px;
                box-shadow: 0 2px 10px rgba(16,24,40,0.06);
                flex-wrap: wrap;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 10px;
                color: #374151 !important;
                font-weight: 700;
                font-size: 17px !important;
                padding: 12px 22px !important;
                cursor: pointer !important;
                transition: all 0.2s ease;
                background: transparent;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background: #eef2ff !important;
                color: #1d4ed8 !important;
                transform: translateY(-2px);
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: #1d4ed8 !important;
                color: #ffffff !important;
                box-shadow: 0 4px 14px rgba(29,78,216,0.35);
            }
            .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
            /* ---- inputs / tables back to light ---- */
            .stTextInput input, .stTextArea textarea, .stNumberInput input,
            .stSelectbox > div > div, .stMultiSelect > div > div,
            [data-baseweb="select"] > div, [data-baseweb="input"] > div,
            .stDateInput input, .stTimeInput input {
                background: #ffffff !important;
                border: 1px solid #d1d5db !important;
                color: #1f2937 !important;
            }
            [data-baseweb="popover"] *, [role="listbox"] * { background: #ffffff !important; color: #1f2937 !important; }
            [data-baseweb="popover"] li:hover { background: #eef2ff !important; }
            [data-testid="stDataFrame"] iframe { filter: none; }
            .stButton > button {
                background: #1d4ed8 !important;
                background-size: auto !important;
                box-shadow: none;
            }
            .stButton > button:hover { background: #1e40af !important; box-shadow: 0 6px 16px rgba(29,78,216,0.3); }
            .stDownloadButton > button { background: #059669 !important; box-shadow: none; }
            .stDownloadButton > button:hover { background: #047857 !important; }
            section[data-testid="stSidebar"] {
                background: #111c3d !important;
            }
            ::-webkit-scrollbar-track { background: #eef1f6; }
            ::-webkit-scrollbar-thumb { background: #94a3b8; }
            ::selection { background: rgba(29,78,216,0.25); }
            /* ---- simple hero / website sections ---- */
            .hero-banner {
                background: linear-gradient(120deg, #0f1f4b 0%, #16307a 60%, #1d4ed8 100%) !important;
                border: none !important;
                border-radius: 20px;
                padding: 38px 34px !important;
                box-shadow: 0 10px 30px rgba(15,31,75,0.25) !important;
                margin-bottom: 6px;
            }
            .hero-banner h1 { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 2.4rem !important; }
            .hero-banner p { color: rgba(255,255,255,0.85) !important; font-size: 17px; }
            .hero-chips { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 18px; }
            .hero-chip {
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 999px;
                padding: 8px 18px;
                color: #ffffff !important;
                font-weight: 600;
                font-size: 14px;
            }
            .section-title {
                font-size: 1.6rem; font-weight: 800; color: #111827 !important;
                margin: 18px 0 4px;
                border-left: 6px solid #1d4ed8; padding-left: 12px;
            }
            .dept-card {
                background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px;
                padding: 18px; height: 100%;
                box-shadow: 0 2px 10px rgba(16,24,40,0.06);
                transition: transform 0.15s ease, box-shadow 0.15s ease;
                cursor: pointer;
            }
            .dept-card:hover { transform: translateY(-4px); box-shadow: 0 10px 26px rgba(16,24,40,0.12); }
            .dept-card .dept-icon { font-size: 30px; }
            .dept-card .dept-name { font-size: 18px; font-weight: 800; color: #111827; margin-top: 6px; }
            .dept-card .dept-meta { color: #6b7280; font-size: 13px; margin-top: 4px; }
            .news-card {
                background: #ffffff; border: 1px solid #e5e7eb; border-left: 5px solid #1d4ed8;
                border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
                box-shadow: 0 2px 8px rgba(16,24,40,0.05);
            }
            .news-card .news-title { font-weight: 800; color: #111827; font-size: 15px; }
            .news-card .news-meta { color: #6b7280; font-size: 12px; margin-top: 2px; }
            .news-card .news-body { color: #374151; font-size: 14px; margin-top: 6px; }
            .celeb-card {
                background: #ffffff; border: 1px solid #e5e7eb; border-top: 4px solid #f59e0b;
                border-radius: 16px; padding: 16px; text-align: center; height: 100%;
                box-shadow: 0 2px 10px rgba(16,24,40,0.06);
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .celeb-card:hover { transform: translateY(-4px); box-shadow: 0 10px 26px rgba(245,158,11,0.18); }
            .celeb-name { font-weight: 800; color: #111827; font-size: 15px; margin-top: 6px; }
            .celeb-meta { color: #6b7280; font-size: 12px; margin-top: 3px; }
            .celeb-years {
                display: inline-block; margin-top: 8px; padding: 3px 12px; border-radius: 999px;
                background: #fef3c7; color: #92400e; font-weight: 700; font-size: 12px;
            }
            /* ================= v4 UPGRADE: BIG TABS + CURSOR EVERYWHERE ================= */
            /* pointer cursor on every interactive element */
            .stTabs [data-baseweb="tab"] *,
            .stButton > button, .stDownloadButton > button,
            [data-baseweb="select"], [data-baseweb="input"],
            [data-testid="stExpander"] summary, [role="checkbox"],
            [data-baseweb="checkbox"], [role="option"],
            .stRadio label, .stCheckbox label {
                cursor: pointer !important;
            }
            /* bigger website-style tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 6px;
                padding: 10px;
                border-radius: 16px;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: 19px !important;
                font-weight: 800 !important;
                padding: 16px 30px !important;
                border-radius: 12px;
                gap: 8px;
            }
            .stTabs [data-baseweb="tab"]:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 18px rgba(29,78,216,0.18);
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                transform: translateY(-2px);
            }
            /* employee spotlight card */
            .spotlight-card {
                display: flex; align-items: center; gap: 16px;
                background: #ffffff; border: 1px solid #e5e7eb;
                border-radius: 16px; padding: 16px 20px;
                box-shadow: 0 2px 10px rgba(16,24,40,0.06);
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .spotlight-card:hover { transform: translateY(-3px); box-shadow: 0 10px 26px rgba(16,24,40,0.12); }
            .spotlight-avatar {
                width: 56px; height: 56px; border-radius: 50%; flex-shrink: 0;
                display: flex; align-items: center; justify-content: center;
                font-size: 24px; font-weight: 800; color: #ffffff !important;
                background: linear-gradient(135deg, #1d4ed8, #3b82f6);
            }
            .spotlight-name { font-weight: 800; font-size: 16px; color: #111827; }
            .spotlight-meta { color: #6b7280; font-size: 13px; }
            .spotlight-tag {
                display: inline-block; margin-top: 4px; margin-right: 6px;
                background: #eff6ff; color: #1d4ed8 !important;
                border-radius: 999px; padding: 2px 10px;
                font-size: 11px; font-weight: 700;
            }
            /* celebrations card */
            .celebration-card {
                background: linear-gradient(120deg, #fffbeb, #fef3c7);
                border: 1px solid #fde68a; border-left: 5px solid #d97706;
                border-radius: 12px; padding: 12px 16px; margin-bottom: 10px;
            }
            .celebration-card .cel-title { font-weight: 800; color: #92400e; font-size: 14px; }
            .celebration-card .cel-meta { color: #a16207; font-size: 12px; margin-top: 2px; }
            /* leaderboard rows */
            .rank-row {
                display: flex; align-items: center; gap: 12px;
                background: #ffffff; border: 1px solid #e5e7eb;
                border-radius: 12px; padding: 10px 16px; margin-bottom: 8px;
                transition: transform 0.15s ease;
            }
            .rank-row:hover { transform: translateX(6px); border-color: #93c5fd; }
            .rank-badge {
                width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
                display: flex; align-items: center; justify-content: center;
                font-weight: 800; font-size: 15px; color: #fff !important;
                background: #1d4ed8;
            }
            .rank-row:nth-child(1) .rank-badge { background: #d97706; }
            .rank-row:nth-child(2) .rank-badge { background: #6b7280; }
            .rank-row:nth-child(3) .rank-badge { background: #b45309; }
            .rank-name { font-weight: 700; color: #111827; flex: 1; }
            .rank-score { font-weight: 800; color: #1d4ed8; }
            /* marquee ticker */
            .ticker-wrap {
                background: #111c3d; border-radius: 12px;
                overflow: hidden; padding: 10px 0; margin-bottom: 8px;
            }
            .ticker {
                display: inline-block; white-space: nowrap;
                animation: tickerScroll 30s linear infinite;
                color: #ffffff !important; font-weight: 600; font-size: 14px;
                padding-left: 100%;
            }
            .ticker span { margin: 0 28px; color: #ffffff !important; }
            .ticker .tick-dot { color: #60a5fa !important; }
            @keyframes tickerScroll {
                0% { transform: translateX(0); }
                100% { transform: translateX(-100%); }
            }
            .ticker-wrap:hover .ticker { animation-play-state: paused; }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="HRMS Portal", page_icon="🏢", layout="wide")

render_css()

init_db()
seed_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
for _k, _v in (("user_email", ""), ("user_role", "")):
    if _k not in st.session_state:
        st.session_state[_k] = _v

if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center; margin-top:6vh;">
        <div style="font-size:64px; line-height:1;">🏢</div>
        <h1 style="font-size:2.6rem; margin:6px 0;">BluePeak <span style="background:linear-gradient(90deg,#a78bfa,#f472b6,#38bdf8); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;">HRMS</span></h1>
        <p style="color:#9aa0c3;">Enterprise Human Resource Management · v3.0 Aurora</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="card" style="max-width:520px; margin:4vh auto; padding:2rem;">', unsafe_allow_html=True)
    st.caption("Demo credentials: admin@company.com / admin123 | manager@company.com / manager123 | employee@company.com / employee123")
    with st.form("login_form"):
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")
    if login:
        valid = {
            "admin@company.com": {"password": "admin123", "role": "admin"},
            "manager@company.com": {"password": "manager123", "role": "manager"},
            "employee@company.com": {"password": "employee123", "role": "employee"},
        }
        if valid.get(username) and valid[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = username
            st.session_state.user_role = valid[username]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

employees_df = load_employees()
attendance_df = pd.DataFrame(fetch_all("SELECT * FROM attendance ORDER BY date DESC"))
wfh_df = pd.DataFrame(fetch_all("SELECT * FROM wfh ORDER BY date DESC"))
timesheets_df = pd.DataFrame(fetch_all("SELECT * FROM timesheets ORDER BY date DESC"))
compoff_df = pd.DataFrame(fetch_all("SELECT * FROM comp_off ORDER BY id DESC"))
resignations_df = pd.DataFrame(fetch_all("SELECT * FROM resignations ORDER BY date DESC"))
onboarding_df = pd.DataFrame(fetch_all("SELECT * FROM onboarding ORDER BY date DESC"))
learning_df = pd.DataFrame(fetch_all("SELECT * FROM learning ORDER BY employee ASC"))
certs_df = pd.DataFrame(fetch_all("SELECT * FROM certifications ORDER BY employee ASC"))
contrib_df = pd.DataFrame(fetch_all("SELECT * FROM contributions ORDER BY employee ASC"))
recruitment_df = pd.DataFrame(fetch_all("SELECT * FROM recruitment ORDER BY status ASC"))
payroll_df = pd.DataFrame(fetch_all("SELECT * FROM payroll ORDER BY name ASC"))
performance_df = pd.DataFrame(fetch_all("SELECT * FROM performance ORDER BY score DESC"))
leave_requests_df = pd.DataFrame(fetch_all("SELECT * FROM leave_requests ORDER BY start_date DESC"))
expense_claims_df = pd.DataFrame(fetch_all("SELECT * FROM expense_claims ORDER BY submitted_on DESC"))
announcements_df = pd.DataFrame(fetch_all("SELECT * FROM announcements ORDER BY created_at DESC"))
asset_requests_df = pd.DataFrame(fetch_all("SELECT * FROM asset_requests ORDER BY requested_on DESC"))
document_df = pd.DataFrame(fetch_all("SELECT * FROM employee_documents ORDER BY uploaded_at DESC"))
payslip_df = pd.DataFrame(fetch_all("SELECT * FROM payslips ORDER BY generated_at DESC"))
interview_df = pd.DataFrame(fetch_all("SELECT * FROM recruiter_interviews ORDER BY interview_date DESC"))
background_df = pd.DataFrame(fetch_all("SELECT * FROM background_checks ORDER BY check_date DESC"))
onboarding_checklist_df = pd.DataFrame(fetch_all("SELECT * FROM onboarding_checklists ORDER BY due_date ASC"))
exit_workflow_df = pd.DataFrame(fetch_all("SELECT * FROM exit_workflows ORDER BY resignation_date DESC"))
email_log_df = pd.DataFrame(fetch_all("SELECT * FROM email_log ORDER BY id DESC LIMIT 10"))

# ---------- Advanced Sidebar ----------
_pending_approvals = (
    int((compoff_df["status"] == "Pending").sum()) if not compoff_df.empty else 0
) + (
    int((resignations_df["status"] == "Pending").sum()) if not resignations_df.empty else 0
) + (
    int((leave_requests_df["status"] == "Pending").sum()) if not leave_requests_df.empty else 0
) + (
    int((expense_claims_df["status"] == "Pending").sum()) if not expense_claims_df.empty else 0
)
_wfh_today = int((employees_df["work_mode"] == "WFH").sum()) if not employees_df.empty else 0
_headcount = len(employees_df)
_open_positions = int(recruitment_df["openings"].sum()) if not recruitment_df.empty else 0

role = st.session_state.user_role
user_initial = st.session_state.user_email[:1].upper() if st.session_state.user_email else "?"
now = datetime.now()

# Resolve the logged-in user's employee record (for the profile card)
_my_emp = employees_df[employees_df["email"].str.lower() == st.session_state.user_email.lower()] if not employees_df.empty else pd.DataFrame()
_my_name = _my_emp.iloc[0]["name"] if not _my_emp.empty else ("Admin User" if role == "admin" else st.session_state.user_email.split("@")[0].title())
_my_id = _my_emp.iloc[0]["employee_id"] if not _my_emp.empty else ("ADM-001" if role == "admin" else "—")
_my_role_label = _my_emp.iloc[0]["role"] if not _my_emp.empty else role.title()

st.sidebar.markdown(
    f"""
    <div class="side-user-card">
        <div class="side-avatar">{user_initial}</div>
        <div>
            <div style="font-weight:700; font-size:14px;">{_my_name}</div>
            <span class="role-chip role-{role}">{role}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- My Profile (slide-down) with user id, name, email + logout ----------
with st.sidebar.expander("👤 My Profile"):
    st.markdown(f"**ID:** {_my_id}")
    st.markdown(f"**Name:** {_my_name}")
    st.markdown(f"**Email:** {st.session_state.user_email}")
    st.markdown(f"**Role:** {_my_role_label.title()}")
    if st.button("🚪 Logout", key="profile_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = ""
        st.rerun()

st.sidebar.markdown(
    f"""
    <div class="side-clock">
        <div class="time">{now.strftime('%H:%M:%S')}</div>
        <div class="date">{now.strftime('%A, %d %B %Y')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    <div class="side-stat"><span>👥 Headcount</span><span class="num">{_headcount}</span></div>
    <div class="side-stat"><span>🏠 WFH Today</span><span class="num">{_wfh_today}</span></div>
    <div class="side-stat"><span>💼 Open Roles</span><span class="num">{_open_positions}</span></div>
    """,
    unsafe_allow_html=True,
)


def go_to(page):
    """Central navigation helper: switches category AND page, then reruns."""
    for g, pages in MENU_GROUPS.items():
        if page in pages:
            st.session_state.selected_group = g
            st.session_state.cat_select = g  # sync the category dropdown widget
            break
    st.session_state.selected_menu = page
    st.rerun()


# Clickable stat cards -> jump to the relevant page
if st.sidebar.button(f"👥 Headcount: {_headcount}", key="stat_head", use_container_width=True):
    go_to("Employee Dashboard")
if st.sidebar.button(f"🏠 WFH Today: {_wfh_today}", key="stat_wfh", use_container_width=True):
    go_to("WFH / WFO")
if st.sidebar.button(f"💼 Open Roles: {_open_positions}", key="stat_roles", use_container_width=True):
    go_to("Recruitment")
if _pending_approvals > 0 and st.sidebar.button(
    f"⚡ {_pending_approvals} pending approval(s)", key="stat_pending", use_container_width=True
):
    go_to("Pending approvals")

# ---------- ONE global search bar for everything (slide-down) ----------
with st.sidebar.expander("🔎 Global Search"):
    global_q = st.text_input(
        "Search everything",
        placeholder="Names, EMP-ID, role, page...",
        key="global_search",
        label_visibility="collapsed",
    )
    if global_q.strip():
        q = global_q.strip().lower()

        st.caption("📄 Pages")
        page_hits = [p for pages in MENU_GROUPS.values() for p in pages if q in p.lower()]
        for ph in page_hits[:6]:
            if st.button(f"➜ {ph}", key=f"gsearch_page_{ph}", use_container_width=True):
                go_to(ph)

        st.caption("👥 Employees")
        emp_hits = employees_df[
            employees_df["name"].str.lower().str.contains(q, na=False)
            | employees_df["employee_id"].str.lower().str.contains(q, na=False)
            | employees_df["role"].str.lower().str.contains(q, na=False)
            | employees_df["department"].str.lower().str.contains(q, na=False)
            | employees_df["email"].str.lower().str.contains(q, na=False)
        ].head(8)
        if emp_hits.empty and not page_hits:
            st.info("No matches found.")
        for _, ehit in emp_hits.iterrows():
            hit_label = f"👤 {ehit['name']} · {ehit['employee_id']}"
            if st.button(hit_label, key=f"gsearch_emp_{ehit['employee_id']}", use_container_width=True):
                st.session_state.profile_employee = ehit["name"]
                go_to("Employee Profiles")

if _pending_approvals > 0:
    st.sidebar.markdown(
        f'<div class="side-alert">⚡ <b>{_pending_approvals}</b> request(s) awaiting your approval!</div>',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown('<div class="side-ok">✅ All caught up — no pending approvals.</div>', unsafe_allow_html=True)

# Quick actions — jump straight to a page (switches category automatically)
st.sidebar.subheader("⚡ Quick Actions")
quick_actions = {
    "🕐 Mark Attendance": "Attendance",
    "🌴 Request Leave": "Leave Management",
    "⏱️ Log Timesheet": "Project Timesheets",
    "🧾 My Payslip": "Payslips",
    "📈 My Performance": "Performance",
}
qa_cols = st.sidebar.columns(2)
for idx, (label, target) in enumerate(quick_actions.items()):
    with qa_cols[idx % 2]:
        if st.button(label, key=f"qa_{idx}", use_container_width=True):
            go_to(target)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    st.rerun()

st.sidebar.subheader("🧭 Navigation")
group_names = list(MENU_GROUPS.keys())
# keep the widget state in sync when go_to() changes the group
if st.session_state.get("cat_select") not in group_names:
    st.session_state.cat_select = st.session_state.get("selected_group", group_names[0])
selected_group = st.sidebar.selectbox("Category", group_names, key="cat_select")
st.session_state.selected_group = selected_group

# ---------- Slide-down search bar for pages inside categories ----------
with st.sidebar.expander("🔎 Search pages", expanded=False):
    nav_q = st.text_input("Search pages", placeholder="Type to filter pages...", key="nav_search", label_visibility="collapsed")
    if nav_q.strip():
        _nq = nav_q.strip().lower()
        _all_hits = [p for pages in MENU_GROUPS.values() for p in pages if _nq in p.lower()]
        if _all_hits:
            st.caption(f"{len(_all_hits)} page(s) found")
            for hp in _all_hits[:10]:
                if st.button(f"➜ {hp}", key=f"navsearch_{hp}", use_container_width=True):
                    go_to(hp)
        else:
            st.info("No pages matched.")

if st.session_state.get("selected_menu") not in MENU_GROUPS[selected_group]:
    st.session_state.selected_menu = MENU_GROUPS[selected_group][0]

menu_container = st.sidebar.container()
with menu_container:
    for page in MENU_GROUPS[selected_group]:
        active = st.session_state.selected_menu == page
        btn_type = "primary" if active else "secondary"
        if st.button(page, key=f"nav_{page}", use_container_width=True, type=btn_type):
            st.session_state.selected_menu = page
            st.rerun()
selected_menu = st.session_state.selected_menu
can_manage_employees = st.session_state.user_role in ["admin", "manager"]
can_approve = st.session_state.user_role in ["admin", "manager"]
approval_history_df = pd.DataFrame(fetch_all("SELECT * FROM approval_history ORDER BY id DESC"))

def render_request_rows(df, table, id_col, name_col, detail_map, empty_msg="No requests found."):
    """Render request rows with Approve / Reject buttons in the LAST column."""
    if df.empty:
        st.info(empty_msg)
        return
    for _, rrow in df.iterrows():
        rid = rrow[id_col]
        cells = st.columns([1.2] + [1.6] * (len(detail_map) - 1) + [0.7, 0.7])
        for ci, (col_label, col_key) in enumerate(detail_map):
            with cells[ci]:
                val = rrow.get(col_key, "")
                if ci == 0:
                    st.markdown(f"**{val}**")
                else:
                    st.markdown(str(val))
        status_val = str(rrow.get("status", ""))
        if status_val == "Pending":
            with cells[-2]:
                if st.button("✅ Approve", key=f"apr_{table}_{rid}", use_container_width=True):
                    execute_query(f"UPDATE {table} SET status = 'Approved' WHERE {id_col} = ?", (rid,))
                    record_approval_history(table, rrow.get(name_col, ""), rrow.get("employee_id", ""), st.session_state.user_email, rrow.get(name_col, ""), "Approved", str(dict(rrow))[:200])
                    st.success("Approved")
                    st.rerun()
            with cells[-1]:
                if st.button("❌ Reject", key=f"rej_{table}_{rid}", use_container_width=True):
                    execute_query(f"UPDATE {table} SET status = 'Rejected' WHERE {id_col} = ?", (rid,))
                    record_approval_history(table, rrow.get(name_col, ""), rrow.get("employee_id", ""), st.session_state.user_email, rrow.get(name_col, ""), "Rejected", str(dict(rrow))[:200])
                    st.warning("Rejected")
                    st.rerun()
        else:
            with cells[-2]:
                st.markdown(f"`{status_val}`")


def download_letter_block(letter_text, label):
    """Small in-page letter template tool with TXT/PDF download."""
    st.markdown(f'<div class="letter-box">{letter_text}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Download as Text", letter_text, f"{label}.txt", "text/plain", key=f"lt_txt_{label}")
    with c2:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            lb = io.BytesIO()
            ld = SimpleDocTemplate(lb, pagesize=A4)
            els = [Paragraph(l or "&nbsp;", getSampleStyleSheet()["Normal"]) for l in letter_text.split("\n")]
            ld.build(els)
            lb.seek(0)
            st.download_button("⬇️ Download as PDF", lb.getvalue(), f"{label}.pdf", "application/pdf", key=f"lt_pdf_{label}")
        except Exception as e:
            st.caption(f"PDF unavailable: {e}")


if selected_menu == "Employee Dashboard":
    # ---------- Company website hero ----------
    dept_list = sorted(employees_df["department"].dropna().unique().tolist())
    city_count = employees_df["address"].str.split(",").str[0].nunique() if not employees_df.empty else 0
    avg_salary = float(employees_df["salary"].mean()) if not employees_df.empty else 0
    total_salary_cost = float(employees_df["salary"].sum()) if not employees_df.empty else 0
    open_roles = int(recruitment_df["openings"].sum()) if not recruitment_df.empty else 0
    pending_all = (
        (int((leave_requests_df["status"] == "Pending").sum()) if not leave_requests_df.empty else 0)
        + (int((expense_claims_df["status"] == "Pending").sum()) if not expense_claims_df.empty else 0)
        + (int((compoff_df["status"] == "Pending").sum()) if not compoff_df.empty else 0)
    )
    present_today = int((attendance_df["status"].isin(["Present", "WFH"]).sum()) if not attendance_df.empty else 0)

    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>BluePeak Solutions</h1>
            <p>People-first enterprise · Building great teams across India since 2012</p>
            <div class="hero-chips">
                <span class="hero-chip">👥 {len(employees_df)} Employees</span>
                <span class="hero-chip">🏢 {len(dept_list)} Departments</span>
                <span class="hero-chip">📍 {city_count} Cities</span>
                <span class="hero-chip">💼 {open_roles} Open Roles</span>
                <span class="hero-chip">💰 Avg CTC ₹{avg_salary:,.0f}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- KPI strip ----------
    kpis = [
        ("👥 Headcount", f"{len(employees_df):,}", "#2563eb"),
        ("✅ Present Today", present_today, "#059669"),
        ("🏠 Working Remote", int((employees_df["work_mode"] == "WFH").sum()), "#7c3aed"),
        ("📋 Pending Requests", pending_all, "#d97706"),
        ("💼 Open Positions", open_roles, "#dc2626"),
        ("💵 Monthly Payroll", f"₹{total_salary_cost/100000:.1f}Cr", "#0d9488"),
    ]
    kcols = st.columns(len(kpis))
    for col, (label, value, color) in zip(kcols, kpis):
        with col:
            st.markdown(
                f"<div class='metric-box' style='border-left-color:{color};'><div class='label'>{label}</div>"
                f"<div style='font-size:2.2rem; font-weight:800; margin-top:6px;'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    # ---------- Live stats ticker ----------
    ticker_items = [
        f"👥 <b>{len(employees_df)}</b> employees on board",
        f"✅ <b>{present_today}</b> present today",
        f"📋 <b>{pending_all}</b> approvals pending",
        f"💼 <b>{open_roles}</b> open positions",
        f"🏠 <b>{int((employees_df['work_mode'] == 'WFH').sum())}</b> working remotely",
        f"🏢 <b>{len(dept_list)}</b> departments",
        f"🎯 <b>{len(interview_df)}</b> interviews scheduled",
        f"🎓 <b>{len(learning_df)}</b> active learning tracks",
    ]
    ticker_html = "".join(f"<span><span class='tick-dot'>●</span> {item}</span>" for item in ticker_items)
    st.markdown(f"<div class='ticker-wrap'><div class='ticker'>{ticker_html}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Workforce Portal</div>", unsafe_allow_html=True)

    tab_overview, tab_dir, tab_analytics, tab_dept, tab_news, tab_perf, tab_celebrate = st.tabs(
        ["🏠 Overview", "👥 Directory", "📊 Analytics", "🏢 Departments", "📣 News", "🏆 Top Talent", "🎂 Celebrations"]
    )

    with tab_overview:
        c1, c2 = st.columns([1, 1.3])
        with c1:
            att_summary = attendance_df["status"].value_counts().reset_index() if not attendance_df.empty else pd.DataFrame(columns=["status", "count"])
            att_summary.columns = ["Status", "Count"]
            fig_att = px.pie(att_summary, names="Status", values="Count", hole=0.55, title="Attendance Split")
            fig_att.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_att, use_container_width=True)
        with c2:
            mode_summary = employees_df["work_mode"].value_counts().reset_index()
            mode_summary.columns = ["Mode", "Employees"]
            fig_mode = px.bar(mode_summary, x="Mode", y="Employees", color="Mode", title="Work Mode Distribution")
            fig_mode.update_layout(margin=dict(t=40, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig_mode, use_container_width=True)

        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown("<div class='card'><b>🌴 Leave Pipeline</b></div>", unsafe_allow_html=True)
            pending_leaves = leave_requests_df[leave_requests_df["status"] == "Pending"].head(5) if not leave_requests_df.empty else pd.DataFrame()
            st.dataframe(pending_leaves[["name", "leave_type", "start_date", "days"]] if not pending_leaves.empty else pd.DataFrame(columns=["name", "leave_type"]), hide_index=True, use_container_width=True)
        with d2:
            st.markdown("<div class='card'><b>🧾 Recent Expense Claims</b></div>", unsafe_allow_html=True)
            recent_exp = expense_claims_df.head(5) if not expense_claims_df.empty else pd.DataFrame()
            st.dataframe(recent_exp[["name", "category", "amount", "status"]] if not recent_exp.empty else pd.DataFrame(columns=["name", "category"]), hide_index=True, use_container_width=True)
        with d3:
            st.markdown("<div class='card'><b>🎉 New Joiners</b></div>", unsafe_allow_html=True)
            new_joiners = employees_df.sort_values("date_joined", ascending=False).head(5)
            st.dataframe(new_joiners[["name", "department", "date_joined"]], hide_index=True, use_container_width=True)

        # ---------- Employee Spotlight (advanced quick search) ----------
        st.markdown("<div class='section-title' style='font-size:1.2rem;'>🔎 Employee Spotlight</div>", unsafe_allow_html=True)
        spot_q = st.text_input("Type a name to spotlight an employee", placeholder="e.g. Aarav", key="spotlight_q")
        spot_df = employees_df[employees_df["name"].str.contains(spot_q, case=False, na=False)].head(4) if spot_q else employees_df.sample(min(4, len(employees_df)))
        if not spot_df.empty:
            spot_cols = st.columns(len(spot_df))
            for scol, (_, sp) in zip(spot_cols, spot_df.iterrows()):
                with scol:
                    initials = "".join(w[0] for w in str(sp["name"]).split()[:2]).upper()
                    st.markdown(
                        f"""
                        <div class='spotlight-card'>
                            <div class='spotlight-avatar'>{initials}</div>
                            <div>
                                <div class='spotlight-name'>{sp['name']}</div>
                                <div class='spotlight-meta'>{sp['role']} · {sp['department']}</div>
                                <span class='spotlight-tag'>{sp['work_mode']}</span>
                                <span class='spotlight-tag'>{sp['employee_id']}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with tab_dir:
        fc1, fc2, fc3 = st.columns([2, 1, 1])
        with fc1:
            search = st.text_input("🔍 Search by name, role or ID", placeholder="e.g. Aarav / Engineer / EMP-1020")
        with fc2:
            dept_filter = st.selectbox("Department", ["All"] + dept_list)
        with fc3:
            mode_filter = st.selectbox("Work Mode", ["All", "WFH", "Office", "Hybrid"])

        directory_df = employees_df.copy()
        if search:
            mask = (
                directory_df["name"].str.contains(search, case=False, na=False)
                | directory_df["role"].str.contains(search, case=False, na=False)
                | directory_df["employee_id"].str.contains(search, case=False, na=False)
            )
            directory_df = directory_df[mask]
        if dept_filter != "All":
            directory_df = directory_df[directory_df["department"] == dept_filter]
        if mode_filter != "All":
            directory_df = directory_df[directory_df["work_mode"] == mode_filter]

        st.caption(f"Showing **{len(directory_df)}** of {len(employees_df)} employees")
        st.dataframe(
            directory_df[["employee_id", "name", "email", "department", "role", "work_mode", "manager", "status"]],
            hide_index=True,
            use_container_width=True,
            height=420,
        )
        dl1, dl2 = st.columns([1, 3])
        with dl1:
            export_buffer = io.BytesIO()
            with pd.ExcelWriter(export_buffer, engine="xlsxwriter") as writer:
                directory_df.to_excel(writer, index=False, sheet_name="Employees")
                recruitment_df.to_excel(writer, index=False, sheet_name="Openings")
            export_buffer.seek(0)
            st.download_button(
                label="⬇️ Export Directory (Excel)",
                data=export_buffer.getvalue(),
                file_name="hrms_directory.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    with tab_analytics:
        a1, a2 = st.columns(2)
        with a1:
            dept_summary = employees_df.groupby("department").size().reset_index(name="Employees")
            fig_d = px.bar(dept_summary.sort_values("Employees"), x="Employees", y="department", orientation="h", color="Employees", title="Headcount by Department")
            fig_d.update_layout(margin=dict(t=40, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig_d, use_container_width=True)
        with a2:
            fig_h = px.histogram(employees_df, x="salary", nbins=30, title="Salary Distribution", color_discrete_sequence=["#1d4ed8"])
            fig_h.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_h, use_container_width=True)
        b1, b2 = st.columns(2)
        with b1:
            avg_dept = employees_df.groupby("department")["salary"].mean().round(0).reset_index()
            fig_avg = px.bar(avg_dept, x="department", y="salary", color="department", title="Average Salary by Department")
            fig_avg.update_layout(margin=dict(t=40, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig_avg, use_container_width=True)
        with b2:
            joined = employees_df.copy()
            joined["year"] = joined["date_joined"].str[:4]
            trend = joined.groupby("year").size().reset_index(name="New Hires")
            fig_t = px.line(trend, x="year", y="New Hires", markers=True, title="Hiring Trend")
            fig_t.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_t, use_container_width=True)

    with tab_dept:
        dept_icons = {"Engineering": "💻", "HR": "🤝", "Finance": "📊", "Sales": "📈", "Operations": "⚙️", "Marketing": "📣", "Support": "🎧"}
        dcols = st.columns(4)
        for i, dept in enumerate(dept_list):
            dstats = employees_df[employees_df["department"] == dept]
            with dcols[i % 4]:
                st.markdown(
                    f"""
                    <div class='dept-card'>
                        <div class='dept-icon'>{dept_icons.get(dept, '🏢')}</div>
                        <div class='dept-name'>{dept}</div>
                        <div class='dept-meta'>👥 {len(dstats)} employees</div>
                        <div class='dept-meta'>💰 Avg ₹{dstats['salary'].mean():,.0f}</div>
                        <div class='dept-meta'>🧭 {dstats['manager'].mode()[0] if not dstats.empty else '—'}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_news:
        if announcements_df.empty:
            st.info("No announcements yet.")
        else:
            for _, row in announcements_df.iterrows():
                st.markdown(
                    f"""
                    <div class='news-card'>
                        <div class='news-title'>📌 {row['title']}</div>
                        <div class='news-meta'>By {row['created_by']} · {row['created_at']}</div>
                        <div class='news-body'>{row['message']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_perf:
        p1, p2 = st.columns([1.2, 1])
        with p1:
            top_perf = performance_df.sort_values("score", ascending=False).head(10) if not performance_df.empty else pd.DataFrame()
            st.markdown("<div class='section-title' style='font-size:1.2rem;'>Top 10 Performers</div>", unsafe_allow_html=True)
            if not top_perf.empty:
                fig_p = px.bar(top_perf, x="score", y="employee", orientation="h", color="score", title="")
                fig_p.update_layout(margin=dict(t=10, b=0, l=0, r=0), showlegend=False, height=380)
                st.plotly_chart(fig_p, use_container_width=True)
            else:
                st.info("No performance data yet.")
        with p2:
            st.markdown("<div class='section-title' style='font-size:1.2rem;'>🌟 Key Contributions</div>", unsafe_allow_html=True)
            if not contrib_df.empty:
                for _, row in contrib_df.head(6).iterrows():
                    st.markdown(
                        f"<div class='news-card'><div class='news-title'>{row['employee']}</div><div class='news-body'>{row['contribution']} · <b>{row['impact']} impact</b></div></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No contributions recorded yet.")

    with tab_celebrate:
        st.markdown("<div class='section-title' style='font-size:1.2rem;'>🎂 Work Anniversaries — This Month</div>", unsafe_allow_html=True)
        celeb = employees_df.copy()
        celeb["join_month"] = celeb["date_joined"].str[5:7]
        this_month = f"{datetime.now().month:02d}"
        anniv = celeb[celeb["join_month"] == this_month].copy()
        if anniv.empty:
            st.info("No work anniversaries this month.")
        else:
            anniv["years"] = datetime.now().year - anniv["date_joined"].str[:4].astype(int)
            anniv = anniv.sort_values("years", ascending=False).head(12)
            acols = st.columns(4)
            for i, (_, arow) in enumerate(anniv.iterrows()):
                with acols[i % 4]:
                    st.markdown(
                        f"""
                        <div class='celeb-card'>
                            <div style='font-size:28px;'>{'🎉🥳🎊⭐'[i % 4]}</div>
                            <div class='celeb-name'>{arow['name']}</div>
                            <div class='celeb-meta'>{arow['department']} · joined {arow['date_joined']}</div>
                            <div class='celeb-years'>{arow['years']} year(s) at BluePeak</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        st.markdown("<div class='section-title' style='font-size:1.2rem;'>📅 Joining Timeline</div>", unsafe_allow_html=True)
        tl = celeb.groupby(celeb["date_joined"].str[:7]).size().reset_index(name="Joiners")
        fig_tl = px.bar(tl.tail(12), x="date_joined", y="Joiners", title="New Joiners by Month", color_discrete_sequence=["#1d4ed8"])
        fig_tl.update_layout(margin=dict(t=40, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig_tl, use_container_width=True)

elif selected_menu == "Employee Profiles":
    st.title("🧑‍💼 Employee Profiles")
    employees_list = employees_df["name"].tolist()
    # If opened via global search, preselect that employee
    default_idx = 0
    if st.session_state.get("profile_employee") in employees_list:
        default_idx = employees_list.index(st.session_state.pop("profile_employee"))
    selected_employee = st.selectbox("Select employee", employees_list, index=default_idx)
    emp = employees_df[employees_df["name"] == selected_employee].iloc[0]

    st.markdown(
        f"""
        <div class='profile-box'>
            <h3>{emp['name']}</h3>
            <div>{emp['role']} · {emp['department']}</div>
            <div>{emp['email']} · {emp['phone']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><b>Manager</b><div>{}</div></div>".format(emp['manager']), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><b>Work Mode</b><div>{}</div></div>".format(emp['work_mode']), unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><b>Salary</b><div>₹{:,}</div></div>".format(int(emp['salary'])), unsafe_allow_html=True)

    st.subheader("Profile Details")
    details = {
        "Employee ID": emp["employee_id"],
        "Department": emp["department"],
        "Role": emp["role"],
        "Status": emp["status"],
        "Location": emp["address"],
        "Joined On": emp["date_joined"],
    }
    st.json(details)

    st.subheader("Recent Attendance")
    att = attendance_df[attendance_df["employee_id"] == emp["employee_id"]].tail(5)
    st.dataframe(att[["date", "status"]], hide_index=True, use_container_width=True)

    st.subheader("Learning & Certifications")
    learning_rows = learning_df[learning_df["employee"] == emp["name"]]
    cert_rows = certs_df[certs_df["employee"] == emp["name"]]
    if not learning_rows.empty:
        st.dataframe(learning_rows, hide_index=True, use_container_width=True)
    else:
        st.info("No learning records found.")
    if not cert_rows.empty:
        st.dataframe(cert_rows, hide_index=True, use_container_width=True)
    else:
        st.info("No certifications found.")

elif selected_menu == "Employee Edit":
    st.title("✏️ Employee Edit")
    if not can_manage_employees:
        st.warning("You do not have permission to edit employee records.")
    else:
        employee_names = employees_df["name"].tolist()
        selected_employee = st.selectbox("Select employee to edit", employee_names)
        emp = employees_df[employees_df["name"] == selected_employee].iloc[0]
        with st.form("employee_edit_page_form"):
            name = st.text_input("Name", value=emp["name"])
            email = st.text_input("Email", value=emp["email"])
            department = st.selectbox("Department", ["Engineering", "HR", "Finance", "Sales", "Operations"], index=["Engineering", "HR", "Finance", "Sales", "Operations"].index(emp["department"]))
            role = st.text_input("Role", value=emp["role"])
            manager = st.text_input("Manager", value=emp["manager"])
            work_mode = st.selectbox("Work Mode", ["WFH", "Office", "Hybrid"], index=["WFH", "Office", "Hybrid"].index(emp["work_mode"]))
            salary = st.number_input("Salary", value=float(emp["salary"]), min_value=0.0, step=1000.0)
            phone = st.text_input("Phone", value=emp["phone"])
            address = st.text_input("Address", value=emp["address"])
            submit = st.form_submit_button("Save Changes")
            delete = st.form_submit_button("Delete Employee")

        if delete:
            execute_query("DELETE FROM employees WHERE employee_id = ?", (emp["employee_id"],))
            execute_query("DELETE FROM attendance WHERE employee_id = ?", (emp["employee_id"],))
            execute_query("DELETE FROM wfh WHERE employee_id = ?", (emp["employee_id"],))
            execute_query("DELETE FROM timesheets WHERE employee_id = ?", (emp["employee_id"],))
            execute_query("DELETE FROM comp_off WHERE employee_id = ?", (emp["employee_id"],))
            execute_query("DELETE FROM resignations WHERE employee_id = ?", (emp["employee_id"],))
            execute_query("DELETE FROM payroll WHERE employee_id = ?", (emp["employee_id"],))
            st.success(f"Employee {emp['name']} deleted successfully.")
            st.rerun()

        if submit:
            execute_query(
                "UPDATE employees SET name = ?, email = ?, department = ?, role = ?, manager = ?, work_mode = ?, salary = ?, phone = ?, address = ? WHERE employee_id = ?",
                (name, email, department, role, manager, work_mode, float(salary), phone, address, emp["employee_id"]),
            )
            st.success("Employee record updated successfully.")
            st.rerun()

        # ---------- Approve / Reject actions beside the employee table ----------
        st.subheader("Employee Approvals")
        st.caption("Approve or reject employees directly from the table. Use search to narrow the list.")
        action_search = st.text_input("🔍 Search employee", placeholder="Name / EMP-ID", key="emp_action_search")
        action_df = employees_df.copy()
        if action_search:
            action_df = action_df[
                action_df["name"].str.contains(action_search, case=False, na=False)
                | action_df["employee_id"].str.contains(action_search, case=False, na=False)
            ]
        action_df = action_df.head(15)
        if action_df.empty:
            st.info("No employees matched.")
        else:
            for _, erow in action_df.iterrows():
                ec1, ec2, ec3, ec4 = st.columns([2, 2, 1, 1])
                with ec1:
                    st.markdown(f"**{erow['name']}**")
                with ec2:
                    st.markdown(f"{erow['employee_id']} · {erow['department']}")
                with ec3:
                    if st.button("✅ Approve", key=f"emp_approve_{erow['employee_id']}"):
                        execute_query("UPDATE employees SET status = 'Approved' WHERE employee_id = ?", (erow["employee_id"],))
                        record_approval_history(
                            "Employee",
                            erow["name"],
                            erow["employee_id"],
                            st.session_state.user_email,
                            st.session_state.user_email,
                            "Approved",
                            f"Employee record approved ({erow['role']})",
                        )
                        st.success(f"{erow['name']} approved.")
                        st.rerun()
                with ec4:
                    if st.button("❌ Reject", key=f"emp_reject_{erow['employee_id']}"):
                        execute_query("UPDATE employees SET status = 'Rejected' WHERE employee_id = ?", (erow["employee_id"],))
                        record_approval_history(
                            "Employee",
                            erow["name"],
                            erow["employee_id"],
                            st.session_state.user_email,
                            st.session_state.user_email,
                            "Rejected",
                            f"Employee record rejected ({erow['role']})",
                        )
                        st.warning(f"{erow['name']} rejected.")
                        st.rerun()

elif selected_menu == "Attendance":
    st.title("🕐 Attendance")
    selected_date = st.date_input("Select date", datetime.today())
    with st.form("attendance_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        status = st.selectbox("Status", ["Present", "Absent", "Leave", "WFH", "Late"])
        submit = st.form_submit_button("Save Attendance")
    if submit:
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        execute_query(
            "INSERT INTO attendance (employee_id, name, date, status) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (emp["employee_id"], emp["name"], str(selected_date), status),
        )
        st.success(f"Attendance saved for {employee_name}.")
        st.rerun()

    # ---------- Attendance table with Present / Absent actions in the last column ----------
    att_date_filter = st.text_input("Filter by date (YYYY-MM-DD, blank = all)", key="att_date_filter")
    att_view = attendance_df.copy()
    if att_date_filter.strip():
        att_view = att_view[att_view["date"].astype(str).str.startswith(att_date_filter.strip())]
    att_view = att_view.head(25)

    if att_view.empty:
        st.info("No attendance records found.")
    else:
        for _, arow in att_view.iterrows():
            ac1, ac2, ac3, ac4, ac5 = st.columns([1.5, 1.5, 1.5, 1, 1])
            with ac1:
                st.markdown(f"**{arow['name']}**")
            with ac2:
                st.markdown(f"{arow['employee_id']}")
            with ac3:
                st.markdown(f"{arow['date']} · `{arow['status']}`")
            with ac4:
                if st.button("🟢 Present", key=f"att_present_{arow['id']}"):
                    execute_query("UPDATE attendance SET status = 'Present' WHERE id = ?", (arow["id"],))
                    st.success(f"Marked Present: {arow['name']}")
                    st.rerun()
            with ac5:
                if st.button("🔴 Absent", key=f"att_absent_{arow['id']}"):
                    execute_query("UPDATE attendance SET status = 'Absent' WHERE id = ?", (arow["id"],))
                    st.warning(f"Marked Absent: {arow['name']}")
                    st.rerun()

    # ---------- Total Present / Absent summary below the table ----------
    if not attendance_df.empty:
        total_present = int(attendance_df["status"].isin(["Present", "WFH"]).sum())
        total_absent = int((attendance_df["status"] == "Absent").sum())
        total_leave = int((attendance_df["status"] == "Leave").sum())
        total_records = len(attendance_df)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("✅ Total Present", total_present)
        s2.metric("❌ Total Absent", total_absent)
        s3.metric("🌴 On Leave", total_leave)
        s4.metric("📋 Total Records", total_records)

elif selected_menu == "WFH / WFO":
    st.title("🏠 WFH / WFO")
    with st.form("wfh_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        mode = st.selectbox("Mode", ["WFH", "Office", "Hybrid"])
        reason = st.text_area("Reason")
        submit = st.form_submit_button("Submit")
    if submit:
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        execute_query(
            "INSERT INTO wfh (employee_id, name, mode, reason, date) VALUES (?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], mode, reason, str(datetime.today().date())),
        )
        st.success(f"{employee_name} updated to {mode}.")
        st.rerun()
    st.dataframe(wfh_df, hide_index=True, use_container_width=True)

elif selected_menu == "Project Timesheets":
    st.title("⏱️ Project Timesheets")
    with st.form("timesheet_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        project = st.text_input("Project Name")
        hours = st.number_input("Hours", min_value=0.5, max_value=24.0, step=0.5)
        submit = st.form_submit_button("Add Timesheet")
    if submit:
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        execute_query(
            "INSERT INTO timesheets (employee_id, name, project, hours, date) VALUES (?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], project, float(hours), str(datetime.today().date())),
        )
        st.success("Timesheet added.")
        st.rerun()
    st.dataframe(timesheets_df, hide_index=True, use_container_width=True)

elif selected_menu == "Admin Profile":
    st.title("👤 Admin Profile")
    user_email = st.session_state.get("user_email", "")
    admin_row = employees_df[employees_df["email"].str.lower() == user_email.lower()] if not employees_df.empty else pd.DataFrame()
    st.markdown(
        f"""
        <div class='profile-box'>
            <h3>{admin_row.iloc[0]['name'] if not admin_row.empty else 'Administrator'}</h3>
            <div>{user_email}</div>
            <div>Role: <b>{st.session_state.get('user_role', '').title()}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='card'><b>👤 User ID</b><div>{}</div></div>".format(admin_row.iloc[0]['employee_id'] if not admin_row.empty else 'ADMIN-001'), unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'><b>📛 Name</b><div>{}</div></div>".format(admin_row.iloc[0]['name'] if not admin_row.empty else 'Administrator'), unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card'><b>📧 Email</b><div>{}</div></div>".format(user_email), unsafe_allow_html=True)
    st.subheader("Account Actions")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = ""
        st.rerun()

elif selected_menu == "Comp-Off":
    st.title("🎁 Comp-Off")
    with st.form("compoff_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        hours = st.number_input("Comp-Off Hours", min_value=1, max_value=24)
        reason = st.text_area("Reason")
        submit = st.form_submit_button("Request Comp-Off")
    if submit:
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        execute_query(
            "INSERT INTO comp_off (employee_id, name, reason, hours, status) VALUES (?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], reason, int(hours), "Pending"),
        )
        st.success("Comp-Off request submitted.")
        st.rerun()
    co_q = st.text_input("🔍 Search comp-off requests", placeholder="Name / reason / status", key="co_search")
    co_view = compoff_df.copy()
    if co_q.strip():
        co_view = co_view[co_view.apply(lambda r: co_q.lower() in str(r.to_dict()).lower(), axis=1)]
    render_request_rows(
        co_view, "comp_off", "id", "name",
        [("Employee", "name"), ("Hours", "hours"), ("Reason", "reason"), ("Date", "requested_on" if "requested_on" in compoff_df.columns else "reason")],
        empty_msg="No comp-off requests found.",
    )

elif selected_menu == "Resignation alerts":
    st.title("🚪 Resignation alerts")
    with st.form("resignation_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        reason = st.text_area("Reason")
        submit = st.form_submit_button("Submit resignation")
    if submit:
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        execute_query(
            "INSERT INTO resignations (employee_id, name, reason, status, date) VALUES (?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], reason, "Pending", str(datetime.today().date())),
        )
        st.success("Resignation alert saved.")
        st.rerun()
    re_q = st.text_input("🔍 Search resignation alerts", placeholder="Name / reason / status", key="re_search")
    re_view = resignations_df.copy()
    if re_q.strip():
        re_view = re_view[re_view.apply(lambda r: re_q.lower() in str(r.to_dict()).lower(), axis=1)]
    render_request_rows(
        re_view, "resignations", "id", "name",
        [("Employee", "name"), ("Reason", "reason"), ("Date", "date")],
        empty_msg="No resignation alerts found.",
    )

elif selected_menu == "Onboarding":
    st.title("👋 Onboarding")
    with st.form("onboarding_form"):
        name = st.text_input("New employee name")
        role = st.text_input("Role")
        stage = st.selectbox("Stage", ["Offer Letter Sent", "Documents Verified", "IT Setup", "Training", "Joining Ready"])
        submit = st.form_submit_button("Add onboarding")
    if submit:
        execute_query(
            "INSERT INTO onboarding (employee_id, name, role, stage, date) VALUES (?, ?, ?, ?, ?)",
            (f"EMP-{datetime.now().strftime('%f')}", name, role, stage, str(datetime.today().date())),
        )
        st.success(f"Onboarding updated for {name}.")
        st.rerun()
    st.dataframe(onboarding_df, hide_index=True, use_container_width=True)

elif selected_menu == "Learning Management":
    st.title("🎓 Learning Management")
    with st.form("learning_form"):
        course = st.text_input("Course name")
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        progress = st.slider("Progress %", 0, 100, 50)
        status = st.selectbox("Status", ["In Progress", "Completed", "Not Started"])
        submit = st.form_submit_button("Add learning item")
    if submit:
        execute_query(
            "INSERT INTO learning (course, employee, progress, status) VALUES (?, ?, ?, ?)",
            (course, employee_name, int(progress), status),
        )
        st.success("Learning record added.")
        st.rerun()
    st.dataframe(learning_df, hide_index=True, use_container_width=True)

elif selected_menu == "Professional Certifications":
    st.title("📜 Professional Certifications")
    with st.form("cert_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        certification = st.text_input("Certification")
        expiry = st.date_input("Expiry", datetime.today())
        submit = st.form_submit_button("Add certification")
    if submit:
        execute_query(
            "INSERT INTO certifications (employee, certification, expiry) VALUES (?, ?, ?)",
            (employee_name, certification, str(expiry)),
        )
        st.success("Certification added.")
        st.rerun()
    st.dataframe(certs_df, hide_index=True, use_container_width=True)

elif selected_menu == "Employee Contributions":
    st.title("🌟 Employee Contributions")
    with st.form("contrib_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        contribution = st.text_area("Contribution details")
        impact = st.selectbox("Impact", ["High", "Medium", "Low"])
        submit = st.form_submit_button("Save contribution")
    if submit:
        execute_query(
            "INSERT INTO contributions (employee, contribution, impact) VALUES (?, ?, ?)",
            (employee_name, contribution, impact),
        )
        st.success("Contribution saved.")
        st.rerun()
    st.dataframe(contrib_df, hide_index=True, use_container_width=True)

elif selected_menu == "Recruitment":
    st.title("💼 Recruitment")
    with st.form("recruitment_form"):
        title = st.text_input("Job title")
        location = st.text_input("Location")
        openings = st.number_input("Openings", min_value=1, max_value=20)
        status = st.selectbox("Status", ["Open", "Closed", "In Review"])
        submit = st.form_submit_button("Add job opening")
    if submit:
        execute_query(
            "INSERT INTO recruitment (title, location, openings, status) VALUES (?, ?, ?, ?)",
            (title, location, int(openings), status),
        )
        st.success("Recruitment record added.")
        st.rerun()
    st.dataframe(recruitment_df, hide_index=True, use_container_width=True)

elif selected_menu == "Payroll":
    st.title("💰 Payroll")
    with st.form("payroll_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        basic = st.number_input("Basic Salary", min_value=0, step=1000)
        bonus = st.number_input("Bonus", min_value=0, step=500)
        submit = st.form_submit_button("Save payroll")
    if submit:
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        execute_query(
            "INSERT INTO payroll (employee_id, name, basic_salary, bonus, net_pay) VALUES (?, ?, ?, ?, ?) ON CONFLICT(employee_id) DO UPDATE SET basic_salary=excluded.basic_salary, bonus=excluded.bonus, net_pay=excluded.net_pay",
            (emp["employee_id"], emp["name"], float(basic), float(bonus), float(basic + bonus)),
        )
        st.success("Payroll updated.")
        st.rerun()
    st.dataframe(payroll_df, hide_index=True, use_container_width=True)

elif selected_menu == "Performance":
    st.title("📈 Performance")
    with st.form("performance_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        score = st.slider("Performance score", 0, 100, 80)
        rating = st.selectbox("Rating", ["Excellent", "Very Good", "Good", "Needs Improvement"])
        submit = st.form_submit_button("Save review")
    if submit:
        execute_query(
            "INSERT INTO performance (employee, score, rating) VALUES (?, ?, ?)",
            (employee_name, int(score), rating),
        )
        st.success("Performance review saved.")
        st.rerun()
    st.dataframe(performance_df, hide_index=True, use_container_width=True)

elif selected_menu == "Analytics":
    st.title("📊 Analytics")
    if not employees_df.empty:
        dep = employees_df.groupby("department").size().reset_index(name="count")
        fig1 = px.bar(dep, x="department", y="count", title="Employees by Department")
        st.plotly_chart(fig1, use_container_width=True)
        salary_chart = employees_df[["name", "salary"]].copy()
        fig2 = px.bar(salary_chart, x="name", y="salary", title="Salary Overview")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available yet.")

elif selected_menu == "Leave Calendar":
    st.title("📅 Leave Calendar")
    selected_month = st.selectbox("Month", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    selected_year = st.selectbox("Year", [2025, 2026, 2027])
    month_index = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].index(selected_month) + 1
    days_in_month = 31 if month_index in [1, 3, 5, 7, 8, 10, 12] else 30 if month_index in [4, 6, 9, 11] else 28
    month_data = []
    for day in range(1, days_in_month + 1):
        date_str = f"{selected_year}-{month_index:02d}-{day:02d}"
        names = leave_requests_df[(leave_requests_df["status"] == "Approved") & (leave_requests_df["start_date"].str.startswith(date_str[:7]))]
        if not names.empty:
            names_on_day = ", ".join(names["name"].tolist())
        else:
            names_on_day = "-"
        month_data.append({"Date": date_str, "Approved Leave": names_on_day})
    st.dataframe(pd.DataFrame(month_data), hide_index=True, use_container_width=True)

elif selected_menu == "Payslips":
    st.title("🧾 Payslips")
    employee_name = st.selectbox("Employee", employees_df["name"].tolist())
    emp = employees_df[employees_df["name"] == employee_name].iloc[0]
    month_label = st.selectbox("Payslip Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    payroll_entry = payroll_df[payroll_df["employee_id"] == emp["employee_id"]]
    if payroll_entry.empty:
        st.warning("No payroll record found for this employee.")
    else:
        row = payroll_entry.iloc[0]
        basic = float(row["basic_salary"])
        bonus = float(row["bonus"])
        net = float(row["net_pay"])
        pdf_buffer = generate_payslip_pdf(emp["name"], emp["employee_id"], basic, bonus, month_label)
        if st.button("Generate Payslip Record"):
            execute_query(
                "INSERT INTO payslips (employee_id, employee_name, month, basic_salary, bonus, net_pay, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (emp["employee_id"], emp["name"], month_label, basic, bonus, net, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            st.success("Payslip record saved.")
            st.rerun()
        st.download_button(
            label="Download PDF Payslip",
            data=pdf_buffer.getvalue(),
            file_name=f"payslip_{emp['employee_id']}_{month_label.lower()}.pdf",
            mime="application/pdf",
        )
    st.dataframe(payslip_df[["employee_name", "month", "basic_salary", "bonus", "net_pay", "generated_at"]], hide_index=True, use_container_width=True)

elif selected_menu == "Employee Documents":
    st.title("📁 Employee Documents")
    doc_employee = st.selectbox("Employee", employees_df["name"].tolist())
    emp = employees_df[employees_df["name"] == doc_employee].iloc[0]
    uploaded_file = st.file_uploader("Upload document", type=["pdf", "doc", "docx", "jpg", "png", "jpeg"])
    document_type = st.selectbox("Document Type", ["Offer Letter", "ID Proof", "Bank Details", "Education Certificate", "Experience Letter", "Other"])
    if uploaded_file is not None and st.button("Save Document"):
        doc_dir = BASE_DIR / "employee_documents" / emp["employee_id"]
        doc_dir.mkdir(parents=True, exist_ok=True)
        target_path = doc_dir / uploaded_file.name
        target_path.write_bytes(uploaded_file.getvalue())
        execute_query(
            "INSERT INTO employee_documents (employee_id, employee_name, file_name, file_path, uploaded_at, document_type) VALUES (?, ?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], uploaded_file.name, str(target_path), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), document_type),
        )
        st.success("Document uploaded successfully.")
        st.rerun()
    employee_docs = document_df[document_df["employee_id"] == emp["employee_id"]]
    if employee_docs.empty:
        st.info("No documents uploaded for this employee yet.")
    else:
        st.dataframe(employee_docs[["file_name", "document_type", "uploaded_at"]], hide_index=True, use_container_width=True)

elif selected_menu == "Recruiter Interviews":
    st.title("🎯 Recruiter Interviews")
    with st.form("interview_form"):
        candidate_name = st.text_input("Candidate Name")
        role = st.text_input("Role")
        interviewer = st.text_input("Interviewer")
        interview_date = st.date_input("Interview Date", datetime.today())
        stage = st.selectbox("Stage", ["Screening", "Technical", "Manager Round", "HR Round", "Offer"])
        status = st.selectbox("Status", ["Scheduled", "Completed", "Selected", "Rejected", "Hold"])
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Save Interview")
    if submit:
        execute_query(
            "INSERT INTO recruiter_interviews (candidate_name, role, interviewer, interview_date, stage, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (candidate_name, role, interviewer, str(interview_date), stage, status, notes),
        )
        st.success("Interview record saved.")
        st.rerun()
    st.dataframe(interview_df[["candidate_name", "role", "interviewer", "interview_date", "stage", "status"]], hide_index=True, use_container_width=True)

elif selected_menu == "Background Verification":
    st.title("🔎 Background Verification")
    with st.form("verification_form"):
        employee_name = st.selectbox("Employee", employees_df["name"].tolist())
        emp = employees_df[employees_df["name"] == employee_name].iloc[0]
        check_type = st.selectbox("Check Type", ["Identity Verification", "Employment Check", "Education Check", "Reference Check", "Police Verification"])
        status = st.selectbox("Status", ["Pending", "In Progress", "Verified", "Rejected"])
        check_date = st.date_input("Check Date", datetime.today())
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Save Verification")
    if submit:
        execute_query(
            "INSERT INTO background_checks (employee_id, employee_name, check_type, status, check_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], check_type, status, str(check_date), notes),
        )
        st.success("Background verification record saved.")
        st.rerun()
    st.dataframe(background_df[["employee_name", "check_type", "status", "check_date", "notes"]], hide_index=True, use_container_width=True)

elif selected_menu == "Onboarding Checklist":
    st.title("✅ Onboarding Checklist Tracker")
    with st.form("onboarding_checklist_form"):
        checklist_employee = st.selectbox("Employee", employees_df["name"].tolist())
        emp = employees_df[employees_df["name"] == checklist_employee].iloc[0]
        checklist_item = st.text_input("Checklist Item")
        item_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        due_date = st.date_input("Due Date", datetime.today())
        assigned_to = st.text_input("Assigned To")
        submit = st.form_submit_button("Add Checklist")
    if submit:
        execute_query(
            "INSERT INTO onboarding_checklists (employee_id, employee_name, checklist_item, status, due_date, assigned_to) VALUES (?, ?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], checklist_item, item_status, str(due_date), assigned_to),
        )
        st.success("Checklist item added.")
        st.rerun()
    st.dataframe(onboarding_checklist_df[["employee_name", "checklist_item", "status", "due_date", "assigned_to"]], hide_index=True, use_container_width=True)

elif selected_menu == "Payroll Summary":
    st.title("💼 Payroll Summary Report")
    if payroll_df.empty:
        st.info("No payroll data available yet.")
    else:
        payroll_summary = payroll_df.groupby("name").agg(total_salary=("basic_salary", "sum"), bonus=("bonus", "sum"), net_pay=("net_pay", "sum")).reset_index()
        total_cost = payroll_summary["net_pay"].sum()
        avg_salary = payroll_summary["net_pay"].mean()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Payroll", f"₹{total_cost:,.0f}")
        col2.metric("Average Net Pay", f"₹{avg_salary:,.0f}")
        col3.metric("Employees with Payroll", len(payroll_summary))
        st.dataframe(payroll_summary, hide_index=True, use_container_width=True)

elif selected_menu == "Exit Workflow":
    st.title("🚪 Employee Resignation & Exit Workflow")
    with st.form("exit_workflow_form"):
        exit_employee = st.selectbox("Employee", employees_df["name"].tolist())
        emp = employees_df[employees_df["name"] == exit_employee].iloc[0]
        resignation_date = st.date_input("Resignation Date", datetime.today())
        last_working_day = st.date_input("Last Working Day", datetime.today())
        exit_status = st.selectbox("Exit Status", ["Pending", "Notice Period", "Exit In Progress", "Completed"])
        reason = st.text_area("Reason")
        notes = st.text_area("Notes")
        save_exit = st.form_submit_button("Save Exit Workflow")
    if save_exit:
        execute_query(
            "INSERT INTO exit_workflows (employee_id, employee_name, resignation_date, last_working_day, exit_status, reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (emp["employee_id"], emp["name"], str(resignation_date), str(last_working_day), exit_status, reason, notes),
        )
        st.success("Exit workflow saved.")
        st.rerun()
    st.dataframe(exit_workflow_df[["employee_name", "resignation_date", "last_working_day", "exit_status", "reason"]], hide_index=True, use_container_width=True)

elif selected_menu == "HR Letter Templates":
    st.title("📄 HR Letter Templates")
    template_type = st.selectbox("Select template", [
        "Offer Letter",
        "Exit Letter",
        "Relieving Letter",
        "Bonus Letter",
        "Hike Letter",
        "Medical Assistance Letter",
        "Travel Letter",
        "Leave Application – Annual Leave",
        "Leave Application – Casual Leave",
        "Leave Application – Sick Leave",
        "Leave Application – Maternity Leave",
        "Leave Application – Paternity Leave",
        "Leave Application – Comp-Off",
        "Leave Application – Unpaid Leave",
        "Payslip Request Letter",
        "Payslip Correction Request",
    ])

    leave_type_name = template_type.replace("Leave Application – ", "") if template_type.startswith("Leave Application") else ""
    leave_start = st.date_input("Leave Start Date", datetime.today()) if leave_type_name else None
    leave_end = st.date_input("Leave End Date", datetime.today()) if leave_type_name else None
    leave_days = (leave_end - leave_start).days + 1 if leave_type_name else 0
    leave_reason = st.text_area("Reason for Leave", "Please mention the reason for your leave request.") if leave_type_name else ""
    employee_name = st.selectbox("Employee", employees_df["name"].tolist())
    emp = employees_df[employees_df["name"] == employee_name].iloc[0]
    company_name = st.text_input("Company Name", "BluePeak Solutions Pvt Ltd")
    manager_name = st.text_input("Manager / HR Name", "Prabal Mehta")
    subject_line = st.text_input("Subject", f"{template_type} for {emp['name']}")
    effective_date = st.date_input("Effective Date", datetime.today())
    extra_note = st.text_area("Extra Matter / Additional Details", "This letter is issued in accordance with company policy and mutually agreed terms.")

    if template_type.startswith("Leave Application"):
        letter_text = (
            f"To,\n{manager_name}\nHR Department\n{company_name}\n\n"
            f"Date: {datetime.today().strftime('%d %B %Y')}\n\n"
            f"Subject: Application for {leave_type_name}\n\n"
            f"Dear {manager_name},\n\n"
            f"I, {emp['name']} (Employee ID: {emp['employee_id']}), working as {emp['role']} in the {emp['department']} department, "
            f"would like to request {leave_type_name} for {leave_days} day(s), from {leave_start.strftime('%d %B %Y')} to {leave_end.strftime('%d %B %Y')}.\n\n"
            f"Reason: {leave_reason}\n\n"
            f"I will ensure that my pending responsibilities are handed over appropriately and that my team is informed before the leave begins. "
            f"I shall remain reachable on email/phone for any urgent matters, if required.\n\n"
            f"Kindly consider and approve my leave request.\n\n"
            f"{extra_note}\n\n"
            f"Thanking you,\nYours sincerely,\n{emp['name']}\n{emp['employee_id']} - {emp['role']}"
        )
    elif template_type == "Payslip Request Letter":
        letter_text = (
            f"To,\n{manager_name}\nHR / Payroll Department\n{company_name}\n\n"
            f"Date: {datetime.today().strftime('%d %B %Y')}\n\n"
            f"Subject: Request for Payslip Issuance\n\n"
            f"Dear {manager_name},\n\n"
            f"I, {emp['name']} (Employee ID: {emp['employee_id']}), am writing to request a copy of my payslip(s) for the month of {effective_date.strftime('%B %Y')}. "
            f"I require the payslip for documentation and verification purposes.\n\n"
            f"Kindly issue the payslip at the earliest convenience or direct me to the portal where it can be downloaded.\n\n"
            f"Thanking you,\nYours sincerely,\n{emp['name']}\n{emp['employee_id']} - {emp['role']}"
        )
    elif template_type == "Payslip Correction Request":
        letter_text = (
            f"To,\n{manager_name}\nHR / Payroll Department\n{company_name}\n\n"
            f"Date: {datetime.today().strftime('%d %B %Y')}\n\n"
            f"Subject: Request for Correction in Payslip - {effective_date.strftime('%B %Y')}\n\n"
            f"Dear {manager_name},\n\n"
            f"I, {emp['name']} (Employee ID: {emp['employee_id']}), have reviewed my payslip for {effective_date.strftime('%B %Y')} and noticed a discrepancy that requires correction.\n\n"
            f"Details of the discrepancy: {extra_note}\n\n"
            f"I kindly request the payroll team to verify the figures and issue a corrected payslip. I am happy to provide any supporting documents needed.\n\n"
            f"Thanking you,\nYours sincerely,\n{emp['name']}\n{emp['employee_id']} - {emp['role']}"
        )
    elif template_type == "Offer Letter":
        letter_text = (
            f"{company_name}\n\n"
            f"Date: {datetime.today().strftime('%d %B %Y')}\n\n"
            f"Dear {emp['name']},\n\n"
            f"Subject: Offer of Employment - {emp['role']}\n\n"
            f"Following your interviews with us, we are delighted to offer you the position of {emp['role']} in the {emp['department']} department with {company_name}, "
            f"reporting to {manager_name}. Your employment will commence on {effective_date.strftime('%d %B %Y')}.\n\n"
            f"1. Compensation: Your annual compensation will be as per the approved hiring plan and communicated through your payroll records.\n"
            f"2. Work Location & Mode: Your primary work location will be {emp['address']}, with work mode as per company policy.\n"
            f"3. Probation: You will be on probation for six months, during which your performance will be reviewed.\n"
            f"4. Confidentiality: This offer is subject to the company policies, confidentiality obligations, and performance expectations.\n\n"
            f"To accept this offer, please sign and return a copy of this letter. We are confident that your skills and experience will add value to the team, and we look forward to welcoming you aboard.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}\n\n"
            f"Accepted & Agreed: ______________________  ({emp['name']})"
        )
    elif template_type == "Exit Letter":
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"We are pleased to offer you the position of {emp['role']} in the {emp['department']} department with {company_name}. "
            f"This offer is effective from {effective_date.strftime('%d %B %Y')} and is subject to the company policies, confidentiality obligations, and performance expectations.\n\n"
            f"Your annual compensation will be in line with the approved hiring plan and will be communicated through your payroll records.\n\n"
            f"We are confident that your skills and experience will add value to the team. We look forward to welcoming you aboard.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )
    elif template_type == "Exit Letter":
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"This letter confirms that your employment with {company_name} will be formally concluded in accordance with the notice period and exit process. "
            f"Your resignation dated {effective_date.strftime('%d %B %Y')} has been acknowledged and will be processed as per company policy.\n\n"
            f"Please return all company assets, documents, and access credentials before your final exit.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )
    elif template_type == "Relieving Letter":
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"This is to confirm that your employment with {company_name} has formally ended on {effective_date.strftime('%d %B %Y')}. "
            f"We appreciate your contributions during your tenure and confirm that you have fulfilled all obligations to the organization.\n\n"
            f"The company is issuing this relieving letter as proof of separation and acknowledges your services rendered.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )
    elif template_type == "Bonus Letter":
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"This is to inform you that the Management has approved a performance bonus for the financial period ending {effective_date.strftime('%d %B %Y')}. "
            f"This bonus is a recognition of your contribution, dedication, and consistent performance in the organization.\n\n"
            f"The approved amount will be reflected in your payroll and communicated through the designated payroll process.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )
    elif template_type == "Hike Letter":
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"We are pleased to inform you that your compensation has been revised effective {effective_date.strftime('%d %B %Y')}. "
            f"This revision reflects your performance, contribution, and continued commitment to the organization.\n\n"
            f"The revised compensation terms will be implemented in the payroll cycle and will be communicated through your official salary records.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )
    elif template_type == "Medical Assistance Letter":
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"This letter confirms that {company_name} has approved medical assistance support in accordance with the company policy and applicable terms. "
            f"The assistance is intended to support medical expenses and to ensure employee well-being.\n\n"
            f"The details of the support will be managed through the HR and finance team in line with documentation and policy guidelines.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )
    else:
        letter_text = (
            f"Dear {emp['name']},\n\n"
            f"This letter is issued to confirm the travel arrangement approved by {company_name} for official purposes. "
            f"The company has approved travel support for the business requirement as communicated by your reporting authority.\n\n"
            f"All travel arrangements should be in accordance with the company travel policy and duly approved expenses will be reimbursed as per policy.\n\n"
            f"{extra_note}\n\n"
            f"Sincerely,\n{manager_name}\nHR Department\n{company_name}"
        )

    st.subheader(subject_line)
    st.markdown(f'<div class="letter-box">{letter_text}</div>', unsafe_allow_html=True)

    col_txt, col_pdf = st.columns(2)
    with col_txt:
        st.download_button(
            label="Download Template as Text",
            data=letter_text,
            file_name=f"{template_type.lower().replace(' ', '_')}_{emp['name'].lower().replace(' ', '_')}.txt",
            mime="text/plain",
        )
    with col_pdf:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

            pdf_buf = io.BytesIO()
            pdf_doc = SimpleDocTemplate(pdf_buf, pagesize=A4)
            pstyles = getSampleStyleSheet()
            pelements = []
            for pline in letter_text.split("\n"):
                pelements.append(Paragraph(pline.replace("&", "&amp;").replace("<", "&lt;") or "&nbsp;", pstyles["Normal"]))
                pelements.append(Spacer(1, 4))
            pdf_doc.build(pelements)
            pdf_buf.seek(0)
            st.download_button(
                label="Download Template as PDF",
                data=pdf_buf.getvalue(),
                file_name=f"{template_type.lower().replace(' ', '_')}_{emp['name'].lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
            )
        except Exception as pexc:
            st.caption(f"PDF export unavailable: {pexc}")

elif selected_menu == "Leave Management":
    st.title("🌴 Leave Management")
    with st.form("leave_form"):
        l_emp = st.selectbox("Employee", employees_df["name"].tolist())
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            l_type = st.selectbox("Leave Type", ["Annual Leave", "Casual Leave", "Sick Leave", "Maternity Leave", "Paternity Leave", "Comp-Off", "Unpaid Leave"])
        with lc2:
            l_start = st.date_input("Start Date", datetime.today())
        with lc3:
            l_end = st.date_input("End Date", datetime.today())
        l_reason = st.text_area("Reason")
        if st.form_submit_button("Submit Leave Request"):
            l_emp_row = employees_df[employees_df["name"] == l_emp].iloc[0]
            days = max(1, (l_end - l_start).days + 1)
            execute_query(
                "INSERT INTO leave_requests (employee_id, name, leave_type, start_date, end_date, days, reason, status, requested_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (l_emp_row["employee_id"], l_emp, l_type, str(l_start), str(l_end), days, l_reason, "Pending", st.session_state.user_email),
            )
            st.success(f"Leave request submitted for {l_emp} ({days} day(s)).")
            st.rerun()

    st.subheader("Leave Requests")
    lst1, lst2 = st.columns(2)
    with lst1:
        l_status_filter = st.selectbox("Status", ["All", "Pending", "Approved", "Rejected"])
    with lst2:
        l_search = st.text_input("🔍 Search employee", key="leave_search")
    l_view = leave_requests_df.copy()
    if l_status_filter != "All":
        l_view = l_view[l_view["status"] == l_status_filter]
    if l_search:
        l_view = l_view[l_view["name"].str.contains(l_search, case=False, na=False)]
    l_view = l_view.head(30)
    if can_approve and not l_view.empty:
        render_request_rows(l_view, "leave_requests", "id", "name",
                            [("Employee", "name"), ("Type", "leave_type"), ("Dates", "start_date"), ("Days", "days"), ("Reason", "reason")])
    else:
        st.dataframe(l_view[["name", "leave_type", "start_date", "end_date", "days", "reason", "status"]], hide_index=True, use_container_width=True)

    lm1, lm2, lm3 = st.columns(3)
    lm1.metric("⏳ Pending", int((leave_requests_df["status"] == "Pending").sum()))
    lm2.metric("✅ Approved", int((leave_requests_df["status"] == "Approved").sum()))
    lm3.metric("❌ Rejected", int((leave_requests_df["status"] == "Rejected").sum()))

    with st.expander("📄 Quick Leave Application Letter"):
        l_emp_row = employees_df.iloc[0]
        if not l_view.empty:
            l_emp_row = employees_df[employees_df["name"] == l_view.iloc[0]["name"]].iloc[0]
        letter = (f"To,\nHR Department\n\nDate: {datetime.today().strftime('%d %B %Y')}\n\nSubject: Application for Leave\n\n"
                  f"Dear Sir/Madam,\n\nI, {l_emp_row['name']} (Employee ID: {l_emp_row['employee_id']}), would like to request leave.\n"
                  f"Kindly consider and approve my request.\n\nYours sincerely,\n{l_emp_row['name']}")
        download_letter_block(letter, "leave_application")

elif selected_menu == "Expense Claims":
    st.title("🧾 Expense Claims")
    with st.form("expense_form"):
        e_emp = st.selectbox("Employee", employees_df["name"].tolist())
        ec1, ec2 = st.columns(2)
        with ec1:
            e_cat = st.selectbox("Category", ["Travel", "Food", "Conference", "Equipment", "Internet", "Other"])
            e_amt = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        with ec2:
            e_desc = st.text_area("Description")
        if st.form_submit_button("Submit Expense Claim"):
            e_emp_row = employees_df[employees_df["name"] == e_emp].iloc[0]
            execute_query(
                "INSERT INTO expense_claims (employee_id, name, category, amount, description, status, submitted_on) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (e_emp_row["employee_id"], e_emp, e_cat, float(e_amt), e_desc, "Pending", str(datetime.today().date())),
            )
            st.success("Expense claim submitted.")
            st.rerun()

    st.subheader("Expense Claims")
    e_view = expense_claims_df.copy().head(30)
    if can_approve and not e_view.empty:
        render_request_rows(e_view, "expense_claims", "id", "name",
                            [("Employee", "name"), ("Category", "category"), ("Amount", "amount"), ("Description", "description"), ("Date", "submitted_on")])
    else:
        st.dataframe(e_view[["name", "category", "amount", "description", "status", "submitted_on"]], hide_index=True, use_container_width=True)
    if not expense_claims_df.empty:
        em1, em2 = st.columns(2)
        em1.metric("💰 Total Claimed", f"₹{expense_claims_df['amount'].sum():,.0f}")
        em2.metric("⏳ Pending", int((expense_claims_df["status"] == "Pending").sum()))

elif selected_menu == "Announcements":
    st.title("📣 Announcements")
    with st.form("announcement_form"):
        a_title = st.text_input("Title")
        a_msg = st.text_area("Message")
        if st.form_submit_button("Publish Announcement"):
            execute_query(
                "INSERT INTO announcements (title, message, created_by, created_at) VALUES (?, ?, ?, ?)",
                (a_title, a_msg, st.session_state.user_email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            st.success("Announcement published.")
            st.rerun()
    for _, arow in announcements_df.iterrows():
        st.markdown(
            f"""<div class='news-card'><div class='news-title'>📌 {arow['title']}</div>
            <div class='news-meta'>By {arow['created_by']} · {arow['created_at']}</div>
            <div class='news-body'>{arow['message']}</div></div>""",
            unsafe_allow_html=True,
        )

elif selected_menu == "Asset Requests":
    st.title("💻 Asset Requests")
    with st.form("asset_form"):
        as_emp = st.selectbox("Employee", employees_df["name"].tolist())
        as_type = st.selectbox("Asset Type", ["Laptop", "Laptop Upgrade", "Monitor", "Keyboard/Mouse", "Headset", "Access Card", "Other"])
        as_reason = st.text_area("Reason")
        if st.form_submit_button("Submit Asset Request"):
            as_emp_row = employees_df[employees_df["name"] == as_emp].iloc[0]
            execute_query(
                "INSERT INTO asset_requests (employee_id, name, asset_type, reason, status, requested_on) VALUES (?, ?, ?, ?, ?, ?)",
                (as_emp_row["employee_id"], as_emp, as_type, as_reason, "Pending", str(datetime.today().date())),
            )
            st.success("Asset request submitted.")
            st.rerun()
    st.subheader("Asset Requests")
    as_view = asset_requests_df.copy().head(30)
    if can_approve and not as_view.empty:
        render_request_rows(as_view, "asset_requests", "id", "name",
                            [("Employee", "name"), ("Asset", "asset_type"), ("Reason", "reason"), ("Date", "requested_on")])
    else:
        st.dataframe(as_view[["name", "asset_type", "reason", "status", "requested_on"]], hide_index=True, use_container_width=True)

elif selected_menu == "Pending approvals":
    st.title("📋 Pending approvals")

    # ---------- Collect pending requests from EVERY module ----------
    summary = []
    for _, row in compoff_df.iterrows():
        if row.get("status") == "Pending":
            summary.append({"id": row["id"], "table": "comp_off", "Type": "Comp-Off", "Employee": row["name"], "employee_id": row["employee_id"], "Details": f"{row['hours']} hrs — {row['reason']}", "requested_by": row["name"]})
    for _, row in resignations_df.iterrows():
        if row.get("status") == "Pending":
            summary.append({"id": row["id"], "table": "resignations", "Type": "Resignation", "Employee": row["name"], "employee_id": row["employee_id"], "Details": row["reason"], "requested_by": row["name"]})
    for _, row in leave_requests_df.iterrows():
        if row.get("status") == "Pending":
            summary.append({"id": row["id"], "table": "leave_requests", "Type": "Leave", "Employee": row["name"], "employee_id": row["employee_id"], "Details": f"{row['leave_type']} · {row['start_date']} → {row['end_date']} ({row['days']} d) — {row['reason']}", "requested_by": row.get("requested_by", row["name"])})
    for _, row in expense_claims_df.iterrows():
        if row.get("status") == "Pending":
            summary.append({"id": row["id"], "table": "expense_claims", "Type": "Expense", "Employee": row["name"], "employee_id": row["employee_id"], "Details": f"{row['category']} · ₹{float(row['amount']):,.2f} — {row['description']}", "requested_by": row["name"]})
    for _, row in asset_requests_df.iterrows():
        if row.get("status") == "Pending":
            summary.append({"id": row["id"], "table": "asset_requests", "Type": "Asset", "Employee": row["name"], "employee_id": row["employee_id"], "Details": f"{row['asset_type']} — {row['reason']}", "requested_by": row["name"]})
    for _, row in wfh_df.iterrows():
        if str(row.get("status", "")).lower() == "pending":
            summary.append({"id": row["id"], "table": "wfh", "Type": "WFH / WFO", "Employee": row["name"], "employee_id": row["employee_id"], "Details": f"{row['mode']} — {row['reason']}", "requested_by": row["name"]})

    if summary:
        approvals_df = pd.DataFrame(summary)
        # Filter by request type + search
        fcol1, fcol2 = st.columns([1, 2])
        with fcol1:
            type_filter = st.selectbox("Request type", ["All"] + sorted(approvals_df["Type"].unique().tolist()), key="pa_type_filter")
        with fcol2:
            pa_search = st.text_input("Search", placeholder="Employee name / ID / details", key="pa_search", label_visibility="collapsed")
        view_df = approvals_df
        if type_filter != "All":
            view_df = view_df[view_df["Type"] == type_filter]
        if pa_search.strip():
            _qs = pa_search.strip().lower()
            view_df = view_df[
                view_df["Employee"].str.lower().str.contains(_qs, na=False)
                | view_df["employee_id"].str.lower().str.contains(_qs, na=False)
                | view_df["Details"].str.lower().str.contains(_qs, na=False)
            ]

        st.caption(f"⚡ {len(view_df)} pending request(s) of {len(approvals_df)} total")
        if view_df.empty:
            st.success("No pending approvals match your filter.")
        else:
            for _, item in view_df.iterrows():
                with st.container(border=True):
                    r1, r2, r3, r4 = st.columns([1.2, 2.6, 1, 1])
                    with r1:
                        st.markdown(f"**{item['Type']}**")
                        st.caption(f"👤 {item['Employee']} · {item['employee_id']}")
                    with r2:
                        st.markdown(item["Details"])
                        st.caption(f"Requested by {item['requested_by']}")
                    with r3:
                        if st.button("✅ Approve", key=f"pa_appr_{item['table']}_{item['id']}", use_container_width=True):
                            execute_query(f"UPDATE {item['table']} SET status = 'Approved' WHERE id = ?", (item["id"],))
                            record_approval_history(item["Type"], item["Employee"], item["employee_id"], st.session_state.user_email, item["requested_by"], "Approved", item["Details"])
                            emp_email_row = employees_df[employees_df["employee_id"] == item["employee_id"]]
                            if not emp_email_row.empty:
                                send_email(emp_email_row.iloc[0]["email"], f"HRMS: {item['Type']} request Approved", f"Hi {item['Employee']}, your {item['Type']} request has been APPROVED.\n\nDetails: {item['Details']}")
                            st.success(f"{item['Type']} approved for {item['Employee']}.")
                            st.rerun()
                    with r4:
                        if st.button("❌ Reject", key=f"pa_rej_{item['table']}_{item['id']}", use_container_width=True):
                            execute_query(f"UPDATE {item['table']} SET status = 'Rejected' WHERE id = ?", (item["id"],))
                            record_approval_history(item["Type"], item["Employee"], item["employee_id"], st.session_state.user_email, item["requested_by"], "Rejected", item["Details"])
                            emp_email_row = employees_df[employees_df["employee_id"] == item["employee_id"]]
                            if not emp_email_row.empty:
                                send_email(emp_email_row.iloc[0]["email"], f"HRMS: {item['Type']} request Rejected", f"Hi {item['Employee']}, your {item['Type']} request has been REJECTED.\n\nDetails: {item['Details']}")
                            st.warning(f"{item['Type']} rejected for {item['Employee']}.")
                            st.rerun()
    else:
        st.success("✅ No pending approvals. All requests have been processed.")

elif selected_menu == "Approval History":
    st.title("🧾 Approval History")
    history = pd.DataFrame(fetch_all("SELECT * FROM approval_history ORDER BY id DESC"))
    if history.empty:
        st.info("No approval history available yet.")
    else:
        st.dataframe(history[["request_type", "employee_name", "approver", "status", "created_at", "details"]], hide_index=True, use_container_width=True)

elif selected_menu == "Date of Joining":
    st.title("📅 Date of Joining")
    doj_df = employees_df[["employee_id", "name", "department", "role", "date_joined"]].copy()
    doj_df["tenure_years"] = datetime.now().year - doj_df["date_joined"].str[:4].astype(int)
    doj_df["tenure_years"] = doj_df["tenure_years"].clip(lower=0)
    doj_df["anniversary_this_month"] = doj_df["date_joined"].str[5:7] == f"{datetime.now().month:02d}"
    doj_search = st.text_input("🔍 Search employee", placeholder="Name / EMP-ID", key="doj_search")
    if doj_search.strip():
        _q = doj_search.strip().lower()
        doj_df = doj_df[doj_df["name"].str.lower().str.contains(_q, na=False) | doj_df["employee_id"].str.lower().str.contains(_q, na=False)]
    st.dataframe(doj_df, hide_index=True, use_container_width=True, height=420)
    j1, j2, j3 = st.columns(3)
    j1.metric("👥 Total Employees", len(doj_df))
    j2.metric("🎂 Anniversaries This Month", int(doj_df["anniversary_this_month"].sum()))
    j3.metric("⏳ Longest Tenure (yrs)", int(doj_df["tenure_years"].max()) if not doj_df.empty else 0)

elif selected_menu == "Schedule Interviews":
    st.title("🗓️ Schedule Interviews")
    with st.form("schedule_interview_form"):
        s_candidate = st.text_input("Candidate Name")
        s_role = st.text_input("Role")
        sc1, sc2 = st.columns(2)
        with sc1:
            s_date = st.date_input("Interview Date", datetime.today())
            s_time = st.time_input("Interview Time")
        with sc2:
            s_mode = st.selectbox("Mode", ["Online", "In-Person", "Phone"])
            s_interviewer = st.text_input("Interviewer")
        s_notes = st.text_area("Notes")
        if st.form_submit_button("Schedule Interview"):
            execute_query(
                "INSERT INTO scheduled_interviews (candidate_name, role, interview_date, interview_time, mode, interviewer, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (s_candidate, s_role, str(s_date), str(s_time), s_mode, s_interviewer, "Scheduled", s_notes),
            )
            st.success(f"Interview scheduled for {s_candidate} on {s_date} at {s_time}.")
            st.rerun()
    sched_df = pd.DataFrame(fetch_all("SELECT * FROM scheduled_interviews ORDER BY interview_date DESC"))
    if sched_df.empty:
        st.info("No interviews scheduled yet.")
    else:
        st.subheader("Upcoming & Past Interviews")
        for _, irow in sched_df.iterrows():
            with st.container(border=True):
                ic1, ic2, ic3 = st.columns([2, 2, 1])
                with ic1:
                    st.markdown(f"**{irow['candidate_name']}** — {irow['role']}")
                    st.caption(f"{irow['interview_date']} · {irow['interview_time']} · {irow['mode']}")
                with ic2:
                    st.markdown(f"Interviewer: {irow['interviewer']}")
                    st.caption(irow.get("notes", ""))
                with ic3:
                    if irow["status"] == "Scheduled" and can_approve:
                        if st.button("✅ Complete", key=f"si_done_{irow['id']}", use_container_width=True):
                            execute_query("UPDATE scheduled_interviews SET status = 'Completed' WHERE id = ?", (irow["id"],))
                            st.success("Marked completed.")
                            st.rerun()
                    else:
                        st.markdown(f"`{irow['status']}`")

elif selected_menu == "Company Calendar":
    st.title("📆 Company Calendar")
    cal_df = pd.DataFrame(fetch_all("SELECT * FROM company_calendar ORDER BY event_date ASC"))
    with st.form("calendar_event_form"):
        ev_title = st.text_input("Event Title")
        ec1, ec2 = st.columns(2)
        with ec1:
            ev_date = st.date_input("Event Date", datetime.today())
        with ec2:
            ev_type = st.selectbox("Event Type", ["Meeting", "Holiday", "Celebration", "Training", "Interview", "Other"])
        ev_desc = st.text_area("Description")
        if st.form_submit_button("Add Event"):
            execute_query(
                "INSERT INTO company_calendar (title, event_date, event_type, description) VALUES (?, ?, ?, ?)",
                (ev_title, str(ev_date), ev_type, ev_desc),
            )
            st.success(f"Event '{ev_title}' added.")
            st.rerun()
    st.subheader(f"Events — {datetime.now().strftime('%B %Y')}")
    month_prefix = f"{datetime.now().year}-{datetime.now().month:02d}"
    month_events = cal_df[cal_df["event_date"].str.startswith(month_prefix)] if not cal_df.empty else pd.DataFrame()
    if month_events.empty:
        st.info("No events this month.")
    else:
        for _, crow in month_events.iterrows():
            st.markdown(
                f"""<div class='news-card'><div class='news-title'>📅 {crow['title']} <span style='font-weight:400; color:#6b7280;'>({crow['event_type']})</span></div>
                <div class='news-meta'>{crow['event_date']}</div><div class='news-body'>{crow['description']}</div></div>""",
                unsafe_allow_html=True,
            )
    with st.expander("View All Upcoming Events"):
        if cal_df.empty:
            st.info("No events in calendar.")
        else:
            st.dataframe(cal_df[["title", "event_date", "event_type", "description"]], hide_index=True, use_container_width=True)

elif selected_menu == "Birthday Wishes":
    st.title("🎂 Birthday Wishes")
    bday_df = employees_df.copy()
    bday_df["dob_month"] = bday_df["date_of_birth"].fillna("").str[5:7]
    bday_df["dob_day"] = bday_df["date_of_birth"].fillna("").str[8:10]
    today_month = f"{datetime.now().month:02d}"
    today_day = f"{datetime.now().day:02d}"
    todays = bday_df[(bday_df["dob_month"] == today_month) & (bday_df["dob_day"] == today_day)]
    if not todays.empty:
        st.markdown(
            f"""<div class='celebration-card' style='text-align:center; padding:24px;'>
            <div style='font-size:52px;'>🎉🎂🎉</div>
            <div class='cel-title' style='font-size:22px;'>Happy Birthday!</div>
            <div style='font-weight:700; color:#92400e; font-size:18px; margin-top:8px;'>{" · ".join(todays["name"].tolist())}</div>
            <div class='cel-meta'>Wishing a fantastic day from everyone at BluePeak! 🎈</div></div>""",
            unsafe_allow_html=True,
        )
        for _, brow in todays.iterrows():
            if st.button(f"💌 Send birthday email to {brow['name']}", key=f"bday_{brow['employee_id']}", use_container_width=True):
                ok, msg = send_email(
                    brow["email"],
                    "Happy Birthday from BluePeak! 🎂",
                    f"Hi {brow['name']},\n\nWishing you a very Happy Birthday from all of us at BluePeak Solutions! Have a fantastic year ahead. 🎉",
                )
                st.success(msg if ok else f"Queued: {msg}")
    else:
        st.info("No birthdays today.")
    st.subheader("🎂 Birthdays This Month")
    this_month_bdays = bday_df[bday_df["dob_month"] == today_month].sort_values("dob_day")
    if this_month_bdays.empty:
        st.caption("No birthdays this month.")
    else:
        bcols = st.columns(4)
        for i, (_, brow) in enumerate(this_month_bdays.iterrows()):
            with bcols[i % 4]:
                initials = "".join(w[0] for w in str(brow["name"]).split()[:2]).upper()
                st.markdown(
                    f"""<div class='celeb-card'><div style='font-size:26px;'>🎂</div>
                    <div class='celeb-name'>{brow['name']}</div>
                    <div class='celeb-meta'>{brow['department']} · {brow['dob_day']} {datetime.now().strftime('%B')}</div></div>""",
                    unsafe_allow_html=True,
                )

st.sidebar.markdown("---")
if st.session_state.user_role == "admin":
    st.sidebar.subheader("Create Employee")
    with st.sidebar.form("create_employee_form"):
        new_name = st.text_input("Employee Name")
        new_email = st.text_input("Email")
        new_department = st.selectbox("Department", ["Engineering", "HR", "Finance", "Sales", "Operations"])
        new_role = st.text_input("Role")
        new_manager = st.text_input("Manager")
        create_employee = st.form_submit_button("Create Employee")
    if create_employee and new_name and new_email:
        emp_id = f"EMP-{int(datetime.now().timestamp() % 1000000):06d}"
        execute_query(
            "INSERT INTO employees (employee_id, name, email, department, role, status, work_mode, manager, salary, phone, address, date_joined) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (emp_id, new_name, new_email, new_department, new_role, "Active", "Office", new_manager, 80000, "+91 90000 00000", "India", str(datetime.today().date())),
        )
        st.sidebar.success(f"Employee {new_name} created successfully.")
        st.rerun()

st.sidebar.subheader("Send Employee Email")
with st.sidebar.form("email_form"):
    to_email = st.selectbox("To", employees_df["email"].tolist())
    subject = st.text_input("Subject", "Welcome to HRMS")
    body = st.text_area("Message", "Welcome to the company! Please complete your onboarding steps and confirm your details.")
    email_send = st.form_submit_button("Send Email")
if email_send and to_email:
    ok, msg = send_email(to_email, subject, body)
    st.sidebar.success(msg) if ok else st.sidebar.warning(msg)

st.sidebar.markdown("---")
st.sidebar.subheader("SMTP Configuration")
with st.sidebar.form("smtp_settings_form"):
    smtp_settings = get_smtp_settings()
    smtp_host = st.text_input("SMTP Host", value=smtp_settings.get("SMTP_HOST", ""))
    smtp_port = st.text_input("SMTP Port", value=str(smtp_settings.get("SMTP_PORT", "587")))
    smtp_user = st.text_input("SMTP User", value=smtp_settings.get("SMTP_USER", ""))
    smtp_password = st.text_input("SMTP Password", value=smtp_settings.get("SMTP_PASSWORD", ""), type="password")
    smtp_tls = st.checkbox("Use TLS", value=str(smtp_settings.get("SMTP_USE_TLS", "true")).lower() == "true")
    save_smtp = st.form_submit_button("Save SMTP Settings")
if save_smtp:
    config = {
        "SMTP_HOST": smtp_host,
        "SMTP_PORT": smtp_port,
        "SMTP_USER": smtp_user,
        "SMTP_PASSWORD": smtp_password,
        "SMTP_USE_TLS": str(smtp_tls).lower(),
    }
    save_smtp_config(config)
    os.environ["SMTP_HOST"] = smtp_host
    os.environ["SMTP_PORT"] = smtp_port
    os.environ["SMTP_USER"] = smtp_user
    os.environ["SMTP_PASSWORD"] = smtp_password
    os.environ["SMTP_USE_TLS"] = str(smtp_tls).lower()
    st.sidebar.success("SMTP settings saved.")

st.sidebar.caption("Gmail: smtp.gmail.com · 587 · TLS")
st.sidebar.markdown(
    '<div class="side-footer">🏢 <b>HRMS Portal</b><br/>v2.0 · Color Edition<br/>© 2026 BluePeak Solutions</div>',
    unsafe_allow_html=True,
)

email_log_df = pd.DataFrame(fetch_all("SELECT * FROM email_log ORDER BY id DESC LIMIT 5"))
if not email_log_df.empty:
    st.sidebar.caption("Recent email log")
    st.sidebar.dataframe(email_log_df[["to_email", "subject", "status"]], hide_index=True, use_container_width=True)

