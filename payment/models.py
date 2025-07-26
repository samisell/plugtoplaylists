from django.db import models
from django.conf import settings

class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in Naira
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ₦{self.price}"

    class Meta:
        ordering = ['price']
        verbose_name = "Package"
        verbose_name_plural = "Packages"
