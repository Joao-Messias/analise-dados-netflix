import base64
import io
from io import BytesIO
from imblearn.over_sampling import SMOTE
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.metrics import mean_squared_error, classification_report, f1_score, recall_score, precision_score, \
    accuracy_score
from sklearn.model_selection import train_test_split


class MLModelHandler:
    @staticmethod
    def preprocess_data(data, target_type='movie'):
        """
        Prepara os dados para análise, ajustando o alvo (target) entre filmes e séries.
        """
        # Filtrar apenas filmes ou séries
        data = data[data['type'].isin(['movie', 'tv series'])]

        # Ajustar o target: dependendo de `target_type`, invertemos a lógica
        if target_type == 'movie':
            data['Target'] = data['type'].apply(lambda x: 1 if x == 'movie' else 0)
        elif target_type == 'series':
            data['Target'] = data['type'].apply(lambda x: 1 if x == 'tv series' else 0)
        else:
            raise ValueError("O parâmetro target_type deve ser 'movie' ou 'series'.")

        # Extrair a hora do dia de 'Start_Time'
        data['Hour'] = pd.to_datetime(data['Start_Time'], errors='coerce').dt.hour

        # Criar intervalos de horários
        bins = [0, 6, 12, 18, 24]
        labels = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
        data['Time Range'] = pd.cut(data['Hour'], bins=bins, labels=labels, right=False)

        return data.dropna(subset=['Hour', 'Target'])

    @staticmethod
    def train_model(data, model_type='random_forest', n_estimators=100, max_depth=None, 
                    penalty='l2', regularization_c=1.0, l1_ratio=None, target_type='movie'):
        """
        Treina um modelo para prever filmes ou séries, usando SMOTE para balancear os dados.
        """
        from imblearn.over_sampling import SMOTE

        # Pré-processar os dados
        processed_data = MLModelHandler.preprocess_data(data, target_type=target_type)

        # Separar features (X) e target (y)
        X = pd.get_dummies(processed_data[['Hour']], drop_first=True)
        y = processed_data['Target']

        # Aplicar SMOTE para balancear as classes
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)

        # Dividir em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

        # Selecionar e treinar o modelo
        if model_type == 'random_forest':
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        elif model_type == 'logistic_regression':
            if penalty == 'elasticnet' and l1_ratio is None:
                raise ValueError("l1_ratio deve ser especificado para a penalidade ElasticNet.")
            model = LogisticRegression(
                penalty=penalty,
                C=regularization_c,
                l1_ratio=l1_ratio if penalty == 'elasticnet' else None,
                solver='saga' if penalty in ['l1', 'elasticnet'] else 'lbfgs',
                max_iter=1000,
                random_state=42
            )
        else:
            raise ValueError("Modelo inválido. Escolha entre 'random_forest' ou 'logistic_regression'.")

        model.fit(X_train, y_train)

        # Adicionar probabilidades ao processed_data (opcional, para gráficos)
        X_processed = pd.get_dummies(processed_data[['Hour']], drop_first=True)
        processed_data['Probability'] = model.predict_proba(X_processed)[:, 1]

        return model, processed_data


    @staticmethod
    def generate_combined_probability_chart(data):
        """
        Gera um gráfico de probabilidade combinada para filmes e séries por intervalo de horário.
        """
        # Processar separadamente para filmes e séries
        _, movie_data = MLModelHandler.train_model(data, target_type='movie')
        _, series_data = MLModelHandler.train_model(data, target_type='series')

        # Agrupar por intervalo de horário e calcular as médias
        movie_probs = (
            movie_data.groupby('Time Range')['Probability']
            .mean()
            .reindex(['Madrugada', 'Manhã', 'Tarde', 'Noite'])
        )
        series_probs = (
            series_data.groupby('Time Range')['Probability']
            .mean()
            .reindex(['Madrugada', 'Manhã', 'Tarde', 'Noite'])
        )

        # Configurar os índices
        bar_width = 0.35
        x = np.arange(len(movie_probs.index))

        plt.figure(figsize=(12, 8))
        plt.bar(x - bar_width / 2, series_probs * 100, bar_width, color='blue', label='Séries')
        plt.bar(x + bar_width / 2, movie_probs * 100, bar_width, color='red', label='Filmes')

        # Adicionar títulos e rótulos
        plt.title("Probabilidade de Assistir a Filmes e Séries por Período de Horário", fontsize=16)
        plt.xlabel("Período de Horário", fontsize=12)
        plt.ylabel("Probabilidade Média (%)", fontsize=12)
        plt.xticks(x, movie_probs.index, rotation=45, ha='right')
        plt.legend(title="Tipo de Conteúdo")
        plt.tight_layout()

        # Salvar o gráfico como imagem em base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

        return chart