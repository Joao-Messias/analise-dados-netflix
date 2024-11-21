from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect
import pandas as pd
import matplotlib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from netflix import settings

matplotlib.use('Agg')  # Para renderização sem interface gráfica
import matplotlib.pyplot as plt
import io
import base64

# Tradução dos dias da semana e meses para português
days_translation = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}

months_translation = {
    "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril",
    "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto",
    "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
}

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']

        # Definir o caminho para salvar os arquivos na pasta "datasets"
        fs = FileSystemStorage(location=settings.DATASET_ROOT)
        filename = fs.save(file.name, file)
        uploaded_file_path = fs.path(filename)

        try:
            # Carregar o arquivo CSV
            uploaded_df = pd.read_csv(uploaded_file_path)

            # Armazenar o dataset no session como JSON
            request.session['uploaded_data'] = uploaded_df.to_json()

            # Redirecionar para o dashboard
            return redirect('analysis:analysis_dashboard')
        except Exception as e:
            return JsonResponse({'error': f'Erro ao processar o arquivo: {str(e)}'})

    return render(request, 'analysis/upload_file.html')

def analysis_dashboard(request):
    # Recuperar os dados carregados do session
    uploaded_data = request.session.get('uploaded_data')
    if not uploaded_data:
        return redirect('analysis:upload_file')

    # Reconstruir DataFrame
    df = pd.read_json(uploaded_data)

    # Convertendo a coluna de data
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['Day of Week'] = df['Start Time'].dt.day_name().map(days_translation)
    df['Month'] = df['Start Time'].dt.month_name().map(months_translation)

    # Identificar filmes e séries
    df['Is Movie'] = df['Title'].apply(lambda x: ':' not in x)

    # Filtrar métricas de interesse para machine learning
    profiles = df['Profile Name'].unique()
    profile_metrics = []

    for profile in profiles:
        profile_data = df[df['Profile Name'] == profile]
        total_sessions = len(profile_data)
        total_time = pd.to_timedelta(profile_data['Duration']).sum().total_seconds() / 3600  # em horas

        # Contagem de dispositivos únicos usados por perfil
        unique_devices = profile_data['Device Type'].nunique()

        # Agregando as métricas
        profile_metrics.append([total_sessions, total_time, unique_devices])

    # Converter os dados para um DataFrame
    metrics_df = pd.DataFrame(profile_metrics, columns=['Total Sessions', 'Total Time', 'Unique Devices'])
    metrics_df['Profile Name'] = profiles

    # Pré-processar os dados para o modelo K-Means
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(metrics_df[['Total Sessions', 'Total Time', 'Unique Devices']])

    # Aplicar K-Means para agrupar perfis semelhantes
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    # Adicionar o cluster ao DataFrame de métricas
    metrics_df['Cluster'] = clusters

    # Informações para o contexto do template
    cluster_info = metrics_df.groupby('Cluster')['Profile Name'].apply(list).to_dict()

    # Análises detalhadas por perfil
    movies_by_profile = {}
    days_by_profile = {}
    months_by_profile = {}
    devices_by_profile = {}

    for profile in profiles:
        profile_data = df[df['Profile Name'] == profile]

        # Filmes mais assistidos por perfil
        top_movies = profile_data[profile_data['Is Movie']]['Title'].value_counts().head(5)
        movies_by_profile[profile] = top_movies.to_dict()

        # Dias mais assistidos por perfil
        days_freq = profile_data['Day of Week'].value_counts().head(7)
        days_by_profile[profile] = days_freq.to_dict()

        # Meses mais assistidos por perfil
        months_freq = profile_data['Month'].value_counts().head(12)
        months_by_profile[profile] = months_freq.to_dict()

        # Dispositivos mais utilizados por perfil
        top_devices = profile_data['Device Type'].value_counts().head(3)
        devices_by_profile[profile] = top_devices.to_dict()

    # Métricas gerais
    most_active_profile = df['Profile Name'].value_counts().idxmax()
    most_popular_movie = df[df['Is Movie']]['Title'].value_counts().idxmax()
    series = df[~df['Is Movie']]
    series['Base Title'] = series['Title'].apply(lambda x: x.split(':')[0].strip())
    top_series = series['Base Title'].value_counts().head(10)
    most_popular_series = top_series.idxmax()

    # Gerar gráficos
    charts = {}

    # 1. Total de Sessões por Perfil
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_df.set_index('Profile Name')['Total Sessions'].plot(kind='bar', ax=ax, title="Total de Sessões por Perfil")
    ax.set_ylabel("Total de Sessões")
    ax.set_xlabel("Perfis")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    charts['chart_sessions_profile'] = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # 2. Tempo Total Assistido por Perfil
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_df.set_index('Profile Name')['Total Time'].plot(kind='bar', ax=ax, title="Tempo Total Assistido por Perfil (Horas)")
    ax.set_ylabel("Tempo Total (Horas)")
    ax.set_xlabel("Perfis")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    charts['chart_time_profile'] = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # 3. Filmes Mais Assistidos por Perfil
    for profile, movies in movies_by_profile.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        pd.Series(movies).plot(kind='bar', ax=ax, title=f"Filmes Mais Assistidos ({profile})")
        ax.set_ylabel("Frequência")
        ax.set_xlabel("Filmes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        charts[f'chart_movies_{profile}'] = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

    # 4. Dias da Semana Mais Assistidos por Perfil
    for profile, days in days_by_profile.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        pd.Series(days).plot(kind='bar', ax=ax, title=f"Dias da Semana Mais Assistidos ({profile})")
        ax.set_ylabel("Frequência")
        ax.set_xlabel("Dias da Semana")
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        charts[f'chart_days_{profile}'] = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

    # 5. Meses Mais Assistidos por Perfil
    for profile, months in months_by_profile.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        pd.Series(months).plot(kind='bar', ax=ax, title=f"Meses Mais Assistidos ({profile})")
        ax.set_ylabel("Frequência")
        ax.set_xlabel("Meses")
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        charts[f'chart_months_{profile}'] = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

    # Contexto para o template
    context = {
        'charts': charts,
        'most_active_profile': most_active_profile,
        'most_popular_movie': most_popular_movie,
        'most_popular_series': most_popular_series,
        'cluster_info': cluster_info,
        'movies_by_profile': movies_by_profile,
        'days_by_profile': days_by_profile,
        'months_by_profile': months_by_profile,
        'devices_by_profile': devices_by_profile,
    }

    return render(request, 'analysis/dashboard.html', context)
