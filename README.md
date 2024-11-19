### **Netflix Análise de Dados Pessoais**

Este projeto permite que você analise seus dados pessoais de visualização da Netflix. Com ele, você pode descobrir padrões interessantes no seu consumo de filmes e séries, como os dias da semana e meses mais assistidos, além de identificar seus filmes e séries favoritos.

O objetivo é ajudar você a entender melhor como utiliza a plataforma, fornecendo gráficos claros e listas organizadas para consulta.

---

### **Funcionalidades**
- **Dias Mais Assistidos:** Veja quais dias da semana você mais utiliza a Netflix.
- **Frequência por Mês:** Descubra em quais meses você assistiu mais conteúdo.
- **Comparação entre Filmes e Séries:** Descubra se você prefere assistir filmes ou séries, além de ver padrões por dia da semana.
- **Filmes Mais Assistidos:** Uma lista dos filmes que você mais viu.
- **Séries Mais Assistidas:** Lista de séries mais vistas, considerando todos os episódios e temporadas.
- **Gráficos:** Resultados apresentados em gráficos simples e em português.

---

### **Como Obter Seus Dados da Netflix**
1. Faça login na sua conta da Netflix.
2. Vá até **Configurações**.
3. Encontre a opção **Baixe uma cópia dos seus dados**.
4. Solicite os dados do seu perfil. Pode levar alguns dias para a Netflix enviar o link de download.
5. Quando os dados estiverem disponíveis, baixe o arquivo.
6. Dentro do pacote, localize o arquivo chamado `ViewingActivity.csv`.

---

### **Como Usar**
1. Faça o download deste projeto ou clone o repositório.
2. Instale o Python em sua máquina (se ainda não estiver instalado).
3. Coloque o arquivo `ViewingActivity.csv` que você baixou da Netflix na pasta de upload disponível no sistema.
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

---

### **Observações**
- Certifique-se de que o arquivo `ViewingActivity.csv` foi baixado corretamente da Netflix.
- Este projeto é uma ferramenta educativa para visualização e análise dos seus próprios dados, sem compartilhar informações com terceiros.

---

### **Contribuições**
Se você quiser contribuir ou melhorar este projeto, sinta-se à vontade para compartilhar ideias ou sugestões. Divirta-se analisando seu tempo na Netflix! 🎥📊

