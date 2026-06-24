from django.db import models
from django.contrib.auth.models import User

class PatientScan(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    patient_id = models.CharField(max_length=100)
    age = models.IntegerField()
    
    scan_file = models.FileField(upload_to='scans/')
    
    prediction = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    
    matrix_image = models.ImageField(upload_to='matrices/', blank=True, null=True)
    severity_stage = models.CharField(max_length=100, blank=True, default="N/A")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.patient_id} - {self.prediction}"

    class Meta:
        ordering = ['-created_at']