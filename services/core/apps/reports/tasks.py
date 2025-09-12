import io
import logging
from celery import shared_task
from django.conf import settings
from .models import Report
from apps.trades.models import Trade
from packages.common.s3.client import s3_client
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import openpyxl
from .kafka import send_kafka_event
from packages.common.kafka.events import ReportCompletedEvent

logger = logging.getLogger(__name__)


@shared_task
def generate_report(report_id: int):
    """
    Генерация отчёта (PDF/Excel) и загрузка в MinIO.
    """
    try:
        report = Report.objects.get(id=report_id)
        logger.info(f"Start generating report {report.id} ({report.format})")

        trades = Trade.objects.filter(user=report.profile)

        if report.format == Report.Format.PDF:
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            p.setFont("Helvetica", 12)
            p.drawString(100, 800, f"Report #{report.id} for {report.profile.user.username}")
            y = 760

            for trade in trades:
                line = f"{trade.symbol} | qty={trade.quantity} | buy={trade.buy_price}"
                if trade.sold and hasattr(trade, "sale"):
                    line += f" | sell={trade.sale.sell_price} | profit={trade.sale.profit}"
                else:
                    line += " | OPEN"
                p.drawString(100, y, line)
                y -= 20
                if y < 50:
                    p.showPage()
                    y = 800
            p.save()
            buffer.seek(0)
            file_bytes = buffer.getvalue()
            file_ext = "pdf"

        elif report.format == Report.Format.EXCEL:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Trades"
            ws.append(["Symbol", "Quantity", "Buy price", "Bought at", "Sold", "Sell price", "Profit"])

            for trade in trades:
                if trade.sold and hasattr(trade, "sale"):
                    ws.append([
                        trade.symbol,
                        float(trade.quantity),
                        float(trade.buy_price),
                        trade.bought_at.isoformat(),
                        "YES",
                        float(trade.sale.sell_price),
                        float(trade.sale.profit),
                    ])
                else:
                    ws.append([
                        trade.symbol,
                        float(trade.quantity),
                        float(trade.buy_price),
                        trade.bought_at.isoformat(),
                        "NO",
                        None,
                        None,
                    ])

            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            file_bytes = buffer.getvalue()
            file_ext = "xlsx"

        else:
            raise ValueError(f"Unsupported format: {report.format}")

        file_key = f"{report.profile.id}/{report.id}.{file_ext}"
        buffer = io.BytesIO(file_bytes)
        s3_client.upload_file(buffer, file_key)
        logger.info(f"Uploaded file to S3: key={file_key}")

        file_url = s3_client.get_file_url(file_key, expires_in=3600*24)

        report.status = Report.Status.READY
        report.file_url = file_url
        report.save(update_fields=["status", "file_url"])

        logger.info(f"Report {report.id} generated successfully")

        event = ReportCompletedEvent(
            report_id=report.id,
            profile_id=report.profile.id,
            format=report.format,
            status=report.status,
            file_url=report.file_url,
        )
        send_kafka_event("report.completed", event.to_dict())

        return {"status": "ok", "report_id": report.id, "url": file_url}

    except Exception as e:
        logger.exception(f"Failed to generate report {report_id}: {e}")
        Report.objects.filter(id=report_id).update(status=Report.Status.FAILED)
        return {"status": "error", "report_id": report_id, "error": str(e)}


@shared_task
def send_report_email(report_id: int, email: str):
    """
    Отправка отчёта на e-mail.
    """
    try:
        report = Report.objects.get(id=report_id)

        if not report.is_ready or not report.file_url:
            logger.warning(f"Report {report.id} is not ready, cannot send email")
            return {"status": "error", "message": "Report not ready"}

        subject = f"Your report #{report.id}"
        body = f"Hello!\n\nYour report is ready.\nDownload link: {report.file_url}\n\nRegards,\nCrypto Analytics System"

        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        message.send(fail_silently=False)

        logger.info(f"Report {report.id} sent to {email}")
        return {"status": "ok", "report_id": report.id, "email": email}

    except Exception as e:
        logger.exception(f"Failed to send report {report_id} to {email}: {e}")
        return {"status": "error", "report_id": report_id, "error": str(e)}
