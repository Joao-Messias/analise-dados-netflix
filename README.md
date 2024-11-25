
markdown
Copiar código
# Netflix Data Analyzer

Este é um aplicativo web para análise e visualização de dados de consumo da plataforma Netflix. O sistema permite o upload de datasets no formato CSV, gera gráficos interativos e realiza análises com base em métricas diversas, além de treinar modelos de machine learning para predição de padrões de consumo.


---

# 🚀 Funcionalidades

- **Upload de arquivos CSV**: Carregue datasets para análise de consumo de conteúdo.
- **Visualização dos dados carregados**: Exiba os dados tratados e limpos.
- **Gráficos interativos**: Explore métricas de uso e padrões com gráficos intuitivos por usuário.
- **Múltiplos tipos de análises e métricas**:
  - Total de horas assistidas
  - Sessões totais
  - Ranking de perfis mais ativos
  - Top 5 títulos mais assistidos
  - Gráficos semanais, mensais e por título
- **Modelos de Machine Learning**:
  - Treinamento com Random Forest ou Regressão Logística
  - Configuração personalizada de parâmetros
  - Análise de probabilidade de assistir filmes ou séries em diferentes horários do dia
  - Visualização de métricas de desempenho, como precisão, recall e F1-score.

---

## 📋 Pré-requisitos

- **Python 3.7+**
- **pip** (gerenciador de pacotes Python)

---

### **Como Obter Seus Dados da Netflix**
1. Faça login na sua conta da Netflix.
2. Vá até **Configurações**.
3. Encontre a opção **Baixe uma cópia dos seus dados**.
4. Solicite os dados do seu perfil. Pode levar alguns dias para a Netflix enviar o link de download.
5. Quando os dados estiverem disponíveis, baixe o arquivo.
6. Dentro do pacote, localize o arquivo chamado `ViewingActivity.csv`.

---

### 📦 Dependências Principais
- Django: Framework web para construir o backend.
- pandas: Manipulação de dados.
- numpy: Operações matemáticas e vetoriais.
- matplotlib: Criação de gráficos.
- scikit-learn: Machine Learning e métricas.
- imbalanced-learn: Balanceamento de dados usando SMOTE.

---

### **Como Usar**
1. Faça o download deste projeto ou clone o repositório.
2. Instale o Python em sua máquina (se ainda não estiver instalado).
3. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
4. Instale as dependencias necessárias.
   ```bash
   cd analise-dados-netflix
   pip install -r requirements.txt
   ```
4. Execute o projeto no terminal:
   ```bash
   python manage.py runserver
   ```
5. Acesse o endereço exibido no terminal, que geralmente será: [http://127.0.0.1:8000/analysis/](http://127.0.0.1:8000/analysis/).
6. Faça o upload do arquivo `ViewingActivity.csv`.
7. Após o upload, você será redirecionado automaticamente para o painel com gráficos e listas.

---

### **Exemplo de Resultados**
1. **Gráfico de Dias Mais Assistidos:**
   Um gráfico que mostra quais dias da semana você mais utiliza a Netflix.

2. **Gráfico de Frequência por Mês:**
   Um gráfico que indica os meses em que você assistiu mais conteúdos.

3. **Lista de Filmes Mais Assistidos:**
   Filmes que você viu mais vezes no período analisado.

4. **Lista de Séries Mais Assistidas:**
   Séries que você mais assistiu, considerando todas as temporadas e episódios.

5. **Gráfico de atividade mensal por usuário**
   Um gráfico que indica a atividade mensal por usuário.
---

### 📈 Métricas de Avaliação
- Relatório completo de classificação:
- Precisão
- Recall
- F1-Score
- Matriz de confusão visual

### **Observações**
- Certifique-se de que o arquivo `ViewingActivity.csv` foi baixado corretamente da Netflix.
- Este projeto é uma ferramenta educativa para visualização e análise dos seus próprios dados, sem compartilhar informações com terceiros.

---

### **Contribuições**
Se você quiser contribuir ou melhorar este projeto, sinta-se à vontade para compartilhar ideias ou sugestões. Divirta-se analisando seu tempo na Netflix! 🎥📊

### **Autores**
- João Pedro Messias
- Milena Schrickte
- Gustavo Guedes
- Gabriel Rossa
