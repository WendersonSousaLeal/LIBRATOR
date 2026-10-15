# 📌 MVP 1 — Core Datilológico & Pipeline de Visão Computacional (Librator)

## 🎯 Objetivo do MVP (Sprint 1)
- **Qual problema resolve?**  
  A falta de ferramentas acessíveis e em tempo real para interpretação da datilologia (alfabeto manual de Libras) em ambientes computacionais das unidades Etec e Fatec (Centro Paula Souza).
- **Qual hipótese foi validada?**  
  A hipótese de que a extração de 21 marcos anatômicos (landmarks) tridimensionais da mão via MediaPipe Tasks, combinada com normalização espacial (invariante a escala e distância) e um classificador supervisionado (*RandomForestClassifier*), é suficiente para classificar em tempo real as 26 letras do alfabeto manual com acurácia superior a 85%.
- **Qual valor foi entregue ao usuário final?**  
  Capacidade de sinalizar letras diante de qualquer webcam ou celular e vê-las reconhecidas instantaneamente na tela do navegador, compondo palavras com controle temporal de confirmação (*Hold Time*) sem duplicações indevidas.

---

## 📝 Descrição da Solução
Nesta primeira etapa, concebeu-se a espinha dorsal técnica do **Librator**:
- Captura de vídeo contínua via OpenCV com espelhamento horizontal intuitivo (*mirror view*).
- Extração de 21 coordenadas (x, y, z) utilizando a biblioteca **Google MediaPipe Tasks (HandLandmarker)**.
- Normalização matemática das coordenadas: translação fixando o pulso na origem $(0,0,0)$ e fator de escala baseado na distância pulso $\to$ articulação metacarpofalângica do dedo médio.
- Implementação de vetor de features extendido de 126 valores (63 landmarks atuais + 63 gradientes temporais de velocidade) para permitir a classificação de letras dinâmicas (`H, J, K, X, Z`).
- Classificador **Random Forest** treinado com 300 árvores de decisão e balanceamento ponderado de classes (`class_weight="balanced"`).
- Mecanismo de confirmação por tempo de permanência (*Hold Time* de 1 segundo) com feedback visual por anel de progresso circular em SVG.

**Limitações conhecidas da Sprint 1:**
- Reconhecimento focado exclusivamente no alfabeto manual (A–Z); sinais contextuais completos e expressões faciais não são abrangidos.
- Dependência de iluminação ambiente adequada para que o MediaPipe não perca o contraste dos dedos.

---

## 👥 Personas / Usuários-Alvo (Conforme Guia API)
- **Persona 1 — Aluno Surdo (Lucas, 19 anos, Estudante do Curso Técnico/Superior no CPS):**  
  *Dores:* Dificuldade em se expressar com atendentes ouvintes que desconhecem Libras; frustração ao soletrar e ver caracteres duplicados na tela por falta de calibração do sistema.  
  *Atendimento:* Reconhecimento estável letra a letra com feedback visual transparente de quando a letra foi aceita.
- **Persona 2 — Atendente da Secretaria Acadêmica / Professor (Cristina, 44 anos):**  
  *Dores:* Não compreender os sinais manuais e não ter como acompanhar o que o aluno está soletrando.  
  *Atendimento:* Painel de leitura em tempo real com indicador de confiança da inteligência artificial.

---

## 🔑 User Stories (Backlog do MVP — Sprint 1)

| ID | User Story (INVEST) | Prioridade | Estimativa | Sprint | Critérios de Aceitação |
|:---:|:---|:---:|:---:|:---:|:---|
| **US01** | Como **aluno surdo**, quero posicionar minha mão diante da câmera para ter meus sinais manuais rastreados com o esqueleto anatômico sobreposto na imagem. | 🔴 Alta | 5 SP | 1 | - Taxa de detecção da mão estável a no mínimo 20 FPS.<br>- Esqueleto com 21 pontos e conexões desenhados em tempo real.<br>- Mensagem clara na tela caso a mão saia do enquadramento. |
| **US02** | Como **aluno surdo**, quero que cada letra sinalizada com estabilidade seja classificada pelo modelo de machine learning, para formar caracteres na tela. | 🔴 Alta | 8 SP | 1 | - Acurácia mínima de 85% no conjunto de teste estratificado.<br>- Limiar de confiança de corte configurado para evitar falsos positivos.<br>- Votação por maioria temporal nos últimos 8 frames. |
| **US03** | Como **aluno surdo**, quero um indicador visual de tempo de permanência (*hold time*), para saber o instante exato em que a letra foi aceita pelo sistema. | 🔴 Alta | 5 SP | 1 | - Anel de progresso preenchido suavemente durante 1 segundo.<br>- Trava de repetição que impede a inserção de letras repetidas em sequência sem troca de sinal ou afastamento da mão. |
| **US04** | Como **aluno surdo**, quero comandos de teclado e botões para dar espaço, apagar e limpar caracteres, para organizar meu texto livremente. | 🟡 Média | 3 SP | 1 | - Botão e tecla `Espaço` inserem separador entre palavras.<br>- Botão e tecla `Backspace` apagam o último caractere.<br>- Botão de limpeza zera o buffer da frase. |

*Capacidade planejada da equipe: 21 Story Points. Realizado: 21 Story Points.*

---

## 📊 Critérios de Aceitação Gerais do MVP 1
1. O sistema deve carregar o modelo treinado sem dependência de internet após a primeira inicialização.
2. O atraso (latência de inferência) por frame não deve exceder 50 ms em hardware padrão com processador Intel Core i3/i5 ou Ryzen equivalente.
3. As letras com movimento do pulso (`H, J, K, X, Z`) devem apresentar acurácia superior a 80% através do vetor diferencial de velocidade.

---

## 📈 Métricas de Validação da Sprint 1
- **Acurácia Média na Validação Cruzada (5-fold CV):** $94.2\%$ no dataset balanceado de 26 classes.
- **Taxa de Quadros por Segundo (FPS):** Média de 28.4 FPS com resolução de captura 640x480.
- **Tempo de Confirmação por Letra:** 1.0 segundo (ajustável).

---

## 🚀 Próximos Passos (Planejado para a Sprint 2)
- Implementar o recurso de **Autocompletar Preditivo** com vocabulário das unidades Etec e Fatec para reduzir drasticamente o tempo de digitação.
- Integrar síntese de voz nativa (**Text-to-Speech**) em português para que o atendente ouvinte possa ouvir o que o aluno escreveu.
- Adicionar canal de réplica para o atendente responder em texto ampliado.
