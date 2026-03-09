# Skill: Lineage-Connector
---
description: High-fidelity visualization and interaction engine for column-level data lineage.
---

## Overview
The `lineage-connector` skill handles the mathematical and visual representation of data flows. it translates logical mappings into interactive architectural diagrams using SVG and JavaScript.

## Core Logic
1. **Coordinate Mapping Strategy**:
   - Calculates the dynamic `(x, y)` anchor points for every column row within an object box.
   - Ensures vertical alignment is maintained regardless of the list length.
2. **Bezier Path Generation**:
   - Implements Cubic Bezier curves (`C` command in SVG) to create fluid, non-overlapping strings between parent and child columns.
   - Calculates central control points (`cx`) to ensure the "entry" and "exit" of lines are perfectly horizontal.
3. **Reactive Interaction (State Management)**:
   - **Cross-Component Highlighting**: Hovering on a column triggers a state change across the edge and the peer column simultaneously.
   - **Dynamic Iframe Scaling**: Calculates the total height requirement based on the column count to prevent unnecessary scrollbars or cut-off content.

## Design System
- **Color Palette**: Uses curated high-contrast colors (Material Blue/Purple) to distinguish between object types.
- **Theming**: Dark mode optimized (#1a1d2e) for maximum readability of vibrant connection lines.

## Technical Constraints
- **Performance**: Edge rendering is limited to the DOM to ensure smooth performance even with hundreds of column mappings.
- **Browser Support**: Requires a browser with SVG 2.0 support for path rendering and pointer-event handling.

## Future Extensibility
- **Multi-hop Traversal**: The architecture is designed to support recursive traversal by chaining connector instances.
- **Impact Analysis**: Can be extended to calculate "Blast Radius" when a source column changes.
