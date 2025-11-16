#from django.db import models
#
## Create your models here.
from django.db import models
from django.conf import settings

class Department(models.Model):
    hospital_id = models.PositiveIntegerField()  # Decoupled link to hospitals app
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    head_doctor_id = models.PositiveIntegerField(blank=True, null=True)  # reference to doctor
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, null=True) # URL to department image


    class Meta:
        unique_together = ("hospital_id", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (Hospital {self.hospital_id})"
