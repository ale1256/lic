import os
import csv
from django.shortcuts import render, redirect, get_object_or_404
from .models import PatientScan
from .ml_logic import analyze_fmri, generate_viewer_volume
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.forms import UserCreationForm
from .cloud_utils import save_scan_to_cloud
from django.contrib import messages
from django.core.files import File

@login_required
def dashboard(request):
    """
    Displays the clinical dashboard with all processed scans.
    """
    query = request.GET.get('q', '').strip()
    scans = PatientScan.objects.filter(doctor=request.user)
    if query:
        scans = scans.filter(patient_id__icontains=query)
    scans = scans.order_by('-created_at')
    
    total_scans = scans.count()
    pd_cases = scans.filter(prediction="Parkinson's Disease").count()
    healthy_cases = scans.filter(prediction="Healthy Control").count()
    
    avg_conf = 0
    if total_scans > 0:
        total_conf = sum([s.confidence for s in scans if s.confidence])
        avg_conf = round(total_conf / total_scans, 1)

    context = {
        'scans': scans,
        'total_scans': total_scans,
        'pd_cases': pd_cases,
        'healthy_cases': healthy_cases,
        'accuracy': f"{avg_conf}%",
        'query': query
    }
    
    return render(request, 'diagnosis/dashboard.html', context)

@login_required
def methodology(request):
    """
    Displays the scientific methodology page.
    """
    return render(request, 'diagnosis/methodology.html')

@login_required
def help_page(request):
    """
    Displays the interactive help page.
    """
    return render(request, 'diagnosis/help.html')

@login_required
def pacs_viewer(request):
    """
    Displays the embedded PACS viewer (OHIF).
    """
    viewer_url = getattr(settings, "OHIF_VIEWER_URL", "http://localhost:3000")
    return render(request, 'diagnosis/pacs_viewer.html', {
        'viewer_url': viewer_url
    })

@login_required
def upload_scan(request):
    if request.method == 'POST' and request.FILES.get('scan_file'):
        p_id = request.POST.get('patient_id')
        age = request.POST.get('age')
        myfile = request.FILES['scan_file']
        t1_file = request.FILES.get('t1_file')

        scan = PatientScan.objects.create(
            patient_id=p_id, 
            age=age, 
            scan_file=myfile,
            doctor=request.user
        )
        
        pred, conf, viewer_filename, stage, matrix_filename = analyze_fmri(scan.scan_file.path)
        used_structural_for_viewer = False
        
        scan.prediction = pred
        scan.confidence = conf
        scan.severity_stage = stage

        if not viewer_filename:
            base_name = os.path.basename(scan.scan_file.name)
            clean_name = base_name.replace('.nii.gz', '').replace('.nii', '')
            viewer_filename = f"{clean_name}_viewer.nii.gz"

        if t1_file and viewer_filename:
            scan_dir = os.path.dirname(scan.scan_file.path)
            source_name = t1_file.name.lower()
            if source_name.endswith('.nii.gz'):
                t1_ext = '.nii.gz'
            elif source_name.endswith('.nii'):
                t1_ext = '.nii'
            else:
                t1_ext = '.nii.gz'

            temp_t1_path = os.path.join(scan_dir, f"_t1_source_{scan.id}{t1_ext}")
            target_viewer_path = os.path.join(scan_dir, viewer_filename)
            try:
                with open(temp_t1_path, 'wb+') as destination:
                    for chunk in t1_file.chunks():
                        destination.write(chunk)
                generate_viewer_volume(temp_t1_path, target_viewer_path)
                used_structural_for_viewer = True
            except Exception:
                messages.warning(
                    request,
                    "T1 structural file could not be processed. Falling back to fMRI-based viewer."
                )
            finally:
                if os.path.exists(temp_t1_path):
                    os.remove(temp_t1_path)
        
        if matrix_filename:
            temp_matrix_path = os.path.join(os.path.dirname(scan.scan_file.path), matrix_filename)
            if os.path.exists(temp_matrix_path):
                with open(temp_matrix_path, 'rb') as f:
                    scan.matrix_image.save(matrix_filename, File(f), save=True)

        scan.save()

        base_name = os.path.basename(scan.scan_file.name)
        clean_name = base_name.replace('.nii.gz', '').replace('.nii', '')
        
        scan_dir_url = os.path.dirname(scan.scan_file.url)
        viewer_url = f"{scan_dir_url}/{clean_name}_viewer.nii.gz"

        cloud_payload = {
            'patient_id': p_id,
            'prediction': pred,
            'confidence': conf,
            'severity': stage,
            'age': int(age) if age else 0,
            'doctor_username': request.user.username
        }
        save_scan_to_cloud(request.user.id, cloud_payload)
        
        if pred == "Unsupported Modality":
            messages.warning(request, "Fișierul nu pare fMRI 4D; analiza ML a fost sărită. Viewer-ul rămâne disponibil.")
        elif pred == "Analysis Error":
            messages.error(request, "Analiza ML a eșuat. Verifică formatul fișierului și încearcă din nou.")
        elif pred == "Model Missing":
            messages.warning(request, "Modelul ML nu este disponibil. Viewer-ul este generat, dar fără predicție.")

        if used_structural_for_viewer:
            messages.success(request, "Analysis completed. Viewer is generated from structural T1.")
        else:
            messages.success(request, "Analysis completed.")
        
        return render(request, 'diagnosis/result.html', {
            'scan': scan, 
            'viewer_url': viewer_url
        })

    return render(request, 'diagnosis/upload.html')

@login_required
def view_result(request, scan_id):
    scan = get_object_or_404(PatientScan, id=scan_id, doctor=request.user)
    
    base_name = os.path.basename(scan.scan_file.name)
    clean_name = base_name.replace('.nii.gz', '').replace('.nii', '')
    
    scan_dir_url = os.path.dirname(scan.scan_file.url)
    viewer_url = f"{scan_dir_url}/{clean_name}_viewer.nii.gz"
        
    return render(request, 'diagnosis/result.html', {'scan': scan, 'viewer_url': viewer_url})

@login_required
def export_data(request):
    """
    Exports patient data to CSV format for Excel.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="NeuroDetect_Patients.csv"'

    writer = csv.writer(response)
    writer.writerow(['Patient ID', 'Age', 'Diagnosis', 'Confidence (%)', 'Severity Stage', 'Scan Date', 'Doctor'])

    scans = PatientScan.objects.filter(doctor=request.user).order_by('-created_at')
    for scan in scans:
        writer.writerow([
            scan.patient_id,
            scan.age,
            scan.prediction,
            scan.confidence,
            scan.severity_stage,
            scan.created_at.strftime("%Y-%m-%d"),
            scan.doctor.username
        ])

    return response

@login_required
def generate_pdf(request, scan_id):
    """
    Generates a professional clinical PDF report.
    """
    scan = get_object_or_404(PatientScan, id=scan_id, doctor=request.user)
    template_path = 'diagnosis/pdf_layout.html'
    context = {'scan': scan}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="NeuroDetect_Report_{scan.patient_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF report.')
    return response

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. You can now login.")
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
