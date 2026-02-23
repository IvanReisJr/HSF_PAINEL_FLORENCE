# Painel Florence - Sistema de Gestão de Enfermagem
**Hospital São Francisco na Providência de Deus**

> *"Florence Nightingale: A pioneira da enfermagem moderna e da visualização de dados em saúde"*

## 📊 Visão Geral

O **Painel Florence** é uma aplicação web desenvolvida em Python com Streamlit, dedicada à equipe de enfermagem do Hospital São Francisco na Providência de Deus. Inspirada nos princípios de Florence Nightingale - que revolucionou a enfermagem através do uso de dados e estatísticas - esta plataforma fornece visualizações interativas e indicadores em tempo real para apoiar a tomada de decisão clínica e a gestão de cuidados de enfermagem.

### 🎯 Objetivos do Sistema

- **Monitoramento em Tempo Real**: Acompanhar o censo de pacientes e suas classificações de risco
- **Apoio à Decisão Clínica**: Fornecer dados estruturados sobre escalas de avaliação e risco
- **Gestão de Recursos**: Otimizar a alocação de profissionais baseada em indicadores
- **Qualidade do Cuidado**: Identificar pacientes que necessitam de atenção especializada
- **Transparência e Accountability**: Gerar relatórios detalhados para auditoria e melhoria contínua

## 🏥 Funcionalidades Principais

### 1. Dashboard de Censo de Pacientes
- **Visualização por Setor**: Filtrar pacientes por unidade de internação
- **Classificações de Risco**: Monitorar escalas MEWS, BRADEN, SAPS3, RASS, GLASGOW, FUGULIN, MARTINS
- **Status de Leitos**: Visualização em tempo real da ocupação hospitalar
- **Exportação de Dados**: Geração de relatórios em Excel para análises adicionais

### 2. Indicadores de Cirurgias
- **Centro Cirúrgico**: Acompanhamento de procedimentos cirúrgicos
- **Análise por Caráter**: Eletivas vs. Urgências/Emergências
- **Porte Cirúrgico**: Classificação dos procedimentos por complexidade
- **Tendências Temporais**: Análise histórica de volumes cirúrgicos

### 3. Outras Páginas
- **Cirurgias**: Indicadores operacionais do centro cirúrgico

## 🛠️ Arquitetura Tecnológica

### Stack de Tecnologias
- **Backend**: Python 3.8+
- **Framework Web**: Streamlit
- **Banco de Dados**: Oracle Database (via oracledb + Instant Client)
- **Bibliotecas de Dados**: Pandas
- **Exportação**: OpenPyXL (Excel)

### Estrutura do Projeto
```
HSF_PAINEL_FLORENCE/
├── Home.py                    # Página principal e navegação
├── Pages/
│   ├── Censo.py              # Dashboard de censo de pacientes
│   ├── Cirurgias_Centro_Cirurgico.py  # Dashboard de cirurgias
│   └── query.sql             # Queries do banco de dados (censo)
├── instantclient-basiclite-windows.x64-23.6.0.24.10/  # Oracle Instant Client
├── .streamlit/
│   └── config.toml (opcional)  # Configurações do Streamlit
├── requirements.txt           # Dependências Python
└── HSF_LOGO_-_1228x949_001.png  # Identidade visual do hospital
```

## 📋 Escalas de Avaliação Suportadas

### MEWS (Modified Early Warning Score)
- **Faixas**: Baixo (0-4), Médio (5-6), Alto (7-12)
- **Uso**: Detecção precoce de deterioração clínica
- **Frequência**: Recomendada a cada 4-6 horas

### BRADEN (Escala de Risco para Úlceras por Pressão)
- **Faixas**: Sem risco (19-23), Risco leve (15-18), Risco moderado (13-14), Risco alto (≤12)
- **Uso**: Prevenção de lesões por pressão
- **Ações**: Protocolos de prevenção baseados no escore

### SAPS 3 (Simplified Acute Physiology Score)
- **Uso**: Predição de mortalidade em UTI
- **Parâmetros**: Fisiologia aguda, idade, comorbidades
- **Interpretação**: Percentual de risco predito

### RASS (Richmond Agitation-Sedation Scale)
- **Faixas**: -5 (Não responsivo) a +4 (Combativo)
- **Alvo terapêutico**: Geralmente -2 a 0 para pacientes ventilados
- **Monitoramento**: Contínuo em pacientes sedados

