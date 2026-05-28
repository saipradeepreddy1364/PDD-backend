from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import json
import os

app = Flask(__name__)
CORS(app)  # Allow Spring Boot to call this API

# ============================================================
# Load Model on Startup
# ============================================================
print("Loading dental lab model...")
with open("saved_model/dental_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("saved_model/label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

with open("saved_model/model_metadata.json", "r") as f:
    metadata = json.load(f)

print(f"Model loaded: {metadata['best_model']}")
print(f"Accuracy: {metadata['accuracy']*100:.2f}%")

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "model": metadata["best_model"],
        "accuracy": f"{metadata['accuracy']*100:.2f}%",
        "total_classes": metadata["total_classes"]
    })


@app.route("/api/next-step", methods=["POST"])
def next_step():
    """
    Main endpoint — predicts the next step
    Body: { "procedure": "FPD", "subtype": "Metal Ceramic", "current_step": "Metal Coping" }
    """
    data = request.get_json()

    procedure    = data.get("procedure", "").strip()
    subtype      = data.get("subtype", "").strip()
    current_step = data.get("current_step", "").strip()

    if not procedure or not subtype or not current_step:
        return jsonify({"error": "procedure, subtype and current_step are required"}), 400

    # Build input text same way as training
    input_text = f"{procedure.lower()} | {subtype.lower()} | {current_step.lower()}"

    try:
        pred_encoded = model.predict([input_text])[0]
        pred_proba   = model.predict_proba([input_text])[0]
        confidence   = round(float(max(pred_proba)) * 100, 2)
        next_step_val = le.inverse_transform([pred_encoded])[0]

        return jsonify({
            "procedure":    procedure,
            "subtype":      subtype,
            "current_step": current_step,
            "next_step":    next_step_val,
            "confidence":   confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict-full", methods=["POST"])
def predict_full():
    """
    Predict full procedure chain from start
    Body: { "procedure": "FPD", "subtype": "Metal Ceramic" }
    """
    data = request.get_json()
    procedure = data.get("procedure", "").strip()
    subtype   = data.get("subtype", "").strip()

    if not procedure or not subtype:
        return jsonify({"error": "procedure and subtype are required"}), 400

    steps = []
    current = "Start"
    visited = set()
    max_steps = 15  # prevent infinite loop

    for _ in range(max_steps):
        if current in visited:
            break
        visited.add(current)

        input_text = f"{procedure.lower()} | {subtype.lower()} | {current.lower()}"
        try:
            pred_encoded  = model.predict([input_text])[0]
            next_step_val = le.inverse_transform([pred_encoded])[0]
            steps.append({
                "step_number": len(steps) + 1,
                "current_step": current,
                "next_step": next_step_val
            })
            current = next_step_val
        except:
            break

    return jsonify({
        "procedure": procedure,
        "subtype":   subtype,
        "total_steps": len(steps),
        "workflow":  steps
    })


@app.route("/api/model-info", methods=["GET"])
def model_info():
    """Returns model metadata"""
    return jsonify(metadata)


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print("\nStarting Dental Lab ML API...")
    print("Endpoints:")
    print("  GET  /health")
    print("  POST /api/next-step")
    print("  POST /api/predict-full")
    print("  GET  /api/model-info")
    app.run(host="0.0.0.0", port=5000, debug=True)
