from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.upload_file, name='upload_file'),  # Página principal do app
    path('dashboard/', views.analysis_dashboard, name='analysis_dashboard'),  # Dashboard de análises

    path('ml-dashboard/', views.ml_analysis, name='ml_dashboard'),  # Dashboard de Machine Learning

]
