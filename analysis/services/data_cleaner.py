import pandas as pd

class DataCleaner:
    @staticmethod
    def clean_data(data):
        # Padronizar os nomes das colunas para substituir espaços por underscores
        data.columns = data.columns.str.replace(' ', '_')

        # Filtrar os dados para manter apenas as linhas em que "Supplemental Video Type" é nulo
        filtered_data = data[data['Supplemental_Video_Type'].isnull()]

        # Criar a nova coluna "type" com base na presença de ":" no título
        filtered_data['type'] = filtered_data['Title'].apply(
            lambda x: 'tv series' if ':' in str(x) else 'movie'
        )

        # Converter a coluna "Start_Time" para o tipo datetime (se ainda não for) e extrair o dia da semana
        if 'Start_Time' in filtered_data.columns:
            filtered_data['Start_Time'] = pd.to_datetime(filtered_data['Start_Time'], errors='coerce')
            filtered_data['Day_of_Week'] = filtered_data['Start_Time'].dt.day_name()  # Nome do dia da semana (ex: Monday)

        return filtered_data
