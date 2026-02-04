from django.contrib import admin
from .models import PatientScan

@admin.register(PatientScan)
class PatientScanAdmin(admin.ModelAdmin):
    # Coloanele care vor apărea în tabelul de administrare
    list_display = ('patient_id', 'age', 'prediction', 'confidence', 'created_at', 'doctor')
    
    # Filtre pentru a găsi rapid datele
    list_filter = ('prediction', 'created_at')
    
    # Câmpuri după care poți căuta
    search_fields = ('patient_id', 'prediction')
    
    # Permitem editarea rapidă a vârstei direct din listă
    list_editable = ('age',)