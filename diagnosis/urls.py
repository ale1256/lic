from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_scan, name='upload'),
    path('methodology/', views.methodology, name='methodology'),
    path('result/<int:scan_id>/', views.view_result, name='view_result'),
    path('report/<int:scan_id>/', views.generate_pdf, name='generate_pdf'),
]
