from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default="#3b82f6", help_text="Hex color or Tailwind color class")
    icon = models.CharField(max_length=50, default="fa-cube", help_text="FontAwesome icon class (e.g., fa-cube)")

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
