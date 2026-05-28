import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import pickle
import os

print("=" * 60)
print("DENTAL LAB NEXT STEP PREDICTOR - MODEL TRAINING")
print("=" * 60)

# ============================================================
# STEP 1 — Load Dataset
# ============================================================
print("\nStep 1: Loading dataset...")
df = pd.read_csv("dental_steps.csv")
print(f"Total rows loaded: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nProcedures found: {df['procedure'].nunique()}")
print(f"Unique next steps: {df['next_step'].nunique()}")

# ============================================================
# STEP 2 — Feature Engineering
# ============================================================
print("\nStep 2: Preparing features...")

# Combine procedure + subtype + current_step as one text feature
# This is the input the model will use to predict next_step
df['combined_input'] = (
    df['procedure'].str.lower() + " | " +
    df['subtype'].str.lower() + " | " +
    df['current_step'].str.lower()
)

X = df['combined_input']
y = df['next_step']

print(f"Sample input: {X.iloc[0]}")
print(f"Sample output: {y.iloc[0]}")

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"\nTotal unique classes (next steps): {len(le.classes_)}")

# ============================================================
# STEP 3 — Split Data
# ============================================================
print("\nStep 3: Splitting data (80% train / 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")

# ============================================================
# STEP 4 — Build & Train Models
# ============================================================
print("\nStep 4: Training models...")

models = {
    "Random Forest": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=42))
    ]),
    "SVM": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ('clf', SVC(kernel='rbf', probability=True, random_state=42))
    ]),
    "Logistic Regression": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ('clf', LogisticRegression(max_iter=1000, random_state=42))
    ])
}

results = {}
best_model = None
best_accuracy = 0
best_name = ""

for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    results[name] = acc
    print(f"  {name} Accuracy: {acc:.4f} ({acc*100:.2f}%)")

    if acc > best_accuracy:
        best_accuracy = acc
        best_model = model
        best_name = name

# ============================================================
# STEP 5 — Evaluate Best Model
# ============================================================
print("\n" + "=" * 60)
print(f"BEST MODEL: {best_name}")
print(f"BEST ACCURACY: {best_accuracy*100:.2f}%")
print("=" * 60)

y_pred_best = best_model.predict(X_test)
print("\nClassification Report (Top predictions):")
# Show report for first 10 classes only to keep output readable
unique_test = np.unique(y_test)[:10]
print(classification_report(
    y_test, y_pred_best,
    labels=unique_test,
    target_names=le.classes_[unique_test],
    zero_division=0
))

# ============================================================
# STEP 6 — Test With Sample Inputs
# ============================================================
print("\nStep 6: Testing with sample inputs...")

def predict_next_step(procedure, subtype, current_step):
    input_text = f"{procedure.lower()} | {subtype.lower()} | {current_step.lower()}"
    pred_encoded = best_model.predict([input_text])[0]
    pred_proba = best_model.predict_proba([input_text])[0]
    confidence = max(pred_proba) * 100
    next_step = le.inverse_transform([pred_encoded])[0]
    return next_step, confidence

test_cases = [
    ("FPD", "Metal Ceramic", "Secondary Cast"),
    ("FPD", "Metal Ceramic", "FPD Wax Pattern"),
    ("FPD", "Metal Ceramic", "Metal Coping"),
    ("Complete Denture", "BPS Teeth Setting", "Articulation"),
    ("Complete Denture", "CD Processing", "CD Teeth Setting"),
    ("Implant", "Metal Ceramic", "FPD Wax Pattern"),
    ("Cast Partial Denture", "Manual", "Block Out"),
    ("FVC Single Crown", "Hand Layered Crown", "Secondary Cast"),
]

print(f"\n{'Input':<60} {'Predicted Next Step':<35} {'Confidence'}")
print("-" * 110)
for proc, sub, curr in test_cases:
    next_step, conf = predict_next_step(proc, sub, curr)
    input_display = f"{proc} | {sub} | {curr}"
    print(f"{input_display:<60} {next_step:<35} {conf:.1f}%")

# ============================================================
# STEP 7 — Save Model
# ============================================================
print("\nStep 7: Saving model...")
os.makedirs("saved_model", exist_ok=True)

with open("saved_model/dental_model.pkl", "wb") as f:
    pickle.dump(best_model, f)

with open("saved_model/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

# Save model metadata
import json
metadata = {
    "best_model": best_name,
    "accuracy": best_accuracy,
    "total_training_rows": len(X_train),
    "total_test_rows": len(X_test),
    "total_classes": len(le.classes_),
    "all_model_accuracies": results
}
with open("saved_model/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\nModel saved to: saved_model/dental_model.pkl")
print(f"Label encoder saved to: saved_model/label_encoder.pkl")
print(f"Metadata saved to: saved_model/model_metadata.json")
print("\nTRAINING COMPLETE!")
