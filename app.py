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

# Legacy main sheet
def get_main_rows(instrument=None):
    try:
        sheet = get_sheet("Sheet1")
        rows = sheet.get_all_records()
        if instrument:
            rows = [r for r in rows if str(r.get("Instrument", "")).strip() == instrument]
        return rows
    except:
        return []

# ================== INSTRUMENT DATA LOADERS ==================
def get_magnetic_rows():
    try:
        sheet = get_sheet("magnetic_flow_meter")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading magnetic_flow_meter tab: {e}")
        return []

DIA_SEAL_COLUMN = "Dia seal: Integral, Dia seal: Remote non Integral"

def get_transmitter_rows():
    try:
        sheet = get_sheet("transmitter")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading transmitter tab: {e}")
        return []

TEMP_TYPE_COLUMN = "temperature_transmitter"
CHAMBER_COLUMN = "Dual/ single chamber/NA"

def get_temperature_rows():
    try:
        sheet = get_sheet("temperature_transmitter")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading temperature_transmitter tab: {e}")
        return []

def get_flow_meter_rows():
    try:
        sheet = get_sheet("vortex_flow_meter")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading vortex_flow_meter tab: {e}")
        return []

def get_control_valve_rows():
    try:
        sheet = get_sheet("control_valve")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading control_valve tab: {e}")
        return []

# Cable Instruments
def get_signal_pair_rows():
    try:
        sheet = get_sheet("Signal Pair Cables")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Signal Pair Cables tab: {e}")
        return []

def get_signal_core_rows():
    try:
        sheet = get_sheet("Signal Core Cables")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Signal Core Cables tab: {e}")
        return []

def get_signal_triad_rows():
    try:
        sheet = get_sheet("Signal Triad Cables")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Signal Triad Cables tab: {e}")
        return []

def get_extension_cable_rows():
    try:
        sheet = get_sheet("Extension/ Compensation cable")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Extension/ Compensation cable tab: {e}")
        return []

# New 10 Instruments
def get_pg_dpg_rows():
    try:
        sheet = get_sheet("PG & DPG")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading PG & DPG tab: {e}")
        return []

def get_ps_dps_rows():
    try:
        sheet = get_sheet("PS & DPS")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading PS & DPS tab: {e}")
        return []

def get_analysers_rows():
    try:
        sheet = get_sheet("Analysers")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Analysers tab: {e}")
        return []

def get_level_gauges_rows():
    try:
        sheet = get_sheet("LG")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading LG tab: {e}")
        return []

def get_flow_elements_rows():
    try:
        sheet = get_sheet("Flow Elements")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Flow Elements tab: {e}")
        return []

def get_temperature_gauges_rows():
    try:
        sheet = get_sheet("TG")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading TG tab: {e}")
        return []

def get_level_transmitter_rows():
    try:
        sheet = get_sheet("Level Transmitter")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Level Transmitter tab: {e}")
        return []

def get_ls_fs_rows():
    try:
        sheet = get_sheet("LS & FS")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading LS & FS tab: {e}")
        return []

def get_temperature_elements_rows():
    try:
        sheet = get_sheet("Temperture Elements")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Temperture Elements tab: {e}")
        return []

def get_misc_instruments_rows():
    try:
        sheet = get_sheet("Misc Instruments")
        records = sheet.get_all_records()
        return [{k: str(v).strip() if v not in ("", None) else "" for k, v in row.items()} for row in records]
    except Exception as e:
        print(f"Error loading Misc Instruments tab: {e}")
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
    return render_template("index.html", title="Instrumentation Cost Data-Bank")

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

    sizes = sorted({row.get("Size", "") for row in get_magnetic_rows() if row.get("Size", "")})
    return render_template("instruments/magnetic_flow.html", sizes=sizes, result=result, searched=searched)

@app.route("/api/magnetic/sizes")
def api_magnetic_sizes():
    return jsonify(sorted({row.get("Size", "") for row in get_magnetic_rows() if row.get("Size", "")}))

@app.route("/api/magnetic/types")
def api_magnetic_types():
    size = request.args.get("size", "").strip()
    if not size: return jsonify([])
    return jsonify(sorted({row.get("Type", "") for row in get_magnetic_rows() if row.get("Size", "") == size and row.get("Type", "")}))

@app.route("/api/magnetic/liners")
def api_magnetic_liners():
    size = request.args.get("size", "").strip()
    type_ = request.args.get("type", "").strip()
    if not size or not type_: return jsonify([])
    return jsonify(sorted({row.get("Liner Material", "") for row in get_magnetic_rows() if row.get("Size", "") == size and row.get("Type", "") == type_ and row.get("Liner Material", "")}))

