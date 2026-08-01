"""Orchestrate the whole pipeline.

Running this module reads the raw color list, computes features, writes two
processed CSVs, and renders both self-contained HTML visualizations into
``outputs/``. Run it with::

    cd src && python -m colorviz.build

Only the Python standard library is used; the rendered HTML pulls fonts from
Google Fonts but has no other dependencies.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

try:  # normal package import
    from .parse import parse_colors
    from .color_features import build_records, FAMILIES
    from .spiral import compute_spiral
except ImportError:  # allow running the file directly
    from parse import parse_colors
    from color_features import build_records, FAMILIES
    from spiral import compute_spiral

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "xkcd_rgb.txt"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs"

FAM_ORDER = FAMILIES + ["grey"]
# short, single-word labels used under each drip column
FAM_LABEL = {f: f for f in FAM_ORDER}
# a representative swatch per family, used for the spiral's filter chips
CHIP_COLOR = {
    "red": "#e50000", "orange": "#f97306", "yellow": "#ffff14",
    "chartreuse": "#9dff00", "green": "#15b01a", "teal": "#04d8b2",
    "cyan": "#02ccfe", "azure": "#0165fc", "blue": "#3d21d0",
    "violet": "#9a0eea", "magenta": "#c20078", "rose": "#f7022a",
    "grey": "#929591",
}


# --------------------------------------------------------------------------- #
# processed data                                                              #
# --------------------------------------------------------------------------- #
def write_csvs(records):
    PROC.mkdir(parents=True, exist_ok=True)
    with open(PROC / "color_families.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "hex", "hue", "lightness", "saturation", "family"])
        w.writeheader()
        w.writerows(records)

    counts = Counter(r["family"] for r in records)
    with open(PROC / "family_counts.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "count"])
        for fam in FAM_ORDER:
            w.writerow([fam, counts.get(fam, 0)])
    return counts


def _sample(seq, n):
    """Pick *n* evenly spaced items from *seq* (returns seq if shorter)."""
    if len(seq) <= n:
        return list(seq)
    step = (len(seq) - 1) / (n - 1)
    return [seq[round(i * step)] for i in range(n)]


# --------------------------------------------------------------------------- #
# drip chart                                                                  #
# --------------------------------------------------------------------------- #
def render_drip_svg(records):
    y0, scale, W, rt, rb = 64.0, 2.8, 42, 12, 21
    x_left, area = 70, 930
    slot = area / 13

    by_fam = defaultdict(list)
    for r in records:
        by_fam[r["family"]].append(r)

    defs, grid, cols, labs, datapts = [], [], [], [], []
    for gc in (50, 100, 150):
        y = y0 + gc * scale
        grid.append(f'<line x1="70" y1="{y:.0f}" x2="1000" y2="{y:.0f}" '
                    f'stroke="#d8d6d0" stroke-width="1" stroke-dasharray="2 5"/>')
        grid.append(f'<text class="axis" x="62" y="{y+4:.0f}" text-anchor="end">{gc}</text>')

    for i, fam in enumerate(FAM_ORDER):
        members = sorted(by_fam.get(fam, []), key=lambda r: r["lightness"])
        count = len(members)
        cx = x_left + slot * (i + 0.5)
        L = count * scale
        yb = y0 + L
        datapts.append((cx, yb))
        light_first = [m["hex"] for m in members][::-1]  # light at top, dark at bottom
        picks = _sample(light_first, 6) if light_first else ["#cccccc"]
        stops = "".join(
            f'<stop offset="{int(k/(len(picks)-1)*100) if len(picks)>1 else 0}%" stop-color="{c}"/>'
            for k, c in enumerate(picks)
        )
        defs.append(f'<linearGradient id="g{i}" gradientUnits="userSpaceOnUse" '
                    f'x1="0" y1="{y0}" x2="0" y2="{yb:.1f}">{stops}</linearGradient>')
        l, rr = cx - W / 2, cx + W / 2
        path = (f'M {l:.1f} {y0+rt} Q {l:.1f} {y0} {l+rt:.1f} {y0} '
                f'L {rr-rt:.1f} {y0} Q {rr:.1f} {y0} {rr:.1f} {y0+rt} '
                f'L {rr:.1f} {yb-rb:.1f} Q {rr:.1f} {yb:.1f} {cx:.1f} {yb:.1f} '
                f'Q {l:.1f} {yb:.1f} {l:.1f} {yb-rb:.1f} Z')
        cols.append(
            f'<g class="col" style="animation-delay:{i*70}ms">'
            f'<path d="{path}" fill="url(#g{i})" stroke="#35342f" stroke-width="1.1" '
            f'stroke-opacity="0.6" stroke-linejoin="round"/>'
            f'<rect x="{cx-W/2+6:.1f}" y="{y0+8:.0f}" width="5" height="{max(L-32,6):.0f}" '
            f'rx="2.5" fill="#ffffff" opacity="0.14"/></g>'
        )
        labs.append(f'<text class="fam" x="{cx:.0f}" y="38" text-anchor="middle">{FAM_LABEL[fam]}</text>')
        labs.append(f'<text class="cnt" x="{cx:.0f}" y="52" text-anchor="middle">{count}</text>')

    tp = f'M {datapts[0][0]:.1f} {datapts[0][1]:.1f} '
    for k in range(1, len(datapts)):
        x0, v0 = datapts[k - 1]
        x1, v1 = datapts[k]
        tp += f'Q {x0:.1f} {v0:.1f} {(x0+x1)/2:.1f} {(v0+v1)/2:.1f} '
    tp += f'T {datapts[-1][0]:.1f} {datapts[-1][1]:.1f}'
    trend = ['<g id="trend">',
             f'<path d="{tp}" fill="none" stroke="#8f8d82" stroke-width="1.6" '
             f'stroke-dasharray="6 5" opacity="0.85"/>']
    trend += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#6e6c62"/>' for x, y in datapts]
    trend.append("</g>")

    svg = ['<svg viewBox="0 0 1040 520" xmlns="http://www.w3.org/2000/svg" role="img" '
           'aria-label="Chart of xkcd color names per hue family as hanging paint columns, '
           'with a trend line through the true counts.">',
           "<defs>" + "".join(defs) + "</defs>"]
    svg += grid
    svg.append('<rect x="70" y="56" width="930" height="8" rx="4" fill="#2b2b28"/>')
    svg += cols + trend + labs
    svg.append(f'<text class="axtitle" x="62" y="{y0-4:.0f}" text-anchor="end">names</text>')
    svg.append("</svg>")
    return "\n".join(svg)


# --------------------------------------------------------------------------- #
# spiral                                                                      #
# --------------------------------------------------------------------------- #
def render_spiral_data(records):
    placed = compute_spiral(records)
    data = [{"x": p["x"], "y": p["y"], "c": p["hex"], "n": p["name"], "f": p["family"]}
            for p in placed]
    counts = Counter(r["family"] for r in records)
    chips = [{"f": f, "n": counts.get(f, 0)} for f in FAM_ORDER]
    return data, chips


# --------------------------------------------------------------------------- #
# HTML templates (kept as plain strings so CSS braces are safe)               #
# --------------------------------------------------------------------------- #
DRIP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>We name a whole rainbow, but our words clump</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{ --wall:#f4f4f2; --ink:#16150f; --muted:#7c7a70; --line:#d8d6d0; }
  *{ box-sizing:border-box; }
  body{ margin:0; background:var(--wall); color:var(--ink);
        font-family:"Inter",system-ui,sans-serif; -webkit-font-smoothing:antialiased;
        display:flex; justify-content:center; padding:56px 24px 48px; }
  .sheet{ width:100%; max-width:1080px; }
  .eyebrow{ font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.22em;
            text-transform:uppercase; color:var(--muted); margin:0 0 14px; }
  h1{ font-family:"Fraunces",serif; font-weight:500; font-size:clamp(28px,4.6vw,46px);
      line-height:1.06; letter-spacing:-0.01em; margin:0 0 14px; max-width:20ch; }
  .subtitle{ font-size:clamp(15px,1.7vw,18px); line-height:1.6; color:#4a463c;
             max-width:62ch; margin:0 0 8px; }
  .chart{ margin-top:26px; }
  svg{ width:100%; height:auto; display:block; overflow:visible; }
  .fam{ font-family:"Inter",sans-serif; font-size:13px; font-weight:500; fill:#2b2b28; }
  .cnt{ font-family:"IBM Plex Mono",monospace; font-size:11px; fill:var(--muted); }
  .axis{ font-family:"IBM Plex Mono",monospace; font-size:11px; fill:#a8a59c; }
  .axtitle{ font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em;
            text-transform:uppercase; fill:#a8a59c; }
  .col{ transform-box:fill-box; transform-origin:top center; cursor:pointer;
        animation:pour 1.15s cubic-bezier(.2,.9,.25,1) both; transition:opacity .3s ease; }
  @keyframes pour{ from{ transform:scaleY(0);} to{ transform:scaleY(1);} }
  .chart:hover .col{ opacity:.42; }
  .chart .col:hover{ opacity:1; }
  #trend{ transition:opacity .3s ease; }
  .chart:hover #trend{ opacity:.25; }
  .placard{ margin-top:30px; padding-top:16px; border-top:1px solid var(--line);
            font-family:"IBM Plex Mono",monospace; font-size:12px; line-height:1.7;
            color:var(--muted); max-width:80ch; }
  .placard b{ color:#4a463c; font-weight:500; }
  @media (prefers-reduced-motion:reduce){ .col{ animation:none; } }
</style>
</head>
<body>
  <main class="sheet">
    <p class="eyebrow">Color &middot; language &middot; a specimen</p>
    <h1>We name a whole rainbow, but our words clump</h1>
    <p class="subtitle">Of 954 crowd-sourced color names, oranges and roses run deep while blues barely drip &mdash; our vocabulary pools around a few favorite hues.</p>
    <div class="chart">
    __SVG__
    </div>
    <p class="placard"><b>Source</b> &mdash; xkcd Color Survey by Randall Munroe (xkcd.com/color), released CC BY-NC. ~200,000 participants named over 5 million swatches, distilled to 954 colors. <b>Method</b> &mdash; each name binned into a hue family from its sRGB value; column length = number of names in that family, threaded by the dashed trend line. Hover a color to isolate it.</p>
  </main>
</body>
</html>
"""

SPIRAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>A galaxy of color names</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{ --bg:#141414; --panel:#1d1d1c; --ink:#f3f2ee; --muted:#9a988e; --line:#2e2e2b; }
  *{ box-sizing:border-box; }
  body{ margin:0; background:var(--bg); color:var(--ink);
        font-family:"Inter",system-ui,sans-serif; -webkit-font-smoothing:antialiased;
        display:flex; justify-content:center; padding:52px 24px 44px; }
  .sheet{ width:100%; max-width:900px; }
  .eyebrow{ font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.22em;
            text-transform:uppercase; color:var(--muted); margin:0 0 14px; }
  h1{ font-family:"Fraunces",serif; font-weight:500; font-size:clamp(28px,4.4vw,42px);
      line-height:1.08; letter-spacing:-0.01em; margin:0 0 12px; max-width:22ch; }
  .subtitle{ font-size:clamp(15px,1.7vw,17px); line-height:1.6; color:#c9c7bd;
             max-width:60ch; margin:0 0 22px; }
  .chips{ display:flex; flex-wrap:wrap; gap:8px; margin:0 0 8px; }
  .chip{ display:inline-flex; align-items:center; gap:7px; cursor:pointer;
         background:var(--panel); color:var(--ink); border:1px solid var(--line);
         border-radius:999px; padding:6px 12px; font-family:"Inter",sans-serif;
         font-size:13px; transition:border-color .2s, background .2s; }
  .chip em{ font-style:normal; color:var(--muted); font-family:"IBM Plex Mono",monospace; font-size:11px; }
  .chip:hover{ border-color:#4a4a45; }
  .chip.active{ background:#2a2a28; border-color:#6f6f66; }
  .chip .sw{ width:11px; height:11px; border-radius:50%; }
  .wrap{ position:relative; margin-top:14px; }
  svg{ width:100%; height:auto; display:block; }
  circle.dot{ transform-box:fill-box; transform-origin:center; }
  .anim circle.dot{ animation:bloom .5s ease both; }
  @keyframes bloom{ from{ transform:scale(0); opacity:0;} to{ transform:scale(1); opacity:1;} }
  .dot.dim{ opacity:.06 !important; }
  #tip{ position:absolute; pointer-events:none; opacity:0; transform:translate(-50%,-140%);
        background:#000; border:1px solid #3a3a36; border-radius:8px; padding:7px 10px;
        display:flex; align-items:center; gap:8px; white-space:nowrap; transition:opacity .12s;
        font-size:13px; }
  #tip .ts{ width:14px; height:14px; border-radius:3px; border:1px solid rgba(255,255,255,.2); }
  #tip .th{ font-family:"IBM Plex Mono",monospace; color:var(--muted); font-size:11px; }
  .placard{ margin-top:26px; padding-top:16px; border-top:1px solid var(--line);
            font-family:"IBM Plex Mono",monospace; font-size:12px; line-height:1.7;
            color:var(--muted); max-width:80ch; }
  .placard b{ color:#c9c7bd; font-weight:500; }
  @media (prefers-reduced-motion:reduce){ .anim circle.dot{ animation:none; } }
</style>
</head>
<body>
  <main class="sheet">
    <p class="eyebrow">Color &middot; language &middot; explore</p>
    <h1>The same clumps, wound into a spiral</h1>
    <p class="subtitle">Every one of 954 crowd-sourced color names, placed by hue and spiralling outward. Where names crowd, the coil thickens. Hover a dot to read its name; tap a family to isolate it.</p>
    <div class="chips" id="chips">
      <button class="chip active" data-f="all"><span class="sw" style="background:linear-gradient(90deg,#e50000,#ffff14,#15b01a,#0165fc,#9a0eea)"></span>all <em>954</em></button>
      __CHIPS__
    </div>
    <div class="wrap">
      <svg id="spiral" viewBox="0 0 760 760" role="img" aria-label="Spiral of 954 color names arranged by hue; crowded hues form thicker arcs."></svg>
      <div id="tip"><span class="ts"></span><span><span class="tn"></span> <span class="th"></span></span></div>
    </div>
    <p class="placard"><b>Source</b> &mdash; xkcd Color Survey by Randall Munroe (xkcd.com/color), CC BY-NC &middot; 954 named colors. <b>Reading it</b> &mdash; angle follows hue around the wheel; each color winds outward by rank, so families with more names trace longer arcs.</p>
  </main>
<script>
const DATA = __DATA__;
const svg = document.getElementById('spiral');
const NS='http://www.w3.org/2000/svg';
const frag=document.createDocumentFragment();
DATA.forEach((d,i)=>{
  const c=document.createElementNS(NS,'circle');
  c.setAttribute('cx',d.x); c.setAttribute('cy',d.y); c.setAttribute('r',3.4);
  c.setAttribute('fill',d.c); c.setAttribute('stroke','rgba(255,255,255,0.16)');
  c.setAttribute('stroke-width','0.5'); c.setAttribute('class','dot');
  c.dataset.f=d.f; c.dataset.n=d.n; c.dataset.c=d.c;
  c.style.animationDelay=(i*1.6)+'ms';
  frag.appendChild(c);
});
svg.appendChild(frag);
requestAnimationFrame(()=>document.querySelector('.wrap').classList.add('anim'));

const tip=document.getElementById('tip');
const tsw=tip.querySelector('.ts'), tnm=tip.querySelector('.tn'), thx=tip.querySelector('.th');
const wrap=document.querySelector('.wrap');
svg.addEventListener('mouseover',e=>{
  if(e.target.classList.contains('dot')){
    const t=e.target; tsw.style.background=t.dataset.c;
    tnm.textContent=t.dataset.n; thx.textContent=t.dataset.c;
    const r=svg.getBoundingClientRect(), wr=wrap.getBoundingClientRect();
    const sx=r.width/760, sy=r.height/760;
    tip.style.left=(+t.getAttribute('cx')*sx + (r.left-wr.left))+'px';
    tip.style.top=(+t.getAttribute('cy')*sy + (r.top-wr.top))+'px';
    tip.style.opacity=1;
  }
});
svg.addEventListener('mouseout',e=>{ if(e.target.classList.contains('dot')) tip.style.opacity=0; });

const chips=document.getElementById('chips');
chips.addEventListener('click',e=>{
  const b=e.target.closest('.chip'); if(!b) return;
  [...chips.children].forEach(c=>c.classList.remove('active')); b.classList.add('active');
  const f=b.dataset.f;
  document.querySelectorAll('circle.dot').forEach(c=>{
    c.classList.toggle('dim', f!=='all' && c.dataset.f!==f);
  });
});
</script>
</body>
</html>
"""


def render_drip_html(records):
    return DRIP_HTML.replace("__SVG__", render_drip_svg(records))


def render_spiral_html(records):
    data, chips = render_spiral_data(records)
    chip_html = "".join(
        f'<button class="chip" data-f="{c["f"]}">'
        f'<span class="sw" style="background:{CHIP_COLOR[c["f"]]}"></span>{c["f"]} <em>{c["n"]}</em></button>'
        for c in chips
    )
    return (SPIRAL_HTML
            .replace("__DATA__", json.dumps(data, separators=(",", ":")))
            .replace("__CHIPS__", chip_html))


# --------------------------------------------------------------------------- #
# entry point                                                                 #
# --------------------------------------------------------------------------- #
def main():
    pairs = parse_colors(RAW)
    records = build_records(pairs)
    counts = write_csvs(records)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "color-vocabulary-drips.html").write_text(render_drip_html(records), encoding="utf-8")
    (OUT / "color-vocabulary-spiral.html").write_text(render_spiral_html(records), encoding="utf-8")

    print(f"parsed {len(records)} colors")
    print("family counts:", dict(counts))
    print(f"wrote {PROC/'color_families.csv'}")
    print(f"wrote {PROC/'family_counts.csv'}")
    print(f"wrote {OUT/'color-vocabulary-drips.html'}")
    print(f"wrote {OUT/'color-vocabulary-spiral.html'}")


def cli():
    """Console-script entry point: write both charts to the current directory.

    Works from an installed package (uses the bundled color list), unlike
    ``main()`` which regenerates the repository's data/ and outputs/ folders.
    """
    from .parse import parse_default

    records = build_records(parse_default())
    Path("color-vocabulary-drips.html").write_text(render_drip_html(records), encoding="utf-8")
    Path("color-vocabulary-spiral.html").write_text(render_spiral_html(records), encoding="utf-8")
    print("wrote color-vocabulary-drips.html and color-vocabulary-spiral.html")


if __name__ == "__main__":
    main()
