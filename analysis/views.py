from django.shortcuts import render, redirect
from .forms import DatasetForm
import pandas as pd
from django.shortcuts import render
import matplotlib
matplotlib.use('Agg')  # Usa o backend 'Agg' para renderização sem interface gráfica
import matplotlib.pyplot as plt
import io
import base64


def upload_file(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save()
            # Processar o arquivo carregado
            file_path = dataset.file.path
            try:
                df = pd.read_csv(file_path)
                request.session['uploaded_data'] = df.to_json()  # Armazena o dataset
                return redirect('analysis:analysis_dashboard')
            except Exception as e:
                form.add_error('file', 'Erro ao processar o arquivo: ' + str(e))
    else:
        form = DatasetForm()
    return render(request, 'analysis/upload_file.html', {'form': form})


def analysis_dashboard(request):
    uploaded_data = request.session.get('uploaded_data')
    if not uploaded_data:
        return redirect('analysis:upload_file')

    # Reconstruir DataFrame
    df = pd.read_json(uploaded_data)

    # Gêneros Mais Populares
    genres = df['genres'].dropna().str.split(', ')
    genres_counts = genres.explode().value_counts()

    # Filmes mais votados
    top_movies = df[df['type'] == 'movie'].nlargest(10, 'imdbNumVotes')[['title', 'imdbAverageRating', 'imdbNumVotes']]

    # Séries mais votadas
    top_series = df[df['type'] == 'tv'].nlargest(10, 'imdbNumVotes')[['title', 'imdbAverageRating', 'imdbNumVotes']]

    # Geração do Gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    genres_counts.head(10).plot(kind='bar', ax=ax, title="Gêneros Mais Populares")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    context = {
        'chart': chart_data,
        'top_movies': top_movies.to_dict(orient='records'),
        'top_series': top_series.to_dict(orient='records'),
    }
    return render(request, 'analysis/dashboard.html', context)
