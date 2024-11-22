class DataCleaner:
    @staticmethod
    def clean_data(data):

        filtered_data = data[data['Supplemental Video Type'].isnull()]

        filtered_data['type'] = filtered_data['Title'].apply(
            lambda x: 'tv series' if ':' in str(x) else 'movie'
        )

        return filtered_data
