# test_accuracy.py
import json
import sys
from pathlib import Path

# Calculate absolute path to backend
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from orchestrator.claims_orchestrator import process_claim  # type: ignore

TEST_FOLDER = project_root / "test_claims"
results = []
total = 0

print("STARTING ACCURACY TEST ON ALL JSON FILES IN test_claims/\n")

# Change from *.pdf to *.json
for json_file in sorted(TEST_FOLDER.glob("*.json")):
    print(f"Processing → {json_file.name}")
    try:
        with open(json_file, "rb") as f:
            result = process_claim(
                file_bytes=f.read(),
                content_type="application/json",  # Fixed: JSON mime type
                filename=json_file.name  
            )
        
        decision = result["final_decision"]["decision"]
        fraud_risk = result["fraud"]["risk_level"]
        amount = result["extracted"].get("claim_amount", 0)
        patient = result["extracted"].get("patient_name", "Unknown")

        print(f"   Decision: {decision} | Fraud: {fraud_risk} | Amount: ${amount} | Patient: {patient}\n")

        results.append({
            "file": json_file.name,
            "decision": decision,
            "fraud_risk": fraud_risk,
            "amount": amount,
            "patient": patient
        })
        
        total += 1
    except Exception as e:
        print(f"   ERROR: {e}\n")
        import traceback
        traceback.print_exc()

# Save results
output_file = project_root / "system_results.json"
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nTEST COMPLETE! Processed {total} files.")
print(f"Results saved to {output_file}")