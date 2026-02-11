from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import fonts
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import HRFlowable
from datetime import datetime


def generate_ticket_pdf(booking: dict, file_path: str) -> None:
    """
    Generate train ticket PDF.
    """

    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # ----------------------------
    # Title
    # ----------------------------
    elements.append(Paragraph("Train Ticket Confirmation", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # ----------------------------
    # Booking Info Table
    # ----------------------------
    data = [
        ["Booking Code", booking["booking_code"]],
        ["Passenger", booking.get("username", "N/A")],
        ["Train", f'{booking["train_number"]} - {booking["train_name"]}'],
        ["Route", f'{booking["origin_station"]} → {booking["destination_station"]}'],
        ["Departure", f'{booking["departure_date"]} {booking["departure_time"]}'],
        ["Arrival", f'{booking["arrival_date"]} {booking["arrival_time"]}'],
        ["Fare Paid", f'₹{booking["fare"]}'],
        ["Booking Status", booking["booking_status"]],
        ["Payment Status", booking.get("payment_status", "N/A")],
        ["Transaction ID", booking.get("transaction_id", "N/A")],
        ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M")],
    ]

    table = Table(data, colWidths=[2.2 * inch, 3.5 * inch])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(HRFlowable(width="100%"))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(
        Paragraph(
            "Thank you for booking with TrainBookingSystem. "
            "Please carry this ticket during your journey.",
            normal_style,
        )
    )

    doc.build(elements)

import os
import platform
import subprocess


def open_file_auto(file_path: str) -> None:
    """
    Open a file automatically depending on OS.
    """

    try:
        system_name = platform.system()

        if system_name == "Windows":
            os.startfile(file_path)

        elif system_name == "Darwin":  # macOS
            subprocess.call(["open", file_path])

        elif system_name == "Linux":
            subprocess.call(["xdg-open", file_path])

    except Exception:
        # We silently fail here — UI will handle message
        raise
