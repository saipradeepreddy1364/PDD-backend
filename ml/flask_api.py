from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import json
import os
import csv

app = Flask(__name__)
CORS(app)

# ============================================================
# Step Descriptions — based on DIAS template + dental books
# ============================================================
STEP_DESCRIPTIONS = {
    "Start": "Beginning of the dental lab procedure workflow.",
    "Secondary Cast": "An accurate stone cast is poured from the final impression received from the dentist. This serves as the working model on which the prosthesis will be fabricated.",
    "Special Tray": "A custom-made impression tray is fabricated on the primary cast to obtain an accurate final impression of the patient's mouth.",
    "Verification Jig": "A rigid acrylic jig is fabricated to verify the accuracy of implant positions before final prosthesis fabrication.",
    "FPD Wax Pattern": "A precise wax pattern of the fixed partial denture is sculpted on the working cast to define the shape, contour, and occlusion of the final restoration.",
    "Metal Coping": "The wax pattern is invested and cast in metal alloy. The resulting metal coping is a thin shell that forms the substructure for ceramic application.",
    "Bisque Trial": "The ceramic-layered restoration is sent to the dentist in bisque (unglazed) stage for clinical trial and shade verification before final glazing.",
    "Crown Fabrication": "The final crown is fabricated based on the prescribed material — monolithic zirconia, metal ceramic, or full metal — ready for delivery.",
    "Ceramic Coping": "A ceramic coping is milled or pressed from zirconia or lithium disilicate to form the substructure for hand layering.",
    "Hand Layered Crown": "Ceramic powders are layered manually over the coping by a skilled technician to achieve the desired shade, shape, and translucency.",
    "Ceramic Facing": "Ceramic material is applied to the facial/visible surface of the metal framework to provide aesthetic appearance while maintaining metal strength.",
    "Implant Wax Pattern": "A customized wax pattern is created for the implant abutment or suprastructure to define the emergence profile and restoration shape.",
    "Metal Cast Custom Abutment": "The wax pattern is cast in metal to create a patient-specific abutment that connects the implant to the final crown.",
    "Block Out": "Undercuts on the master cast are blocked out with wax or blockout material to allow clean removal of the cast partial denture framework.",
    "CPD Wax Pattern": "A wax pattern of the cast partial denture framework is sculpted, defining the clasps, connectors, and rest seats.",
    "CPD Metal Denture Base": "The wax pattern is invested and cast to produce the metal framework of the removable partial denture using cobalt-chromium alloy.",
    "Articulation": "The casts are mounted on an articulator to simulate the patient's jaw movements and establish correct occlusion for teeth arrangement.",
    "CPD Teeth Setting": "Artificial teeth are selected and arranged on the framework in correct occlusion and aesthetically pleasing positions.",
    "CPD Processing": "The denture is flasked, the wax is eliminated, and acrylic resin is packed and cured to form the denture base with teeth in final position.",
    "Duplication": "The blocked-out master cast is duplicated using agar or silicone to create a refractory cast on which the metal framework wax pattern is built.",
    "Framework": "The metal framework for the removable partial denture is cast, finished, and polished, ready for denture base addition.",
    "Wax Pattern": "A wax pattern is built up to define the shape and contours of the prosthesis before investing and casting.",
    "Investing": "The wax pattern is surrounded by investment material in a casting ring. The investment hardens to form a mold for casting.",
    "Casting": "Molten metal alloy is forced into the investment mold under pressure or centrifugal force to produce the metal component.",
    "Devesting": "The solidified casting is removed from the investment material. Excess investment is cleaned off using steam or ultrasonic cleaning.",
    "Finishing and Polishing": "The casting is trimmed, finished with abrasive stones and polishing compounds to achieve a smooth, biocompatible surface.",
    "Soldering": "Metal components are joined using a solder alloy at high temperature to create connectors between crowns in a bridge or between framework parts.",
    "Survey and Design": "The master cast is analyzed on a surveyor to identify undercuts and design the optimal path of insertion for the removable partial denture.",
    "Occlusal Rims": "Wax rims are fabricated on the record base to record the patient's jaw relationships, vertical dimension, and lip support.",
    "Denture Base": "A record base is fabricated from acrylic resin on the cast to carry the occlusal rims during jaw relationship recording.",
    "Flexible Denture Base": "The flexible denture material (Biodentaplast or Bredent Polyan) is injection-molded to create a flexible, metal-free partial denture base.",
    "Flexible Denture Processing": "The flexible thermoplastic material is heated and injection-molded around the arranged teeth to form the final flexible denture.",
    "Adjustment": "Minor corrections are made to the prosthesis to improve fit, occlusion, or aesthetics based on clinical feedback.",
    "Repair or Reline": "The denture is repaired if fractured, or relined to improve fit by adding new acrylic to the tissue-bearing surface.",
    "Trimming": "Excess plaster or stone is trimmed from the cast using a model trimmer to achieve standard dimensions and a flat base.",
    "Mounting": "The casts are attached to the articulator using plaster, replicating the patient's jaw relationship for accurate prosthesis fabrication.",
    "Cleaning": "The casting or prosthesis is cleaned using steam, ultrasonic bath, or chemical solutions to remove investment, debris, and contamination.",
    "Coating": "A separating medium or die spacer is applied to the die to ensure accurate fit and easy removal of the wax pattern.",
    "Trial": "The prosthesis is assessed at a try-in stage for fit, occlusion, aesthetics, and patient comfort before final processing.",
    "Delivery": "The completed prosthesis is polished, inspected, and packaged for delivery to the dentist for patient fitting.",
    "Zirconia Milling": "A zirconia block is milled using CAD/CAM technology based on a digital scan to produce the crown or framework in pre-sintered zirconia.",
    "DMLS Printing": "Direct Metal Laser Sintering technology is used to 3D print the metal framework or denture base in titanium or cobalt-chromium.",
    "PMMA CADCAM": "A PMMA (polymethyl methacrylate) block is milled using CAD/CAM to produce a temporary or long-term acrylic crown or bridge.",
    "Temporary Acrylic Crown": "A short-term acrylic crown is fabricated to protect the prepared tooth while the permanent restoration is being made.",
    "Diagnostic Wax Up Manual": "A wax mock-up is hand-sculpted on the study cast to visualize and plan the final aesthetic and functional outcome.",
    "Diagnostic Wax Up CADCAM": "A digital wax-up is designed using CAD software and milled from PMMA to simulate the final restorative outcome.",
    "Oral Appliance": "An orthodontic or functional appliance is fabricated from acrylic and wire components to move teeth or maintain arch space.",
    "PSI Finishing And Polishing": "Post-soldering inspection and final polishing is performed to ensure all joints are clean and the surface is smooth.",
    "Primary Coping": "The inner (primary) coping is fabricated in metal and fits precisely over the prepared abutment tooth.",
    "Secondary Coping": "The outer (secondary) coping is fabricated to fit over the primary coping, providing retention for the removable telescopic prosthesis.",
    "Welding Soldering": "Framework components or clasps are joined by welding or soldering to repair or connect metal parts.",
    "Maryland Bridge": "Metal wings are cast and bonded to adjacent teeth to support the pontic without crown preparation.",
    "Maryland Pontic": "The artificial tooth (pontic) is fabricated and attached to the Maryland bridge retainer wings.",
    "Post And Core": "A metal post is cast to fit into the root canal and a core is built up to provide retention for the final crown.",
    "Metal Onlay": "A metal onlay is cast to cover the cusps and occlusal surface of a tooth with minimal tooth reduction.",
    "Ceramic Onlay": "A ceramic onlay is pressed or milled from lithium disilicate or zirconia to restore the occlusal surface aesthetically.",
    "Metal Inlay": "A metal inlay is cast to restore a cavity within the tooth structure using a gold or base metal alloy.",
    "Ceramic Inlay": "A ceramic inlay is fabricated from zirconia or lithium disilicate for aesthetic restoration of a tooth cavity.",
    "Malo Framework": "A full-arch implant-supported metal framework is 3D printed in titanium for the All-on-4 or All-on-6 type prosthesis.",
    "BPS Teeth Setting": "Teeth are set using the Biofunctional Prosthetic System protocol ensuring balanced occlusion and optimal function.",
    "BPS CD Processing": "The complete denture is processed using Ivoclar's BPS processing protocol with Ivocap injection system for superior fit.",
    "CD Teeth Setting": "Acrylic teeth are arranged on the wax denture base in correct occlusion and aesthetic position for patient trial.",
    "CD Processing": "The denture is flasked and processed — wax is boiled out, acrylic resin is packed and pressure-cured to form the final denture.",
    "Relining Rebasing Repair": "The existing denture is refitted to the current tissue contour by adding new acrylic to the fitting surface.",
    "Teeth Setting Correction": "The tooth positions are corrected based on clinical trial feedback to improve aesthetics or occlusion.",
    "TPD Denture Processing": "The transitional partial denture is processed in acrylic resin with the arranged teeth in their final positions.",
    "Endo Crown": "A one-piece ceramic restoration is fabricated to restore a root-canal-treated posterior tooth without a separate post and core.",
    "FVC Wax Pattern": "A wax pattern is sculpted for a fixed veneer crown on the die, defining the final shape before casting.",
    "ML Acrylic Temporary Crown": "A multilayer acrylic temporary crown is milled from PMMA-ML block for superior aesthetics during the provisional phase.",
    "Monolayer Acrylic Temp Crown": "A single-layer PMMA temporary crown is milled for short-term use as a provisional restoration.",
    "Hard Splint": "A rigid acrylic occlusal splint is fabricated to protect teeth from bruxism or stabilize the jaw joint.",
    "Soft Splint": "A flexible thermoplastic splint is fabricated as a night guard or sports guard.",
}

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

