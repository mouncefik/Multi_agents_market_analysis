import gradio as gr
from src.graph import MarketResearchGraph
import os
import markdown
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

class ReportPDF(FPDF):
    def __init__(self, topic):
        super().__init__()
        self.topic = topic
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_draw_color(226, 232, 240) 
            self.line(20, 25, 190, 25)
            
            self.set_y(15)
            self.set_font('helvetica', 'B', 9)
            self.set_text_color(100, 116, 139)  # Slate-500
            self.cell(0, 10, 'MARKET INTELLIGENCE REPORT', new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
            
            self.set_font('helvetica', '', 9)
            self.cell(0, 10, datetime.now().strftime('%Y-%m-%d'), new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')
            self.ln(15)
    
    def footer(self):
        if self.page_no() > 1:
            self.set_y(-20)
            self.set_draw_color(226, 232, 240)
            self.line(20, 275, 190, 275)
            
            self.set_y(-15)
            self.set_font('helvetica', '', 8)
            self.set_text_color(148, 163, 184)  # Slate-400
            self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
            self.set_text_color(0, 0, 0)
    
    def add_cover_page(self):
        self.add_page()
        
        # Geometric Background
        self.set_fill_color(99, 102, 241)  # Indigo-500
        self.rect(0, 0, 210, 297, 'F')
        
        # White Content Card
        self.set_fill_color(255, 255, 255)
        self.rect(20, 40, 170, 217, 'F')
        
        # Decorative Accent
        self.set_fill_color(79, 70, 229)  # Indigo-600
        self.rect(20, 40, 170, 10, 'F')
        
        # Content
        self.set_y(80)
        self.set_text_color(30, 41, 59)  # Slate-800
        self.set_font('helvetica', 'B', 32)
        self.multi_cell(0, 14, 'MARKET\nRESEARCH\nREPORT', 0, 'C')
        
        self.ln(20)
        self.set_draw_color(99, 102, 241)
        self.set_line_width(1)
        self.line(70, self.get_y(), 140, self.get_y())
        
        self.ln(20)
        self.set_font('helvetica', '', 16)
        self.set_text_color(71, 85, 105)  # Slate-600
        self.multi_cell(0, 10, self.topic, 0, 'C')
        
        # Footer Info
        self.set_y(220)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, 'PREPARED BY', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font('helvetica', '', 12)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, 'AI Market Agents System', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(2)
        self.set_font('helvetica', '', 10)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, datetime.now().strftime('%B %d, %Y'), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

def export_pdf(markdown_content, chart_paths, topic="Market Research"):
    if not markdown_content:
        return None
    
    # Sanitize text
    replacements = {
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-',
        '\u2026': '...',
        '\u00a0': ' ',
    }
    for old, new in replacements.items():
        markdown_content = markdown_content.replace(old, new)
    
    pdf = ReportPDF(topic)
    pdf.add_cover_page()
    pdf.add_page()
    
    # Executive Summary Styling
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(79, 70, 229)  # Indigo-600
    pdf.cell(0, 10, 'EXECUTIVE SUMMARY', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(2)
    
    # Parse content
    sections = markdown_content.split('##')
    
    for i, section in enumerate(sections):
        if not section.strip(): continue
        
        if i == 0:  # Intro/Exec Summary
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(51, 65, 85)  # Slate-700
            
            safe_text = section.strip().encode('latin-1', 'replace').decode('latin-1')
            import re
            safe_text = re.sub(r'!\[.*?\]\(.*?\)', '', safe_text)
            pdf.multi_cell(0, 6, safe_text)
            pdf.ln(10)
        else:
            lines = section.strip().split('\n', 1)
            section_title = lines[0].strip()
            section_content = lines[1] if len(lines) > 1 else ""
            
            if 'Visualizations' in section_title or 'visualization' in section_title.lower():
                continue
            
            # Section Header
            if pdf.get_y() > 250: pdf.add_page()
            
            pdf.set_font('helvetica', 'B', 14)
            pdf.set_text_color(79, 70, 229)
            pdf.cell(0, 10, section_title.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
            pdf.set_draw_color(226, 232, 240)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(5)
            
            # Content
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(51, 65, 85)
            safe_text = section_content.strip().encode('latin-1', 'replace').decode('latin-1')
            safe_text = re.sub(r'!\[.*?\]\(.*?\)', '', safe_text)
            pdf.multi_cell(0, 6, safe_text)
            pdf.ln(8)
    
    # Visualizations Section
    if chart_paths:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_text_color(79, 70, 229)
        pdf.cell(0, 10, 'DATA VISUALIZATIONS', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(10)
        
        for idx, chart_path in enumerate(chart_paths):
            if os.path.exists(chart_path):
                if pdf.get_y() > 180: pdf.add_page()
                
                pdf.set_font('helvetica', 'B', 10)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 8, f'Figure {idx + 1}: Market Analysis Chart', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                
                try:
                    img_width = 170
                    x_pos = (pdf.w - img_width) / 2
                    pdf.image(chart_path, x=x_pos, w=img_width)
                    pdf.ln(10)
                except Exception as e:
                    print(f"Error adding chart: {e}")
    
    output_filename = "report.pdf"
    try:
        pdf.output(output_filename)
    except Exception as e:
        print(f"Failed to save PDF: {e}")
        return None
    
    return output_filename

import json
import shutil
from datetime import datetime

class HistoryManager:
    def __init__(self, history_dir="history"):
        self.history_dir = history_dir
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
            
    def save_report(self, topic, report_content, chart_paths, pdf_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join([c for c in topic if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
        report_id = f"{timestamp}_{safe_topic}"
        report_dir = os.path.join(self.history_dir, report_id)
        
        os.makedirs(report_dir)
        
        # Save metadata
        metadata = {
            "id": report_id,
            "topic": topic,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "charts": [],
            "pdf": "report.pdf" if pdf_path else None
        }
        
        # Save report content
        with open(os.path.join(report_dir, "report.md"), "w", encoding="utf-8") as f:
            f.write(report_content)
            
        # Copy charts
        for chart_path in chart_paths:
            if os.path.exists(chart_path):
                chart_name = os.path.basename(chart_path)
                shutil.copy2(chart_path, os.path.join(report_dir, chart_name))
                metadata["charts"].append(chart_name)
                
        # Copy PDF
        if pdf_path and os.path.exists(pdf_path):
            shutil.copy2(pdf_path, os.path.join(report_dir, "report.pdf"))
            
        # Save metadata json
        with open(os.path.join(report_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        return report_id

    def get_history(self):
        reports = []
        if not os.path.exists(self.history_dir):
            return []
            
        for report_id in os.listdir(self.history_dir):
            meta_path = os.path.join(self.history_dir, report_id, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        reports.append(meta)
                except:
                    continue
        
        # Sort by date descending
        return sorted(reports, key=lambda x: x["id"], reverse=True)

    def load_report(self, report_id):
        report_dir = os.path.join(self.history_dir, report_id)
        if not os.path.exists(report_dir):
            return None
            
        # Load content
        with open(os.path.join(report_dir, "report.md"), "r", encoding="utf-8") as f:
            content = f.read()
            
        # Load metadata
        with open(os.path.join(report_dir, "metadata.json"), "r", encoding="utf-8") as f:
            meta = json.load(f)
            
        # Get chart paths
        chart_paths = [os.path.join(report_dir, c) for c in meta["charts"]]
        pdf_path = os.path.join(report_dir, "report.pdf") if meta["pdf"] else None
        
        return content, chart_paths, pdf_path

def create_timeline_html(completed_steps, current_step=None):
    """Generate HTML for timeline progress visualization"""
    all_steps = ["researcher", "analyst", "reviewer", "chart_generator", "writer"]
    step_icons = {
        "researcher": "search",
        "analyst": "analytics",
        "reviewer": "rate_review",
        "chart_generator": "insert_chart",
        "writer": "description"
    }
    step_labels = {
        "researcher": "Research",
        "analyst": "Analysis",
        "reviewer": "Review & QA",
        "chart_generator": "Visualization",
        "writer": "Report Writing"
    }
    
    html = """
    <div class="timeline-container">
    """
    
    for idx, step in enumerate(all_steps):
        is_completed = step in completed_steps
        is_current = step == current_step
        is_pending = not is_completed and not is_current
        
        status_class = "completed" if is_completed else ("current" if is_current else "pending")
        
        # Handle loop back visualization (if researcher is active but analyst was completed)
        if step == "researcher" and "analyst" in completed_steps and current_step == "researcher":
            status_class = "current"
            
        html += f"""
        <div class="timeline-item {status_class}">
            <div class="timeline-marker">
                <div class="timeline-icon">
                    <span class="material-symbols-outlined">{step_icons[step]}</span>
                </div>
            </div>
            <div class="timeline-content">
                <div class="timeline-title">{step_labels[step]}</div>
                <div class="timeline-status">
                    {"✓ Completed" if is_completed else ("⏳ In Progress..." if is_current else "Pending")}
                </div>
            </div>
        </div>
        """
        
        # Add connector line except after last item
        if idx < len(all_steps) - 1:
            connector_class = "completed" if completed_steps and all_steps.index(completed_steps[-1]) > idx else "pending"
            html += f'<div class="timeline-connector {connector_class}"></div>'
    
    html += """
    </div>
    """
    return html

history_manager = HistoryManager()

def generate_report(topic, provider):
    try:
        graph = MarketResearchGraph(model_provider=provider.lower())
        completed_steps = []
        
        # Initial state
        initial_html = create_timeline_html([], None)
        yield initial_html, "", [], None, gr.Button(value="Agents Working ⏳", interactive=False, variant="secondary"), gr.update(choices=[])
        
        for step_name, step_output in graph.run_stream(topic):
            if step_name not in completed_steps:
                completed_steps.append(step_name)
            
            # Find all chart files
            chart_paths = [f for f in os.listdir() if f.startswith("chart_") and f.endswith(".png")]
            chart_paths.sort()
            
            # Determine next step
            all_steps = ["researcher", "analyst", "reviewer", "chart_generator", "writer"]
            try:
                current_idx = all_steps.index(step_name)
                next_step = all_steps[current_idx + 1] if current_idx < len(all_steps) - 1 else None
            except ValueError:
                next_step = None
            
            # If reviewer sends back to researcher, reset completed steps partially or just show status
            if step_name == "reviewer" and step_output.get("feedback"):
                # Loop detected
                next_step = "researcher"
            
            timeline_html = create_timeline_html(completed_steps, next_step)
            yield timeline_html, "", chart_paths, None, gr.Button(value="Agents Working ⏳", interactive=False, variant="secondary"), gr.update()
            
            if step_name == "writer":
                final_report = step_output.get("final_report", "")
                # Generate PDF with topic
                pdf_path = export_pdf(final_report, chart_paths, topic)
                
                # Save to history
                history_manager.save_report(topic, final_report, chart_paths, pdf_path)
                
                # Update history list
                history = history_manager.get_history()
                history_choices = [f"{h['date']} - {h['topic']}" for h in history]
                
                final_timeline = create_timeline_html(completed_steps, None)
                yield final_timeline, final_report, chart_paths, pdf_path, gr.Button(value="Generate Report", interactive=True, variant="primary"), gr.update(choices=history_choices, value=history_choices[0] if history_choices else None)
                
    except Exception as e:
        error_html = f'<div style="color: red; padding: 20px;">Error: {str(e)}</div>'
        yield error_html, "", [], None, gr.Button(value="Generate Report", interactive=True, variant="primary"), gr.update()

def load_history_report(selection):
    if not selection:
        return None, None, None, None
        
    # Parse selection to get topic and date to find ID (simplified matching)
    history = history_manager.get_history()
    selected_report = None
    for h in history:
        if f"{h['date']} - {h['topic']}" == selection:
            selected_report = h
            break
            
    if selected_report:
        content, chart_paths, pdf_path = history_manager.load_report(selected_report["id"])
        # Re-create timeline as completed
        timeline = create_timeline_html(["researcher", "analyst", "reviewer", "chart_generator", "writer"], None)
        return timeline, content, chart_paths, pdf_path
    
    return None, None, None, None

from openai import OpenAI

def generate_audio_summary(report_text):
    if not report_text:
        return None
        
    try:
        # Extract Executive Summary
        summary = ""
        if "## Executive Summary" in report_text:
            summary = report_text.split("## Executive Summary")[1].split("##")[0].strip()
        else:
            summary = report_text[:1000] # Fallback to first 1000 chars
            
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=f"Here is your market research executive summary. {summary}"
        )
        
        output_path = "summary.mp3"
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def app():
    # Custom theme configuration
    theme = gr.themes.Ocean(
        primary_hue="indigo",
        secondary_hue="violet",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        radius_size=gr.themes.sizes.radius_lg,
    ).set(
        body_background_fill="linear-gradient(135deg, #f0f4ff 0%, #eef2ff 100%)",
        block_background_fill="rgba(255, 255, 255, 0.8)",
        block_border_width="0px",
        block_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        button_primary_background_fill="linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
        button_primary_background_fill_hover="linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)",
        button_primary_text_color="white",
        button_secondary_background_fill="white",
        button_secondary_border_color="#e2e8f0",
        button_secondary_text_color="#475569",
    )
    
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');
    
    :root {
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.5);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }

    body {
        font-family: 'Inter', sans-serif;
        background-attachment: fixed;
    }
    
    .container { 
        max-width: 1400px; 
        margin: auto; 
        padding: 40px 20px;
    }
    
    /* Premium Header */
    .header { 
        text-align: center; 
        margin-bottom: 50px; 
        animation: fadeInDown 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
        position: relative;
    }
    
    .header h1 { 
        font-size: 3.5em; 
        font-weight: 800; 
        letter-spacing: -0.02em;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
        display: inline-flex;
        align-items: center;
        gap: 15px;
    }
    
    .header p { 
        font-size: 1.25em; 
        color: var(--text-secondary); 
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        box-shadow: var(--glass-shadow);
        border-radius: 24px;
        padding: 30px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.1);
    }
    
    .input-group {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.05);
        margin-bottom: 40px;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.2s backwards;
        border: 1px solid rgba(255,255,255,0.8);
    }
    
    .status-box { 
        border-radius: 20px; 
        background: white;
        padding: 25px;
        box-shadow: 0 4px 20px -5px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        height: 100%;
    }
    
    .results-section {
        margin-top: 40px;
        animation: fadeIn 1s ease-out 0.4s backwards;
    }
    
    .results-title {
        font-size: 1.75em;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        vertical-align: middle;
    }
    
    /* Timeline Styles - Refined */
    .timeline-container {
        padding: 10px 0;
    }
    
    .timeline-item {
        display: flex;
        position: relative;
        padding: 15px 0;
        animation: fadeInLeft 0.5s ease-out;
    }
    
    .timeline-marker {
        position: relative;
        margin-right: 25px;
        flex-shrink: 0;
        z-index: 2;
    }
    
    .timeline-icon {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        background: white;
        border: 2px solid #f1f5f9;
    }
    
    .timeline-item.completed .timeline-icon {
        background: #10b981;
        border-color: #10b981;
        color: white;
        transform: scale(1.05);
    }
    
    .timeline-item.current .timeline-icon {
        background: white;
        border-color: #6366f1;
        color: #6366f1;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
    }
    
    .timeline-item.pending .timeline-icon {
        background: #f8fafc;
        color: #cbd5e1;
        border-color: #f1f5f9;
    }
    
    .timeline-content {
        flex-grow: 1;
        padding-top: 8px;
    }
    
    .timeline-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    
    .timeline-status {
        font-size: 13px;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .timeline-connector {
        position: absolute;
        left: 21px;
        width: 2px;
        height: 100%;
        top: 44px;
        background: #f1f5f9;
        z-index: 1;
    }
    
    .timeline-connector.completed {
        background: #10b981;
    }
    
    /* Button Enhancements */
    button.primary {
        background: var(--primary-gradient) !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
        padding: 18px 36px !important;
        border-radius: 16px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.4) !important;
        text-transform: none !important;
        letter-spacing: -0.01em !important;
    }
    
    button.primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.5) !important;
    }
    
    button.primary:active {
        transform: translateY(1px) !important;
    }
    
    /* Tabs Styling */
    .tabs {
        background: white;
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
    }
    
    .tab-nav {
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 20px;
    }
    
    /* Markdown Content */
    .prose {
        font-size: 1.05em;
        line-height: 1.7;
        color: #334155;
    }
    
    .prose h1, .prose h2, .prose h3 {
        color: #1e293b;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .prose blockquote {
        border-left: 4px solid #6366f1;
        background: #f8fafc;
        padding: 1em;
        border-radius: 0 12px 12px 0;
        font-style: italic;
    }

    /* Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    """

    with gr.Blocks(theme=theme, css=css, title="Market Research Agents") as demo:
        with gr.Column(elem_classes="container"):
            # Header
            with gr.Column(elem_classes="header"):
                gr.HTML("<h1><span class='material-symbols-outlined'>rocket_launch</span>Market Research AI System</h1>")
                gr.Markdown("Intelligent market analysis powered by multi-agent AI collaboration")

            with gr.Row():
                # Sidebar (History)
                with gr.Column(scale=1, min_width=300):
                    with gr.Column(elem_classes="glass-card"):
                        gr.Markdown("### 📂 Report History")
                        history_dropdown = gr.Dropdown(
                            label="Previous Reports",
                            choices=[f"{h['date']} - {h['topic']}" for h in history_manager.get_history()],
                            interactive=True,
                            info="Select a past report to view",
                            show_label=False
                        )
                        load_btn = gr.Button("Load Report", variant="secondary")

                # Main Content
                with gr.Column(scale=3):
                    # Command Center
                    with gr.Group(elem_classes="glass-card"):
                        gr.Markdown("### 🎯 Command Center")
                        with gr.Row():
                            topic_input = gr.Textbox(
                                label="Research Topic", 
                                placeholder="e.g., Future of Renewable Energy, AI in Financial Services", 
                                scale=3,
                                info="What market or technology would you like to analyze?",
                                show_label=True,
                                elem_id="topic-input"
                            )
                            provider_input = gr.Dropdown(
                                choices=["Gemini", "OpenAI"], 
                                value="Gemini", 
                                label="AI Provider",
                                scale=1,
                                info="Select your preferred AI engine"
                            )
                        
                        submit_btn = gr.Button(
                            "Generate Comprehensive Report", 
                            variant="primary", 
                            size="lg",
                            elem_classes="primary",
                            elem_id="submit-btn"
                        )

                    # Results Area
                    with gr.Column(elem_classes="results-section"):
                        gr.HTML("<div class='results-title'><span class='material-symbols-outlined'>analytics</span>Research Dashboard</div>")
                        
                        # Status & Downloads
                        with gr.Row():
                            with gr.Column(scale=2):
                                status_output = gr.HTML(
                                    value="<div style='padding: 20px; text-align: center; color: #64748b;'>Ready to start research...</div>",
                                    label="Agent Workflow"
                                )
                            with gr.Column(scale=1):
                                with gr.Group(elem_classes="glass-card"):
                                    gr.Markdown("### 📥 Exports")
                                    pdf_download = gr.File(label="Download PDF", show_label=False)
                                    audio_btn = gr.Button("Generate Audio Brief 🎧", variant="secondary")
                                    audio_output = gr.Audio(label="Podcast Summary", type="filepath", show_label=False)

                        # Content Tabs
                        with gr.Tabs(elem_classes="tabs"):
                            with gr.TabItem("📄 Full Report", elem_id="tab-report"):
                                output_display = gr.Markdown(
                                    line_breaks=True,
                                    value="*Your comprehensive market research report will appear here...*",
                                    elem_classes="prose"
                                )
                            with gr.TabItem("📊 Visualizations", elem_id="tab-charts"):
                                chart_output = gr.Gallery(
                                    label="Generated Charts", 
                                    columns=2, 
                                    height="auto",
                                    object_fit="contain",
                                    elem_classes="gallery",
                                    show_label=False
                                )
                            with gr.TabItem("🔍 Raw Data", elem_id="tab-data"):
                                gr.Markdown("*Raw research data and analysis logs will appear here...*")

            submit_btn.click(
                fn=generate_report,
                inputs=[topic_input, provider_input],
                outputs=[status_output, output_display, chart_output, pdf_download, submit_btn, history_dropdown]
            )
            
            load_btn.click(
                fn=load_history_report,
                inputs=[history_dropdown],
                outputs=[status_output, output_display, chart_output, pdf_download]
            )
            
            audio_btn.click(
                fn=generate_audio_summary,
                inputs=[output_display],
                outputs=[audio_output]
            )

    demo.launch(allowed_paths=["."])

if __name__ == "__main__":
    app()
