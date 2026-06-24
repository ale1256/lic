from django.contrib import admin
from .models import PatientScan

@admin.register(PatientScan)
class PatientScanAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'age', 'prediction', 'confidence', 'created_at', 'doctor')
    
    list_filter = ('prediction', 'created_at')
    
    search_fields = ('patient_id', 'prediction')
    
    list_editable = ('age',)