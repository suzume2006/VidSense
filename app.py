import gradio as gr
from pipeline import run_pipeline

# ── API KEY ───────────────────────────────────────────
GROQ_API_KEY = "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"

# ── CUSTOM CSS ────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

* { box-sizing: border-box; }

:root {
    --vs-bg:      #060810;
    --vs-card:    #111827;
    --vs-border:  #1e2d42;
    --vs-blue:    #3b82f6;
    --vs-cyan:    #06b6d4;
    --vs-green:   #10b981;
    --vs-amber:   #f59e0b;
    --vs-red:     #ef4444;
    --vs-text:    #e2e8f0;
    --vs-muted:   #64748b;
    --vs-font:    'Outfit', sans-serif;
    --vs-mono:    'JetBrains Mono', monospace;
}

body, .gradio-container {
    background: var(--vs-bg) !important;
    font-family: var(--vs-font) !important;
    color: var(--vs-text) !important;
    min-height: 100vh;
}

.gradio-container { max-width: 1400px !important; margin: 0 auto !important; }

.gradio-container::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 90% 60% at 15% 5%,  rgba(59,130,246,0.09) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 85% 15%, rgba(6,182,212,0.07)  0%, transparent 55%),
        radial-gradient(ellipse 60% 70% at 50% 90%, rgba(139,92,246,0.06) 0%, transparent 55%);
    pointer-events: none; z-index: 0;
}

.gradio-container h2 {
    font-size: 1.05rem !important; font-weight: 600 !important;
    color: var(--vs-muted) !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important; display: flex !important;
    align-items: center !important; gap: 10px !important;
}
.gradio-container h2::before {
    content: '' !important; display: inline-block !important;
    width: 4px !important; height: 18px !important;
    background: linear-gradient(180deg, #3b82f6, #06b6d4) !important;
    border-radius: 2px !important;
}

label span {
    font-size: 0.72rem !important; font-weight: 600 !important;
    color: #3b82f6 !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

textarea, select, input {
    background: #111827 !important;
    border: 1px solid #1e2d42 !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 10px !important;
}

.gradio-container .block, .gradio-container .form {
    background: transparent !important; border: none !important;
}

button.primary {
    background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
    border: none !important; border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; letter-spacing: 0.05em !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.35) !important;
    transition: all 0.25s !important;
}
button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(59,130,246,0.5) !important;
}

.logo-header {
    display: flex; align-items: center; gap: 18px; padding: 8px 0 4px;
}
.logo-icon {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    border-radius: 16px; display: flex; align-items: center;
    justify-content: center; font-size: 28px;
    box-shadow: 0 0 30px rgba(59,130,246,0.45);
}
.logo-name {
    font-family: 'Outfit', sans-serif; font-size: 2.6rem;
    font-weight: 900; letter-spacing: -0.05em;
    background: linear-gradient(135deg, #fff 10%, #3b82f6 55%, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1;
}
.logo-sub {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    color: #64748b; letter-spacing: 0.1em; text-transform: uppercase;
}

.chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: 100px;
    font-family: 'Outfit', sans-serif; font-size: 0.75rem;
    font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
}
.chip-blue   { background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3); color: #93c5fd; }
.chip-green  { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); color: #6ee7b7; }
.chip-amber  { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.3); color: #fcd34d; }
.chip-purple { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.3); color: #c4b5fd; }