@app.route("/api/magnetic/details")
def api_magnetic_details():
    size = request.args.get("size", "").strip()
    type_ = request.args.get("type", "").strip()
    liner = request.args.get("liner", "").strip()
    if not all([size, type_, liner]): return jsonify([])
    matches = [row for row in get_magnetic_rows() if row.get("Size", "") == size and row.get("Type", "") == type_ and row.get("Liner Material", "") == liner]
    return jsonify(matches)

# ---------- TRANSMITTER ----------
@app.route("/transmitter")
def transmitter_page():
    types = sorted({row.get("Type", "") for row in get_transmitter_rows() if row.get("Type", "")})
    return render_template("instruments/transmitter.html", types=types)

@app.route("/api/transmitter/types")
def api_transmitter_types():
    return jsonify(sorted({row.get("Type", "") for row in get_transmitter_rows() if row.get("Type", "")}))

@app.route("/api/transmitter/dia_seal")
def api_transmitter_dia_seal():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({row.get(DIA_SEAL_COLUMN, "") for row in get_transmitter_rows() if row.get("Type", "") == type_val and row.get(DIA_SEAL_COLUMN, "")}))

@app.route("/api/transmitter/range_value")
def api_transmitter_range_value():
    type_val = request.args.get("type", "").strip()
    dia_seal = request.args.get("dia_seal", "").strip()
    if not type_val or not dia_seal: return jsonify([])
    return jsonify(sorted({row.get("Range value", "") for row in get_transmitter_rows() if row.get("Type", "") == type_val and row.get(DIA_SEAL_COLUMN, "") == dia_seal and row.get("Range value", "")}))

@app.route("/api/transmitter/range_unit")
def api_transmitter_range_unit():
    type_val = request.args.get("type", "").strip()
    dia_seal = request.args.get("dia_seal", "").strip()
    range_val = request.args.get("range_value", "").strip()
    if not all([type_val, dia_seal, range_val]): return jsonify([])
    return jsonify(sorted({row.get("Range in mmwcl or Kg/cm2", "") for row in get_transmitter_rows() if row.get("Type", "") == type_val and row.get(DIA_SEAL_COLUMN, "") == dia_seal and row.get("Range value", "") == range_val and row.get("Range in mmwcl or Kg/cm2", "")}))

@app.route("/api/transmitter/details")
def api_transmitter_details():
    type_val = request.args.get("type", "").strip()
    dia_seal = request.args.get("dia_seal", "").strip()
    range_val = request.args.get("range_value", "").strip()
    unit = request.args.get("unit", "").strip()
    if not all([type_val, dia_seal, range_val, unit]): return jsonify([])
    matches = [row for row in get_transmitter_rows() if row.get("Type", "") == type_val and row.get(DIA_SEAL_COLUMN, "") == dia_seal and row.get("Range value", "") == range_val and row.get("Range in mmwcl or Kg/cm2", "") == unit]
    return jsonify(matches)

# ---------- TEMPERATURE TRANSMITTER ----------
@app.route("/temperature-transmitter")
def temperature_transmitter_page():
    temp_types = sorted({row.get(TEMP_TYPE_COLUMN, "") for row in get_temperature_rows() if row.get(TEMP_TYPE_COLUMN, "")})
    return render_template("instruments/temperature.html", temp_types=temp_types)

@app.route("/api/temperature/types")
def api_temperature_types():
    return jsonify(sorted({row.get(TEMP_TYPE_COLUMN, "") for row in get_temperature_rows() if row.get(TEMP_TYPE_COLUMN, "")}))

@app.route("/api/temperature/chamber")
def api_temperature_chamber():
    temp_type = request.args.get("temp_type", "").strip()
    if not temp_type: return jsonify([])
    return jsonify(sorted({row.get(CHAMBER_COLUMN, "") for row in get_temperature_rows() if row.get(TEMP_TYPE_COLUMN, "") == temp_type and row.get(CHAMBER_COLUMN, "")}))

@app.route("/api/temperature/details")
def api_temperature_details():
    temp_type = request.args.get("temp_type", "").strip()
    chamber = request.args.get("chamber", "").strip()
    if not all([temp_type, chamber]): return jsonify([])
    matches = [row for row in get_temperature_rows() if row.get(TEMP_TYPE_COLUMN, "") == temp_type and row.get(CHAMBER_COLUMN, "") == chamber]
    return jsonify(matches)

# ---------- FLOW METER ----------
@app.route("/flow-meter")
def flow_meter_page():
    types = sorted({row.get("Type", "") for row in get_flow_meter_rows() if row.get("Type", "")})
    return render_template("instruments/flow_meter.html", types=types)

@app.route("/api/flow/types")
def api_flow_types():
    return jsonify(sorted({row.get("Type", "") for row in get_flow_meter_rows() if row.get("Type", "")}))

@app.route("/api/flow/sizes")
def api_flow_sizes():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({row.get("size_mm", "") for row in get_flow_meter_rows() if row.get("Type", "") == type_val and row.get("size_mm", "")}))

