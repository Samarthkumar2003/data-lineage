import pandas as pd

def load_and_parse_lineage(file):
    """
    Modular implementation of the 'lineage-parser' OpenSpec skill.
    This function can be tested independently of the Streamlit UI.
    """
    df = pd.read_excel(file)
    
    # Standard OpenSpec Cleaning Rules
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Standard OpenSpec Validation Rules
    df = df[
        (df['Parent Object Name'].notna()) & (df['Parent Object Name'] != 'nan') &
        (df['Child Object Name'].notna()) & (df['Child Object Name'] != 'nan')
    ]
    return df

def get_lineage_connector_html(data_json, height):
    """
    Modular implementation of the 'lineage-connector' OpenSpec skill.
    Encapsulates the SVG and JS rendering logic.
    """
    # Note: Using the exact same JS logic defined in the skill.md 
    # to maintain consistency between spec and code.
    return f"""
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

let edgeData = [];
const boxes = document.querySelectorAll('.box');

function drawLines() {{
    svg.innerHTML = '';
    edgeData = [];

    const pBoxH = boxes.length > 0 ? boxes[0].offsetHeight : 0;
    const cBoxH = boxes.length > 1 ? boxes[1].offsetHeight : 0;
    const totalH = Math.max(pBoxH, cBoxH) + START_Y + 40;

    wrapper.style.height = totalH + 'px';
    svg.setAttribute('width', cBoxX + BOX_W + 40);
    svg.setAttribute('height', totalH);

    function getOffsetTop(el) {{
        let top = 0;
        while (el && el !== wrapper) {{
            top += el.offsetTop;
            el = el.offsetParent;
        }}
        return top;
    }}

    D.edges.forEach(e => {{
        const pIdx = D.parent_cols.indexOf(e.from_col);
        const cIdx = D.child_cols.indexOf(e.to_col);
        if (pIdx < 0 || cIdx < 0) return;

        const pRow = pRows[pIdx];
        const cRow = cRows[cIdx];
        
        const y1 = getOffsetTop(pRow) + pRow.offsetHeight / 2;
        const y2 = getOffsetTop(cRow) + cRow.offsetHeight / 2;
        
        const x1 = START_X + BOX_W;
        const x2 = cBoxX;
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
}}

drawLines();

// Redraw if layout changes (e.g. custom fonts loading)
if (document.fonts) {{
    document.fonts.ready.then(drawLines);
}}
const ro = new ResizeObserver(drawLines);
boxes.forEach(b => ro.observe(b));
setTimeout(drawLines, 100);


function hlPair(pIdx, cIdx, on) {{
    const pEl = pRows[pIdx], cEl = cRows[cIdx];
    if (pEl) on ? pEl.classList.add('hl') : pEl.classList.remove('hl');
    if (cEl) on ? cEl.classList.add('hl') : cEl.classList.remove('hl');
}}

function updateTip(ev) {{
    tip.style.left = (ev.clientX + 15) + 'px';
    tip.style.top = (ev.clientY - 10) + 'px';
}}

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
