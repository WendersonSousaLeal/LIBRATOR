# LIBRATOR — Leitor de Libras em Tempo Real

Sistema web para reconhecimento do alfabeto manual de Libras (**A–Z**) via
câmera, usando MediaPipe (extração de landmarks da mão) + RandomForest
(classificação) + Flask (interface web com streaming de vídeo).

Além de reconhecer uma letra por vez, o sistema agora **monta palavras e
frases**: as letras confirmadas vão formando o texto, com comandos para dar
espaço entre palavras e para encerrar a palavra e passar para a linha de baixo.

Exemplo: sinalizando as letras e usando os comandos de espaço e de nova linha,

```
O → L → A → [espaço] → M → U → N → D → O → [nova linha]
B → O → M → [espaço] → D → I → A → [nova linha]
```

o texto montado na tela fica:

```
OLA MUNDO
BOM DIA
```

Como o reconhecimento é do alfabeto manual (A–Z), o texto sai em letras
maiúsculas, sem acentos e sem pontuação.

## Estrutura do projeto

```
LIBRATOR/
├── Docs/                     # Documentação (TCC)
├── MVP/                      # Versão inicial
├── libras-recognizer/        # Versão anterior (uma letra por vez)
└── librator/                 # Versão atual (montagem de frases)
    ├── app.py                # Servidor Flask (streaming + predição + montagem do texto)
    ├── collect_data.py       # Script de coleta de dados via câmera
    ├── train_model.py        # Script de treinamento do RandomForest
    ├── hand_utils.py         # Módulo compartilhado: MediaPipe + normalização
    ├── requirements.txt
    ├── README.md
    ├── data/
    │   └── landmarks_dataset.csv     (dataset A–Z; gerado/acrescentado por collect_data.py)
    ├── models/
    │   ├── hand_landmarker.task      (baixado automaticamente na 1ª execução)
    │   └── libras_rf_model.pkl       (gerado por train_model.py)
    └── templates/
        └── index.html        # Interface web (viewfinder + painel de leitura)
```

> O `index.html` precisa ficar dentro de `templates/`, senão o Flask retorna
> `TemplateNotFound`.

## Como o pipeline funciona

1. **Captura**: o OpenCV lê os frames da câmera (webcam ou celular).
2. **Extração**: o MediaPipe HandLandmarker detecta a mão e retorna 21
   pontos (x, y, z) por frame.
3. **Normalização** (`hand_utils.normalize_landmarks`): os pontos são
   deslocados para que o pulso vire a origem (0,0,0) e depois escalados
   pela distância pulso → base do dedo médio. Isso torna o reconhecimento
   independente de onde a mão está na tela e de quão perto/longe da câmera
   o usuário está. A orientação da mão é preservada de propósito, pois em
   Libras ela é parte do significado do sinal.
4. **Velocidade (opcional, ligado por padrão)**: para ajudar a reconhecer
   as letras com movimento (H, J, K, X, Z), cada frame também guarda a
   diferença entre a posição normalizada atual e a do frame anterior,
   dobrando o vetor de features de 63 para 126 valores.
5. **Classificação**: o vetor de features é passado para o
   `RandomForestClassifier` treinado, que retorna a letra + a confiança.
6. **Suavização**: a aplicação faz uma votação por maioria entre as últimas
   predições antes de aceitar uma letra, evitando "piscar" entre letras
   erradas de frame a frame.
7. **Montagem do texto**: a letra estável é confirmada e adicionada à palavra
   atual. Os comandos de espaço e de nova linha organizam o texto em palavras
   e frases.

## Guia de execução

```bash
# 1. Entrar na pasta do projeto
cd librator

# 2. Criar e ativar um ambiente virtual (use Python 3.10 ou 3.11)
py -3.11 -m venv venv           # Linux/Mac: python3.11 -m venv venv
venv\Scripts\activate           # Linux/Mac: source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. (Opcional) Coletar mais dados de treinamento
python collect_data.py

# 5. Treinar o modelo com os dados coletados
python train_model.py

# 6. Rodar a aplicação web
python app.py
# Acesse http://localhost:5000 no navegador
```

> As versões fixadas no `requirements.txt` (`numpy==1.26.4`,
> `mediapipe==0.10.14`) não têm pacotes para Python 3.12 em diante. No Windows,
> o 3.11 pode ser instalado com `winget install Python.Python.3.11`.

### Coleta de dados (`collect_data.py`)

- Clique na janela da câmera, aperte uma letra (A–Z) e use **ESPAÇO** para
  gravar uma amostra ou **C** para gravação contínua. **ESC** encerra.
- O script **acrescenta** ao CSV, então dá para rodar várias vezes.
- Antes de trocar de letra no modo contínuo, desligue com **C** de novo.

### Dataset

O dataset em `data/landmarks_dataset.csv` já cobre as letras de **A a Z**.
Para conferir:

```python
import pandas as pd
df = pd.read_csv("data/landmarks_dataset.csv")
print(df.shape)
print(df["label"].value_counts().sort_index())
```

Sempre que o dataset mudar, rode `train_model.py` de novo e reinicie o
`app.py`: o modelo só é carregado na inicialização.

