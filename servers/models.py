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


class ServerAgentMonitor(models.Model):
    server = models.OneToOneField(Server, on_delete=models.CASCADE, related_name='agent_monitor')
    agent_url = models.URLField(max_length=500)
    agent_auth_key = models.CharField(max_length=255)

    def __str__(self):
        return f"Agent Monitor - {self.server.name}"
