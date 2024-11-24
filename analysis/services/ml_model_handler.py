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