# Painel de Laboratório - Hospital São Francisco na Providência de Deus

Este é um painel de controle desenvolvido em Python com a biblioteca Streamlit, destinado à equipe e gerência do Laboratório do Hospital São Francisco na Providência de Deus. A aplicação fornece visualizações e indicadores em tempo real para monitorar a performance e a qualidade dos serviços.

## Visão Geral

O objetivo principal deste painel é oferecer uma ferramenta centralizada para:
- **Monitorar o Turnaround Time (TAT):** Acompanhar os tempos de processamento dos exames do Pronto Socorro, identificando gargalos e atrasos.
- **Analisar Valores Críticos:** Visualizar e filtrar exames que apresentaram resultados críticos, permitindo uma ação rápida e informada.

## Funcionalidades

O painel é dividido em duas seções principais:

### 1. Monitoramento do Pronto Socorro
- **KPIs em Tempo Real:** Métricas chave como total de exames, percentual de aderência ao prazo, e tempo médio de conclusão (Coleta → Aprovação).
- **Status dos Exames:** Visualização da distribuição de exames por etapa (Pendente de Coleta, Material Coletado, Área Técnica, etc.).
- **Lista de Exames Atrasados:** Tabela detalhada com todos os exames que excederam o tempo esperado.
- **Visão Analítica:** Um dashboard completo com todos os exames do período, com filtros dinâmicos por tipo de exame (Hemograma, Glicose, Uréia, etc.).

### 2. Análise de Valores Críticos
- **Filtro por Período:** Permite selecionar o intervalo de datas para a análise.
- **Indicadores de Criticidade:** Métricas sobre o volume de exames críticos, tipos de exames mais afetados e número de pacientes únicos com resultados críticos.
- **Análise por Tipo de Exame:** Dashboards específicos para análise de valores críticos em:
    - Hemogramas
    - Coagulogramas (INR)
    - Hepatogramas
    - Lipidogramas
- **Tabela Detalhada:** Visão analítica de todos os exames com valores críticos no período selecionado.

## Tecnologias Utilizadas

- **Python 3**
- **Streamlit:** Para a construção da interface web interativa.
- **Pandas:** Para manipulação e análise de dados.
- **Oracledb:** Para a conexão com o banco de dados Oracle.
- **Oracle Instant Client:** Dependência para a comunicação com o banco de dados (já incluído no projeto).

## Pré-requisitos

- Python 3.8 ou superior.
- Acesso à rede do banco de dados Oracle do hospital.

## Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto em sua máquina local.

### 1. Clonar o Repositório
```bash
git clone <URL_DO_REPOSITORIO_INTERNO>
cd HSF_PAINEL_LABORATORIO
```

### 2. Criar e Ativar um Ambiente Virtual

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 4. Configurar as Credenciais do Banco de Dados

Para garantir a segurança, as credenciais de acesso ao banco de dados não são armazenadas no código. Em vez disso, utilizamos o sistema de segredos do Streamlit.

Crie um arquivo chamado `secrets.toml` dentro da pasta `.streamlit`. Se a pasta não existir, crie-a na raiz do projeto.

**Caminho do arquivo:** `.streamlit/secrets.toml`

Adicione o seguinte conteúdo ao arquivo, substituindo os valores pelos corretos:

```toml
# .streamlit/secrets.toml

[database]
user = "SEU_USUARIO_DO_BANCO"
password = "SUA_SENHA_DO_BANCO"
dsn = "IP_DO_BANCO:PORTA/SERVICE_NAME"
```

**Exemplo:**
```toml
[database]
user = "TASY"
password = "aloisk"
dsn = "192.168.5.9:1521/TASYPRD"
```

Este arquivo é ignorado pelo Git (através do `.gitignore`) para evitar que as credenciais sejam enviadas para o repositório.

## Como Executar a Aplicação

Com o ambiente configurado e o arquivo de segredos criado, execute o seguinte comando no seu terminal, na raiz do projeto:

```bash
streamlit run Home.py --server.port 8002
```

A aplicação será aberta automaticamente no seu navegador padrão no endereço `http://localhost:8002`.
