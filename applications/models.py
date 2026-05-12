from django.db import models
from django.utils.text import slugify
from categories.models import Category
from servers.models import Server

class Application(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='applications')
    
    logo_url = models.URLField(max_length=500, blank=True, help_text="URL to application logo")
    logo_image = models.ImageField(upload_to='logos/', blank=True, null=True)
    
    framework = models.CharField(max_length=100, blank=True, help_text="Backend/Framework (e.g., Django, Node.js)")
    database = models.CharField(max_length=100, blank=True)
    repository = models.URLField(max_length=500, blank=True, verbose_name="Git Repository")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    maintenance_notes = models.TextField(blank=True)
    deployment_notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def ordered_environments(self):
        return sorted(self.environments.all(), key=lambda item: item.environment_rank)

    @property
    def highest_environment(self):
        environments = self.ordered_environments
        if not environments:
            return None
        return environments[-1]

    @property
    def highest_environment_label(self):
        environment = self.highest_environment
        return environment.environment if environment else '-'


class ApplicationEnvironment(models.Model):
    ENV_CHOICES = [
        ('DEV', 'Development'),
        ('BETA', 'Beta/Staging'),
        ('PROD', 'Production'),
    ]
    ENV_ORDER = {
        'DEV': 1,
        'BETA': 2,
        'PROD': 3,
    }

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='environments')
    environment = models.CharField(max_length=10, choices=ENV_CHOICES)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, related_name='application_environments', blank=True)
    url = models.URLField(max_length=500, blank=True, verbose_name="Domain / URL")
    local_ip = models.CharField(max_length=100, blank=True, verbose_name="Local IP")
    port = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Status Aktif")
    deployment_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['application', 'environment']
        constraints = [
            models.UniqueConstraint(fields=['application', 'environment'], name='unique_application_environment')
        ]

    @property
    def environment_rank(self):
        return self.ENV_ORDER.get(self.environment, 0)

    def __str__(self):
        return f"{self.application.name} - {self.environment}"

class AppAdmin(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='admins')
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    role = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name="Nomor WhatsApp")
    access_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.application.name}"

class UpdateHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    date = models.DateField(auto_now_add=True)
    version = models.CharField(max_length=50, blank=True)
    notes = models.TextField()

    class Meta:
        verbose_name_plural = "Update Histories"
        ordering = ['-date']
