import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Força o uso de um backend sem GUI
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
import calendar


class MetricsHandler:
    @staticmethod
    def total_sessions(data):
        """
        Retorna o total de sessões (linhas na base de dados).
        """
        return len(data)

    @staticmethod
    def total_time_consumed(data):
        """
        Retorna o tempo total consumido (em horas) somando a coluna de duração.
        """
        # Verifica se a coluna "Duration" existe e está no formato correto
        if 'Duration' in data.columns:
            try:
                # Converte a duração para timedelta
                data['Duration'] = pd.to_timedelta(data['Duration'])
                # Soma os tempos e converte para horas
                total_time = data['Duration'].sum().total_seconds() / 3600
                return round(total_time, 2)  # Arredondar para 2 casas decimais
            except Exception as e:
                raise ValueError(f"Erro ao calcular o tempo total consumido: {e}")
        else:
            raise ValueError("A coluna 'Duration' não foi encontrada na base de dados.")

    @staticmethod
    def activity_ranking_by_hours(data):
        """
        Retorna o ranking de perfis com base no tempo assistido.
        """
        if 'Profile_Name' in data.columns and 'Duration' in data.columns:
            try:
                data['Duration'] = pd.to_timedelta(data['Duration'])
                print(data['Duration'])
                ranking = data.groupby('Profile_Name')['Duration'].sum().reset_index()
                ranking['Total_Hours'] = ranking['Duration'].dt.total_seconds() / 3600
                ranking['Total_Hours'] = ranking['Total_Hours'].round(2)
                ranking = ranking.sort_values(by='Total_Hours', ascending=False)
                return ranking[['Profile_Name', 'Total_Hours']]
            except Exception as e:
                raise ValueError(f"Erro ao calcular o ranking por horas: {e}")
        else:
            raise ValueError("As colunas necessárias ('Profile_Name', 'Duration') não foram encontradas.")
        
        
    @staticmethod
    def top_5_titles_by_duration(data):
        """
        Retorna os top 5 títulos mais assistidos
        """
        if 'Title' in data.columns and 'Duration' in data.columns:
            try:
                data['Duration'] = pd.to_timedelta(data['Duration'])
               
                # Identifica se é série ou filme
                data['Is_Series'] = data['Title'].apply(lambda x: ':' in x)
               
                # Agrupa por título base (sem temporada) e soma as durações
                data['Base_Title'] = data['Title'].apply(lambda x: x.split(':')[0] if ':' in x else x)
                title_ranking = data.groupby('Base_Title')['Duration'].sum().reset_index()
               
                # Converte a duração total para horas
                title_ranking['Total_Hours'] = title_ranking['Duration'].dt.total_seconds() / 3600
                title_ranking['Total_Hours'] = title_ranking['Total_Hours'].round(2)
               
                # Ordena e seleciona os top 5 títulos
                top_5_titles = title_ranking.sort_values(by='Total_Hours', ascending=False).head(5)
                return top_5_titles[['Base_Title', 'Total_Hours']]
            except Exception as e:
                raise ValueError(f"Erro ao calcular os top 5 títulos: {e}")
        else:
            raise ValueError("As colunas necessárias ('Title', 'Duration') não foram encontradas.")

    @staticmethod
    def plot_average_usage_by_weekday(data):
        """
        Gera um gráfico de barras com o tempo médio de uso em horas por dia da semana.
        """
        if 'Duration' in data.columns and 'Day_of_Week' in data.columns:
            try:
                # Converte a coluna "Duration" para timedelta, caso ainda não tenha sido feita
                data['Duration'] = pd.to_timedelta(data['Duration'], errors='coerce')
                
                # Calcula a soma total de horas e o número de sessões por dia da semana
                grouped = data.groupby('Day_of_Week')['Duration'].agg(['sum', 'count']).reset_index()
                
                # Calcula a média de horas por dia da semana
                grouped['Average_Hours'] = grouped['sum'].dt.total_seconds() / 3600 / grouped['count']
                grouped['Average_Hours'] = grouped['Average_Hours'].round(2)
                
                # Ordena os dias da semana na ordem correta
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                grouped = grouped.set_index('Day_of_Week').reindex(days_order).reset_index()

                # Gráfico
                plt.figure(figsize=(16, 9))
                plt.bar(grouped['Day_of_Week'], grouped['Average_Hours'], color='red', edgecolor='red')
                plt.xlabel('Dia da Semana')
                plt.xticks(rotation=45, ha='right', fontsize=12)
                plt.tight_layout()
                plt.show()
            except Exception as e:
                raise ValueError(f"Erro ao gerar o gráfico de tempo médio por dia da semana: {e}")
        else:
            raise ValueError("As colunas necessárias ('Duration', 'Day_of_Week') não foram encontradas.")

    @staticmethod
    def movie_vs_series_count(data):
        """
        Retorna a contagem de filmes e séries assistidos por perfil.
        """
        if 'Profile_Name' in data.columns and 'type' in data.columns:
            try:
                # Conta o número de filmes e séries por perfil
                count_data = data.groupby(['Profile_Name', 'type']).size().reset_index(name='Count')

                # Reestrutura os dados para uma tabela pivô (colunas: filmes/séries, linhas: perfis, valores: contagens)
                pivot_data = count_data.pivot_table(
                    index='Profile_Name', columns='type', values='Count', aggfunc='sum'
                ).fillna(0)

                # Adiciona total de filmes e séries para quem não assistiu um dos tipos
                if 'movie' not in pivot_data.columns:
                    pivot_data['movie'] = 0
                if 'tv series' not in pivot_data.columns:
                    pivot_data['tv series'] = 0

                return pivot_data
            except Exception as e:
                raise ValueError(f"Erro ao calcular a contagem de filmes e séries: {e}")
        else:
            raise ValueError("As colunas necessárias ('Profile_Name', 'type') não foram encontradas.")

    @staticmethod
    def generate_movie_vs_series_chart(data):
        """
        Gera um gráfico de barras agrupadas comparando a quantidade de filmes e séries assistidos por perfil.
        """
        try:
            # Gera os dados para o gráfico
            count_data = MetricsHandler.movie_vs_series_count(data)

            # Configuração do gráfico
            profiles = count_data.index
            x = np.arange(len(profiles))  # Índices das barras (uma barra por perfil)
            bar_width = 0.35  # Largura de cada barra

            plt.figure(figsize=(12, 6))

            # Barras para filmes
            plt.bar(x - bar_width / 2, count_data['movie'], width=bar_width, label='Filmes', color='blue')

            # Barras para séries
            plt.bar(x + bar_width / 2, count_data['tv series'], width=bar_width, label='Séries', color='orange')

            # Configuração dos eixos e rótulos
            plt.xlabel('Perfis', fontsize=14)
            plt.ylabel('Quantidade Assistida', fontsize=14)
            plt.xticks(x, profiles, rotation=45, ha='right', fontsize=12)
            plt.tight_layout()

            # Salvar o gráfico como uma imagem base64 para exibir no HTML
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            return image_base64
        except Exception as e:
            raise ValueError(f"Erro ao gerar o gráfico de comparação filmes vs séries: {e}")
        

    @staticmethod
    def generate_time_spent_by_title_chart(data, profile_name=None):
        """
        Gera um gráfico de barras com o tempo gasto por título, somando temporadas e permitindo filtro por perfil.
        """
        try:
            # Converte a duração para timedelta
            data['Duration'] = pd.to_timedelta(data['Duration'])

            # Filtrar por perfil, se fornecido
            if profile_name:
                data = data[data['Profile_Name'] == profile_name]

            # Criar a coluna base do título (remover temporadas)
            data['Base_Title'] = data['Title'].apply(lambda x: x.split(':')[0] if ':' in x else x)

            # Agrupar pelo título base e somar as durações
            time_spent = data.groupby('Base_Title')['Duration'].sum().reset_index()
            time_spent['Total_Hours'] = time_spent['Duration'].dt.total_seconds() / 3600

            # Ordenar pelos mais assistidos e limitar a 10
            time_spent = time_spent.sort_values(by='Total_Hours', ascending=False).head(10)

            # Gerar o gráfico
            plt.figure(figsize=(12, 6 ))
            plt.bar(time_spent['Base_Title'], time_spent['Total_Hours'], color='skyblue', edgecolor='black')
            plt.xlabel('Títulos', fontsize=14)
            plt.ylabel('Horas Assistidas', fontsize=14)
            plt.xticks(rotation=45, ha='right', fontsize=12)
            plt.tight_layout()

            # Converter o gráfico em imagem Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            return image_base64
        except Exception as e:
            raise ValueError(f"Erro ao gerar o gráfico de tempo gasto por título: {e}")
        

    @staticmethod
    def generate_monthly_activity_chart(data):
        """
        Gera um gráfico de barras com a frequência média de atividades por mês ao longo de todos os anos.
        """
        try:
            # Verifica se a coluna de datas está presente
            if 'Start_Time' not in data.columns:
                raise ValueError("A coluna 'Start_Time' não foi encontrada na base de dados.")

            # Converte a coluna 'Start_Time' para datetime
            data['Start_Time'] = pd.to_datetime(data['Start_Time'])

            # Extrai o mês e o ano da coluna 'Start_Time'
            data['Month'] = data['Start_Time'].dt.month
            data['Year'] = data['Start_Time'].dt.year

            # Agrupa os dados por mês e ano e conta as atividades para cada combinação
            monthly_activity = data.groupby(['Year', 'Month']).size().reset_index(name='Frequency')

            # Somar a frequência de atividades por mês, considerando todos os anos
            monthly_sum = monthly_activity.groupby('Month')['Frequency'].sum().reset_index()

            # Calcular a quantidade total de anos presentes
            total_years = len(data['Year'].unique())

            # Calcular a média de atividades por mês ao longo de todos os anos
            monthly_sum['Average_Frequency'] = monthly_sum['Frequency'] / total_years

            # Garante que todos os meses (jan-dez) estejam presentes, mesmo que não haja dados para algum mês
            all_months = pd.Series(range(1, 13), name='Month')  # Meses de 1 a 12
            monthly_sum = pd.merge(all_months, monthly_sum, on='Month', how='left').fillna(0)

            # Gera o gráfico com tamanho maior (largura = 16, altura = 8)
            plt.figure(figsize=(12, 6))  
            plt.bar(monthly_sum['Month'].astype(str), monthly_sum['Average_Frequency'], color='teal')
            plt.xlabel('Mês', fontsize=14)
            plt.ylabel('Frequência Média de Atividades', fontsize=15)
            plt.xticks(rotation=45, ha='right', fontsize=12)
            plt.tight_layout()

            # Salva o gráfico como imagem Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            return image_base64
        except Exception as e:
            raise ValueError(f"Erro ao gerar o gráfico de atividades mensais: {e}")

    @staticmethod
    def generate_monthly_activity_per_user_chart(data):
        """
        Gera um gráfico de barras empilhadas para exibir a atividade mensal por usuário.
        """
        try:
            # Verifica se as colunas necessárias estão presentes
            if 'Start_Time' not in data.columns or 'Profile_Name' not in data.columns:
                raise ValueError("As colunas 'Start_Time' e 'Profile_Name' são necessárias.")

            # Converte a coluna 'Start_Time' para datetime
            data['Start_Time'] = pd.to_datetime(data['Start_Time'], errors='coerce')

            # Extrai o número do mês (1-12)
            data['Month'] = data['Start_Time'].dt.month

            # Conta atividades por usuário e mês
            activity = data.groupby(['Month', 'Profile_Name']).size().unstack(fill_value=0)

            # Reindexar para garantir que todos os meses estejam presentes no eixo X
            activity = activity.reindex(index=range(1, 13), fill_value=0)

            # Substituir os números do mês por seus nomes em português
            month_labels = [calendar.month_name[i].capitalize() for i in range(1, 13)]
            activity.index = month_labels

            # Calcular as porcentagens
            activity_percentage = activity.div(activity.sum(axis=1), axis=0) * 100

            # Gera o gráfico de barras empilhadas
            fig, ax = plt.subplots(figsize=(18, 5))
            activity.plot(kind='bar', stacked=True, colormap='tab20', ax=ax)

            # Adiciona as porcentagens dentro das barras
            for i, (month, row) in enumerate(activity_percentage.iterrows()):
                bottom = 0  # Controle da posição inferior da barra
                for user, value in row.items():
                    if value > 0:  # Apenas adiciona rótulos para valores > 0
                        ax.text(
                            x=i,
                            y=bottom + (activity.loc[month, user] / 2),
                            s=f"{value:.1f}%",
                            ha='center',
                            va='center',
                            fontsize=9,
                            color='white' if value > 10 else 'black'
                        )
                        bottom += activity.loc[month, user]

            # Configuração dos eixos e título
            ax.set_xlabel('Meses', fontsize=14)
            ax.set_ylabel('Atividade', fontsize=14)
            ax.legend(title='Usuários', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Salva o gráfico como imagem Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            return image_base64
        except Exception as e:
            raise ValueError(f"Erro ao gerar o gráfico de atividade mensal por usuário: {e}")

    @staticmethod
    def preprocess_sessions(data, max_gap_minutes=30):
            """
            Prepara os dados para o modelo de Machine Learning, calculando sessões contínuas.

            :param data: DataFrame com as colunas ['Profile_Name', 'Start_Time', 'Duration', 'type'].
            :param max_gap_minutes: Intervalo máximo (em minutos) entre sessões para serem consideradas contínuas.
            :return: DataFrame com dados preparados para análise.
            """
            try:
                # Converter colunas para tipos apropriados
                data['Start_Time'] = pd.to_datetime(data['Start_Time'])
                data['Duration'] = pd.to_timedelta(data['Duration'])
                data['End_Time'] = data['Start_Time'] + data['Duration']

                # Ordenar por usuário e horário de início
                data = data.sort_values(by=['Profile_Name', 'Start_Time'])

                # Identificar novas sessões com base no intervalo de tempo
                data['New_Session'] = (
                        data.groupby('Profile_Name')['Start_Time']
                        .diff()
                        .fillna(pd.Timedelta(seconds=0)) > pd.Timedelta(minutes=max_gap_minutes)
                ).astype(int).cumsum()

                # Agrupar por perfil, tipo, e sessões contínuas
                sessions = (
                    data.groupby(['Profile_Name', 'type', 'New_Session'])
                    .agg(
                        Total_Hours=('Duration', lambda x: x.sum().total_seconds() / 3600),
                        Start_Time=('Start_Time', 'min'),
                        End_Time=('End_Time', 'max'),
                        Day=('Start_Time', lambda x: x.dt.date.min())
                    )
                    .reset_index()
                )
                return sessions
            except Exception as e:
                raise ValueError(f"Erro ao preprocessar sessões: {e}")



