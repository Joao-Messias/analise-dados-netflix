import json

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from netflix import settings
from .services.file_handler import FileHandler
from .services.data_cleaner import DataCleaner
import logging
import pandas as pd

from .services.metrics_handler import MetricsHandler

logger = logging.getLogger(__name__)

def upload_file(request):
    """
    Página de upload do arquivo CSV.
    """
    context = {}
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']

        # Salva o arquivo na pasta datasets
        fs = FileSystemStorage(location=settings.DATASET_ROOT)
        filename = fs.save(file.name, file)
        uploaded_file_path = fs.path(filename)

        try:
            # Carrega o CSV e limpa os dados
            df = FileHandler.load_csv(uploaded_file_path)
            cleaned_df = DataCleaner.clean_data(df)

            # Salva os dados na sessão
            request.session['uploaded_data'] = cleaned_df.to_json()

            # Redireciona para o dashboard
            return redirect('analysis:analysis_dashboard')
        except Exception as e:
            logger.error(f"Erro ao processar o arquivo: {e}")
            context['error'] = "Ocorreu um erro ao processar o arquivo. Por favor, tente novamente."

    return render(request, 'analysis/upload_file.html', context)

def analysis_dashboard(request):
    """
    Página de dashboard com análises gráficas.
    """
    uploaded_data = request.session.get('uploaded_data')
    if not uploaded_data:
        return redirect('analysis:upload_file')

    # Converte o JSON de volta para um DataFrame
    df = pd.read_json(uploaded_data)

    # Calcula as métricas
    total_sessions = MetricsHandler.total_sessions(df)
    total_time = MetricsHandler.total_time_consumed(df)
    ranking_by_hours = MetricsHandler.activity_ranking_by_hours(df).head(5)  # Top 5

    # Faz análises ou processa os dados para gráficos
    context = {
        'data_summary': df.describe().to_html(classes="table table-striped"),
        'total_sessions': total_sessions,
        'total_time': total_time,
        'ranking_by_hours': ranking_by_hours.to_dict(orient='records'),  # Passar como lista de dicionários
    }

    return render(request, 'analysis/dashboard.html', context)