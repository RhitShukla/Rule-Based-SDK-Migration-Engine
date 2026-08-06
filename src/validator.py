import ast
import json


class Validator:
    def __init__(self, report):
        self.report = report

    def syntax_check(self, filename):
        try:
            with open(filename, "r") as f:
                ast.parse(f.read())
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, str(e)

    def migration_check(self, filename):
        with open(filename) as f:
            code = f.read()

        issues = []

        if "LegacySquare" in code:
            issues.append("LegacySquare still exists.")

        if "access_token=" in code:
            issues.append("access_token not migrated.")

        if "custom_url=" in code:
            issues.append("custom_url not migrated.")

        if "square_version=" in code:
            issues.append("square_version not migrated.")

        if "http_call_back=" in code:
            issues.append("Deprecated http_call_back still exists.")

        if "user_agent_detail=" in code:
            issues.append("Deprecated user_agent_detail still exists.")

        return issues

    def validate(self, filename):
        ok, msg = self.syntax_check(filename)

        issues = self.migration_check(filename)

        result = {
            "syntax": ok,
            "syntax_message": msg,
            "migration_issues": issues,
            "rules_applied": len(self.report["applied_rules"]),
            "validation": "PASS" if ok and len(issues) == 0 else "FAIL"
        }

        return result
