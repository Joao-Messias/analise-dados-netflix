import pandas as pd

class FileHandler:
    @staticmethod
    def load_csv(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Erro ao carregar o arquivo CSV: {e}")
