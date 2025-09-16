from django.db import models
from apps.users.models import User


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    file_url = models.CharField(max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id} ({self.format}, {self.status})"

    @property
    def is_ready(self):
        return self.status == self.Status.READY