def get_description(step_name):
    for key, desc in STEP_DESCRIPTIONS.items():
        if key.lower() == step_name.lower():
            return desc
    return f"{step_name} — a standard dental laboratory procedure step."

# ============================================================
# Helper — Predict Next Step
# ============================================================
def predict_next(procedure, subtype, current_step):
    proc = procedure.strip().lower()
    sub  = subtype.strip().lower()
    curr = current_step.strip().lower()

    key = f"{proc}|{sub}|{curr}"
    if key in LOOKUP:
        return LOOKUP[key], 100.0, "lookup"

    key2 = f"{proc}||{curr}"
    if key2 in LOOKUP:
        return LOOKUP[key2], 90.0, "lookup_no_subtype"

    for k, v in LOOKUP.items():
        k_proc, k_sub, k_curr = k.split("|", 2)
        if k_proc == proc and k_curr == curr:
            return v, 85.0, "lookup_partial"

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
        "procedure":          procedure,
        "subtype":            subtype,
        "current_step":       current_step,
        "current_step_description": get_description(current_step),
        "next_step":          next_step_val,
        "next_step_description": get_description(next_step_val),
        "confidence":         confidence,
        "source":             source
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
            "step_number":        len(steps) + 1,
            "current_step":       current,
            "current_description": get_description(current),
            "next_step":          next_step_val,
            "next_description":   get_description(next_step_val),
            "confidence":         confidence,
            "source":             source
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