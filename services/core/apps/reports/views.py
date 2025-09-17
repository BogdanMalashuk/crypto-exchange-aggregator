from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Report
from .serializers import ReportCreateSerializer, SendEmailSerializer
from .tasks import generate_report, send_report_email


class ReportViewSet(viewsets.ViewSet):
    def create(self, request):
        """
        POST /reports/ — запросить отчет
        """
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        generate_report.delay(report.id)

        return Response(
            {"id": report.id, "format": report.format},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """
        GET /reports/{id}/download — получить ссылку на отчет
        """
        report = get_object_or_404(Report, pk=pk)
        if not report.is_ready:
            return Response(
                {"status": "pending", "message": "Report is not ready yet"},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            {"id": report.id, "file_url": report.file_url},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="send-email")
    def send_email(self, request, pk=None):
        """
        POST /reports/{id}/send-email — отправить отчет на почту
        """
        report = get_object_or_404(Report, pk=pk)
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if not report.is_ready:
            return Response(
                {"status": "pending", "message": "Report is not ready yet"},
                status=status.HTTP_202_ACCEPTED,
            )

        send_report_email.delay(report.id, email)
        return Response(
            {"status": "queued", "report_id": report.id, "email": email},
            status=status.HTTP_200_OK,
        )
