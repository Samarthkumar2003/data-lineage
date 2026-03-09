# Multi-hop Lineage Connections
---
description: Proposal to enhance the lineage connection logic to support multi-hop flows and improved visualizations.
---

## Summary
Currently, the app only shows a single Parent -> Child pair. This proposal introduces the "Multi-hop" feature, allowing users to see the full path of a column across multiple tables (e.g., Mirror -> Stage -> SDM) in a single view.

## Why
Data engineers often need to see the entire "life" of a field from ingestion to the presentation layer. Seeing only one step at a time requires too much manual switching.

## Proposed Changes
1. **Skill Integration**: Use the `lineage-connector` skill to recursively find all downstream/upstream connections for a selected table/column.
2. **Dynamic UI**: Add a checkbox for "Enable Multi-hop" which renders all related tables in the sequence.
3. **Auto-Layout**: Update the canvas logic to handle 3 or more boxes horizontally.

## Tasks
- [ ] Update `app.py` to support recursive connection lookup.
- [ ] Modify the JS visualization to handle dynamic column counts (more than 2).
- [ ] Add breadcrumbs or layer headers for the multi-hop view.