### GLASGOW (Escala de Coma de Glasgow)
- **Componentes**: Abertura ocular, resposta verbal, resposta motora
- **Faixa**: 3 (Coma profundo) a 15 (Normal)
- **Crítico**: ≤8 indica necessidade de proteção de via aérea

### FUGULIN (Classificação de Dependência)
- **Níveis**: Cuidados Mínimos, Intermediários, Alta Dependência, Semi-Intensivos, Intensivos
- **Uso**: Alocação de recursos e custeio hospitalar

### MARTINS (Escala de Dependência para Atividades de Vida Diária)
- **Avaliação**: Capacidade para auto-cuidado
- **Uso**: Planejamento de alta e necessidades pós-alta

## 🔧 Configuração e Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Acesso ao banco de dados Oracle do hospital
- Permissões de rede apropriadas

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <URL_DO_REPOSITORIO>
cd HSF_PAINEL_FLORENCE
```

2. **Crie e ative ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o Oracle Instant Client**
O Oracle Instant Client já está incluído no projeto. Certifique-se de que o caminho esteja correto:
```python
# Verificado automaticamente no código
caminho_instantclient = os.path.join(diretorio_raiz_projeto, "instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6")
```

5. **Configure as credenciais do banco**
Crie o arquivo `.streamlit/secrets.toml`:
```toml
[database]
user = "SEU_USUARIO"
password = "SUA_SENHA"
dsn = "IP_SERVIDOR:PORTA/SERVICE_NAME"
```

6. **Execute a aplicação**
```bash
streamlit run Home.py --server.port 8002
```

## 📊 Uso e Navegação

### Página Inicial (Home)
- **Logo HSF**: Identidade visual do hospital
- **Título**: Dashboard Florence - HSF - Enfermagem
- **Navegação**: Sidebar com acesso às diferentes seções

### Dashboard de Censo
1. **Filtros de Data**: Selecione o período de análise
2. **Filtro de Setor**: Escolha unidades específicas ou "Todos"
3. **Indicadores Principais**: Total de atendimentos e classificações
4. **Tabela Detalhada**: Visualização completa com exportação
5. **Análise por Escala**: Gráficos de distribuição por tipo de escala

### Dashboard de Cirurgias
1. **Período de Análise**: Filtro por datas
2. **Resumo Executivo**: KPIs principais (Total, Eletivas, Urgências)
3. **Análise por Caráter**: Distribuição entre tipos de cirurgia
4. **Análise por Porte**: Complexidade dos procedimentos
5. **Exportação Excel**: Relatórios formatados para gestão

## 🔒 Considerações
- Dados clínicos são obtidos via consultas ao Oracle. Configure credenciais localmente em `.streamlit/secrets.toml` (não versionado).

## 📈 Performance
- Uso de cache via `st.connection(..., ttl=3600)` onde aplicável.

## 🎯 Público-Alvo
- Equipe de Enfermagem e Gestores assistenciais.

## 🔧 Manutenção
- Atualize queries conforme necessidade clínica e desempenho.

## 📚 Referências e Recursos

### Bibliografia Recomendada
1. Nightingale, F. (1858). *Notes on Matters Affecting the Health, Efficiency, and Hospital Administration of the British Army*
2. Institute of Medicine. (2011). *The Future of Nursing: Leading Change, Advancing Health*
3. American Nurses Association. (2021). *Nursing: Scope and Standards of Practice*

### Diretrizes Clínicas
- **MEWS**: Royal College of Physicians Guidelines
- **BRADEN**: National Pressure Ulcer Advisory Panel
- **SAPS 3**: European Society of Intensive Care Medicine

### Recursos Online
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Oracle Database Documentation](https://docs.oracle.com/en/database/)
- [Healthcare Data Visualization Best Practices](https://www.healthitanalytics.com/)

## 🤝 Contribuições
- Veja [CONTRIBUTING.md](file:///c:/IvanReis/Paineis/HSF_PAINEL_FLORENCE/CONTRIBUTING.md) para diretrizes de contribuição.

## 📄 Licença e Termos de Uso

Este sistema é propriedade do Hospital São Francisco na Providência de Deus e está licenciado para uso interno apenas. A reprodução, distribuição ou modificação não autorizada é estritamente proibida.

---

**"Como Florence Nightingale usou dados para revolucionar a saúde pública no século XIX, continuamos sua tradição aplicando tecnologia moderna para melhorar os cuidados de enfermagem no século XXI."**

*Desenvolvido com ❤️ pela equipe de TI do Hospital São Francisco - Inspirado por Florence Nightingale (1820-1910)*
