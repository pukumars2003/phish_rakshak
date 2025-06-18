import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from transformers import pipeline

matplotlib.use('Agg')

# Load model using Hugging Face
model = pipeline('text-classification', model="Ajay1311/phish")

def create_speedometer_chart(confidence, is_phishing):
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw={'projection': 'polar'})

    confidence_pct = confidence * 100
    theta = np.linspace(np.pi, 0, 100)
    ax.plot(theta, [1]*100, color='lightgray', linewidth=15, alpha=0.3)

    angle = np.pi * (1 - (confidence_pct / 100))
    ax.plot([np.pi, angle], [0, 1], color='red' if is_phishing else 'green', linewidth=4)

    ax.fill_between(theta, 0, 1, where=(theta >= angle), color='red' if is_phishing else 'green', alpha=0.25)

    ax.set_rticks([])
    ax.set_xticks([])
    ax.set_yticklabels([])
    ax.set_facecolor("white")
    ax.spines['polar'].set_visible(False)
    ax.set_ylim(0, 1.1)

    label = f"{'PHISHING' if is_phishing else 'BENIGN'}\n{confidence_pct:.1f}%"
    ax.text(0, -0.2, label, ha='center', va='center', fontsize=14, fontweight='bold', color='black')

    return fig

def analyze_phishing(text):
    if not text.strip():
        return "No input provided.", None, "Please enter valid email or URL content for analysis."
    
    result = model(text)
    label = result[0]['label']
    score = result[0]['score']
    is_phishing = label.lower() == 'phishing'
    chart = create_speedometer_chart(score, is_phishing)

    if is_phishing:
        analysis = f"""
        ⚠️ **Phishing Likely Detected**  
        The provided input has characteristics associated with phishing content.  
        **Confidence:** {score*100:.1f}%
        
        **Indicators of phishing may include:**
        - Suspicious or misspelled URLs
        - Requests for personal credentials
        - Unusual urgency or threats
        - Unexpected attachments or links
        **Recommendation:** Do not interact with the content until verified by your IT or security team.
        """
    else:
        analysis = f"""
        ✅ **No Threat Detected**  
        The content appears legitimate based on the current model.  
        **Confidence:** {score*100:.1f}%
        
        **General Safety Tips:**
        - Avoid clicking unknown links
        - Be cautious with personal data
        - Always confirm requests from unknown senders
        **Recommendation:** Proceed with standard caution.
        """

    return f"{'Phishing Detected' if is_phishing else 'Content Safe'} (Confidence: {score*100:.1f}%)", chart, analysis

theme = gr.themes.Soft(primary_hue="blue", secondary_hue="gray").set(
    button_primary_background_fill="*primary_600",
    button_primary_text_color="white",
    block_label_background_fill="*neutral_100",
    block_title_text_color="*primary_600",
)

with gr.Blocks(theme=theme, css=""".container { max-width: 800px; margin: 0 auto; }""") as demo:
    with gr.Column(elem_classes="container"):
        gr.HTML("""<div class="header"><h1>Cyber Swa Raksha</h1><p>Protect From Phishing By Yourself</p></div>""")
        
        with gr.Group():
            input_text = gr.Textbox(
                placeholder="Enter email content, message, or suspicious URL...",
                lines=4,
                label="Input Text"
            )
        
        with gr.Row():
            analyze_btn = gr.Button("Analyze", variant="primary")
            clear_btn = gr.Button("Clear")
        
        with gr.Group():
            result_text = gr.Textbox(label="Detection Summary", elem_classes="result-box")
            result_plot = gr.Plot(label="Confidence Meter")
            analysis_md = gr.Markdown(label="Detailed Analysis")

        analyze_btn.click(
            analyze_phishing,
            inputs=input_text,
            outputs=[result_text, result_plot, analysis_md]
        )

        clear_btn.click(
            lambda: ("", None, ""),
            inputs=None,
            outputs=[input_text, result_plot, analysis_md]
        )

        gr.HTML("""<div class="footer">Cyber Swa Raksha</div>""")

if __name__ == "__main__":
    demo.launch(share=True)
