import base64
from io import BytesIO

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


class MLModelHandler:
    @staticmethod
    def train_watch_duration_model(data, model_type='linear_regression', **params):
        """
        Treina um modelo para prever a duração contínua de sessões de filmes/séries.

        :param data: DataFrame com os dados preprocessados.
        :param model_type: Tipo de modelo (linear_regression, random_forest, decision_tree, knn).
        :param params: Parâmetros do modelo.
        :return: Dicionário com modelo treinado e métricas.
        """
        # Selecionar variáveis independentes (features) e dependente (target)
        X = data[['Profile_Name', 'type']]
        y = data['Total_Hours']

        # Converter variáveis categóricas para valores numéricos
        X = pd.get_dummies(X, columns=['Profile_Name', 'type'])

        # Dividir os dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Escolher o modelo com base no tipo
        if model_type == 'linear_regression':
            model = LinearRegression()
        elif model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=100, max_depth=params.get('max_depth'))
        elif model_type == 'decision_tree':
            model = DecisionTreeRegressor(max_depth=params.get('max_depth'))
        elif model_type == 'knn':
            model = KNeighborsRegressor(n_neighbors=params.get('n_neighbors', 5))
        else:
            raise ValueError("Modelo não suportado!")

        # Treinar o modelo
        model.fit(X_train, y_train)

        # Fazer predições
        predictions = model.predict(X_test)

        # Calcular erro médio quadrático
        mse = mean_squared_error(y_test, predictions)

        return {
            'model': model,
            'mse': mse,
            'predictions': predictions,
            'test_data': X_test,
            'actual_values': y_test
        }

    @staticmethod
    def analyze_model_performance(data, predictions, mse):
        """
        Analisa a performance do modelo e calcula métricas adicionais, incluindo média e mediana.
        """
        analysis = {
            "mse": mse,
            "average_duration_by_type": {},
            "median_duration_by_type": {},
            "session_counts_by_type": {}
        }

        # Cálculo da duração média, mediana e contagem por tipo de conteúdo
        if "type" in data.columns and "Total_Hours" in data.columns:
            group = data.groupby("type")["Total_Hours"]
            analysis["average_duration_by_type"] = group.mean().to_dict()
            analysis["median_duration_by_type"] = group.median().to_dict()
            analysis["session_counts_by_type"] = data["type"].value_counts().to_dict()

        return analysis

    @staticmethod
    def generate_analysis_charts(data):
        """
        Gera gráficos para análise do modelo:
        - Boxplot para comparar a duração de séries e filmes.
        - Histograma para visualizar a distribuição da duração.
        """
        graphs = {}

        # Boxplot: Comparação de Duração por Tipo de Conteúdo
        plt.figure(figsize=(10, 6))
        data.boxplot(column="Total_Hours", by="type", grid=False, showmeans=True)
        plt.title("Boxplot: Duração por Tipo de Conteúdo")
        plt.suptitle("")  # Remove o título automático do pandas
        plt.xlabel("Tipo de Conteúdo")
        plt.ylabel("Duração (Horas)")
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        graphs["boxplot_duration"] = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close()

        # Histograma: Distribuição da Duração
        plt.figure(figsize=(10, 6))
        for content_type in data["type"].unique():
            subset = data[data["type"] == content_type]
            plt.hist(subset["Total_Hours"], bins=15, alpha=0.5, label=content_type, edgecolor="black")
        plt.title("Histograma: Distribuição da Duração por Tipo")
        plt.xlabel("Duração (Horas)")
        plt.ylabel("Frequência")
        plt.legend(title="Tipo de Conteúdo")
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        graphs["histogram_duration"] = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close()

        return graphs

    @staticmethod
    def predict_watch_time_by_profile(data, model):
        """
        Gera predições de duração para cada perfil com base no modelo.
        """
        # Criar cópias separadas para 'movie' e 'tv series'
        movie_data = data.copy()
        movie_data['type'] = 'movie'

        series_data = data.copy()
        series_data['type'] = 'tv series'

        # One-hot encode para filmes e séries
        movie_encoded = pd.get_dummies(movie_data, columns=['type', 'Profile_Name'])
        series_encoded = pd.get_dummies(series_data, columns=['type', 'Profile_Name'])

        # Ajustar colunas para garantir que ambos tenham as mesmas features do modelo
        required_columns = model.feature_names_in_
        movie_encoded = movie_encoded.reindex(columns=required_columns, fill_value=0)
        series_encoded = series_encoded.reindex(columns=required_columns, fill_value=0)

        # Predizer a duração para filmes e séries
        movie_predictions = model.predict(movie_encoded)
        series_predictions = model.predict(series_encoded)

        # Consolidar os resultados por perfil
        predictions = pd.DataFrame({
            'Profile_Name': data['Profile_Name'],
            'Predicted_Movie_Hours': movie_predictions,
            'Predicted_Series_Hours': series_predictions,
        })

        # Agrupar por perfil para prever o total esperado
        predictions = predictions.groupby('Profile_Name').mean().reset_index()
        return predictions

    @staticmethod
    def generate_profile_prediction_chart(predictions):
        """
        Gera um gráfico de barras para exibir as predições de horas assistidas por perfil.
        """
        plt.figure(figsize=(12, 8))

        # Ordenar por perfil para consistência
        predictions = predictions.sort_values(by='Profile_Name')

        # Configurar o gráfico
        bar_width = 0.35
        profiles = predictions['Profile_Name']
        x = np.arange(len(profiles))

        plt.bar(x - bar_width / 2, predictions['Predicted_Movie_Hours'], bar_width, label='Filmes', color='blue')
        plt.bar(x + bar_width / 2, predictions['Predicted_Series_Hours'], bar_width, label='Séries', color='orange')

        # Configurações dos eixos
        plt.xlabel('Perfil', fontsize=12)
        plt.ylabel('Horas Previstas', fontsize=12)
        plt.title('Predição de Horas de Visualização por Perfil', fontsize=14)
        plt.xticks(x, profiles, rotation=45, ha='right', fontsize=10)
        plt.legend(title='Tipo de Conteúdo', fontsize=10)
        plt.tight_layout()

        # Converter o gráfico em base64
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close()

        return chart_base64