## Comandos da interface

<!-- Confirme as teclas/botões de acordo com o app.py e o index.html atuais -->

| Ação | Como fazer | Resultado |
|------|------------|-----------|
| Formar letras | Faça o sinal e mantenha estável | A letra confirmada entra na palavra |
| Dar espaço | `[tecla/botão de espaço]` | Separa uma palavra da outra |
| Encerrar e ir para a linha de baixo | `[tecla/botão de nova linha]` | Fecha a palavra e começa uma nova linha |

## Usando o celular como câmera

Apps como Iriun Webcam e DroidCam criam uma câmera virtual no Windows. Para
descobrir o índice dela:

```bash
python -c "import cv2; [print(i, cv2.VideoCapture(i, cv2.CAP_DSHOW).isOpened()) for i in range(4)]"
```

Troque o índice em `collect_data.py` e `app.py`:

```python
cv2.VideoCapture(2, cv2.CAP_DSHOW)   # use o índice que deu True
```

Use a mesma câmera, posição e rotação na coleta e no app.

## Onde editar

| Quero mudar... | Arquivo | O quê |
|----------------|---------|-------|
| Sensibilidade da detecção | `app.py` | `CONFIDENCE_THRESHOLD`, `SMOOTHING_WINDOW`, `STABILITY_MIN_RATIO` |
| Features de movimento | `hand_utils.py` | `INCLUDE_VELOCITY` (True/False) |
| Letras com movimento | `hand_utils.py` | `MOVEMENT_LETTERS` |
| Parâmetros do modelo | `train_model.py` | bloco `RandomForestClassifier(...)` |
| Visual da página | `templates/index.html` | CSS no `<style>` e JS no final |
| Câmera usada | `app.py` e `collect_data.py` | índice do `cv2.VideoCapture` |

Se mudar `INCLUDE_VELOCITY`, apague o CSV, recolete tudo e treine de novo: o
número de colunas muda (63 vs 126) e dados antigos ficam incompatíveis.

## Dicas de otimização para letras com movimento/variação

- **Features de velocidade**: habilitadas por padrão em `hand_utils.py`
  (`INCLUDE_VELOCITY = True`). Dão ao RandomForest um sinal direto de "quanto
  e para onde" a mão se moveu entre dois frames, sem precisar de um modelo
  sequencial (LSTM/GRU).
- **Coleta em modo contínuo**: para H, J, K, X e Z, use a tecla `C` em
  `collect_data.py` e faça o gesto completo várias vezes.
- **Não normalize a rotação**: letras como K/H/P ou G/Q têm dedos parecidos e
  se diferenciam pela orientação da mão.
- **Suavização temporal**: a votação por maioria em `app.py`
  (`SMOOTHING_WINDOW`, `STABILITY_MIN_RATIO`) reduz o efeito de frames
  ruidosos durante o movimento.
- **Limiar de confiança**: `CONFIDENCE_THRESHOLD` descarta predições em que o
  modelo está pouco confiante.
- **Quantidade e diversidade de dados**: colete 150–300 amostras por letra,
  variando distância, ângulo, iluminação e, se possível, mais de uma pessoa.
  `train_model.py` avisa quando alguma letra tem poucas amostras.
- **class_weight="balanced"**: já usado em `train_model.py` para compensar
  letras com menos amostras.
- **Feature importance**: `train_model.py` imprime as 10 features mais
  importantes, útil para ver se o modelo usa landmarks que fazem sentido.
- **Relatório otimista**: frames do modo contínuo são quase idênticos entre si
  e caem no treino e no teste. Se o app errar mais do que o relatório sugere,
  colete com mais variação e em sessões diferentes.
- **Limite do RandomForest**: ele classifica cada frame de forma
  independente. Para sinais dinâmicos mais longos (palavras inteiras em
  Libras), o próximo passo seria um modelo sequencial (ex.: LSTM).

## Tratamento de "nenhuma mão visível"

Tanto em `collect_data.py` (overlay "Nenhuma mao detectada" + amostras
ignoradas) quanto em `app.py` (buffer de suavização limpo e painel com
"Aguardando mão no quadro...") o sistema trata explicitamente a ausência de
mão, em vez de prever uma letra a partir de dados inexistentes.

## Problemas comuns

| Problema | Solução |
|----------|---------|
| `pip install` falha no mediapipe | Use Python 3.10/3.11 |
| `No module named 'cv2'` | Ative o venv antes de abrir o Python |
| `TemplateNotFound` | Mova o `index.html` para `templates/` |
| App reconhece só algumas letras | O CSV em `data/` está antigo; confira com `value_counts()` e treine de novo |
| Câmera não abre | Feche Zoom/Teams, troque o índice ou use `cv2.CAP_DSHOW` |
| `mp.solutions` não existe | Fixe `mediapipe==0.10.14` |
| Modelo não encontrado | Rode `train_model.py` antes do `app.py` |

## Tecnologias

Python · OpenCV · MediaPipe · scikit-learn · pandas · NumPy · Flask · HTML/CSS/JS
