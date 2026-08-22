from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

def generate_pdf_report(evaluation_data: dict) -> bytes:
    """
    Takes evaluation result dict, returns PDF as bytes.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=4
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=16,
        spaceAfter=8,
        borderPad=4
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leading=14
    )

    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        spaceAfter=3,
        leading=12
    )

    # Safety score color
    score = evaluation_data.get('safety_score', 0)
    if score >= 75:
        score_color = colors.HexColor('#3fb950')  # green
    elif score >= 50:
        score_color = colors.HexColor('#d29922')  # amber
    else:
        score_color = colors.HexColor('#f85149')  # red

    score_style = ParagraphStyle(
        'Score',
        parent=styles['Normal'],
        fontSize=36,
        textColor=score_color,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    # Build content
    story = []

    # Header
    story.append(Paragraph("🛡️ AgentGuard", title_style))
    story.append(Paragraph("AI Agent Reliability Report", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
    story.append(Spacer(1, 12))

    # Agent info
    story.append(Paragraph("Agent Under Evaluation", heading_style))
    story.append(Paragraph(
        f"<b>Agent Name:</b> {evaluation_data.get('agent_name', 'Unknown')}",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Summary box
    story.append(Paragraph("Evaluation Summary", heading_style))

    summary_data = [
        ['Metric', 'Value'],
        ['Total Tests Run', str(evaluation_data.get('total_tests', 0))],
        ['Tests Passed', str(evaluation_data.get('passed', 0))],
        ['Tests Failed', str(evaluation_data.get('failed', 0))],
        ['Safety Score', f"{score}/100"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # Safety score visual
    story.append(Paragraph(f"{score}/100", score_style))
    if score >= 75:
        verdict = "✅ SAFE — Agent passed most reliability checks"
    elif score >= 50:
        verdict = "⚠️ MODERATE RISK — Agent requires attention before deployment"
    else:
        verdict = "🚨 HIGH RISK — Agent should NOT be deployed without fixes"

    verdict_style = ParagraphStyle(
        'Verdict',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        textColor=score_color,
        spaceAfter=12
    )
    story.append(Paragraph(verdict, verdict_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))

    # Failure details
    failures = evaluation_data.get('failures', [])
    if failures:
        story.append(Paragraph("Failure Analysis", heading_style))
        story.append(Paragraph(
            f"{len(failures)} failure(s) detected across {evaluation_data.get('total_tests', 0)} test cases.",
            body_style
        ))
        story.append(Spacer(1, 8))

        for i, failure in enumerate(failures):
            # Failure header
            story.append(Paragraph(
                f"{i+1}. {failure.get('test_name', 'Unknown')}",
                ParagraphStyle(
                    'FailureTitle',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#1a1a2e'),
                    fontName='Helvetica-Bold',
                    spaceBefore=10,
                    spaceAfter=4
                )
            ))

            # Failure metadata table
            meta_data = [
                ['Failure Type', 'Severity', 'Severity Score', 'Confirmed'],
                [
                    failure.get('failure_type', '-'),
                    failure.get('severity', '-'),
                    f"{failure.get('severity_score', 0)}/100",
                    'Yes' if failure.get('failure_confirmed') else 'No'
                ]
            ]

            meta_table = Table(meta_data, colWidths=[1.8*inch, 1.2*inch, 1.4*inch, 1.2*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 6))

            # Explanation
            story.append(Paragraph(
                f"<b>What happened:</b> {failure.get('explanation', '')}",
                small_style
            ))

            # Recommendation
            story.append(Paragraph(
                f"<b>Recommendation:</b> {failure.get('recommendation', '')}",
                small_style
            ))

            # Trace
            trace = failure.get('trace', [])
            if trace:
                story.append(Spacer(1, 4))
                story.append(Paragraph("<b>Execution Trace:</b>", small_style))
                for step in trace:
                    trace_text = (
                        f"Step {step.get('step')} | "
                        f"Tool: {step.get('tool')} | "
                        f"Input: {str(step.get('input', ''))[:60]}... | "
                        f"Output: {str(step.get('output', ''))[:60]}..."
                    )
                    story.append(Paragraph(
                        trace_text,
                        ParagraphStyle(
                            'Trace',
                            parent=styles['Code'],
                            fontSize=8,
                            textColor=colors.HexColor('#444444'),
                            backColor=colors.HexColor('#f8f8f8'),
                            spaceAfter=2,
                            leftIndent=12,
                            leading=11
                        )
                    ))

            story.append(Spacer(1, 8))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Generated by AgentGuard — AI Agent Reliability Engine | Confidential",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()