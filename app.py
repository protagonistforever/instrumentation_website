from flask import Flask, render_template, request, redirect, session
import os, json, gspread, re
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ================== GOOGLE SHEETS (CACHED) ==================
_sheet = None

def get_sheet():
    global _sheet
    if _sheet is None:
        creds = Credentials.from_service_account_info(
            json.loads(os.environ["GOOGLE_CREDENTIALS"]),
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        _sheet = client.open_by_key(os.environ["SHEET_ID"]).sheet1
    return _sheet


def get_rows(instrument=None):
    rows = get_sheet().get_all_records()
    if instrument:
        rows = [r for r in rows if r["Instrument"] == instrument]
    return rows


def add_row(data):
    get_sheet().append_row([
        data.get("Instrument"),
        data.get("Range"),
        data.get("Cost")
    ])


# ================== UTILITIES ==================
def parse_range(range_str):
    """
    Accepts:
    0-100
    0 – 100
    0 to 100
    """
    nums = re.findall(r"[\d.]+", range_str)
    if len(nums) != 2:
        return None, None
    return float(nums[0]), float(nums[1])


def find_match(rows, value):
    for r in rows:
        min_r, max_r = parse_range(r["Range"])
        if min_r is None:
            continue
        if min_r <= value <= max_r:
            return r
    return None


# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html", title="Instrument Selection")


# ---------- MAGNETIC FLOW ----------
@app.route("/magnetic-flow-meter", methods=["GET", "POST"])
def magnetic():
    result = None
    searched = False

    if request.method == "POST":
        searched = True
        flow = float(request.form["flow_rate"])
        rows = get_rows("Magnetic Flow Meter")
        result = find_match(rows, flow)

    return render_template(
        "instruments/magnetic_flow.html",
        result=result,
        searched=searched
    )


# ---------- VORTEX FLOW ----------
@app.route("/vortex-flow-meter", methods=["GET", "POST"])
def vortex():
    result = None
    searched = False

    if request.method == "POST":
        searched = True
        flow = float(request.form["flow_rate"])
        rows = get_rows("Vortex Flow Meter")
        result = find_match(rows, flow)

    return render_template(
        "instruments/vortex_flow.html",
        result=result,
        searched=searched
    )


# ---------- PRESSURE / DP / FLOW TRANSMITTER ----------
@app.route("/transmitter", methods=["GET", "POST"])
def transmitter():
    result = None
    searched = False

    if request.method == "POST":
        searched = True
        pressure = float(request.form["pressure"])
        rows = get_rows("Transmitter")
        result = find_match(rows, pressure)

    return render_template(
        "instruments/transmitter.html",
        result=result,
        searched=searched
    )


# ---------- TEMPERATURE TRANSMITTER ----------
@app.route("/temperature-transmitter", methods=["GET", "POST"])
def temperature():
    result = None
    searched = False

    if request.method == "POST":
        searched = True
        temp = float(request.form["temperature"])
        rows = get_rows("Temperature Transmitter")
        result = find_match(rows, temp)

    return render_template(
        "instruments/temperature.html",
        result=result,
        searched=searched
    )


# ---------- CONTROL VALVE ----------
@app.route("/control-valve", methods=["GET", "POST"])
def valve():
    result = None
    searched = False

    if request.method == "POST":
        searched = True
        flow = float(request.form["flow_rate"])
        rows = get_rows("Control Valve")
        result = find_match(rows, flow)

    return render_template(
        "instruments/control_valve.html",
        result=result,
        searched=searched
    )


# ================== ADMIN ==================
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if (
            request.form["user"] == ADMIN_USER and
            request.form["pass"] == ADMIN_PASS
        ):
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin/login.html")


@app.route("/admin/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/admin")
    return render_template("admin/dashboard.html", rows=get_rows())


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
