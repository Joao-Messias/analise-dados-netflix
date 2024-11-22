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