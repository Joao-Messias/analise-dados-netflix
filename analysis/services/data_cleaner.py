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

        return filtered_data