#output-box textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important; line-height: 1.8 !important;
    background: #0d1117 !important; color: #e2e8f0 !important;
}
"""

THEME_JS = """
function() {
    window._isLight = false;
    window.toggleTheme = function() {
        window._isLight = !window._isLight;
        var light = window._isLight;
        var existing = document.getElementById('theme-style');
        if (existing) existing.remove();
        var style = document.createElement('style');
        style.id = 'theme-style';
        if (light) {
            style.textContent = `
                body, .gradio-container { background-color: #f0f4f8 !important; color: #0f172a !important; }
                textarea, select { background-color: #ffffff !important; color: #0f172a !important; border-color: #cbd5e1 !important; }
                #output-box textarea { background-color: #f1f5f9 !important; color: #1e3a5f !important; }
            `;
        } else {
            style.textContent = `
                body, .gradio-container { background-color: #060810 !important; color: #e2e8f0 !important; }
                #output-box textarea { background-color: #0d1117 !important; color: #e2e8f0 !important; }
            `;
        }
        document.head.appendChild(style);
        var btn = document.getElementById('vs-theme-btn');
        if (btn) {
            btn.innerHTML = light ? '🌙 &nbsp;Dark Mode' : '☀️ &nbsp;Light Mode';
            btn.style.background = light ? '#ffffff' : '#111827';
            btn.style.color = light ? '#0f172a' : '#e2e8f0';
        }
    };
}
"""


# ── FORMAT OUTPUT ─────────────────────────────────────
def format_output(results):
    scores = results.get("scores", {})
    final  = scores.get("final_score", 0)

    if final >= 80:   medal = "🏆"; rating = "★★★★★  EXCELLENT"
    elif final >= 60: medal = "✅"; rating = "★★★★☆  GOOD"
    elif final >= 40: medal = "⚠️";  rating = "★★★☆☆  PARTIAL"
    else:             medal = "❌"; rating = "★★☆☆☆  POOR"

    output = f"""
╔══════════════════════════════════════════════════════╗
║         VIDSENSE  ·  VIDEO UNDERSTANDING REPORT      ║
╚══════════════════════════════════════════════════════╝

  Language         :  {results.get('language','unknown').upper()}
  Caption Source   :  {results.get('caption_source','Auto-Generated by AI')}

──────────────────────────────────────────────────────
  STAGE 1 — SPEECH TRANSCRIPT
──────────────────────────────────────────────────────
{results.get('speech_transcript', 'No speech detected')}

──────────────────────────────────────────────────────
  STAGE 2 — VISUAL SEMANTIC CONTEXT
──────────────────────────────────────────────────────
{results.get('visual_context', 'No visual context')}

──────────────────────────────────────────────────────
  STAGE 3 — ACTION DETECTION
──────────────────────────────────────────────────────
{results.get('actions', 'No actions detected')}

──────────────────────────────────────────────────────
  STAGE 4 — RICH UNIFIED TRANSCRIPT
──────────────────────────────────────────────────────
{results.get('rich_transcript', 'No transcript generated')}

══════════════════════════════════════════════════════
  {medal}  FINAL SCORE  →  {final}%   {rating}
══════════════════════════════════════════════════════
  {scores.get('label', '')}

  ┌───────────────────────────────────────────────┐
  │  Text Similarity   (SBERT)   →  {str(scores.get('sbert_score',0)).rjust(6)}%      │
  │  Word Order        (ROUGE-L) →  {str(scores.get('rouge_score',0)).rjust(6)}%      │
  │  Combined Score              →  {str(scores.get('text_similarity',0)).rjust(6)}%      │
  └───────────────────────────────────────────────┘

──────────────────────────────────────────────────────
  AUTO-GENERATED REFERENCE CAPTION
──────────────────────────────────────────────────────
{results.get('ground_truth', 'None')}

══════════════════════════════════════════════════════
  Powered by VidSense  ·  Whisper + Groq Vision + SBERT
══════════════════════════════════════════════════════
"""
    return output


# ── ANALYZE FUNCTION ──────────────────────────────────
def analyze(video_file):
    if not video_file:
        return "  Please upload a video first."
    try:
        results = run_pipeline(video_path=video_file)
        return format_output(results)
    except Exception as e:
        return f"  Error: {str(e)}"


# ── BUILD UI ──────────────────────────────────────────
def build_ui():
    with gr.Blocks(
        title="VidSense — Multimodal Video Understanding",
        css=CUSTOM_CSS,
        js=THEME_JS,
        theme=gr.themes.Base(
            font=gr.themes.GoogleFont("Outfit"),
            font_mono=gr.themes.GoogleFont("JetBrains Mono"),
        )
    ) as app:

        gr.HTML("""
<button id="vs-theme-btn" onclick="toggleTheme()"
  style="position:fixed;top:18px;right:24px;z-index:9999;
         background:#111827;border:1px solid #243447;border-radius:100px;
         padding:8px 18px;cursor:pointer;font-family:'Outfit',sans-serif;
         font-size:0.82rem;font-weight:600;color:#e2e8f0;
         display:flex;align-items:center;gap:8px;
         box-shadow:0 2px 12px rgba(0,0,0,0.3);transition:all 0.25s;">
  ☀️ &nbsp;Light Mode
