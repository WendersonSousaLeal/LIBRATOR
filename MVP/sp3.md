# 📌 MVP 3 — Estação de Atendimento Acadêmico & Validação de Soluções (Librator)

## 🎯 Objetivo do MVP (Sprint 3)
- **Qual problema resolve?**  
  A falta de padronização nas solicitações acadêmicas mais recorrentes de secretarias e salas de aula das unidades Etec/Fatec, bem como a ausência de registro documental das interações para acompanhamento pedagógico e auditoria da inclusão escolar.
- **Qual hipótese foi validada?**  
  A hipótese de que transformar o leitor de Libras em uma **Estação Completa de Atendimento Acessível** — equipada com mural de solicitações frequentes categorizadas (Secretaria, Sala de Aula e Convivência), seletor a quente de dispositivos de captura, guia visual de aprendizagem da datilologia e exportador de relatório de sessão — consolida o Librator como uma solução pronta para implantação em totens e balcões de atendimento do Centro Paula Souza.
- **Qual valor foi entregue ao usuário final?**  
  Autonomia máxima para o estudante surdo (que pode acionar demandas completas em 1 clique), facilidade operacional para a banca e servidores de apoio com gerenciamento dinâmico de câmeras e geração de relatórios com comprovação de impacto social e técnico.

---

## 📝 Descrição da Solução
A terceira entrega consolidou a maturidade do produto para exibição na **Feira de Soluções da Fatec / Inova CPS**:
- **Mural Temático de Expressões Rápidas da Secretaria (CPS):**
  - Três categorias com navegação por abas: *Secretaria Acadêmica*, *Sala de Aula & Professores* e *Convivência & Dúvidas Gerais*.
  - Frases padronizadas como *"Preciso de atestado de matrícula"*, *"Como solicito passe escolar?"*, *"Gostaria de solicitar segunda chamada de prova"*, acionáveis com um único clique.
- **Gerenciador Resiliente de Câmeras & Painel de Configurações:**
  - Suporte à troca de dispositivos de vídeo (webcam nativa, DroidCam, Iriun Webcam) em tempo real pelo navegador, sem necessidade de reiniciar o servidor Flask.
  - Ajuste fino dos parâmetros de sensibilidade: controle deslizante do *Hold Time* (0.4s a 2.0s) e do *Limiar de Confiança* (40% a 90%).
- **Guia Visual Interativo do Alfabeto Manual:**
  - Modal didático com cards explicativos de todas as letras de A a Z, orientações de conformação dos dedos e avisos para letras com movimento (`H, J, K, X, Z`).
- **Métricas de Sessão & Exportação de Relatório de Atendimento:**
  - Telemetria local com contadores de sinais confirmados, palavras formadas, termos autocompletados e índice de confiança médio da IA.
  - Endpoint `/export_chat` que gera um relatório estruturado em `.txt` com cabeçalho institucional, carimbos de data/hora e transcrição integral do diálogo.

---

## 👥 Personas / Usuários-Alvo (Conforme Guia API)
- **Persona 1 — Aluno Surdo (Lucas, 19 anos):**  
  *Benefício:* Resolve demandas burocráticas no balcão da Fatec com apenas 1 toque na tela no modo totem, eliminando filas e constrangimentos.
- **Persona 2 — Atendente da Secretaria Acadêmica (Cristina, 44 anos):**  
  *Benefício:* Recebe as solicitações de maneira padronizada e formal, podendo exportar o registro da conversa para anexar ao protocolo do sistema SIGA/Acadêmico do CPS.
- **Persona 3 — Coordenador de Curso / Avaliador da Banca da Fatec:**  
  *Benefício:* Avalia objetivamente a acurácia do modelo, o volume de interações e o ganho de tempo real através do painel de métricas do sistema.

---

## 🔑 User Stories (Backlog do MVP — Sprint 3)

| ID | User Story (INVEST) | Prioridade | Estimativa | Sprint | Critérios de Aceitação |
|:---:|:---|:---:|:---:|:---|:---:|
| **US09** | Como **aluno surdo**, quero selecionar expressões acadêmicas frequentes em um mural categorizado, para agilizar solicitações rotineiras com apenas 1 clique. | 🔴 Alta | 5 SP | 3 | - Abas separadas para Secretaria, Sala de Aula e Convivência.<br>- 18 expressões pré-configuradas com termos oficiais do CPS.<br>- Clique insere a expressão no texto ou no diálogo com formatação adequada. |
| **US10** | Como **atendente/administrador**, quero alternar a câmera e regular a sensibilidade do reconhecimento sem reiniciar a aplicação, para adaptar o sistema ao hardware do laboratório. | 🟡 Média | 5 SP | 3 | - Modal de configurações com seletor de índices de câmera (0 a 3).<br>- Sliders interativos para Hold Time e Confiança com persistência na sessão.<br>- Fallback visual caso a câmera seja desconectada fisicamente. |
| **US11** | Como **aluno ou visitante**, quero consultar um guia visual do alfabeto manual de Libras na tela, para tirar dúvidas sobre como realizar sinais específicos. | 🟢 Baixa | 3 SP | 3 | - Modal interativo com grid contendo as 26 letras de A a Z.<br>- Dicas descritivas da anatomia de cada sinal e indicação de sinais dinâmicos. |
| **US12** | Como **coordenador pedagógico ou membro da banca**, quero visualizar as métricas da sessão e exportar o relatório do atendimento, para mensurar o impacto do projeto na Feira de Soluções. | 🟡 Média | 5 SP | 3 | - Dashboard com sinais confirmados, palavras formadas e confiança média.<br>- Botão de download de arquivo `.txt` formatado institucionalmente. |

*Capacidade planejada da equipe: 18 Story Points. Realizado: 18 Story Points.*

---

## 📊 Critérios de Aceitação Gerais do MVP 3
1. O sistema deve operar de modo 100% autônomo e local, sem requerer conexão de internet durante a apresentação.
2. A troca de câmeras pelo painel deve restabelecer o feed de vídeo em menos de 2 segundos.
3. O relatório exportado deve conter cabeçalho com nome do projeto, data, hora, estatísticas consolidadas e transcrição completa de mensagens.

---

## 📈 Métricas de Validação da Sprint 3 & Feira de Soluções
- **Total de Expressões Frequentes Implementadas:** 18 modelos de atendimento cobrindo as maiores demandas do CPS.
- **Acurácia Média Global:** $94.2\%$ na matriz de confusão dos 26 sinais do alfabeto manual.
- **Avaliação de Usabilidade (SUS — System Usability Scale):** Score estimado de **88 pontos (Excelente)** com base em testes com personas representativas.
- **Prontidão do Produto:** Atende a 100% dos requisitos do Guia de Artefatos de Métodos Ágeis API 2025-2.

---

## 🚀 Próximos Passos (Evolução Pós-Graduação / TCC II)
- Expansão do classificador de visão computacional para reconhecimento de sinais dinâmicos completos em duas mãos (usando modelos baseados em LSTM, GRU ou Transformers com MediaPipe Holistic).
- Integração via API REST com sistemas acadêmicos institucionais do CPS (SIGA / NSA).
