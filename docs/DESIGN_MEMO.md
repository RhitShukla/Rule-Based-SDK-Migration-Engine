# Design Memo

**Project:** Rule-Based SDK Breaking Change Migration Prototype  
**Author:** Rhit Shukla

## Problem

Software Development Kits (SDKs) evolve frequently, introducing breaking API changes that require developers to manually update existing code. Although SDK providers publish migration guides, applying these changes across a codebase remains repetitive and error-prone.

This prototype investigates whether a rule-based migration engine can automatically patch one class of documented SDK breaking changes while preserving source formatting and generating an auditable migration report.

---

## Scope

To keep the implementation focused, the project targets:

- **API Provider:** Square Python SDK
- **Breaking Change Class:** Method Signature Evolution

Supported migration operators:

- RenameClass
- RenameParameter
- ReplaceValue
- DeleteParameter

The prototype intentionally excludes endpoint migration, authentication changes, response parsing, and business logic migration.

---

## Design Decisions

Migration rules are stored separately in `migration_rules.json` instead of being hardcoded. This separates migration knowledge from transformation logic, allowing the engine to be reused with different rule sets.

LibCST was selected because it performs syntax-aware source transformations while preserving comments and formatting, making it more suitable than simple text replacement or Python's standard AST for code migration.

---

## Implementation

The migration pipeline consists of five components:

```
migration_rules.json
        │
        ▼
   patcher.py
        │
        ├── patched_client.py
        └── migration_report.json
                │
                ▼
          validator.py
                │
                ▼
         confidence.py
```

The patcher loads official migration rules, traverses the Python source using LibCST, applies migration operators, generates patched code, and records every applied transformation.

The validator performs syntax and migration checks, while the confidence module computes an overall confidence score based on the applied rules.

---

## Results

The prototype successfully demonstrates automated migration for documented parameter evolution in the Square Python SDK.

Generated artifacts include:

- Patched Python source
- Migration report
- Validation status
- Confidence score

---

## Limitations & Future Work

The current implementation is intentionally limited to one deterministic class of breaking change. Future improvements include supporting additional migration operators, multiple SDKs, automatic extraction of migration rules from official documentation, and stronger semantic validation through static analysis and automated test execution.

---

## Conclusion

This prototype demonstrates that documented SDK breaking changes can be automatically patched using a rule-based approach. While not intended as a production migration framework, it provides a reusable architecture that can be extended to support additional SDKs and more complex migration scenarios.