@app.route("/api/flow/details")
def api_flow_details():
    type_val = request.args.get("type", "").strip()
    size = request.args.get("size", "").strip()
    if not all([type_val, size]): return jsonify([])
    matches = [row for row in get_flow_meter_rows() if row.get("Type", "") == type_val and row.get("size_mm", "") == size]
    return jsonify(matches)

# ---------- CONTROL VALVE ----------
@app.route("/control-valve")
def control_valve_page():
    valve_types = sorted({row.get("Valve_type", "") for row in get_control_valve_rows() if row.get("Valve_type", "")})
    return render_template("instruments/control_valve.html", valve_types=valve_types)

@app.route("/api/control/valve_types")
def api_control_valve_types():
    return jsonify(sorted({row.get("Valve_type", "") for row in get_control_valve_rows() if row.get("Valve_type", "")}))

@app.route("/api/control/sizes")
def api_control_sizes():
    valve_type = request.args.get("valve_type", "").strip()
    if not valve_type: return jsonify([])
    return jsonify(sorted({row.get("size_mm", "") for row in get_control_valve_rows() if row.get("Valve_type", "") == valve_type and row.get("size_mm", "")}))

@app.route("/api/control/applications")
def api_control_applications():
    valve_type = request.args.get("valve_type", "").strip()
    size = request.args.get("size", "").strip()
    if not valve_type or not size: return jsonify([])
    return jsonify(sorted({row.get("application", "") for row in get_control_valve_rows() if row.get("Valve_type", "") == valve_type and row.get("size_mm", "") == size and row.get("application", "")}))

@app.route("/api/control/details")
def api_control_details():
    valve_type = request.args.get("valve_type", "").strip()
    size = request.args.get("size", "").strip()
    app = request.args.get("application", "").strip()
    if not all([valve_type, size, app]): return jsonify([])
    matches = [row for row in get_control_valve_rows() if row.get("Valve_type", "") == valve_type and row.get("size_mm", "") == size and row.get("application", "") == app]
    return jsonify(matches)

# ================== CABLE INSTRUMENTS ROUTES ==================
@app.route("/signal-pair-cables")
def signal_pair_cables_page():
    sizes = sorted({r.get("Size", "") for r in get_signal_pair_rows() if r.get("Size", "")})
    return render_template("instruments/signal_pair_cables.html", sizes=sizes)

@app.route("/api/signal-pair/sizes")
def api_signal_pair_sizes():
    return jsonify(sorted({r.get("Size", "") for r in get_signal_pair_rows() if r.get("Size", "")}))

@app.route("/api/signal-pair/pairs")
def api_signal_pair_pairs():
    size = request.args.get("size", "").strip()
    if not size: return jsonify([])
    return jsonify(sorted({r.get("Pair", "") for r in get_signal_pair_rows() if r.get("Size", "") == size and r.get("Pair", "")}))

@app.route("/api/signal-pair/sheaths")
def api_signal_pair_sheaths():
    size = request.args.get("size", "").strip()
    pair = request.args.get("pair", "").strip()
    if not size or not pair: return jsonify([])
    return jsonify(sorted({r.get("Outer sheath", "") for r in get_signal_pair_rows() if r.get("Size", "") == size and r.get("Pair", "") == pair and r.get("Outer sheath", "")}))

@app.route("/api/signal-pair/details")
def api_signal_pair_details():
    size = request.args.get("size", "").strip()
    pair = request.args.get("pair", "").strip()
    sheath = request.args.get("sheath", "").strip()
    if not all([size, pair, sheath]): return jsonify([])
    matches = [r for r in get_signal_pair_rows() if r.get("Size", "") == size and r.get("Pair", "") == pair and r.get("Outer sheath", "") == sheath]
    return jsonify(matches)

@app.route("/signal-core-cables")
def signal_core_cables_page():
    sizes = sorted({r.get("Size", "") for r in get_signal_core_rows() if r.get("Size", "")})
    return render_template("instruments/signal_core_cables.html", sizes=sizes)

@app.route("/api/signal-core/sizes")
def api_signal_core_sizes():
    return jsonify(sorted({r.get("Size", "") for r in get_signal_core_rows() if r.get("Size", "")}))

@app.route("/api/signal-core/cores")
def api_signal_core_cores():
    size = request.args.get("size", "").strip()
    if not size: return jsonify([])
    return jsonify(sorted({r.get("Core", "") for r in get_signal_core_rows() if r.get("Size", "") == size and r.get("Core", "")}))

@app.route("/api/signal-core/sheaths")
def api_signal_core_sheaths():
    size = request.args.get("size", "").strip()
    core = request.args.get("core", "").strip()
    if not size or not core: return jsonify([])
    return jsonify(sorted({r.get("Outer sheath", "") for r in get_signal_core_rows() if r.get("Size", "") == size and r.get("Core", "") == core and r.get("Outer sheath", "")}))

