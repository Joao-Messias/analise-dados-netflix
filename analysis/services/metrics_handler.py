import pandas as pd

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