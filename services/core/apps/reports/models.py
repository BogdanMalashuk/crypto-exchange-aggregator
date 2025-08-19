from django.db import models
from users.models import Profile


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reports")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    params = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id} ({self.format}, {self.status})"