@app.route("/api/signal-core/details")
def api_signal_core_details():
    size = request.args.get("size", "").strip()
    core = request.args.get("core", "").strip()
    sheath = request.args.get("sheath", "").strip()
    if not all([size, core, sheath]): return jsonify([])
    matches = [r for r in get_signal_core_rows() if r.get("Size", "") == size and r.get("Core", "") == core and r.get("Outer sheath", "") == sheath]
    return jsonify(matches)

@app.route("/signal-triad-cables")
def signal_triad_cables_page():
    sizes = sorted({r.get("Size", "") for r in get_signal_triad_rows() if r.get("Size", "")})
    return render_template("instruments/signal_triad_cables.html", sizes=sizes)

@app.route("/api/signal-triad/sizes")
def api_signal_triad_sizes():
    return jsonify(sorted({r.get("Size", "") for r in get_signal_triad_rows() if r.get("Size", "")}))

@app.route("/api/signal-triad/pairs")
def api_signal_triad_pairs():
    size = request.args.get("size", "").strip()
    if not size: return jsonify([])
    return jsonify(sorted({r.get("Pair", "") for r in get_signal_triad_rows() if r.get("Size", "") == size and r.get("Pair", "")}))

@app.route("/api/signal-triad/sheaths")
def api_signal_triad_sheaths():
    size = request.args.get("size", "").strip()
    pair = request.args.get("pair", "").strip()
    if not size or not pair: return jsonify([])
    return jsonify(sorted({r.get("Outer sheath", "") for r in get_signal_triad_rows() if r.get("Size", "") == size and r.get("Pair", "") == pair and r.get("Outer sheath", "")}))

@app.route("/api/signal-triad/details")
def api_signal_triad_details():
    size = request.args.get("size", "").strip()
    pair = request.args.get("pair", "").strip()
    sheath = request.args.get("sheath", "").strip()
    if not all([size, pair, sheath]): return jsonify([])
    matches = [r for r in get_signal_triad_rows() if r.get("Size", "") == size and r.get("Pair", "") == pair and r.get("Outer sheath", "") == sheath]
    return jsonify(matches)

@app.route("/extension-compensation-cable")
def extension_cable_page():
    types = sorted({r.get("Type", "") for r in get_extension_cable_rows() if r.get("Type", "")})
    return render_template("instruments/extension_compensation_cable.html", types=types)

@app.route("/api/extension/types")
def api_extension_types():
    return jsonify(sorted({r.get("Type", "") for r in get_extension_cable_rows() if r.get("Type", "")}))

@app.route("/api/extension/tc_types")
def api_extension_tc_types():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({r.get("T/C Type", "") for r in get_extension_cable_rows() if r.get("Type", "") == type_val and r.get("T/C Type", "")}))

@app.route("/api/extension/sizes")
def api_extension_sizes():
    type_val = request.args.get("type", "").strip()
    tc_type = request.args.get("tc_type", "").strip()
    if not type_val or not tc_type: return jsonify([])
    return jsonify(sorted({r.get("Size in strand/ AWG", "") for r in get_extension_cable_rows() if r.get("Type", "") == type_val and r.get("T/C Type", "") == tc_type and r.get("Size in strand/ AWG", "")}))

@app.route("/api/extension/pairs")
def api_extension_pairs():
    type_val = request.args.get("type", "").strip()
    tc_type = request.args.get("tc_type", "").strip()
    size = request.args.get("size", "").strip()
    if not all([type_val, tc_type, size]): return jsonify([])
    return jsonify(sorted({r.get("Pair", "") for r in get_extension_cable_rows() if r.get("Type", "") == type_val and r.get("T/C Type", "") == tc_type and r.get("Size in strand/ AWG", "") == size and r.get("Pair", "")}))

@app.route("/api/extension/sheaths")
def api_extension_sheaths():
    type_val = request.args.get("type", "").strip()
    tc_type = request.args.get("tc_type", "").strip()
    size = request.args.get("size", "").strip()
    pair = request.args.get("pair", "").strip()
    if not all([type_val, tc_type, size, pair]): return jsonify([])
    return jsonify(sorted({r.get("Sheath", "") for r in get_extension_cable_rows() if r.get("Type", "") == type_val and r.get("T/C Type", "") == tc_type and r.get("Size in strand/ AWG", "") == size and r.get("Pair", "") == pair and r.get("Sheath", "")}))

@app.route("/api/extension/details")
def api_extension_details():
    type_val = request.args.get("type", "").strip()
    tc_type = request.args.get("tc_type", "").strip()
    size = request.args.get("size", "").strip()
    pair = request.args.get("pair", "").strip()
    sheath = request.args.get("sheath", "").strip()
    if not all([type_val, tc_type, size, pair, sheath]): return jsonify([])
    matches = [r for r in get_extension_cable_rows() if r.get("Type", "") == type_val and r.get("T/C Type", "") == tc_type and r.get("Size in strand/ AWG", "") == size and r.get("Pair", "") == pair and r.get("Sheath", "") == sheath]
    return jsonify(matches)

