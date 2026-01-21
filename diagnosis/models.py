from django.db import models

class PatientScan(models.Model):
    patient_id = models.CharField(max_length=50)
    age = models.IntegerField()
    scan_file = models.FileField(upload_to='scans/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prediction = models.CharField(max_length=20, blank=True, null=True) #
    confidence = models.FloatField(blank=True, null=True) 

    def __str__(self):
        return f"Patient {self.patient_id} - {self.uploaded_at.strftime('%Y-%m-%d')}"