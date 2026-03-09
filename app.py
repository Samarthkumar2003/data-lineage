import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="Data Lineage Explorer", layout="wide")

# ── OPEN SPEC DESIGN SYSTEM ───────────────────────────────────────────────────
st.markdown("""
<style>
body, .stApp { background-color: #0f1117; color: #e8eaf6; }
.block-container { padding-top: 1.5rem; }
label, .stSelectbox label, .stFileUploader label { color: #9fa8da !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🔗 Data Lineage Explorer")

# ── SKILL: LINEAGE-PARSER ──────────────────────────────────────────────────────
@st.cache_data
def load_and_parse_lineage(file):
    df = pd.read_excel(file)
    # Clean column names
    df.columns = df.columns.str.strip()
    # Clean data values
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
    # Drop invalid rows
    df = df[
        (df['Parent Object Name'].notna()) & (df['Parent Object Name'] != 'nan') &
        (df['Child Object Name'].notna()) & (df['Child Object Name'] != 'nan')
    ]
    return df

# ── UI: INPUT INTERFACE ────────────────────────────────────────────────────────
uploaded = st.file_uploader("📂 Upload your Data Lineage Excel file", type=["xlsx", "xls"])

if not uploaded:
    st.info("Please upload an Excel file to get started.")
    st.stop()

df = load_and_parse_lineage(uploaded)
st.sidebar.success(f"✅ {len(df)} mappings loaded")

# ── UI: SINGLE PAIR SELECTION ─────────────────────────────────────────────────
parent_objects = sorted(df['Parent Object Name'].unique())
selected_parent = st.sidebar.selectbox("🗂 Parent Object", parent_objects)

child_options = sorted(df[df['Parent Object Name'] == selected_parent]['Child Object Name'].unique())
selected_child = st.sidebar.selectbox("📦 Child Object", child_options)

# Filter data for this specific pair
pair_df = df[
    (df['Parent Object Name'] == selected_parent) &
    (df['Child Object Name']  == selected_child)
].reset_index(drop=True)

st.sidebar.info(f"Showing {len(pair_df)} column mappings.")

# ── SKILL: LINEAGE-CONNECTOR (VISUALIZATION) ──────────────────────────────────
tab1, tab2 = st.tabs(["🔗 Lineage Diagram", "📄 Mapping Table"])

with tab1:
    st.markdown(f"**{selected_parent}** → **{selected_child}**")

    # Data transformation for JS
    parent_cols = list(dict.fromkeys(pair_df['Parent Column Name'].tolist()))
    child_cols  = list(dict.fromkeys(pair_df['Child Column Name'].tolist()))

    edges = []
    for _, row in pair_df.iterrows():
        edges.append({
            'from_col': row['Parent Column Name'],
            'to_col':   row['Child Column Name'],
            'type':     row['Transformation Type'],
            'note':     str(row.get('Transformation Notes', ''))[:150],
        })

    data_json = json.dumps({
        'parent_obj':   selected_parent,
        'child_obj':    selected_child,
        'parent_cols':  parent_cols,
        'child_cols':   child_cols,
        'edges':        edges,
    })

    # Height calculation
    row_h = 28
    head_h = 52
    canvas_h = max(len(parent_cols), len(child_cols)) * row_h + head_h + 100
    iframe_h = min(max(canvas_h + 60, 400), 900)

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 16px; background: #1a1d2e; font-family: 'Segoe UI', sans-serif; color: #fff; overflow: auto; }}
  #wrapper {{ position: relative; width: 100%; }}
  .box {{ position: absolute; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 280px; z-index: 10; }}
  .box-header {{ padding: 10px 14px; font-size: 11px; font-weight: 700; color: #fff; word-break: break-all; }}
  .box-schema {{ font-size: 9px; color: rgba(255,255,255,0.5); display: block; }}
  .col-list {{ background: #13151f; }}
  .col-row {{ padding: 5px 14px; font-size: 11.5px; color: #cfd8dc; border-bottom: 1px solid #1e2133; white-space: nowrap; cursor: default; }}
  .col-row:hover {{ background: #1e2440; color: #82b1ff; }}
  .col-row.hl {{ background: #162a50; color: #90caf9; }}
  .dot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #42a5f5; margin-right: 8px; vertical-align: middle; }}
  svg {{ position: absolute; top: 0; left: 0; pointer-events: none; z-index: 1; }}
  #tip {{ position: fixed; background: #1e2440; border: 1px solid #3949ab; border-radius: 6px; padding: 8px 12px; font-size: 12px; display: none; z-index: 9999; max-width: 320px; box-shadow: 0 4px 16px rgba(0,0,0,0.5); pointer-events: none; }}
</style>
</head>
<body>
<div id="tip"></div>
<div id="wrapper">
  <svg id="svg"></svg>
</div>
<script>
const wrapper = document.getElementById('wrapper');
const svg = document.getElementById('svg');
const tip = document.getElementById('tip');
const D = {data_json};

const BOX_W = 280;
const GAP_X = 220;
const START_X = 20;
const START_Y = 20;
const ROW_H = 28;
const HEAD_H = 52;

function makeBox(fullName, cols, color, x, y) {{
    const box = document.createElement('div');
    box.className = 'box';
    box.style.left = x + 'px'; box.style.top = y + 'px';
    box.style.borderTop = `3px solid ${{color}}`;
    const parts = fullName.split('.');
    box.innerHTML = `<div class="box-header" style="background:${{color}}cc">
        <span>${{parts[parts.length-1]}}</span><span class="box-schema">${{parts.slice(0,-1).join('.')}}</span>
    </div>`;
    const list = document.createElement('div');
    list.className = 'col-list';
    const rows = [];
    cols.forEach(col => {{
        const r = document.createElement('div');
        r.className = 'col-row';
        r.innerHTML = `<span class="dot"></span>${{col}}`;
        list.appendChild(r);
        rows.push(r);
    }});
    box.appendChild(list);
    wrapper.appendChild(box);
    return rows;
}}

const pRows = makeBox(D.parent_obj, D.parent_cols, '#1565c0', START_X, START_Y);
const cBoxX = START_X + BOX_W + GAP_X;
const cRows = makeBox(D.child_obj, D.child_cols, '#6a1b9a', cBoxX, START_Y);

const totalH = Math.max(D.parent_cols.length, D.child_cols.length) * ROW_H + HEAD_H + 40;
wrapper.style.height = totalH + 'px';
svg.setAttribute('width', cBoxX + BOX_W + 40);
svg.setAttribute('height', totalH);

const edgeData = [];
D.edges.forEach(e => {{
    const pIdx = D.parent_cols.indexOf(e.from_col);
    const cIdx = D.child_cols.indexOf(e.to_col);
    if (pIdx < 0 || cIdx < 0) return;

    const x1 = START_X + BOX_W, y1 = START_Y + HEAD_H + (pIdx * ROW_H) + ROW_H/2;
    const x2 = cBoxX, y2 = START_Y + HEAD_H + (cIdx * ROW_H) + ROW_H/2;
    const cx = (x1 + x2) / 2;

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M${{x1}},${{y1}} C${{cx}},${{y1}} ${{cx}},${{y2}} ${{x2}},${{y2}}`);
    path.setAttribute('stroke', '#3949ab'); path.setAttribute('stroke-width', '1.5');
    path.setAttribute('fill', 'none'); path.setAttribute('opacity', '0.5');
    path.style.pointerEvents = 'stroke'; path.style.cursor = 'pointer';
    svg.appendChild(path);
    edgeData.push({{ el: path, pIdx, cIdx, meta: e }});

    path.onmouseenter = (ev) => {{
        hlPair(pIdx, cIdx, true);
        path.setAttribute('stroke', '#ffca28'); path.setAttribute('stroke-width', '2.5'); path.setAttribute('opacity', '1');
        tip.style.display = 'block';
        tip.innerHTML = `<b>📌 ${{e.from_col}}</b> → <b>${{e.to_col}}</b><br><small>${{e.type}}</small><br>${{e.note !== 'nan' ? e.note : ''}}`;
        updateTip(ev);
    }};
    path.onmousemove = updateTip;
    path.onmouseleave = () => {{
        hlPair(pIdx, cIdx, false);
        path.setAttribute('stroke', '#3949ab'); path.setAttribute('stroke-width', '1.5'); path.setAttribute('opacity', '0.5');
        tip.style.display = 'none';
    }};
}});

function hlPair(pIdx, cIdx, on) {{
    const pEl = pRows[pIdx], cEl = cRows[cIdx];
    if (pEl) on ? pEl.classList.add('hl') : pEl.classList.remove('hl');
    if (cEl) on ? cEl.classList.add('hl') : cEl.classList.remove('hl');
}}

function updateTip(ev) {{
    tip.style.left = (ev.clientX + 15) + 'px';
    tip.style.top = (ev.clientY - 10) + 'px';
}}

// ── Row Hover Integration ───────────────────────────────────────────────────
pRows.forEach((r, idx) => {{
    r.onmouseenter = () => edgeData.filter(e => e.pIdx === idx).forEach(e => e.el.dispatchEvent(new Event('mouseenter')));
    r.onmouseleave = () => edgeData.filter(e => e.pIdx === idx).forEach(e => e.el.dispatchEvent(new Event('mouseleave')));
}});
cRows.forEach((r, idx) => {{
    r.onmouseenter = () => edgeData.filter(e => e.cIdx === idx).forEach(e => e.el.dispatchEvent(new Event('mouseenter')));
    r.onmouseleave = () => edgeData.filter(e => e.cIdx === idx).forEach(e => e.el.dispatchEvent(new Event('mouseleave')));
}});
</script>
</body>
</html>
"""
    components.html(html, height=iframe_h, scrolling=True)

with tab2:
    st.subheader(f"Column Mappings: {selected_parent} → {selected_child}")
    st.dataframe(pair_df, use_container_width=True)