# ================== 10 NEW INSTRUMENTS ROUTES ==================
# 1. PG & DPG
@app.route("/pg-dpg")
def pg_dpg_page():
    types = sorted({r.get("Type", "") for r in get_pg_dpg_rows() if r.get("Type", "")})
    return render_template("instruments/pg_dpg.html", types=types)

@app.route("/api/pg-dpg/types")
def api_pg_dpg_types():
    return jsonify(sorted({r.get("Type", "") for r in get_pg_dpg_rows() if r.get("Type", "")}))

@app.route("/api/pg-dpg/sensing")
def api_pg_dpg_sensing():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({r.get("sensing element", "") for r in get_pg_dpg_rows() if r.get("Type", "") == type_val and r.get("sensing element", "")}))

@app.route("/api/pg-dpg/diaseal")
def api_pg_dpg_diaseal():
    type_val = request.args.get("type", "").strip()
    sensing = request.args.get("sensing", "").strip()
    if not all([type_val, sensing]): return jsonify([])
    return jsonify(sorted({r.get("Dia seal", "") for r in get_pg_dpg_rows() if r.get("Type", "") == type_val and r.get("sensing element", "") == sensing and r.get("Dia seal", "")}))

@app.route("/api/pg-dpg/dialsize")
def api_pg_dpg_dialsize():
    type_val = request.args.get("type", "").strip()
    sensing = request.args.get("sensing", "").strip()
    diaseal = request.args.get("diaseal", "").strip()
    if not all([type_val, sensing, diaseal]): return jsonify([])
    return jsonify(sorted({r.get("dial size", "") for r in get_pg_dpg_rows() if r.get("Type", "") == type_val and r.get("sensing element", "") == sensing and r.get("Dia seal", "") == diaseal and r.get("dial size", "")}))

@app.route("/api/pg-dpg/range")
def api_pg_dpg_range():
    type_val = request.args.get("type", "").strip()
    sensing = request.args.get("sensing", "").strip()
    diaseal = request.args.get("diaseal", "").strip()
    dialsize = request.args.get("dialsize", "").strip()
    if not all([type_val, sensing, diaseal, dialsize]): return jsonify([])
    return jsonify(sorted({r.get("range", "") for r in get_pg_dpg_rows() if r.get("Type", "") == type_val and r.get("sensing element", "") == sensing and r.get("Dia seal", "") == diaseal and r.get("dial size", "") == dialsize and r.get("range", "")}))

@app.route("/api/pg-dpg/accessories")
def api_pg_dpg_accessories():
    type_val = request.args.get("type", "").strip()
    sensing = request.args.get("sensing", "").strip()
    diaseal = request.args.get("diaseal", "").strip()
    dialsize = request.args.get("dialsize", "").strip()
    range_val = request.args.get("range", "").strip()
    if not all([type_val, sensing, diaseal, dialsize, range_val]): return jsonify([])
    return jsonify(sorted({r.get("accessories", "") for r in get_pg_dpg_rows() if r.get("Type", "") == type_val and r.get("sensing element", "") == sensing and r.get("Dia seal", "") == diaseal and r.get("dial size", "") == dialsize and r.get("range", "") == range_val and r.get("accessories", "")}))

@app.route("/api/pg-dpg/details")
def api_pg_dpg_details():
    params = {k: request.args.get(k, "").strip() for k in ["type", "sensing", "diaseal", "dialsize", "range", "accessories"]}
    if not all(params.values()): return jsonify([])
    rows = get_pg_dpg_rows()
    matches = [r for r in rows if r.get("Type", "") == params["type"] and r.get("sensing element", "") == params["sensing"] and r.get("Dia seal", "") == params["diaseal"] and r.get("dial size", "") == params["dialsize"] and r.get("range", "") == params["range"] and r.get("accessories", "") == params["accessories"]]
    return jsonify(matches)

# 2. PS & DPS
@app.route("/ps-dps")
def ps_dps_page():
    types = sorted({r.get("type", "") for r in get_ps_dps_rows() if r.get("type", "")})
    return render_template("instruments/ps_dps.html", types=types)

@app.route("/api/ps-dps/types")
def api_ps_dps_types():
    return jsonify(sorted({r.get("type", "") for r in get_ps_dps_rows() if r.get("type", "")}))

@app.route("/api/ps-dps/accessories")
def api_ps_dps_accessories():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({r.get("accessories", "") for r in get_ps_dps_rows() if r.get("type", "") == type_val and r.get("accessories", "")}))

