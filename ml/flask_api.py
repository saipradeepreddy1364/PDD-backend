from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import json
import os
import csv

app = Flask(__name__)
CORS(app)

# ============================================================
# Load ML Model
# ============================================================
print("Loading dental lab model...")
with open("saved_model/dental_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("saved_model/label_encoder.pkl", "rb") as f:
    le = pickle.load(f)
with open("saved_model/model_metadata.json", "r") as f:
    metadata = json.load(f)
print(f"Model loaded: {metadata['best_model']}")

# ============================================================
# Build Lookup Table from CSV
# ============================================================
LOOKUP = {}

def build_lookup():
    csv_path = "dental_steps.csv"
    if not os.path.exists(csv_path):
        print("CSV not found — lookup table empty")
        return
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            proc = row.get("procedure", "").strip().lower()
            sub  = row.get("subtype", "").strip().lower()
            curr = row.get("current_step", "").strip().lower()
            nxt  = row.get("next_step", "").strip()
            if proc and curr and nxt:
                key = f"{proc}|{sub}|{curr}"
                if key not in LOOKUP:
                    LOOKUP[key] = nxt
    print(f"Lookup table built: {len(LOOKUP)} entries")

build_lookup()

# ============================================================
# Helper — Predict Next Step
# ============================================================
def predict_next(procedure, subtype, current_step):
    proc = procedure.strip().lower()
    sub  = subtype.strip().lower()
    curr = current_step.strip().lower()

    # Try exact lookup first
    key = f"{proc}|{sub}|{curr}"
    if key in LOOKUP:
        return LOOKUP[key], 100.0, "lookup"

    # Try without subtype
    key2 = f"{proc}||{curr}"
    if key2 in LOOKUP:
        return LOOKUP[key2], 90.0, "lookup_no_subtype"

    # Try partial subtype match
    for k, v in LOOKUP.items():
        k_proc, k_sub, k_curr = k.split("|", 2)
        if k_proc == proc and k_curr == curr:
            return v, 85.0, "lookup_partial"

    # Fallback to ML model
    input_text = f"{proc} | {sub} | {curr}"
    try:
        pred_encoded = model.predict([input_text])[0]
        pred_proba   = model.predict_proba([input_text])[0]
        confidence   = round(float(max(pred_proba)) * 100, 2)
        next_step    = le.inverse_transform([pred_encoded])[0]
        return next_step, confidence, "ml_model"
    except Exception as e:
        return "Unknown", 0.0, "error"

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "model": metadata["best_model"],
        "accuracy": f"{metadata['accuracy']*100:.2f}%",
        "lookup_entries": len(LOOKUP),
        "total_classes": metadata["total_classes"]
    })

@app.route("/api/next-step", methods=["POST"])
def next_step():
    data = request.get_json()
    procedure    = data.get("procedure", "").strip()
    subtype      = data.get("subtype", "").strip()
    current_step = data.get("current_step", "").strip()

    if not procedure or not current_step:
        return jsonify({"error": "procedure and current_step are required"}), 400

    next_step_val, confidence, source = predict_next(procedure, subtype, current_step)

    return jsonify({
        "procedure":    procedure,
        "subtype":      subtype,
        "current_step": current_step,
        "next_step":    next_step_val,
        "confidence":   confidence,
        "source":       source
    })

@app.route("/api/predict-full", methods=["POST"])
def predict_full():
    data = request.get_json()
    procedure = data.get("procedure", "").strip()
    subtype   = data.get("subtype", "").strip()

    if not procedure or not subtype:
        return jsonify({"error": "procedure and subtype are required"}), 400

    steps   = []
    current = "Start"
    visited = set()

    for _ in range(20):
        if current in visited:
            break
        visited.add(current)
        next_step_val, confidence, source = predict_next(procedure, subtype, current)
        if next_step_val == "Unknown" or next_step_val == current:
            break
        steps.append({
            "step_number":  len(steps) + 1,
            "current_step": current,
            "next_step":    next_step_val,
            "confidence":   confidence,
            "source":       source
        })
        current = next_step_val

    return jsonify({
        "procedure":   procedure,
        "subtype":     subtype,
        "total_steps": len(steps),
        "workflow":    steps
    })

@app.route("/api/procedures", methods=["GET"])
def get_procedures():
    procedures = {}
    for key in LOOKUP:
        proc, sub, curr = key.split("|", 2)
        if proc not in procedures:
            procedures[proc] = set()
        procedures[proc].add(sub)
    result = {k: list(v) for k, v in procedures.items()}
    return jsonify(result)

@app.route("/api/model-info", methods=["GET"])
def model_info():
    return jsonify({
        **metadata,
        "lookup_entries": len(LOOKUP),
        "lookup_accuracy": "100% for known procedures"
    })

if __name__ == "__main__":
    print("\nStarting Dental Lab ML API...")
    app.run(host="0.0.0.0", port=5000, debug=True)