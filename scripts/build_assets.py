#!/usr/bin/env python3
"""Generate the profile's SVG assets (header + project cards) in light and dark.

Edit the content below, then run:  python3 scripts/build_assets.py
Output goes to assets/. No dependencies beyond the standard library.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

THEMES = {
    "dark": dict(
        bg="#0A0B0D", panel="#111316", line="#1E2126", grid="#16181C",
        ink="#EDEDEF", sub="#9A9DA4", faint="#5C6068", accent="#F2B35E",
        accent_soft="#F2B35E22", node="#14171B",
    ),
    "light": dict(
        bg="#FBFAF7", panel="#FFFFFF", line="#E6E3DC", grid="#EFECE6",
        ink="#16171A", sub="#5A5D63", faint="#9A9890", accent="#B8650F",
        accent_soft="#B8650F18", node="#FFFFFF",
    ),
}


def t(x, y, text, size, fill, family=SANS, weight=400, spacing=0, anchor="start", extra=""):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" letter-spacing="{spacing}" fill="{fill}" '
        f'text-anchor="{anchor}" {extra}>{escape(text)}</text>'
    )


# --------------------------------------------------------------------------- header

def header(c):
    W, H = 1200, 400
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mohan Raj, Software Engineer">')
    s.append(f"""<style>
      .flow {{ stroke-dasharray: 3 9; animation: flow 1.6s linear infinite; }}
      .flow.slow {{ animation-duration: 2.4s; }}
      @keyframes flow {{ to {{ stroke-dashoffset: -24; }} }}
      .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
      .caret {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      @media (prefers-reduced-motion: reduce) {{ .flow, .pulse, .caret {{ animation: none; opacity: 1; }} }}
    </style>""")
    s.append(f"""<defs>
      <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="1" fill="{c['grid']}"/>
      </pattern>
    </defs>""")
    s.append(f'<rect width="{W}" height="{H}" rx="14" fill="{c["bg"]}"/>')
    s.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="13.5" fill="url(#dots)" stroke="{c["line"]}"/>')

    # ---- system diagram (right side): ingress -> services -> bus -> sinks
    # Sizes are chosen for the ~830px GitHub profile column (scale ~0.7).
    gx, fs = 636, 13
    nodes = {
        "edge":   (gx + 0,   196, "ingress"),
        "auth":   (gx + 148, 112, "auth"),
        "core":   (gx + 148, 196, "core-api"),
        "usage":  (gx + 148, 280, "usage"),
        "bus":    (gx + 300, 196, "sns/sqs"),
        "notify": (gx + 436, 148, "notify"),
        "store":  (gx + 436, 244, "postgres"),
    }
    # width from label so text never overflows (13px mono ~ 7.9px/char)
    nodes = {k: (x, y, 40 + 7.9 * len(lbl), lbl) for k, (x, y, lbl) in nodes.items()}
    edges = [("edge", "auth", ""), ("edge", "core", ""), ("edge", "usage", "slow"),
             ("core", "bus", ""), ("usage", "bus", "slow"), ("bus", "notify", ""),
             ("bus", "store", "slow"), ("auth", "store", "slow")]

    for a, b, sp in edges:
        x1, y1, w1, _ = nodes[a]
        x2, y2, _, _ = nodes[b]
        x1 += w1
        mx = (x1 + x2) / 2
        d = f"M{x1:.1f},{y1} C{mx:.1f},{y1} {mx:.1f},{y2} {x2},{y2}"
        s.append(f'<path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="1.4"/>')
        s.append(f'<path class="flow {sp}" d="{d}" fill="none" stroke="{c["accent"]}" stroke-width="1.7" stroke-linecap="round" opacity=".9"/>')
    for key, (x, y, w, label) in nodes.items():
        hot = key in ("core", "bus")
        s.append(f'<rect x="{x}" y="{y-18}" width="{w:.1f}" height="36" rx="8" fill="{c["node"]}" stroke="{c["accent"] if hot else c["line"]}" stroke-width="1.2"/>')
        s.append(f'<circle cx="{x+14}" cy="{y}" r="3" fill="{c["accent"] if hot else c["faint"]}" class="{"pulse" if hot else ""}"/>')
        s.append(t(x + 26, y + 4.5, label, fs, c["sub"], MONO, 500))

    # ---- type
    s.append(f'<circle cx="65" cy="75" r="4.5" fill="{c["accent"]}" class="pulse"/>')
    s.append(t(82, 80, "SOFTWARE ENGINEER", 14, c["sub"], MONO, 500, 2))
    s.append(t(272, 80, "/", 14, c["faint"], MONO))
    s.append(t(292, 80, "UNITED KINGDOM", 14, c["sub"], MONO, 500, 2))

    s.append(t(57, 182, "Mohan Raj", 96, c["ink"], SANS, 650, -3.8))

    s.append(t(62, 232, "Backend systems, cloud infrastructure", 24, c["sub"], SANS, 400, -0.3))
    s.append(t(62, 264, "and the data that moves between them.", 24, c["sub"], SANS, 400, -0.3))

    s.append(f'<line x1="62" y1="314" x2="560" y2="314" stroke="{c["line"]}"/>')
    x = 62
    for i, label in enumerate(["Services", "Cloud", "Data"]):
        s.append(t(x, 348, f"0{i+1}", 14, c["accent"], MONO, 600, 1))
        s.append(t(x + 32, 348, label.upper(), 14, c["sub"], MONO, 500, 1.8))
        x += 32 + len(label) * 10.2 + 44  # 14px mono + 1.8 tracking ~ 10.2px/char
    s.append(t(1132, 350, "~/mohan-sys", 14, c["faint"], MONO, 400, 0.3, "end"))
    s.append(f'<rect x="1137" y="337" width="8" height="16" fill="{c["accent"]}" class="caret"/>')

    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- cards

CARDS = [
    dict(
        slug="pulseapi",
        index="01",
        kind="DISTRIBUTED SYSTEMS",
        title="PulseAPI",
        lines=["Multi-tenant API platform with keys,",
               "metered usage and async notifications."],
        metric=("4", "ECS services"),
        pipeline=["ALB", "auth", "core", "SNS", "SQS", "workers"],
        tags=["Java 17", "Spring Boot 3", "Terraform", "AWS"],
    ),
    dict(
        slug="incident",
        index="02",
        kind="SERVERLESS",
        title="Incident Platform",
        lines=["On-call paging with tiered escalation,",
               "SMS and email alerts, MTTA analytics."],
        metric=("\u221270%", "time to ack"),
        pipeline=["API GW", "ingest", "SQS", "escalate", "SNS"],
        tags=["TypeScript", "Lambda", "DynamoDB", "React"],
    ),
]


def card(c, d):
    # Shown at ~49% of an ~830px column (scale ~0.7), so type is sized up.
    W, H = 580, 330
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(d["title"])}">')
    s.append(f"""<style>
      .flow {{ stroke-dasharray: 3 7; animation: flow 1.4s linear infinite; }}
      @keyframes flow {{ to {{ stroke-dashoffset: -20; }} }}
      @media (prefers-reduced-motion: reduce) {{ .flow {{ animation: none; }} }}
    </style>""")
    s.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')

    # eyebrow
    s.append(t(32, 50, d["index"], 13, c["accent"], MONO, 600, 1))
    s.append(t(64, 50, d["kind"], 13, c["sub"], MONO, 500, 1.6))
    s.append(t(W - 30, 51, "\u2197", 18, c["faint"], SANS, 400, 0, "end"))

    # title + metric
    s.append(t(30, 102, d["title"], 36, c["ink"], SANS, 650, -1.2))
    big, small = d["metric"]
    s.append(t(W - 32, 102, big, 36, c["accent"], SANS, 650, -1.2, "end"))
    s.append(t(W - 32, 126, small, 13, c["faint"], MONO, 400, 0, "end"))

    # description
    for i, line in enumerate(d["lines"]):
        s.append(t(32, 160 + i * 26, line, 18, c["sub"], SANS))

    # pipeline strip
    y = 236
    s.append(f'<line x1="32" y1="{y}" x2="{W-32}" y2="{y}" stroke="{c["line"]}"/>')
    s.append(f'<line class="flow" x1="32" y1="{y}" x2="{W-32}" y2="{y}" stroke="{c["accent"]}" stroke-width="1.6" stroke-linecap="round" opacity=".85"/>')
    widths = [7.9 * len(step) + 22 for step in d["pipeline"]]
    gap = (W - 64 - sum(widths)) / (len(widths) - 1)
    x = 32
    for step, w in zip(d["pipeline"], widths):
        s.append(f'<rect x="{x:.1f}" y="{y-15}" width="{w:.1f}" height="30" rx="7" fill="{c["panel"]}" stroke="{c["line"]}"/>')
        s.append(t(f"{x + w/2:.1f}", y + 4.5, step, 13, c["sub"], MONO, 500, 0, "middle"))
        x += w + gap

    # tags
    x = 32
    for tag in d["tags"]:
        w = 8.6 * len(tag) + 26
        s.append(f'<rect x="{x:.1f}" y="272" width="{w:.1f}" height="32" rx="16" fill="{c["accent_soft"]}"/>')
        s.append(t(f"{x + w/2:.1f}", 293, tag, 15, c["ink"], SANS, 500, 0, "middle"))
        x += w + 10

    s.append("</svg>")
    return "\n".join(s)


def main():
    OUT.mkdir(exist_ok=True)
    for name, c in THEMES.items():
        (OUT / f"header-{name}.svg").write_text(header(c))
        for d in CARDS:
            (OUT / f"card-{d['slug']}-{name}.svg").write_text(card(c, d))
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
