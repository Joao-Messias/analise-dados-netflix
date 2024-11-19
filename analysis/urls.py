from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.upload_file, name='upload_file'),  # Página principal do app
    path('dashboard/', views.analysis_dashboard, name='analysis_dashboard'),  # Dashboard de análises
]