</button>""")

        gr.HTML("""
<div class="logo-header">
  <div class="logo-icon">🎬</div>
  <div>
    <div class="logo-name">VidSense</div>
    <div class="logo-sub">Multimodal Video Understanding · Speech + Vision + Actions</div>
  </div>
</div>""")

        gr.HTML("""
<div style="display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 8px;">
  <span class="chip chip-blue">🎙 Whisper ASR</span>
  <span class="chip chip-blue">👁 Visual Semantic Layers</span>
  <span class="chip chip-green">🏃 Action Detection</span>
  <span class="chip chip-green">📝 Rich Transcript</span>
  <span class="chip chip-purple">📊 SBERT + ROUGE-L</span>
</div>""")

        gr.HTML("<hr style='border:none;border-top:1px solid #1e2d42;margin:16px 0 24px;'>")

        with gr.Row(equal_height=False):

            with gr.Column(scale=1):
                gr.Markdown("## 📤 Upload Video")

                video_input = gr.Video(
                    label="Upload Video",
                    sources=["upload"],
                    height=280,
                )

                gr.HTML("<div style='height:12px'></div>")

                analyze_btn = gr.Button(
                    "⚡  Analyze Video",
                    variant="primary",
                    size="lg",
                )

                gr.HTML("<hr style='border:none;border-top:1px solid #1e2d42;margin:24px 0 16px;'>")

                gr.HTML("""
<div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#64748b;line-height:2.2;">
  <div style="color:#3b82f6;font-weight:700;margin-bottom:10px;font-size:0.78rem;">
    ⚙ PIPELINE STAGES
  </div>
  <div>Stage 1 — Whisper extracts speech</div>
  <div>Stage 2 — Groq Vision: 3 semantic layers</div>
  <div>Stage 3 — Groq Vision: action detection</div>
  <div>Stage 4 — LLaMA: rich transcript</div>
  <div>Stage 5 — LLaMA: auto reference caption</div>
  <div>Stage 6 — SBERT + ROUGE-L comparison</div>
</div>""")

                gr.HTML("<hr style='border:none;border-top:1px solid #1e2d42;margin:16px 0;'>")

                gr.HTML("""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
  <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:10px 14px;">
    <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#6ee7b7;font-size:1rem;">80–100%</div>
    <div style="font-size:0.7rem;color:#64748b;">🏆 Excellent</div>
  </div>
  <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.25);border-radius:10px;padding:10px 14px;">
    <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#93c5fd;font-size:1rem;">60–79%</div>
    <div style="font-size:0.7rem;color:#64748b;">✅ Good</div>
  </div>
  <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:10px;padding:10px 14px;">
    <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#fcd34d;font-size:1rem;">40–59%</div>
    <div style="font-size:0.7rem;color:#64748b;">⚠️ Partial</div>
  </div>
  <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);border-radius:10px;padding:10px 14px;">
    <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#fca5a5;font-size:1rem;">0–39%</div>
    <div style="font-size:0.7rem;color:#64748b;">❌ Poor</div>
  </div>
</div>""")

            with gr.Column(scale=1):
                gr.Markdown("## 📊 Analysis Report")

                output_box = gr.Textbox(
                    label="VidSense Report",
                    lines=50,
                    max_lines=70,
                    placeholder=(
                        "  Results will appear here after analysis...\n\n"
                        "  Upload any video and click ⚡ Analyze Video\n\n"
                        "  VidSense will automatically:\n"
                        "  • Transcribe speech (Whisper)\n"
                        "  • Extract visual semantic layers (Groq Vision)\n"
                        "  • Detect actions (Groq Vision)\n"
                        "  • Generate rich unified transcript (LLaMA)\n"
                        "  • Auto-generate reference caption (LLaMA)\n"
                        "  • Compute similarity score (SBERT + ROUGE-L)"
                    ),
                    elem_id="output-box",
                )

        analyze_btn.click(
            fn=analyze,
            inputs=[video_input],
            outputs=output_box,
            show_progress="full",
        )

    return app


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  VidSense — Multimodal Video Understanding")
    print("="*50)
    app = build_ui()
    app.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        inbrowser=True,
    )

 