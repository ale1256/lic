"""
URL configuration for pd_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from diagnosis import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('diagnosis.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/login/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'), 
    path('upload/', views.upload_scan, name='upload'),
    path('methodology/', views.methodology, name='methodology'),
    path('report/<int:scan_id>/', views.generate_pdf, name='generate_pdf'),
    path('result/<int:scan_id>/', views.view_result, name='view_result'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    