@app.route("/api/ps-dps/details")
def api_ps_dps_details():
    type_val = request.args.get("type", "").strip()
    accessories = request.args.get("accessories", "").strip()
    if not all([type_val, accessories]): return jsonify([])
    matches = [r for r in get_ps_dps_rows() if r.get("type", "") == type_val and r.get("accessories", "") == accessories]
    return jsonify(matches)

# 3. Analysers
@app.route("/analysers")
def analysers_page():
    type1 = sorted({r.get("type1", "") for r in get_analysers_rows() if r.get("type1", "")})
    return render_template("instruments/analysers.html", type1=type1)

@app.route("/api/analysers/type1")
def api_analysers_type1():
    return jsonify(sorted({r.get("type1", "") for r in get_analysers_rows() if r.get("type1", "")}))

@app.route("/api/analysers/type2")
def api_analysers_type2():
    type1 = request.args.get("type1", "").strip()
    if not type1: return jsonify([])
    return jsonify(sorted({r.get("type2", "") for r in get_analysers_rows() if r.get("type1", "") == type1 and r.get("type2", "")}))

@app.route("/api/analysers/application")
def api_analysers_application():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    if not all([type1, type2]): return jsonify([])
    return jsonify(sorted({r.get("Application", "") for r in get_analysers_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("Application", "")}))

@app.route("/api/analysers/range")
def api_analysers_range():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    app = request.args.get("application", "").strip()
    if not all([type1, type2, app]): return jsonify([])
    return jsonify(sorted({r.get("Range", "") for r in get_analysers_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("Application", "") == app and r.get("Range", "")}))

@app.route("/api/analysers/details")
def api_analysers_details():
    params = {k: request.args.get(k, "").strip() for k in ["type1", "type2", "application", "range"]}
    if not all(params.values()): return jsonify([])
    matches = [r for r in get_analysers_rows() if r.get("type1", "") == params["type1"] and r.get("type2", "") == params["type2"] and r.get("Application", "") == params["application"] and r.get("Range", "") == params["range"]]
    return jsonify(matches)

# 4. Level Gauges
@app.route("/level-gauges")
def level_gauges_page():
    types = sorted({r.get("type", "") for r in get_level_gauges_rows() if r.get("type", "")})
    return render_template("instruments/level_gauges.html", types=types)

@app.route("/api/level-gauges/types")
def api_level_gauges_types():
    return jsonify(sorted({r.get("type", "") for r in get_level_gauges_rows() if r.get("type", "")}))

@app.route("/api/level-gauges/accessories")
def api_level_gauges_accessories():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({r.get("accessories", "") for r in get_level_gauges_rows() if r.get("type", "") == type_val and r.get("accessories", "")}))

@app.route("/api/level-gauges/distance")
def api_level_gauges_distance():
    type_val = request.args.get("type", "").strip()
    accessories = request.args.get("accessories", "").strip()
    if not all([type_val, accessories]): return jsonify([])
    return jsonify(sorted({r.get("center to center distance", "") for r in get_level_gauges_rows() if r.get("type", "") == type_val and r.get("accessories", "") == accessories and r.get("center to center distance", "")}))

@app.route("/api/level-gauges/details")
def api_level_gauges_details():
    type_val = request.args.get("type", "").strip()
    accessories = request.args.get("accessories", "").strip()
    distance = request.args.get("distance", "").strip()
    if not all([type_val, accessories, distance]): return jsonify([])
    matches = [r for r in get_level_gauges_rows() if r.get("type", "") == type_val and r.get("accessories", "") == accessories and r.get("center to center distance", "") == distance]
    return jsonify(matches)

# 5. Flow Elements
@app.route("/flow-elements")
def flow_elements_page():
    type1 = sorted({r.get("type1", "") for r in get_flow_elements_rows() if r.get("type1", "")})
    return render_template("instruments/flow_elements.html", type1=type1)

@app.route("/api/flow-elements/type1")
def api_flow_elements_type1():
    return jsonify(sorted({r.get("type1", "") for r in get_flow_elements_rows() if r.get("type1", "")}))

@app.route("/api/flow-elements/line_size")
def api_flow_elements_line_size():
    type1 = request.args.get("type1", "").strip()
    if not type1: return jsonify([])
    return jsonify(sorted({r.get("line size", "") for r in get_flow_elements_rows() if r.get("type1", "") == type1 and r.get("line size", "")}))

@app.route("/api/flow-elements/moc")
def api_flow_elements_moc():
    type1 = request.args.get("type1", "").strip()
    line_size = request.args.get("line_size", "").strip()
    if not all([type1, line_size]): return jsonify([])
    return jsonify(sorted({r.get("moc", "") for r in get_flow_elements_rows() if r.get("type1", "") == type1 and r.get("line size", "") == line_size and r.get("moc", "")}))

