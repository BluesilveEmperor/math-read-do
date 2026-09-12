# `_shared/` — Shared layer for nature-skills integration

This directory holds content shared across the three integrated nature sub-skills:

- `nature-reader/` — scientific paper reading and structured extraction,
- `nature-figure/` — submission-grade figure generation in Python or R,
- `nature-paper2ppt/` — paper-to-PPTX presentation building.

Each sub-skill's `manifest.yaml` lists the files it loads from `_shared/` in its `always_load` section.

## Contents

| File | Purpose |
|---|---|
| `core/ethics.md` | Research and publication ethics: data integrity, reproducibility, attribution, AI disclosure. |
| `core/paper-type-taxonomy.md` | Shared paper-type classification (discovery, methods, resource, clinical, materials, review) + sub-type guide. |
| `core/reader-workflow.md` | Cross-skill workflow for reading a scientific paper: steps, outputs, confidence flags. |
| `core/terminology-ledger.md` | Template and rules for building a `Terminology Ledger` to keep technical terms consistent across outputs. |
| `journal-formats/nat-comms.md` | Nature Communications-specific formatting guidelines (article structure, sections, figure limits, reference style). |

## What belongs in `_shared/` vs. inside a sub-skill

- **In `_shared/`**: content that two or more sub-skills load in their manifest's `always_load` section. Content that is shared by reference, not by copy.
- **Inside a sub-skill**: content that is specific to that skill's domain (e.g., paper2ppt's slide design rules, figure's backend selection logic, reader's source-format routers).
