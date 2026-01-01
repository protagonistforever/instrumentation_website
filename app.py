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

# For legacy range-based search (if still needed)
def get_main_rows(instrument=None):
    try:
        sheet = get_sheet("Sheet1")  # Change if your main tab has a different name
        rows = sheet.get_all_records()
        if instrument:
            rows = [r for r in rows if str(r.get("Instrument", "")).strip() == instrument]
        return rows
    except:
        return []

# ================== MAGNETIC FLOW METER ==================
def get_magnetic_rows():
    try:
        sheet = get_sheet("magnetic_flow_meter")
        records = sheet.get_all_records()
        return [
            {k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()}
            for row in records
        ]
    except Exception as e:
        print(f"Error loading magnetic_flow_meter tab: {e}")
        return []

# ================== TRANSMITTER ==================
def get_transmitter_rows():
    try:
        sheet = get_sheet("transmitter")
        records = sheet.get_all_records()
        # Convert all values to strings safely
        cleaned = []
        for row in records:
            cleaned_row = {}
            for k, v in row.items():
                if k == "Dia seal: Intergral, Dia seal: Remote non Integral":
                    # Fix typo in header if present — map to correct key
                    cleaned_row["Dia Seal Type"] = str(v).strip() if v not in ("", None) else ""
                else:
                    cleaned_row[k] = str(v).strip() if v not in ("", None) else ""
            cleaned.append(cleaned_row)
        return cleaned
    except Exception as e:
        print(f"Error loading transmitter tab: {e}")
        return []

def add_row(data):
    try:
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
    except Exception as e:
        print(f"Error adding row: {e}")

# ================== UTILITIES ==================
def parse_range(range_str):
    if not range_str:
        return None, None
    nums = re.findall(r"[\d.]+", str(range_str))
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
    if request.method == "POST" and "flow_rate" in request.form:
        searched = True
        try:
            flow = float(request.form["flow_rate"])
            rows = get_main_rows("Magnetic Flow Meter")
            result = find_match(rows, flow)
        except:
            result = None

    all_rows = get_magnetic_rows()
    sizes = sorted({row.get("Size", "") for row in all_rows if row.get("Size", "")})

    return render_template(
        "instruments/magnetic_flow.html",
        sizes=sizes,
        result=result,
        searched=searched
    )

# Magnetic AJAX
@app.route("/api/magnetic/sizes")
def api_magnetic_sizes():
    rows = get_magnetic_rows()
    sizes = sorted({row.get("Size", "") for row in rows if row.get("Size", "")})
    return jsonify(list(sizes))

@app.route("/api/magnetic/types")
def api_magnetic_types():
    size = request.args.get("size", "").strip()
    if not size:
        return jsonify([])
    rows = get_magnetic_rows()
    types = {row.get("Type", "") for row in rows if row.get("Size", "") == size and row.get("Type", "")}
    return jsonify(sorted(types))

@app.route("/api/magnetic/liners")
def api_magnetic_liners():
    size = request.args.get("size", "").strip()
    type_ = request.args.get("type", "").strip()
    if not size or not type_:
        return jsonify([])
    rows = get_magnetic_rows()
    liners = {row.get("Liner Material", "") for row in rows if row.get("Size", "") == size and row.get("Type", "") == type_ and row.get("Liner Material", "")}
    return jsonify(sorted(liners))

@app.route("/api/magnetic/details")
def api_magnetic_details():
    size = request.args.get("size", "").strip()
    type_ = request.args.get("type", "").strip()
    liner = request.args.get("liner", "").strip()
    if not all([size, type_, liner]):
        return jsonify([])
    rows = get_magnetic_rows()
    matches = [row for row in rows if row.get("Size", "") == size and row.get("Type", "") == type_ and row.get("Liner Material", "") == liner]
    return jsonify(matches)

# ---------- TRANSMITTER (NEW MODERN VERSION) ----------
@app.route("/transmitter")
def transmitter_page():
    all_rows = get_transmitter_rows()
    types = sorted({row.get("Type", "") for row in all_rows if row.get("Type", "")})
    return render_template("instruments/transmitter.html", types=types)

# Transmitter AJAX Endpoints
@app.route("/api/transmitter/types")
def api_transmitter_types():
    rows = get_transmitter_rows()
    types = sorted({row.get("Type", "") for row in rows if row.get("Type", "")})
    return jsonify(list(types))

@app.route("/api/transmitter/dia_seal")
def api_transmitter_dia_seal():
    type_val = request.args.get("type", "").strip()
    if not type_val:
        return jsonify([])
    rows = get_transmitter_rows()
    dia_seals = {row.get("Dia Seal Type", "") for row in rows if row.get("Type", "") == type_val and row.get("Dia Seal Type", "")}
    return jsonify(sorted(dia_seals))

@app.route("/api/transmitter/range_value")
def api_transmitter_range_value():
    type_val = request.args.get("type", "").strip()
    dia_seal = request.args.get("dia_seal", "").strip()
    if not type_val or not dia_seal:
        return jsonify([])
    rows = get_transmitter_rows()
    ranges = {row.get("Range value", "") for row in rows if row.get("Type", "") == type_val and row.get("Dia Seal Type", "") == dia_seal and row.get("Range value", "")}
    return jsonify(sorted(ranges))

@app.route("/api/transmitter/range_unit")
def api_transmitter_range_unit():
    type_val = request.args.get("type", "").strip()
    dia_seal = request.args.get("dia_seal", "").strip()
    range_val = request.args.get("range_value", "").strip()
    if not all([type_val, dia_seal, range_val]):
        return jsonify([])
    rows = get_transmitter_rows()
    units = {row.get("Range in mmwcl or Kg/cm2", "") for row in rows if row.get("Type", "") == type_val and row.get("Dia Seal Type", "") == dia_seal and row.get("Range value", "") == range_val and row.get("Range in mmwcl or Kg/cm2", "")}
    return jsonify(sorted(units))

@app.route("/api/transmitter/details")
def api_transmitter_details():
    type_val = request.args.get("type", "").strip()
    dia_seal = request.args.get("dia_seal", "").strip()
    range_val = request.args.get("range_value", "").strip()
    unit = request.args.get("unit", "").strip()

    if not all([type_val, dia_seal, range_val, unit]):
        return jsonify([])

    rows = get_transmitter_rows()
    matches = [
        row for row in rows
        if row.get("Type", "") == type_val
        and row.get("Dia Seal Type", "") == dia_seal
        and row.get("Range value", "") == range_val
        and row.get("Range in mmwcl or Kg/cm2", "") == unit
    ]
    return jsonify(matches)

# Keep other old routes for backward compatibility
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
    rows = get_main_rows()
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