@app.route("/api/flow-elements/details")
def api_flow_elements_details():
    type1 = request.args.get("type1", "").strip()
    line_size = request.args.get("line_size", "").strip()
    moc = request.args.get("moc", "").strip()
    if not all([type1, line_size, moc]): return jsonify([])
    matches = [r for r in get_flow_elements_rows() if r.get("type1", "") == type1 and r.get("line size", "") == line_size and r.get("moc", "") == moc]
    return jsonify(matches)

# 6. Temperature Gauges
@app.route("/temperature-gauges")
def temperature_gauges_page():
    type1 = sorted({r.get("type1", "") for r in get_temperature_gauges_rows() if r.get("type1", "")})
    return render_template("instruments/temperature_gauges.html", type1=type1)

@app.route("/api/temperature-gauges/type1")
def api_temperature_gauges_type1():
    return jsonify(sorted({r.get("type1", "") for r in get_temperature_gauges_rows() if r.get("type1", "")}))

@app.route("/api/temperature-gauges/type2")
def api_temperature_gauges_type2():
    type1 = request.args.get("type1", "").strip()
    if not type1: return jsonify([])
    return jsonify(sorted({r.get("type2", "") for r in get_temperature_gauges_rows() if r.get("type1", "") == type1 and r.get("type2", "")}))

@app.route("/api/temperature-gauges/moc")
def api_temperature_gauges_moc():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    if not all([type1, type2]): return jsonify([])
    return jsonify(sorted({r.get("moc", "") for r in get_temperature_gauges_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("moc", "")}))

@app.route("/api/temperature-gauges/insertion")
def api_temperature_gauges_insertion():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    moc = request.args.get("moc", "").strip()
    if not all([type1, type2, moc]): return jsonify([])
    return jsonify(sorted({r.get("insertion length", "") for r in get_temperature_gauges_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("moc", "") == moc and r.get("insertion length", "")}))

@app.route("/api/temperature-gauges/dialsize")
def api_temperature_gauges_dialsize():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    moc = request.args.get("moc", "").strip()
    insertion = request.args.get("insertion", "").strip()
    if not all([type1, type2, moc, insertion]): return jsonify([])
    return jsonify(sorted({r.get("dial size", "") for r in get_temperature_gauges_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("moc", "") == moc and r.get("insertion length", "") == insertion and r.get("dial size", "")}))

@app.route("/api/temperature-gauges/details")
def api_temperature_gauges_details():
    params = {k: request.args.get(k, "").strip() for k in ["type1", "type2", "moc", "insertion", "dialsize"]}
    if not all(params.values()): return jsonify([])
    matches = [r for r in get_temperature_gauges_rows() if r.get("type1", "") == params["type1"] and r.get("type2", "") == params["type2"] and r.get("moc", "") == params["moc"] and r.get("insertion length", "") == params["insertion"] and r.get("dial size", "") == params["dialsize"]]
    return jsonify(matches)

# 7. Level Transmitter
@app.route("/level-transmitter")
def level_transmitter_page():
    type1 = sorted({r.get("type1", "") for r in get_level_transmitter_rows() if r.get("type1", "")})
    return render_template("instruments/level_transmitter.html", type1=type1)

@app.route("/api/level-transmitter/type1")
def api_level_transmitter_type1():
    return jsonify(sorted({r.get("type1", "") for r in get_level_transmitter_rows() if r.get("type1", "")}))

@app.route("/api/level-transmitter/type2")
def api_level_transmitter_type2():
    type1 = request.args.get("type1", "").strip()
    if not type1: return jsonify([])
    return jsonify(sorted({r.get("type2", "") for r in get_level_transmitter_rows() if r.get("type1", "") == type1 and r.get("type2", "")}))

@app.route("/api/level-transmitter/application")
def api_level_transmitter_application():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    if not all([type1, type2]): return jsonify([])
    return jsonify(sorted({r.get("application", "") for r in get_level_transmitter_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("application", "")}))

@app.route("/api/level-transmitter/range")
def api_level_transmitter_range():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    app = request.args.get("application", "").strip()
    if not all([type1, type2, app]): return jsonify([])
    return jsonify(sorted({r.get("range", "") for r in get_level_transmitter_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("application", "") == app and r.get("range", "")}))

@app.route("/api/level-transmitter/details")
def api_level_transmitter_details():
    params = {k: request.args.get(k, "").strip() for k in ["type1", "type2", "application", "range"]}
    if not all(params.values()): return jsonify([])
    matches = [r for r in get_level_transmitter_rows() if r.get("type1", "") == params["type1"] and r.get("type2", "") == params["type2"] and r.get("application", "") == params["application"] and r.get("range", "") == params["range"]]
    return jsonify(matches)

# 8. Level & Flow Switch
@app.route("/level-flow-switch")
def ls_fs_page():
    types = sorted({r.get("type", "") for r in get_ls_fs_rows() if r.get("type", "")})
    return render_template("instruments/level_flow_switch.html", types=types)

