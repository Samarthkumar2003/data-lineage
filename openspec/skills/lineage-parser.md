# Skill: Lineage-Parser
---
description: Advanced data extraction and normalization engine for multi-layer data lineage mappings.
---

## Overview
The `lineage-parser` skill is responsible for the ingestion, validation, and normalization of raw Excel data into a standardized graph-ready format. It ensures data integrity across different naming conventions and source formats.

## Capabilities
1. **Schema-Aware Ingestion**: Detects and maps columns regardless of leading/trailing whitespace or case sensitivity.
2. **Layer Classification Engine**: Automatically categorizes database objects into logical architectural tiers (Mirror, Stage, SDM, Generic) based on a regex-driven prefix analysis.
3. **Data Sanitization**: 
   - Trims whitespace from all string inputs to prevent broken joins.
   - Handles `NaN` or empty cells by providing safe default values (e.g., "N/A").
   - Filters out incomplete mapping rows to ensure visualization consistency.

## Technical Specifications
- **Input**: Microsoft Excel (.xlsx, .xls) files.
- **Required Columns**:
  - `Parent Object Name`: Fully qualified name (Database.Schema.Table).
  - `Parent Column Name`: The source field name.
  - `Child Object Name`: Fully qualified target name.
  - `Child Column Name`: The target field name.
- **Output**: A normalized Pandas DataFrame with a consistent schema.

## Best Practices
- **Object Naming**: Always use the fully qualified name to avoid collisions between identical table names in different schemas.
- **Cache Management**: Use `@st.cache_data` when implementing this skill to prevent redundant file processing on every UI interaction.

## Edge Case Handling
- **Duplicate Mappings**: The parser identifies and flags duplicate rows to prevent visual clutter.
- **Missing Columns**: If optional columns like `Transformation Notes` are missing, the skill generates empty placeholders to maintain schema stability.
