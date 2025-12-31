from flask import Flask, render_template, request, redirect, session, jsonify
import os
import json
import gspread
import re
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ================== GOOGLE SHEETS (CACHED PER WORKSHEET) ==================
_sheet_cache = {}

def get_sheet(worksheet_name):
    if worksheet_name not in _sheet_cache:
        creds = Credentials.from_service_account_info(
            json.loads(os.environ["GOOGLE_CREDENTIALS"]),
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(os.environ["SHEET_ID"])
        try:
            _sheet_cache[worksheet_name] = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in the spreadsheet.")
    return _sheet_cache[worksheet_name]

# For original instruments (assumed to be in the first/main tab)
def get_main_rows(instrument=None):
    sheet = get_sheet("Sheet1")  # Change to your actual main tab name if different (e.g., "Instruments")
    rows = sheet.get_all_records()
    if instrument:
        rows = [r for r in rows if r.get("Instrument", "").strip() == instrument]
    return rows

# Specific for Magnetic Flow Meter tab
def get_magnetic_rows():
    try:
        sheet = get_sheet("magnetic_flow_meter")
        return sheet.get_all_records()
    except:
        return []  # Return empty if tab missing or error

def add_row(data):
    # This still adds to main sheet — update if you want per-instrument tabs for adding
    sheet = get_sheet("Sheet1")
    sheet.append_row([
        data.get("Instrument", ""),
        data.get("Size", ""),
        data.get("Type", ""),
        data.get("Liner Material", ""),
        data.get("Cost", ""),
        data.get("Supplier", ""),
        data.get("Date", ""),
    ])

# ================== UTILITIES ==================
def parse_range(range_str):
    nums = re.findall(r"[\d.]+", range_str or "")
    if len(nums) != 2:
        return None, None
    try:
        return float(nums[0]), float(nums[1])
    except:
        return None, None

def find_match(rows, value):
    for r in rows:
        min_r, max_r = parse_range(r.get("Range", ""))
        if min_r is None:
            continue
        if min_r <= value <= max_r:
            return r
    return None

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html", title="Instrument Selection")

# ---------- MAGNETIC FLOW METER ----------
@app.route("/magnetic-flow-meter", methods=["GET", "POST"])
def magnetic():
    result = None
    searched = False

    # Optional: Keep old flow rate search if your main sheet has range-based data
    if request.method == "POST" and "flow_rate" in request.form:
        searched = True
        try:
            flow = float(request.form["flow_rate"])
            rows = get_main_rows("Magnetic Flow Meter")
            result = find_match(rows, flow)
        except:
            result = None

    # Load sizes from dedicated tab
    all_rows = get_magnetic_rows()
    sizes = sorted({row.get("Size", "").strip() for row in all_rows if row.get("Size", "").strip()})

    return render_template(
        "instruments/magnetic_flow.html",
        sizes=sizes,
        result=result,
        searched=searched
    )

# AJAX endpoints (all use the magnetic_flow_meter tab)
@app.route("/api/magnetic/sizes")
def api_magnetic_sizes():
    rows = get_magnetic_rows()
    sizes = sorted({row.get("Size", "").strip() for row in rows if row.get("Size", "").strip()})
    return jsonify(list(sizes))

@app.route("/api/magnetic/types")
def api_magnetic_types():
    size = request.args.get("size", "").strip()
    if not size:
        return jsonify([])
    rows = get_magnetic_rows()
    types = {row.get("Type", "").strip() for row in rows if row.get("Size", "").strip() == size and row.get("Type", "").strip()}
    return jsonify(sorted(types))

@app.route("/api/magnetic/liners")
def api_magnetic_liners():
    size = request.args.get("size", "").strip()
    type_ = request.args.get("type", "").strip()
    if not size or not type_:
        return jsonify([])
    rows = get_magnetic_rows()
    liners = {row.get("Liner Material", "").strip() for row in rows if row.get("Size", "").strip() == size and row.get("Type", "").strip() == type_ and row.get("Liner Material", "").strip()}
    return jsonify(sorted(liners))

@app.route("/api/magnetic/details")
def api_magnetic_details():
    size = request.args.get("size", "").strip()
    type_ = request.args.get("type", "").strip()
    liner = request.args.get("liner", "").strip()
    if not all([size, type_, liner]):
        return jsonify([])
    rows = get_magnetic_rows()
    matches = [
        row for row in rows
        if row.get("Size", "").strip() == size
        and row.get("Type", "").strip() == type_
        and row.get("Liner Material", "").strip() == liner
    ]
    return jsonify(matches)

# Other instruments unchanged (use main sheet)
@app.route("/vortex-flow-meter", methods=["GET", "POST"])
def vortex():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        try:
            flow = float(request.form["flow_rate"])
            rows = get_main_rows("Vortex Flow Meter")
            result = find_match(rows, flow)
        except:
            pass
    return render_template("instruments/vortex_flow.html", result=result, searched=searched)

@app.route("/transmitter", methods=["GET", "POST"])
def transmitter():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        try:
            pressure = float(request.form["pressure"])
            rows = get_main_rows("Transmitter")
            result = find_match(rows, pressure)
        except:
            pass
    return render_template("instruments/transmitter.html", result=result, searched=searched)

@app.route("/temperature-transmitter", methods=["GET", "POST"])
def temperature():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        try:
            temp = float(request.form["temperature"])
            rows = get_main_rows("Temperature Transmitter")
            result = find_match(rows, temp)
        except:
            pass
    return render_template("instruments/temperature.html", result=result, searched=searched)

@app.route("/control-valve", methods=["GET", "POST"])
def valve():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        try:
            flow = float(request.form["flow_rate"])
            rows = get_main_rows("Control Valve")
            result = find_match(rows, flow)
        except:
            pass
    return render_template("instruments/control_valve.html", result=result, searched=searched)

# ================== ADMIN ==================
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["user"] == ADMIN_USER and request.form["pass"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin/login.html")

@app.route("/admin/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/admin")
    rows = get_main_rows()  # Shows main sheet data
    return render_template("admin/dashboard.html", rows=rows)

@app.route("/admin/add", methods=["GET", "POST"])
def add():
    if "admin" not in session:
        return redirect("/admin")
    if request.method == "POST":
        add_row(request.form)
        return redirect("/admin/dashboard")
    return render_template("admin/add_row.html")

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect("/")

# ================== SECURITY HEADERS ==================
@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Cache-Control"] = "no-store"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
