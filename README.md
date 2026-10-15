<div align="center">

# 🤟 LIBRATOR
### Estação Acessível de Atendimento e Tradução de Libras em Tempo Real
**Projeto Integrado Pedagógico — Etec & Fatec (Centro Paula Souza)**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-0097A7?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.5.1-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![WCAG 2.1 AAA](https://img.shields.io/badge/Acessibilidade-WCAG_2.1_AAA-059669?style=for-the-badge)](https://www.w3.org/WAI/standards-guidelines/wcag/)

</div>

---

## 📑 Índice
- [Sobre o Projeto](#-sobre-o-projeto)
- [Objetivo do Projeto](#-objetivo-do-projeto)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Arquitetura da Solução & Pipeline](#-arquitetura-da-solução--pipeline)
- [Equipe de Desenvolvimento](#-equipe-de-desenvolvimento)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Como Executar o Projeto](#-como-executar-o-projeto)
- [Product Backlog (Padrão API Fatec 2025-2)](#-product-backlog-padrão-api-fatec-2025-2)
- [Registro das Sprints & Entregas](#-registro-das-sprints--entregas)
- [Competências Desenvolvidas](#-competências-desenvolvidas)

---

## 📖 Sobre o Projeto

O **Librator** é uma solução de tecnologia assistiva concebida no âmbito da **Aprendizagem por Projetos Integrados (API)** para as faculdades e escolas técnicas do **Centro Paula Souza (Fatec / Etec)**. 

No ambiente educacional, pessoas surdas enfrentam barreiras rotineiras de comunicação em secretarias acadêmicas, guichês de atendimento, coordenações e laboratórios devido à indisponibilidade de intérpretes presenciais de Libras em tempo integral para diálogos pontuais. 

Fundamentado nos princípios da **Lei nº 10.436/2002** e do **Decreto nº 5.626/2005**, o Librator atua como uma ponte de comunicação autônoma, traduzindo o alfabeto manual de Libras (datilologia) em tempo real, integrando predição de vocabulário acadêmico, síntese de voz (TTS) para ouvintes e réplica acessível na tela para o estudante.

---

## 🎯 Objetivo do Projeto

Facilitar a inclusão e a autonomia de estudantes e munícipes surdos nas unidades do Centro Paula Souza por meio de uma estação computacional web capaz de:
1. Reconhecer os 26 sinais do alfabeto manual de Libras com acurácia superior a $90\%$.
2. Reduzir o tempo de composição de mensagens em mais de $70\%$ por meio de **autocompletar de termos acadêmicos** e **mural de solicitações frequentes**.
3. Garantir **comunicação bidirecional** entre surdos e ouvintes com reprodução de áudio e painel de texto em alto contraste.

---

## ✨ Funcionalidades Principais

- 🖐️ **Visão Computacional Invariante:** Rastreamento de 21 landmarks tridimensionais da mão via MediaPipe Tasks, com normalização de translação e escala (invariante a distância da câmera).
- ⚡ **Engenharia de Features Dinâmicas:** Vetor de 126 dimensões incorporando gradiente de velocidade temporal ($\Delta$ posição entre frames) para distinguir com precisão letras com movimento (`H, J, K, X, Z`).
- ⏱️ **Confirmação Estável (Hold Time):** Anel circular de progresso em SVG que confirma a letra apenas após permanência contínua, evitando repetições involuntárias.
- 🎓 **Autocompletar Inteligente de Termos Etec & Fatec:** Chips preditivos instantâneos que completam palavras escolares frequentes (ex.: *Matrícula, Atestado, Horário, Passe Escolar, Professor, Laboratório*).
- 🔊 **Comunicação Bidirecional com Síntese de Voz (TTS):** Botão que lê a mensagem do aluno em voz alta em português do Brasil sem dependência de serviços pagos na nuvem.
- 💬 **Estação de Atendimento & Diálogo Bilíngue:** Histórico de conversa estilo chat para registro de solicitações e campo de resposta direta para o atendente ouvinte.
- 📋 **Mural da Secretaria Acadêmica:** Atalhos com 1 clique para as dúvidas e requerimentos mais recorrentes do Centro Paula Souza.
- 🌓 **Acessibilidade Universal (WCAG 2.1):** Modo Alto Contraste, ampliação tipográfica dinâmica (A+/A-) e guia visual didático do alfabeto manual de A a Z.
- 📊 **Painel de Métricas e Exportação:** Telemetria da sessão (sinais confirmados, palavras formadas, confiança média) e download de relatório de atendimento em `.txt`.

---

## 🏗 Arquitetura da Solução & Pipeline

```
[ Webcam / Celular ]
        │  (OpenCV - 30 FPS)
        ▼
[ MediaPipe Tasks HandLandmarker ] ──► 21 Pontos 3D (x, y, z)
        │
        ▼
[ Normalização Espacial ] ────────────► Origem no Pulso (0,0,0) + Escala (Pulso -> Dedo Médio)
        │
        ▼
[ Vetor de Features (126 Dimensões) ] ─► 63 Posições Normalizadas + 63 Vetores de Velocidade (Δt)
        │
        ▼
[ RandomForestClassifier (300 árvores) ] ─► Predição da Letra + Cálculo de Confiança (%)
        │
        ▼
[ Suavização Temporal & Hold Time ] ──► Votação por maioria (8 frames) + Anel de Progresso (1.0s)
        │
        ▼
[ Interface Web (Flask + HTML/JS) ] ──► Autocompletar Acadêmico + Síntese de Voz (TTS) + Chat Bilíngue
```

---

## 👥 Equipe de Desenvolvimento

| Função | Nome | LinkedIn & GitHub |
|:---:|:---|:---:|
| Team Member | **Wenderson Candido** | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/wendersonleal/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/WendersonSousaLeal) |
| Team Member | **Samuel Domingos** | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/samuel-domingos-2265b3b6/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/samueldomingos1) |
| Team Member | **Pedro Vieira** | [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/PedroVieirasj) |
| Team Member | **Pietro Oliveira** | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/pietro-oliveira-5551823b6/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/Pietro18023) |

---

## 🛠 Tecnologias Utilizadas

| Categoria | Tecnologia | Justificativa de Engenharia |
|---|---|---|
| **Linguagem Principal** | **Python 3.11** | Ecossistema maduro para Visão Computacional e Machine Learning |
| **Visão Computacional** | **OpenCV** | Captura eficiente de frames, manipulação matricial e streaming MJPEG |
| **Rastreamento de Mãos** | **MediaPipe Tasks** | Nova API baseada no modelo `hand_landmarker.task` com alta performance local |
| **Aprendizado de Máquina** | **Scikit-learn** | Classificador `RandomForestClassifier` com 300 estimadores e balanceamento |
| **Servidor Web** | **Flask 3.0** | Servidor leve e modular com rotas REST e streaming multithreaded |
| **Interface de Usuário** | **HTML5 / CSS3 / JavaScript** | Dashboard acessível sem dependências pesadas, compatível com modo Kiosk/Totem |
| **Síntese de Voz (TTS)** | **Web Speech API** | Voz nativa do navegador em língua portuguesa sem custo de nuvem |
| **Persistência de Modelos** | **Joblib** | Serialização rápida do modelo e do codificador de classes |
| **Metodologia Ágil** | **Scrum / API CPS** | Organização com Backlog priorizado por valor de negócio e Sprints incrementais |

---

## 🗂 Estrutura do Repositório

```
LIBRATOR/
├── Docs/                                 # Documentos e Guias de Requisitos API 2025-2
├── MVP/                                  # Artefatos Oficiais das Sprints
│   ├── sp1.md                            # Registro e Métricas da Sprint 1 (Core Datilológico)
│   ├── sp2.md                            # Registro e Métricas da Sprint 2 (Predição e TTS)
│   └── sp3.md                            # Registro e Métricas da Sprint 3 (Atendimento e Totem)
├── librator/                             # Aplicação Principal da Estação
│   ├── app.py                            # Servidor Flask com Gerenciador Resiliente de Câmeras
│   ├── collect_data.py                   # Script assistido de coleta de amostras
│   ├── train_model.py                    # Script de treinamento supervisionado e validação cruzada
│   ├── hand_utils.py                     # Módulo compartilhado: MediaPipe + Normalização + Velocidade
│   ├── requirements.txt                  # Dependências fixadas do projeto
│   ├── data/
│   │   ├── landmarks_dataset_2.csv       # Dataset rotulado A–Z
│   │   └── filtrar_dataset.py            # Utilitário de limpeza de dados
│   ├── models/
│   │   ├── hand_landmarker.task          # Modelo neural de detecção de mãos
│   │   └── libras_rf_model.pkl           # Modelo Random Forest serializado
│   └── templates/
│       └── index.html                    # Interface acessível da Estação de Atendimento
└── README.md                             # Documentação consolidada do projeto
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- **Python 3.10 ou 3.11** instalado (as versões do MediaPipe e NumPy no projeto têm suporte ideal nestas versões).
- Webcam integrada ou câmera externa/celular (DroidCam, Iriun Webcam).

### Passo a Passo

```bash
# 1. Navegue até o diretório da aplicação
cd librator

# 2. Crie e ative o ambiente virtual
python -m venv venv
# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# No Windows (CMD):
venv\Scripts\activate.bat
# No Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Re-treinar o modelo com os dados mais recentes
python train_model.py

# 5. Inicie a Estação Librator
python app.py
```

Acesse **http://localhost:5000** no seu navegador de preferência (Google Chrome, Microsoft Edge ou Firefox).

> 💡 **Dica de Câmera:** Caso esteja utilizando um celular como webcam (ex.: Iriun), você pode alternar o índice da câmera diretamente no painel **"⚙️ Configurações"** da própria página web, sem precisar reiniciar o terminal!

---

## 📋 Product Backlog (Padrão API Fatec 2025-2)

Conforme estabelecido no Guia de Artefatos de Requisitos da Fatec, as histórias de usuário seguem o princípio **INVEST** e os **3 Cs** (Cartão, Conversa, Confirmação):

| Rank | Prioridade | User Story (INVEST) | Estimativa | Sprint | Status |
|:---:|:---:|:---|:---:|:---:|:---:|
| **1** | 🔴 Alta | Como **aluno surdo**, quero que os sinais do alfabeto manual sejam reconhecidos pela câmera e montem letras na tela, para que eu possa iniciar uma mensagem. | 8 SP | 1 | ✅ Concluído |
| **2** | 🔴 Alta | Como **aluno surdo**, quero comandos de edição (espaço, nova linha, apagar e limpar) por gestos ou clique, para corrigir erros de digitação sem perder o texto. | 5 SP | 1 | ✅ Concluído |
| **3** | 🔴 Alta | Como **aluno surdo**, quero receber sugestões de termos acadêmicos (ex.: `AULA`, `MATRICULA`) enquanto soletro, para concluir palavras rapidamente sem digitar letra por letra. | 8 SP | 2 | ✅ Concluído |
| **4** | 🟡 Média | Como **aluno surdo**, quero que a frase que montei seja lida em voz alta pelo computador, para que o atendente ouvinte compreenda o que eu disse sem precisar olhar fixamente para a tela. | 5 SP | 2 | ✅ Concluído |
| **5** | 🟡 Média | Como **atendente ouvinte**, quero um campo simples para responder ao aluno digitando na tela, para que o diálogo seja mantido de forma bidirecional. | 5 SP | 2 | ✅ Concluído |
| **6** | 🟡 Média | Como **aluno surdo**, quero selecionar expressões acadêmicas frequentes em um mural categorizado, para agilizar solicitações rotineiras com apenas 1 clique. | 5 SP | 3 | ✅ Concluído |
| **7** | 🟡 Média | Como **atendente/administrador**, quero alternar a câmera e regular a sensibilidade do reconhecimento sem reiniciar a aplicação, para adaptar o sistema ao hardware do laboratório. | 5 SP | 3 | ✅ Concluído |
| **8** | 🟢 Baixa | Como **aluno ou visitante**, quero consultar um guia visual do alfabeto manual de Libras na tela, para tirar dúvidas sobre como realizar sinais específicos. | 3 SP | 3 | ✅ Concluído |
| **9** | 🟡 Média | Como **coordenador pedagógico ou membro da banca**, quero visualizar as métricas da sessão e exportar o relatório do atendimento, para mensurar o impacto do projeto na Feira de Soluções. | 5 SP | 3 | ✅ Concluído |

---

## 🗓 Registro das Sprints & Entregas

| Sprint | Foco Temático | Status | Documentação Completa |
|:---:|:---|:---:|:---:|
| **01** | Core Datilológico, Pipeline MediaPipe & RandomForest | ✅ Concluído | [Visualizar Artefato MVP 1](MVP/sp1.md) |
| **02** | Autocompletar Acadêmico, Síntese de Voz (TTS) & Acessibilidade | ✅ Concluído | [Visualizar Artefato MVP 2](MVP/sp2.md) |
| **03** | Estação de Atendimento, Mural CPS, Métricas & Feira de Soluções | ✅ Concluído | [Visualizar Artefato MVP 3](MVP/sp3.md) |
| **Feira** | Apresentação Oficial / Banca Examinadora Inova CPS | 🚀 Pronto | [Dashboard da Aplicação](http://localhost:5000) |

---

## 💡 Competências Desenvolvidas

- **Visão Computacional Aplicada:** Rastreamento tridimensional de articulações corporais com o MediaPipe Tasks.
- **Engenharia de Dados e Machine Learning:** Engenharia de atributos temporais com derivadas de velocidade, balanceamento de classes e validação cruzada estratificada.
- **Desenvolvimento Full-Stack:** Construção de servidores assíncronos em Flask com streaming de vídeo MJPEG e interfaces web interativas em tempo real.
- **Design para Acessibilidade e Inclusão:** Aplicação das diretrizes da WCAG 2.1 AAA, tipografia legível e síntese de voz nativa no navegador.
- **Gestão Ágil de Projetos:** Condução de backlog e entregas iterativas em conformidade com as exigências metodológicas de Aprendizagem por Projetos Integrados (API) do Centro Paula Souza.

---

<div align="center">

Feito com 💙 e dedicação pela equipe **Librator**  
*Centro Paula Souza — Etec & Fatec*

</div>
