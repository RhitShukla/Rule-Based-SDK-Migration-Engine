import json


class ConfidenceEngine:

    def __init__(self, report):
        self.report = report

    def calculate(self):

        scores = []

        for rule in self.report["applied_rules"]:
            scores.append(rule["confidence"])

        if len(scores) == 0:
            return {
                "overall_confidence": 0,
                "level": "LOW"
            }

        avg = sum(scores) / len(scores)

        if avg > 0.95:
            level = "HIGH"

        elif avg > 0.80:
            level = "MEDIUM"

        else:
            level = "LOW"

        return {
            "overall_confidence": round(avg, 2),
            "level": level
        }

