from django.shortcuts import render, redirect
from .models import PatientScan
from .ml_logic import analyze_fmri
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.forms import UserCreationForm
from .cloud_utils import save_scan_to_cloud
from django.contrib import messages

@login_required
def dashboard(request):
    """
    Displays the clinical dashboard with all processed scans.
    """
    scans = PatientScan.objects.all().order_by('-created_at')
    
    total_scans = scans.count()
    pd_cases = scans.filter(prediction="Parkinson's Disease").count()
    healthy_cases = scans.filter(prediction="Healthy Control").count()

    context = {
        'scans': scans,
        'total_scans': total_scans,
        'pd_cases': pd_cases,
        'healthy_cases': healthy_cases,
    }
    
    return render(request, 'diagnosis/dashboard.html', context)

@login_required
def methodology(request):
    """
    Displays the scientific methodology page.
    """
    return render(request, 'diagnosis/methodology.html')

# diagnosis/views.py

@login_required
def upload_scan(request):
    """
    Handles file upload, AI analysis, and Cloud Synchronization.
    """
    if request.method == 'POST' and request.FILES.get('scan_file'):
        p_id = request.POST.get('patient_id')
        age = request.POST.get('age')
        myfile = request.FILES['scan_file']

        # 1. Save to Local Database
        scan = PatientScan.objects.create(
            patient_id=p_id, 
            age=age, 
            scan_file=myfile,
            doctor=request.user
        )
        
        # 2. Run Neuro-Scientific Analysis
        pred, conf, viewer_filename = analyze_fmri(scan.scan_file.path)
        
        scan.prediction = pred
        scan.confidence = conf
        scan.save()

        # 3. FIXED: Smart URL generation (Prevents double '_viewer_viewer')
        base_url = scan.scan_file.url
        if base_url.endswith('.nii.gz'):
            # Strip extension and potential existing suffix
            clean_url = base_url[:-7] # remove .nii.gz
            if clean_url.endswith('_viewer'):
                clean_url = clean_url[:-7] # remove _viewer
            viewer_url = f"{clean_url}_viewer.nii.gz"
        else:
            # Fallback for non-compressed .nii
            viewer_url = base_url.replace('.nii', '_viewer.nii')

        # 4. Synchronize with Cloud
        cloud_payload = {
            'patient_id': p_id,
            'prediction': pred,
            'confidence': conf,
            'age': int(age) if age else 0,
            'doctor_username': request.user.username
        }
        
        save_scan_to_cloud(request.user.id, cloud_payload)
        
        messages.success(request, "Analysis completed and synced to Cloud.")
        
        return render(request, 'diagnosis/result.html', {
            'scan': scan, 
            'viewer_url': viewer_url
        })

    return render(request, 'diagnosis/upload.html')

@login_required
def view_result(request, scan_id):
    """
    Displays the result of a specific previous scan.
    """
    scan = PatientScan.objects.get(id=scan_id)
    
    # FIXED: Same smart logic here
    base_url = scan.scan_file.url
    if base_url.endswith('.nii.gz'):
        clean_url = base_url[:-7]
        if clean_url.endswith('_viewer'):
            clean_url = clean_url[:-7]
        viewer_url = f"{clean_url}_viewer.nii.gz"
    else:
        viewer_url = base_url.replace('.nii', '_viewer.nii')
        
    return render(request, 'diagnosis/result.html', {'scan': scan, 'viewer_url': viewer_url})

@login_required
def generate_pdf(request, scan_id):
    """
    Generates a professional clinical PDF report.
    """
    scan = PatientScan.objects.get(id=scan_id)
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
    """
    Handles new user registration.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. You can now login.")
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})