@app.route("/api/level-flow-switch/types")
def api_ls_fs_types():
    return jsonify(sorted({r.get("type", "") for r in get_ls_fs_rows() if r.get("type", "")}))

@app.route("/api/level-flow-switch/accessories")
def api_ls_fs_accessories():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({r.get("accessories", "") for r in get_ls_fs_rows() if r.get("type", "") == type_val and r.get("accessories", "")}))

@app.route("/api/level-flow-switch/details")
def api_ls_fs_details():
    type_val = request.args.get("type", "").strip()
    accessories = request.args.get("accessories", "").strip()
    if not all([type_val, accessories]): return jsonify([])
    matches = [r for r in get_ls_fs_rows() if r.get("type", "") == type_val and r.get("accessories", "") == accessories]
    return jsonify(matches)

# 9. Temperature Elements
@app.route("/temperature-elements")
def temperature_elements_page():
    type1 = sorted({r.get("type1", "") for r in get_temperature_elements_rows() if r.get("type1", "")})
    return render_template("instruments/temperature_elements.html", type1=type1)

@app.route("/api/temperature-elements/type1")
def api_temperature_elements_type1():
    return jsonify(sorted({r.get("type1", "") for r in get_temperature_elements_rows() if r.get("type1", "")}))

@app.route("/api/temperature-elements/type2")
def api_temperature_elements_type2():
    type1 = request.args.get("type1", "").strip()
    if not type1: return jsonify([])
    return jsonify(sorted({r.get("type2", "") for r in get_temperature_elements_rows() if r.get("type1", "") == type1 and r.get("type2", "")}))

@app.route("/api/temperature-elements/type3")
def api_temperature_elements_type3():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    if not all([type1, type2]): return jsonify([])
    return jsonify(sorted({r.get("type3", "") for r in get_temperature_elements_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("type3", "")}))

@app.route("/api/temperature-elements/moc")
def api_temperature_elements_moc():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    type3 = request.args.get("type3", "").strip()
    if not all([type1, type2, type3]): return jsonify([])
    return jsonify(sorted({r.get("moc", "") for r in get_temperature_elements_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("type3", "") == type3 and r.get("moc", "")}))

@app.route("/api/temperature-elements/insertion")
def api_temperature_elements_insertion():
    type1 = request.args.get("type1", "").strip()
    type2 = request.args.get("type2", "").strip()
    type3 = request.args.get("type3", "").strip()
    moc = request.args.get("moc", "").strip()
    if not all([type1, type2, type3, moc]): return jsonify([])
    return jsonify(sorted({r.get("insertion length", "") for r in get_temperature_elements_rows() if r.get("type1", "") == type1 and r.get("type2", "") == type2 and r.get("type3", "") == type3 and r.get("moc", "") == moc and r.get("insertion length", "")}))

@app.route("/api/temperature-elements/details")
def api_temperature_elements_details():
    params = {k: request.args.get(k, "").strip() for k in ["type1", "type2", "type3", "moc", "insertion"]}
    if not all(params.values()): return jsonify([])
    matches = [r for r in get_temperature_elements_rows() if r.get("type1", "") == params["type1"] and r.get("type2", "") == params["type2"] and r.get("type3", "") == params["type3"] and r.get("moc", "") == params["moc"] and r.get("insertion length", "") == params["insertion"]]
    return jsonify(matches)

# 10. Misc Instruments
@app.route("/misc-instruments")
def misc_instruments_page():
    types = sorted({r.get("type", "") for r in get_misc_instruments_rows() if r.get("type", "")})
    return render_template("instruments/misc_instruments.html", types=types)

@app.route("/api/misc/types")
def api_misc_types():
    return jsonify(sorted({r.get("type", "") for r in get_misc_instruments_rows() if r.get("type", "")}))

@app.route("/api/misc/details")
def api_misc_details_field():
    type_val = request.args.get("type", "").strip()
    if not type_val: return jsonify([])
    return jsonify(sorted({r.get("details", "") for r in get_misc_instruments_rows() if r.get("type", "") == type_val and r.get("details", "")}))

@app.route("/api/misc/accessories")
def api_misc_accessories():
    type_val = request.args.get("type", "").strip()
    details = request.args.get("details", "").strip()
    if not all([type_val, details]): return jsonify([])
    return jsonify(sorted({r.get("accessories", "") for r in get_misc_instruments_rows() if r.get("type", "") == type_val and r.get("details", "") == details and r.get("accessories", "")}))

@app.route("/api/misc/results")
def api_misc_results():
    type_val = request.args.get("type", "").strip()
    details = request.args.get("details", "").strip()
    accessories = request.args.get("accessories", "").strip()
    if not all([type_val, details, accessories]): return jsonify([])
    matches = [r for r in get_misc_instruments_rows() if r.get("type", "") == type_val and r.get("details", "") == details and r.get("accessories", "") == accessories]
    return jsonify(matches)

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
