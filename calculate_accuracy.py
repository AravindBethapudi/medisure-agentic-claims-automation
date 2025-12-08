# calculate_accuracy.py
import json
import sys
from pathlib import Path

# Add backend to Python path
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from   orchestrator.claims_orchestrator import process_claim  # pyright: ignore[reportMissingImports]

TEST_FOLDER = project_root / "test_claims"
results = []
correct_decisions = 0
correct_fraud = 0
total = 0

print("\n" + "="*70)
print("TESTING SYSTEM ACCURACY")
print("="*70 + "\n")

for json_file in sorted(TEST_FOLDER.glob("*.json")):
    print(f"Testing: {json_file.name}")
    
    try:
        # Load the test file
        with open(json_file, "r") as f:
            test_data = json.load(f)
        
        # Get what we EXPECT
        expected_decision = test_data.get("expected_decision", "").upper()
        expected_fraud = test_data.get("expected_fraud", "").upper()
        
        # Run it through your system
        with open(json_file, "rb") as f:
            result = process_claim(
                file_bytes=f.read(),
                content_type="application/json",
                filename=json_file.name
            )
        
        # Get what the system ACTUALLY decided
        actual_decision = result["final_decision"]["decision"]
        actual_fraud = result["fraud"]["risk_level"]
        
        # Compare
        decision_correct = (actual_decision == expected_decision)
        fraud_correct = (actual_fraud == expected_fraud)
        
        # Count it
        total += 1
        if decision_correct:
            correct_decisions += 1
        if fraud_correct:
            correct_fraud += 1
        
        # Show results
        print(f"  Expected: Decision={expected_decision}, Fraud={expected_fraud}")
        print(f"  Got:      Decision={actual_decision}, Fraud={actual_fraud}")
        print(f"  Decision: {'✅ CORRECT' if decision_correct else '❌ WRONG'}")
        print(f"  Fraud:    {'✅ CORRECT' if fraud_correct else '❌ WRONG'}")
        print()
        
        results.append({
            "file": json_file.name,
            "expected_decision": expected_decision,
            "actual_decision": actual_decision,
            "decision_correct": decision_correct,
            "expected_fraud": expected_fraud,
            "actual_fraud": actual_fraud,
            "fraud_correct": fraud_correct
        })
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}\n")

# Calculate accuracy
if total > 0:
    decision_accuracy = (correct_decisions / total) * 100
    fraud_accuracy = (correct_fraud / total) * 100
else:
    decision_accuracy = 0
    fraud_accuracy = 0

# Show final results
print("="*70)
print("FINAL ACCURACY REPORT")
print("="*70)
print(f"\nTotal Claims Tested: {total}")
print(f"\n📊 ACCURACY:")
print(f"   Decision Accuracy: {decision_accuracy:.1f}% ({correct_decisions}/{total} correct)")
print(f"   Fraud Accuracy:    {fraud_accuracy:.1f}% ({correct_fraud}/{total} correct)")
print(f"\n{'='*70}\n")

# Save report
with open("accuracy_report.json", "w") as f:
    json.dump({
        "total_tested": total,
        "decision_accuracy": round(decision_accuracy, 2),
        "fraud_accuracy": round(fraud_accuracy, 2),
        "results": results
    }, f, indent=2)

print("📁 Detailed report saved to: accuracy_report.json\n")