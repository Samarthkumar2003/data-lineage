# Initial Lineage Implementation
---
description: Proposal for the initial setup and core features of the Data Lineage Explorer app.
---

## Summary
The goal is to provide a user-friendly interface for visualizing data flow between different database layers (Mirror, Stage, SDM) from an Excel mapping file.

## Why
Manually tracking data flow in large Excel files is error-prone and tedious. A visual representation helps in impact analysis and data governance.

## Changes
- Core Streamlit application with file upload.
- Object-pair selection interface.
- SVG-based column-level lineage graph.
- Interactive tooltips and highlighting.

## Next Steps
- Implement automated layer detection.
- Add multi-hop lineage visualization.
- Export to OpenLineage JSON.
