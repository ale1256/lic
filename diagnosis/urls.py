from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_scan, name='upload'),
    path('methodology/', views.methodology, name='methodology'),
    path('help/', views.help_page, name='help'),
    path('viewer/', views.pacs_viewer, name='pacs_viewer'),
    path('result/<int:scan_id>/', views.view_result, name='view_result'),
    path('report/<int:scan_id>/', views.generate_pdf, name='generate_pdf'),
    path('export/', views.export_data, name='export_data'),
]
