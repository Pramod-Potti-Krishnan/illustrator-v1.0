#!/usr/bin/env python3
"""
Generate remaining template variants programmatically
"""

from pathlib import Path

# Base templates directory
templates_dir = Path(__file__).parent / "templates"

# Generate Funnel 4-stage
funnel_4_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        .funnel-container { width: 100%; height: 100%; max-width: 1800px; max-height: 720px; display: flex; align-items: center; justify-content: center; padding: 40px 60px; font-family: Arial, sans-serif; background: #f8fafc; }
        .funnel-wrapper { width: 100%; height: 100%; display: flex; flex-direction: column; gap: 10px; }
        .funnel-stage { width: 100%; display: grid; grid-template-columns: 340px 1fr 420px; gap: 20px; align-items: center; }
        .stage-title-box { background: white; border: 2px solid; border-radius: 8px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
        .stage-icon { width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
        .stage-title { font-size: 19px; font-weight: 700; flex: 1; }
        .funnel-shape-wrapper { display: flex; justify-content: center; align-items: center; }
        .funnel-shape { width: 100%; max-width: 700px; height: 135px; position: relative; display: flex; align-items: center; justify-content: center; clip-path: polygon(8% 0%, 92% 0%, 85% 100%, 15% 100%); transition: all 0.3s ease; }
        .funnel-stage:hover .funnel-shape { filter: brightness(1.08); transform: scaleX(1.01); }
        .stage-number { color: white; font-size: 64px; font-weight: 900; }
        .stage-description { background: white; border-left: 4px solid; border-radius: 4px; padding: 20px; font-size: 15px; line-height: 1.6; color: #475569; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .stage-1 .stage-title-box { border-color: #38bdf8; } .stage-1 .stage-icon { background: #e0f2fe; color: #0284c7; } .stage-1 .stage-title { color: #0284c7; } .stage-1 .funnel-shape { background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%); } .stage-1 .stage-description { border-left-color: #38bdf8; }
        .stage-2 .stage-title-box { border-color: #3b82f6; } .stage-2 .stage-icon { background: #dbeafe; color: #1d4ed8; } .stage-2 .stage-title { color: #1d4ed8; } .stage-2 .funnel-shape { background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); } .stage-2 .stage-description { border-left-color: #3b82f6; }
        .stage-3 .stage-title-box { border-color: #a855f7; } .stage-3 .stage-icon { background: #f3e8ff; color: #7c3aed; } .stage-3 .stage-title { color: #7c3aed; } .stage-3 .funnel-shape { background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%); } .stage-3 .stage-description { border-left-color: #a855f7; }
        .stage-4 .stage-title-box { border-color: #ec4899; } .stage-4 .stage-icon { background: #fce7f3; color: #db2777; } .stage-4 .stage-title { color: #db2777; } .stage-4 .funnel-shape { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); } .stage-4 .stage-description { border-left-color: #ec4899; }
    </style>
</head>
<body>
    <div class="funnel-container">
        <div class="funnel-wrapper">
            <div class="funnel-stage stage-1">
                <div class="stage-title-box"><div class="stage-icon">{stage_1_icon}</div><div class="stage-title">{stage_1_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">01</div></div></div>
                <div class="stage-description">{stage_1_description}</div>
            </div>
            <div class="funnel-stage stage-2">
                <div class="stage-title-box"><div class="stage-icon">{stage_2_icon}</div><div class="stage-title">{stage_2_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">02</div></div></div>
                <div class="stage-description">{stage_2_description}</div>
            </div>
            <div class="funnel-stage stage-3">
                <div class="stage-title-box"><div class="stage-icon">{stage_3_icon}</div><div class="stage-title">{stage_3_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">03</div></div></div>
                <div class="stage-description">{stage_3_description}</div>
            </div>
            <div class="funnel-stage stage-4">
                <div class="stage-title-box"><div class="stage-icon">{stage_4_icon}</div><div class="stage-title">{stage_4_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">04</div></div></div>
                <div class="stage-description">{stage_4_description}</div>
            </div>
        </div>
    </div>
</body>
</html>"""

# Generate Funnel 3-stage
funnel_3_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        .funnel-container { width: 100%; height: 100%; max-width: 1800px; max-height: 720px; display: flex; align-items: center; justify-content: center; padding: 50px 60px; font-family: Arial, sans-serif; background: #f8fafc; }
        .funnel-wrapper { width: 100%; height: 100%; display: flex; flex-direction: column; gap: 20px; }
        .funnel-stage { width: 100%; display: grid; grid-template-columns: 380px 1fr 450px; gap: 24px; align-items: center; }
        .stage-title-box { background: white; border: 2px solid; border-radius: 8px; padding: 28px 30px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
        .stage-icon { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; flex-shrink: 0; }
        .stage-title { font-size: 22px; font-weight: 700; flex: 1; }
        .funnel-shape-wrapper { display: flex; justify-content: center; align-items: center; }
        .funnel-shape { width: 100%; max-width: 700px; height: 175px; position: relative; display: flex; align-items: center; justify-content: center; clip-path: polygon(8% 0%, 92% 0%, 85% 100%, 15% 100%); transition: all 0.3s ease; }
        .funnel-stage:hover .funnel-shape { filter: brightness(1.08); transform: scaleX(1.01); }
        .stage-number { color: white; font-size: 76px; font-weight: 900; }
        .stage-description { background: white; border-left: 5px solid; border-radius: 4px; padding: 28px 24px; font-size: 16px; line-height: 1.7; color: #475569; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .stage-1 .stage-title-box { border-color: #38bdf8; } .stage-1 .stage-icon { background: #e0f2fe; color: #0284c7; } .stage-1 .stage-title { color: #0284c7; } .stage-1 .funnel-shape { background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%); } .stage-1 .stage-description { border-left-color: #38bdf8; }
        .stage-2 .stage-title-box { border-color: #a855f7; } .stage-2 .stage-icon { background: #f3e8ff; color: #7c3aed; } .stage-2 .stage-title { color: #7c3aed; } .stage-2 .funnel-shape { background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%); } .stage-2 .stage-description { border-left-color: #a855f7; }
        .stage-3 .stage-title-box { border-color: #ec4899; } .stage-3 .stage-icon { background: #fce7f3; color: #db2777; } .stage-3 .stage-title { color: #db2777; } .stage-3 .funnel-shape { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); } .stage-3 .stage-description { border-left-color: #ec4899; }
    </style>
</head>
<body>
    <div class="funnel-container">
        <div class="funnel-wrapper">
            <div class="funnel-stage stage-1">
                <div class="stage-title-box"><div class="stage-icon">{stage_1_icon}</div><div class="stage-title">{stage_1_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">01</div></div></div>
                <div class="stage-description">{stage_1_description}</div>
            </div>
            <div class="funnel-stage stage-2">
                <div class="stage-title-box"><div class="stage-icon">{stage_2_icon}</div><div class="stage-title">{stage_2_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">02</div></div></div>
                <div class="stage-description">{stage_2_description}</div>
            </div>
            <div class="funnel-stage stage-3">
                <div class="stage-title-box"><div class="stage-icon">{stage_3_icon}</div><div class="stage-title">{stage_3_title}</div></div>
                <div class="funnel-shape-wrapper"><div class="funnel-shape"><div class="stage-number">03</div></div></div>
                <div class="stage-description">{stage_3_description}</div>
            </div>
        </div>
    </div>
</body>
</html>"""

# Write funnel templates
(templates_dir / "funnel" / "4.html").write_text(funnel_4_html)
(templates_dir / "funnel" / "3.html").write_text(funnel_3_html)

print("✅ Funnel templates created: 3.html, 4.html")
print(f"   Funnel templates directory: {templates_dir / 'funnel'}")
