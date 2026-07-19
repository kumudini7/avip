from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import settings
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentResultRead
from app.services.document_processor import ensure_directory


def generate_assessment_report(assessment: Assessment, result: AssessmentResultRead) -> Path:
    report_dir = ensure_directory(Path(settings.report_dir) / "assessments")
    output_path = report_dir / f"assessment_{assessment.id}.pdf"

    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], leading=14, fontSize=10))

    classification = result.classification
    story: list = []
    story.append(Paragraph("AutoAssess Report", styles["Title"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(f"Domain: {result.domain}", styles["Body"]))
    story.append(Spacer(1, 0.2 * inch))

    if classification is not None:
        story.append(Paragraph(classification.matched_use_case, styles["SectionTitle"]))
        story.append(
            Paragraph(
                f"Category: {classification.category} | Confidence: {classification.confidence_score:.0f}% | "
                f"Complexity: {classification.complexity} | Timeline: {classification.estimated_timeline}",
                styles["Body"],
            )
        )
        story.append(Spacer(1, 0.1 * inch))
        for reason in classification.reasoning:
            story.append(Paragraph(f"- {reason}", styles["Body"]))
        story.append(Spacer(1, 0.2 * inch))

    if result.roi is not None:
        story.append(Paragraph("ROI Summary", styles["SectionTitle"]))
        story.append(Spacer(1, 0.08 * inch))
        currency = result.roi.currency
        rows = [
            ["Metric", f"Value ({currency})"],
            ["Current annual cost", f"{result.roi.current_annual_cost:,.0f}"],
            ["Post-automation cost", f"{result.roi.post_automation_cost:,.0f}"],
            ["Implementation cost", f"{result.roi.implementation_cost:,.0f}"],
            ["Year 1 net saving", f"{result.roi.year1_net_saving:,.0f}"],
            ["Year 2 saving", f"{result.roi.year2_saving:,.0f}"],
            ["Payback period", f"{result.roi.payback_months} months" if result.roi.payback_months else "N/A"],
        ]
        story.append(
            Table(
                rows,
                colWidths=[2.6 * inch, 3.4 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("LEADING", (0, 0), (-1, -1), 12),
                    ]
                ),
            )
        )

    doc.build(story)
    return output_path
