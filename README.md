# SDK Breaking Change Migration Prototype

> **Research Prototype** for automatically patching documented SDK breaking changes using rule-based source-to-source transformation with **LibCST**.

---

## Project Overview

Modern SDKs evolve continuously. New releases often introduce **breaking API changes** such as renamed classes, modified constructor signatures, renamed parameters, deprecated arguments, or changed constant values.

Although these changes are documented in migration guides, developers still have to manually inspect existing source code, identify affected API calls, modify them, and verify that the migration was performed correctly.

This prototype investigates whether a **rule-based migration engine** can automatically apply documented SDK breaking changes using static source-code transformation while preserving the original formatting and generating an auditable migration report.

---

## Problem Statement

Given

- an existing Python project using an older SDK version
- an official SDK migration guide

can a bot

1. detect documented breaking API changes,
2. automatically patch the client source code,
3. preserve formatting,
4. generate evidence of every transformation, and
5. provide a confidence estimate for the migration?

This prototype focuses on deterministic API migrations where the migration rules are explicitly documented by the SDK provider.

---

## API Provider

**Square Python SDK**

The migration rules were extracted exclusively from the official Square Python SDK migration documentation.

---

## Breaking Change Class

### Method Signature Evolution (Parameter Evolution)

This prototype supports documented interface changes including:

- RenameClass
- RenameParameter
- ReplaceValue
- DeleteParameter

Examples include

Old SDK

```python
client = LegacySquare(
    access_token="TOKEN",
    custom_url="https://sandbox.example.com",
    square_version="2024-01-01",
    environment="sandbox",
    http_call_back=None,
    user_agent_detail="Prototype"
)
```

Migrated SDK

```python
client = Square(
    token="TOKEN",
    base_url="https://sandbox.example.com",
    version="2024-01-01",
    environment=SquareEnvironment.SANDBOX
)
```

---

# Project Structure

```
Rule-Based SDK Migration Engine/

├── data/
│   └── migration_rules.json
│
├── docs/
│   ├── architecture.png
│   ├── pipeline.png
│   ├── Terminal_output.png
│   ├── patched_client.png
│   ├── migration_report.png
│   └── DESIGN_MEMO.md
│
├── samples/
│   ├── old_client.py
│   ├── expected_client.py
│   └── patched_client.py
│
├── src/
│   ├── __init__.py
│   ├── patcher.py
│   ├── validator.py
│   └── confidence.py
│
├── tests/
│   └── README.md
│
├── .gitignore
├── LICENSE
├── migration_report.json
├── README.md
├── requirements.txt
└── run.py
```

---

# System Architecture

The overall architecture is shown below.

```
migration_rules.json
          │
          ▼
     patcher.py
      │       │
      ▼       ▼
patched_client.py
migration_report.json
      │
      ▼
 validator.py
      │
      ▼
confidence.py
      │
      ▼
Migration Summary
```

Refer to

```
docs/architecture.png
```

for the graphical version.

---

# Processing Pipeline

The migration process follows the pipeline below.

```
Official Migration Guide

        │

        ▼

Migration Rule Extraction

        │

        ▼

migration_rules.json

        │

        ▼

LibCST Parser

        │

        ▼

Migration Operators

        │

        ▼

Patched Source Code

        │

        ▼

Validation

        │

        ▼

Confidence Estimation
```

Refer to

```
docs/pipeline.png
```

---

# Migration Operators

The prototype currently supports four migration operators.

| Operator | Description |
|-----------|-------------|
| RenameClass | Renames deprecated SDK classes |
| RenameParameter | Renames keyword parameters |
| ReplaceValue | Replaces obsolete constant values |
| DeleteParameter | Removes deprecated parameters |

Each operator is represented as an independent rule inside

```
migration_rules.json
```

which allows migration knowledge to be separated from the transformation engine.

---

# Implementation

## 1. migration_rules.json

Stores officially documented migration rules extracted from the Square migration guide.

Example

```json
{
    "operator": "RenameParameter",
    "match": {
        "parameter": "access_token"
    },
    "patch": {
        "parameter": "token"
    }
}
```

---

## 2. patcher.py

Core migration engine.

Responsibilities

- Load migration rules
- Parse Python source using LibCST
- Detect affected API calls
- Apply migration operators
- Preserve formatting
- Generate migration report

---

## 3. validator.py

Performs post-migration verification.

Checks include

- Python syntax validation
- Deprecated identifiers removed
- Required transformations applied

---

## 4. confidence.py

Computes an overall confidence score using the confidence values associated with each applied migration rule.

---

# Running the Prototype

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python3 run.py
```

---

# Sample Output

```
SDK BREAKING CHANGE PATCH REPORT

Provider:
Square Python SDK

Migration Class:
Method Signature Evolution

RenameParameter : 3

RenameClass : 2

ReplaceValue : 1

DeleteParameter : 2

Validation : PASS

Confidence : HIGH (0.98)
```

---

# Generated Artifacts

Running the prototype produces

```
patched_client.py
migration_report.json
```

The migration report records

- applied migration rules
- source location
- confidence
- operator statistics

providing an auditable record of every transformation.

---

# Current Limitations

The current prototype intentionally focuses on one class of breaking change.

Out of scope

- endpoint migration
- authentication changes
- response parsing
- business logic migration
- semantic code analysis
- automatic migration rule extraction

---

# Future Work

Possible extensions include

- support for additional migration operators
- automatic extraction of migration rules from SDK documentation
- multi-SDK support
- integration with static analysis
- unit test execution after migration
- confidence estimation using semantic validation

---

# Technologies Used

- Python 3
- LibCST
- JSON
- Abstract Syntax Concepts
- Rule-Based Source Transformation

---

## References

1. Square Developer Documentation – Python SDK Migration Guide  
   https://developer.squareup.com/docs/sdks/python/migration

2. Square Developer Documentation – Python SDK  
   https://developer.squareup.com/docs/sdks/python

3. LibCST Documentation  
   https://libcst.readthedocs.io/en/latest/

4. Wang, S., et al. "Automatic API Migration Using Migration Operators."
