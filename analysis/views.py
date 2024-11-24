import json
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
import logging

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from netflix import settings
from .services.file_handler import FileHandler
from .services.data_cleaner import DataCleaner
from .services.metrics_handler import MetricsHandler
from .services.ml_model_handler import MLModelHandler

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
    Página de dashboard com análises gráficas filtradas.
    """
    uploaded_data = request.session.get('uploaded_data')
    if not uploaded_data:
        return redirect('analysis:upload_file')

    # Converte o JSON de volta para um DataFrame
    df = pd.read_json(uploaded_data)

    # Gera a lista completa de usuários e anos antes de aplicar os filtros
    user_list = df['Profile_Name'].unique() if 'Profile_Name' in df.columns else []
    if 'Start_Time' in df.columns:
        df['Start_Time'] = pd.to_datetime(df['Start_Time'], errors='coerce')
        df['Year'] = df['Start_Time'].dt.year  # Adiciona a coluna para o ano
    year_list = df['Year'].unique() if 'Year' in df.columns else []

    # Recebe os filtros do request
    selected_user = request.GET.get('user')  # Filtro de usuário
    selected_year = request.GET.get('year')  # Filtro de ano

    # Aplica o filtro de usuário, se fornecido
    if selected_user and 'Profile_Name' in df.columns:
        df = df[df['Profile_Name'] == selected_user]

    # Aplica o filtro de ano, se fornecido
    if selected_year:
        df = df[df['Year'] == int(selected_year)]

    # Calcula as métricas
    total_sessions = MetricsHandler.total_sessions(df)
    total_time = MetricsHandler.total_time_consumed(df)
    ranking_by_hours = MetricsHandler.activity_ranking_by_hours(df).head(5)  # Top 5
    top_5_titles = MetricsHandler.top_5_titles_by_duration(df)

    # Gera o gráfico de tempo médio por dia da semana
    buffer = io.BytesIO()
    try:
        # Calcular o tempo médio por dia da semana
        grouped = df.groupby('Day_of_Week')['Duration'].apply(
            lambda x: pd.to_timedelta(x).sum().total_seconds() / 3600 / len(x)
        ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

        # Criar o gráfico
        plt.figure(figsize=(10, 6))
        plt.bar(grouped.index, grouped.values, color='skyblue')
        plt.xlabel('Dia da Semana')
        plt.ylabel('Tempo Médio de Uso (Horas)')
        plt.title('Tempo Médio de Uso por Dia da Semana')
        plt.tight_layout()

        # Salvar o gráfico como imagem em base64
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        average_usage_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()
    except Exception as e:
        logger.error(f"Erro ao gerar o gráfico: {e}")
        average_usage_chart = None

    # Gera gráficos adicionais
    time_spent_chart = MetricsHandler.generate_time_spent_by_title_chart(df)
    monthly_activity_chart = MetricsHandler.generate_monthly_activity_chart(df)
    movie_vs_series_chart = MetricsHandler.generate_movie_vs_series_chart(df)
    monthly_activity_user_chart = MetricsHandler.generate_monthly_activity_per_user_chart(df)

    # Passa os dados e os gráficos para o contexto
    context = {
        'data_summary': df.describe().to_html(classes="table table-striped"),
        'total_sessions': total_sessions,
        'total_time': total_time,
        'ranking_by_hours': ranking_by_hours.to_dict(orient='records'),
        'top_5_titles': top_5_titles.to_dict(orient='records'),
        'movie_vs_series_chart': movie_vs_series_chart,
        'graph_time_spent_chart': time_spent_chart,
        'monthly_activity_chart': monthly_activity_chart,
        'average_usage_chart': average_usage_chart,
        'monthly_activity_user_chart': monthly_activity_user_chart,
        'user_list': user_list,  # Lista de usuários para o filtro
        'year_list': year_list,  # Lista de anos para o filtro
        'selected_user': selected_user,  # Usuário selecionado
        'selected_year': selected_year,  # Ano selecionado
    }

    return render(request, 'analysis/dashboard.html', context)

def ml_analysis(request):
    uploaded_data = request.session.get('uploaded_data')
    if not uploaded_data:
        return redirect('analysis:upload_file')

    # Carregar os dados preprocessados
    df = pd.read_json(uploaded_data)
    sessions = MetricsHandler.preprocess_sessions(df, max_gap_minutes=30)

    context = {'columns': df.columns}

    if request.method == 'POST':
        # Recuperar as configurações do formulário
        model_type = request.POST.get('model_type')
        max_depth = request.POST.get('max_depth', None)
        n_neighbors = request.POST.get('n_neighbors', None)

        # Lista de modelos válidos
        valid_models = ['linear_regression', 'random_forest', 'decision_tree', 'knn']

        if model_type not in valid_models:
            context['error'] = f"Modelo '{model_type}' não é válido. Escolha entre: {', '.join(valid_models)}"
            return render(request, 'analysis/ml_dashboard.html', context)

        # Parâmetros do modelo
        params = {}
        if model_type in ['random_forest', 'decision_tree'] and max_depth:
            params['max_depth'] = int(max_depth)
        if model_type == 'knn' and n_neighbors:
            params['n_neighbors'] = int(n_neighbors)

        try:
            # Treinar o modelo
            result = MLModelHandler.train_watch_duration_model(sessions, model_type=model_type, **params)

            # Predizer horas por perfil
            profile_predictions = MLModelHandler.predict_watch_time_by_profile(sessions, result['model'])

            # Gerar gráfico de predição por perfil
            profile_chart = MLModelHandler.generate_profile_prediction_chart(profile_predictions)

            # Adicionar os resultados ao contexto
            context.update({
                'mse': result['mse'],
                'profile_chart': profile_chart,
            })
        except Exception as e:
            context['error'] = f"Ocorreu um erro ao treinar o modelo: {str(e)}"

    return render(request, 'analysis/ml_dashboard.html', context)
