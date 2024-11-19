from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect
import pandas as pd
import matplotlib

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
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day of Week'] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month_name()

    # Identificar filmes e séries
    df['Is Movie'] = df['Title'].apply(lambda x: ':' not in x)  # Separa filmes (sem ':')

    # Análises:
    # Dias mais assistidos
    day_freq = df['Day of Week'].value_counts()
    day_freq.index = day_freq.index.map(days_translation)  # Tradução para português

    # Meses mais assistidos
    month_freq = df['Month'].value_counts()
    month_freq.index = month_freq.index.map(months_translation)  # Tradução para português

    # Filmes mais assistidos
    top_movies = df[df['Is Movie']]['Title'].value_counts().head(10)

    # Séries mais assistidas (somar episódios)
    series = df[~df['Is Movie']]
    series['Base Title'] = series['Title'].apply(lambda x: x.split(':')[0].strip())  # Título base da série
    top_series = series['Base Title'].value_counts().head(10)

    # Gerar gráficos
    # 1. Dias mais assistidos
    fig, ax = plt.subplots(figsize=(10, 6))
    day_freq.plot(kind='bar', ax=ax, title="Dias Mais Assistidos")
    ax.set_ylabel("Frequência")
    ax.set_xlabel("Dias da Semana")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_day = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # 2. Frequência por mês
    fig, ax = plt.subplots(figsize=(10, 6))
    month_freq.plot(kind='bar', ax=ax, title="Frequência por Mês")
    ax.set_ylabel("Frequência")
    ax.set_xlabel("Meses")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_month = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Contexto para o template
    context = {
        'chart_day': chart_day,
        'chart_month': chart_month,
        'top_movies': top_movies.to_dict(),
        'top_series': top_series.to_dict(),
    }
    return render(request, 'analysis/dashboard.html', context)
