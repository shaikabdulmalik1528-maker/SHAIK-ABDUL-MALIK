import csv
import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class ReportExporter:
    @staticmethod
    def generate_student_pdf(report_data: Dict[str, Any]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"Student Performance Report - ID: {report_data['student_id']}", styles['Title']))
        story.append(Spacer(1, 12))

        metrics = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Sessions", str(report_data['total_sessions']), "Overall Accuracy", f"{report_data['overall_accuracy']}%"],
            ["Total Attempts", str(report_data['total_attempts']), "Current Session Accuracy", f"{report_data['current_session_accuracy']}%"],
            ["Avg Confidence", f"{report_data['avg_confidence']}%", "Avg Inference Time", f"{report_data['avg_inference_time_ms']} ms"]
        ]
        
        t = Table(metrics, colWidths=[130, 120, 130, 120])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Alphabet Performance Breakdown", styles['Heading2']))
        story.append(Spacer(1, 6))

        breakdown_data = [
            ["Category", "Alphabets"],
            ["Strongest Alphabets", ", ".join(report_data['strongest_alphabets']) or "None"],
            ["Weakest Alphabets", ", ".join(report_data['weakest_alphabets']) or "None"],
            ["Most Practiced", ", ".join(report_data['most_frequently_practiced']) or "None"],
            ["Most Misclassified", ", ".join(report_data['most_misclassified']) or "None"]
        ]

        t_breakdown = Table(breakdown_data, colWidths=[180, 320])
        t_breakdown.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_breakdown)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Personalized Recommendations", styles['Heading2']))
        story.append(Spacer(1, 6))
        for rec in report_data['recommendations']:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 4))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_student_csv(report_data: Dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Student ID", report_data['student_id']])
        writer.writerow(["Total Sessions", report_data['total_sessions']])
        writer.writerow(["Total Attempts", report_data['total_attempts']])
        writer.writerow(["Overall Accuracy (%)", report_data['overall_accuracy']])
        writer.writerow(["Current Session Accuracy (%)", report_data['current_session_accuracy']])
        writer.writerow(["Average Confidence (%)", report_data['avg_confidence']])
        writer.writerow(["Average Inference Time (ms)", report_data['avg_inference_time_ms']])
        writer.writerow(["Strongest Alphabets", ", ".join(report_data['strongest_alphabets'])])
        writer.writerow(["Weakest Alphabets", ", ".join(report_data['weakest_alphabets'])])
        writer.writerow(["Most Frequent Alphabets", ", ".join(report_data['most_frequently_practiced'])])
        writer.writerow(["Most Misclassified Alphabets", ", ".join(report_data['most_misclassified'])])
        
        return output.getvalue()
    