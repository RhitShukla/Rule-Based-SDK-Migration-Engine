from src.patcher import run_patcher
from src.validator import Validator
from src.confidence import ConfidenceEngine

INPUT_FILE = "samples/old_client.py"
OUTPUT_FILE = "samples/patched_client.py"

# -----------------------------
# Execute Migration
# -----------------------------
report = run_patcher(INPUT_FILE, OUTPUT_FILE)

# -----------------------------
# Validate Migration
# -----------------------------
validator = Validator(report)
validation = validator.validate(OUTPUT_FILE)

# -----------------------------
# Calculate Confidence
# -----------------------------
confidence_engine = ConfidenceEngine(report)
confidence = confidence_engine.calculate()

# -----------------------------
# Final Summary
# -----------------------------
print("=" * 60)
print("              MIGRATION VALIDATION")
print("=" * 60)

print(f"Syntax Check        : {'PASS' if validation['syntax'] else 'FAIL'}")
print(f"Migration Status    : {validation['validation']}")
print(f"Rules Applied       : {validation['rules_applied']}")

if validation["migration_issues"]:
    print("\nMigration Issues")
    print("-" * 60)
    for issue in validation["migration_issues"]:
        print(f"✗ {issue}")
else:
    print("Migration Issues    : None")

print("\n" + "=" * 60)
print("              CONFIDENCE REPORT")
print("=" * 60)

print(f"Overall Confidence : {confidence['overall_confidence']:.2f}")
print(f"Confidence Level   : {confidence['level']}")

print("=" * 60)
print("Prototype Execution Completed Successfully")
print("=" * 60)
