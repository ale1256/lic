from django.db import models
from django.contrib.auth.models import User

class PatientScan(models.Model):
    patient_id = models.CharField(max_length=50)
    age = models.IntegerField()
    scan_file = models.FileField(upload_to='scans/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prediction = models.CharField(max_length=20, blank=True, null=True) #
    confidence = models.FloatField(blank=True, null=True) 

    def __str__(self):
        return f"Patient {self.patient_id} - {self.uploaded_at.strftime('%Y-%m-%d')}"


class PatientScan(models.Model):
    # Legăm scanarea de medicul care a urcat-o
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Datele pacientului
    patient_id = models.CharField(max_length=100)
    age = models.IntegerField()
    
    # Fișierul fMRI (se salvează în media/scans/)
    scan_file = models.FileField(upload_to='scans/')
    
    # Rezultatele analizei ML
    prediction = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    
    # Data la care a fost efectuată analiza
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.patient_id} - {self.prediction}"

    class Meta:
        ordering = ['-created_at'] # Cele mai noi analize apar primele