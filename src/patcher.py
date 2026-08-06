import json
import libcst as cst
from libcst import parse_module, MetadataWrapper
from libcst.metadata import PositionProvider

class SquareMigrationTransformer(cst.CSTTransformer):
    """
    Transformer that applies Square SDK migration rules:
    Renames class LegacySquare->Square, parameters access_token->token, etc.
    Logs each applied rule with location from metadata.
    """
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, rules):
        # rules is a dict mapping operator to lists of rule definitions
        super().__init__()
        self.rules = rules
        self.applied = []  # Will store applied rule info for the report

    def leave_Call(self, original_node, updated_node):
        """
        Called after visiting a function/class call. We handle:
        - RenameClass: replace LegacySquare(...) with Square(...)
        - RenameParameter/DeleteParameter/ReplaceValue: adjust keyword args.
        """
        new_func = updated_node.func
        new_args = []
        # Handle RenameClass: if class name is LegacySquare, change to Square
        if isinstance(updated_node.func, cst.Name):
            name = updated_node.func.value
            for rule in self.rules.get("RenameClass", []):
                if name == rule["match"]["class"]:
                    # Apply RenameClass
                    new_name = rule["patch"]["class"]
                    new_func = cst.Name(new_name)
                    # Record rule application
                    pos = self.get_metadata(PositionProvider, original_node).start
                    self.applied.append({
                        "rule_id": rule["id"],
                        "rule": "RenameClass",
                        "confidence": rule.get("confidence", 1.0),
                        "line": pos.line,
                        "col": pos.column
                    })
                    break

        # Process each keyword argument for other operators
        for arg in updated_node.args:
            # Only consider keyword arguments (arg.keyword is cst.Name)
            if arg.keyword and isinstance(arg.keyword, cst.Name):
                key = arg.keyword.value
                handled = False

                # Check RenameParameter rules
                for rule in self.rules.get("RenameParameter", []):
                    if key == rule["match"]["parameter"]:
                        new_key = rule["patch"]["parameter"]
                        new_args.append(arg.with_changes(keyword=cst.Name(new_key)))
                        # Record rule application
                        pos = self.get_metadata(PositionProvider, original_node).start
                        self.applied.append({
                            "rule_id": rule["id"],
                            "rule": "RenameParameter",
                            "confidence": rule.get("confidence", 1.0),
                            "line": pos.line,
                            "col": pos.column
                        })
                        handled = True
                        break
                if handled:
                    continue

                # Check DeleteParameter rules
                delete_names = {rule["match"]["parameter"] for rule in self.rules.get("DeleteParameter", [])}
                if key in delete_names:
                    # Skip adding this arg => it is removed
                    for rule in self.rules.get("DeleteParameter", []):
                        if key == rule["match"]["parameter"]:
                            pos = self.get_metadata(PositionProvider, original_node).start
                            self.applied.append({
                                "rule_id": rule["id"],
                                "rule": "DeleteParameter",
                                "confidence": rule.get("confidence", 1.0),
                                "line": pos.line,
                                "col": pos.column
                            })
                            break
                    # Don't append this arg (deletion)
                    continue

                # Check ReplaceValue rules (specific to environment="sandbox")
                # We match literal values, not operator-based here
                for rule in self.rules.get("ReplaceValue", []):
                    old_val = rule["match"].get("value")
                    # Compare string literal (including quotes)
                    if key == "environment" and isinstance(arg.value, cst.SimpleString) \
                       and arg.value.value == old_val:
                        new_val_code = rule["patch"]["value"]
                        # Parse the new expression with module config
                        new_expr = cst.parse_expression(new_val_code)
                        new_args.append(arg.with_changes(value=new_expr))
                        pos = self.get_metadata(PositionProvider, original_node).start
                        self.applied.append({
                            "rule_id": rule["id"],
                            "rule": "ReplaceValue",
                            "confidence": rule.get("confidence", 1.0),
                            "line": pos.line,
                            "col": pos.column
                        })
                        handled = True
                        break
                if handled:
                    continue

                # No rule matched: keep argument unchanged
                new_args.append(arg)
            else:
                # Positional arguments or others are unchanged
                new_args.append(arg)

        # Return updated call node with any changes to func or args
        updated_call = updated_node.with_changes(func=new_func, args=new_args)
        return updated_call

    def leave_Name(self, original_node, updated_node):
        """
        Handle standalone class references (e.g., if LegacySquare was used as a value).
        Replace LegacySquare name with Square.
        """
        name = original_node.value
        for rule in self.rules.get("RenameClass", []):
            if name == rule["match"]["class"]:
                pos = self.get_metadata(PositionProvider, original_node).start
                self.applied.append({
                    "rule_id": rule["id"],
                    "rule": "RenameClass",
                    "confidence": rule.get("confidence", 1.0),
                    "line": pos.line,
                    "col": pos.column
                })
                return cst.Name(rule["patch"]["class"])
        return updated_node

def run_patcher(input_file: str, output_file: str):
    """
    Load migration_rules.json and apply the transformer to the given file.
    Write patched code and print a JSON report of applied rules.
    """
    # Load migration rules
    with open("data/migration_rules.json") as f:
        rules_list = json.load(f)
    # Organize rules by operator
    rules = {"RenameParameter": [], "RenameClass": [], "ReplaceValue": [], "DeleteParameter": []}
    for rule in rules_list:
        rules[rule["operator"]].append(rule)

    # Parse the source file with LibCST
    source_code = open(input_file, 'r').read()
    module = parse_module(source_code)
    # Wrap with MetadataWrapper to enable position info
    wrapper = MetadataWrapper(module)
    transformer = SquareMigrationTransformer(rules)
    patched_tree = wrapper.visit(transformer)

    # Write patched code to file
    with open(output_file, 'w') as f:
        f.write(patched_tree.code)

    # -----------------------------
    # Prepare Migration Report
    # -----------------------------

    # Count how many times each operator was applied
    operator_counts = {}

    for rule in transformer.applied:
        operator = rule["rule"]
        operator_counts[operator] = operator_counts.get(operator, 0) + 1

    report = {
        "summary": {
            "provider": "Square Python SDK",
            "migration_class": "Method Signature Evolution",
            "input_file": input_file,
            "output_file": output_file,
            "total_rules_applied": len(transformer.applied),
            "operator_statistics": operator_counts
        },
    "applied_rules": transformer.applied
    }

    # Save report
    with open("migration_report.json", "w") as f:
        json.dump(report, f, indent=4)

    # Pretty terminal output
    print("\n" + "=" * 60)
    print("      SDK BREAKING CHANGE PATCH REPORT")
    print("=" * 60)

    print(f"Provider              : Square Python SDK")
    print(f"Migration Class       : Method Signature Evolution")
    print(f"Input File            : {input_file}")
    print(f"Output File           : {output_file}")

    print("\nMigration Operators Applied")
    print("-" * 60)

    for operator, count in operator_counts.items():
        print(f"{operator:<22}: {count}")

    print("-" * 60)
    print(f"Total Transformations : {len(transformer.applied)}")

    print("\nGenerated Files")
    print("-" * 60)
    print(f"✓ {output_file}")
    print("✓ migration_report.json")

    print("=" * 60 + "\n")

    return report
if __name__ == "__main__":
    # Example usage: migrate samples/old_client.py -> samples/patched_client.py
    run_patcher("samples/old_client.py", "samples/patched_client.py")
