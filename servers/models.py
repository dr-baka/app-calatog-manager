from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=100)
    host_ip = models.CharField(max_length=100, verbose_name="Host/IP Server")
    username = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=100, verbose_name="Sistem Operasi", blank=True)
    provider = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    specs = models.TextField(verbose_name="Spesifikasi Server", blank=True)
    deployment_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.host_ip})"
