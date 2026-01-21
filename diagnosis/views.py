from django.shortcuts import render, redirect
from .models import PatientScan
from .ml_logic import analyze_fmri
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

@login_required
def dashboard(request):
    scans = PatientScan.objects.all().order_by('-uploaded_at')
    total_scans = scans.count()
    pd_count = scans.filter(prediction="Parkinson's Disease").count()
    
    context = {
        'scans': scans,
        'total_scans': total_scans,
        'pd_count': pd_count,
    }
    return render(request, 'diagnosis/dashboard.html', context)

@login_required
def methodology(request):
    return render(request, 'diagnosis/methodology.html')

@login_required
def upload_scan(request):
    if request.method == 'POST' and request.FILES.get('scan_file'):
        p_id = request.POST.get('patient_id')
        age = request.POST.get('age')
        myfile = request.FILES['scan_file']

        # Salvare inițială pentru a obține calea fișierului
        scan = PatientScan.objects.create(patient_id=p_id, age=age, scan_file=myfile)
        
        # Analiză (aici se vor încărca nilearn/sklearn pentru prima dată)
        pred, conf = analyze_fmri(scan.scan_file.path)
        
        # Salvare rezultate
        scan.prediction = pred
        scan.confidence = conf
        scan.save()

        return render(request, 'diagnosis/result.html', {'scan': scan})

    return render(request, 'diagnosis/upload.html')

@login_required
def view_result(request, scan_id):
    scan = PatientScan.objects.get(id=scan_id)
    return render(request, 'diagnosis/result.html', {'scan': scan})

@login_required
def generate_pdf(request, scan_id):
    scan = PatientScan.objects.get(id=scan_id)
    template_path = 'diagnosis/pdf_layout.html' # Asigură-te că acest fișier există
    context = {'scan': scan}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Report_{scan.patient_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Eroare la generarea PDF-ului.')
    return response