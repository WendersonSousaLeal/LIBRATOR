<div align="center">

# 🤟 Librator
### Tradutor de Libras para Texto

Um projeto pedagógico que une tecnologia e inclusão social.

</div>

---

## 📑 Índice
- [Sobre o Projeto](#-sobre-o-projeto)
- [Objetivo do Projeto](#-objetivo-do-projeto)
- [Funcionalidades](#-funcionalidades)
- [Equipe](#-equipe)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Como Executar](#-como-executar)
- [Product Backlog](#-product-backlog)
- [Competências Desenvolvidas](#-competências-desenvolvidas)
- [Registro das Sprints](#-registro-das-sprints)

---

## 📖 Sobre o Projeto

O **Librator** é um projeto pedagógico que abrange áreas profissionais de diversos segmentos. Com foco no desenvolvimento de competências e fundamentado nos pilares da **inclusão** e da **resolução de problemas reais da sociedade**, a iniciativa visa aprimorar a comunicação e auxiliar o ensino em locais públicos e privados, oferecendo versatilidade para uso em diversas plataformas.

## 🎯 Objetivo do Projeto

Facilitar a comunicação entre pessoas surdas e ouvintes por meio de um sistema de tradução automática da Língua Brasileira de Sinais (Libras), utilizando visão computacional e aprendizado de máquina para converter sinais em texto de forma acessível e em tempo real.

---

## ✨ Funcionalidades

- 🖐️ **Reconhecimento do alfabeto manual de Libras (A–Z)** em tempo real, pela câmera.
- 📝 **Montagem de palavras e frases**: as letras confirmadas formam o texto na tela.
- ␣ **Comando de espaço** para separar palavras e **comando de nova linha** para encerrar a palavra e ir para a linha de baixo.
- ✅ **Confirmação de letras** por estabilidade e filtro de confiança, para evitar letras erradas.
- 📱 **Câmera do celular** como webcam (Iriun Webcam, DroidCam etc.).
- 🌐 **Interface web** com vídeo ao vivo e painel de leitura.

Exemplo: sinalizando `O → L → A → [espaço] → M → U → N → D → O → [nova linha]`, o texto na tela fica:

```
OLA MUNDO
```

> O reconhecimento é do alfabeto manual, então o texto sai em letras maiúsculas, sem acentos e sem pontuação.

---

## 👥 Equipe

| Função | Nome | LinkedIn & GitHub |
|:---:|:---|:---:|
| Team Member | Wenderson Candido | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/wendersonleal/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/WendersonSousaLeal) |
| Team Member | Samuel Domingos | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/samuel-domingos-2265b3b6/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/samueldomingos1) |
| Team Member | Pedro Vieira | [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/PedroVieirasj) |
| Team Member | Pietro Oliveira | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/pietro-oliveira-5551823b6/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/Pietro18023) |

---

## 🛠 Tecnologias Utilizadas

<div align="left">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square&logo=google&logoColor=white)
![Scikit--learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![Excel](https://img.shields.io/badge/Microsoft_Excel-217346?style=flat-square&logo=microsoft-excel&logoColor=white)
![Jira](https://img.shields.io/badge/Jira_Software-0052CC?style=flat-square&logo=jira&logoColor=white)

</div>

| Categoria | Tecnologia | Uso no projeto |
|---|---|---|
| Linguagem | **Python** | Desenvolvimento principal do sistema |
| Visão Computacional | **OpenCV** | Captura e processamento de imagens/vídeo |
| Detecção de Mãos | **MediaPipe** | Rastreamento dos 21 pontos-chave (landmarks) da mão |
| Machine Learning | **Scikit-learn** | Treinamento do modelo de classificação |
| Modelo | **RandomForestClassifier** | Classificação das letras do alfabeto em Libras |
| Pré-processamento | **Normalização de landmarks** | Pulso como origem, escala pela mão e features de velocidade (`hand_utils.py`) |
| Persistência | **Joblib** | Salvamento e carregamento do modelo treinado |
| Manipulação de dados | **NumPy / Pandas** | Operações numéricas e leitura do dataset (CSV) |
| Interface Web | **Flask + HTML/CSS/JS** | Servidor, streaming de vídeo e painel de leitura |
| Gestão do Projeto | **Jira Software** | Organização das sprints e backlog |
| Documentação | **Microsoft Excel** | Controle de dados e planilhas de apoio |

---

## 🗂 Estrutura do Repositório

```
LIBRATOR/
├── Docs/                 # Documentação do projeto (TCC)
├── MVP/                  # Versão inicial e registros das sprints
├── libras-recognizer/    # Versão anterior: uma letra por vez
├── librator/             # Versão atual: montagem de palavras e frases
└── landmarkv2.txt        # Dataset de landmarks
```

O passo a passo técnico (pipeline, coleta de dados, treino e ajustes) está no README da pasta [`librator/`](librator/README.md).

---

## 🚀 Como Executar

Use **Python 3.10 ou 3.11** (as versões do `requirements.txt` não têm pacotes para o 3.12 em diante).

```bash
cd librator

# Ambiente virtual
py -3.11 -m venv venv           # Linux/Mac: python3.11 -m venv venv
venv\Scripts\activate           # Linux/Mac: source venv/bin/activate

# Dependências
pip install -r requirements.txt

# (Opcional) coletar mais amostras de letras
python collect_data.py

# Treinar o modelo
python train_model.py

# Abrir a aplicação
python app.py
```

Acesse **http://localhost:5000** no navegador.

> O dataset em `data/landmarks_dataset.csv` deve conter as letras de A a Z. Sempre que ele mudar, treine o modelo de novo e reinicie o `app.py`.

---

## 📋 Product Backlog

| Rank | Prioridade | User Story | Estimativa | Sprint |
|:---:|:---:|:---|:---:|:---:|
| 1 | 🔴 Alta | Conversão automática dos sinais para texto | 5 | 1 |
| 2 | 🔴 Alta | Histórico das frases traduzidas | 8 | 1 |
| 3 | 🔴 Alta | Detecção das mãos (visão computacional) | 5 | 2 |
| ... | 🟡 Média | ... | ... | ... |
| 17 | 🟢 Baixa | Brindes | 2 | 3 |

> 📌 *Backlog em atualização contínua conforme evolução das sprints.*

---

## 💡 Competências Desenvolvidas

- Visão computacional aplicada à detecção e rastreamento de mãos
- Treinamento e avaliação de modelos de classificação (Machine Learning)
- Desenvolvimento de aplicação web com Flask e streaming de vídeo
- Coleta, organização e tratamento de datasets
- Trabalho em equipe com metodologias ágeis (Scrum)
- Organização e priorização de backlog de produto
- Documentação técnica de projetos

---

## 🗓 Registro das Sprints

| Sprint | Previsão | Status | Histórico |
|:---:|:---:|:---:|:---:|
| 01 | dd/mm/aaaa | 🔲 A fazer | [MVP](MVP/sp1.md) |
| 02 | dd/mm/aaaa | 🔲 A fazer | [MVP](MVP/sp2.md) |
| 03 | dd/mm/aaaa | 🔲 A fazer | [MVP](MVP/sp3.md) |
| Feira de Soluções | dd/mm/aaaa | 🔲 A fazer | [MVP](#) |

---

<div align="center">

Feito com 💙 pela equipe **Librator**

</div>
