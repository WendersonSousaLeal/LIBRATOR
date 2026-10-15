# 📌 MVP 2 — Produtividade Acadêmica & Acessibilidade Bidirecional (Librator)

## 🎯 Objetivo do MVP (Sprint 2)
- **Qual problema resolve?**  
  A lentidão intrínseca da soletração datilológica pura (demora média de 40 a 60 segundos por frase simples), que desmotiva o uso prático em balcões de atendimento, e a falta de retorno auditivo para o interlocutor ouvinte.
- **Qual hipótese foi validada?**  
  A hipótese de que a introdução de uma barra de predição inteligente com termos frequentes do cotidiano escolar de Etecs e Fatecs (ex.: *Matrícula, Atestado, Horário, Professor, Prova, Falta*), aliada à síntese de voz (TTS) nativa do navegador, reduz o tempo de composição em mais de 70% e viabiliza a comunicação bidirecional sem custo de infraestrutura.
- **Qual valor foi entregue ao usuário final?**  
  O estudante surdo agora soletra apenas o início da palavra e clica no termo desejado (ou usa atalhos rápidos), podendo reproduzir a frase em voz audível para o atendente ouvinte, que por sua vez dispõe de um canal de resposta imediato na mesma interface.

---

## 📝 Descrição da Solução
Nesta segunda entrega, o foco migrou da viabilidade técnica do modelo para a **produtividade e usabilidade comunicativa**:
- **Módulo de Predição de Palavras Escolares (Autocompletar T9 Acadêmico):**
  - Implementação de um banco léxico com mais de 45 termos do ecossistema do Centro Paula Souza.
  - Exibição de chips preditivos dinâmicos conforme o aluno soletra duas ou mais letras.
  - Seleção via clique ou atalho de teclado (`Alt + 1..3`), inserindo a palavra completa com espaçamento automático.
- **Módulo de Síntese de Voz (Text-to-Speech — TTS):**
  - Integração com a *Web Speech Synthesis API* nativa (`lang: 'pt-BR'`), sem necessidade de conexões com APIs de nuvem externas ou cobranças financeiras.
  - Botão **"🔊 Ouvir Frase"** com pronúncia clara em língua portuguesa.
- **Canal de Resposta do Ouvinte:**
  - Campo de réplica direta para o atendente/professor com suporte a digitação e ditado por voz (*Web Speech Recognition*).
  - Exibição da resposta em destaque visual para facilitar a leitura por pessoas com deficiência auditiva.
- **Adaptação de Acessibilidade Visual (WCAG 2.1):**
  - Modo Alto Contraste com paleta de alta luminância para estudantes com baixa visão comórbida.
  - Controle de escala tipográfica dinâmica (A+ / A-).

---

## 👥 Personas / Usuários-Alvo (Conforme Guia API)
- **Persona 1 — Aluno Surdo (Lucas, 19 anos):**  
  *Benefício:* Comunicação até 4x mais rápida em requerimentos na secretaria escolar; certeza de que sua mensagem foi escutada pelo atendente ouvinte.
- **Persona 2 — Atendente da Secretaria Acadêmica (Cristina, 44 anos):**  
  *Benefício:* Escuta a solicitação do aluno por áudio sem precisar decodificar o alfabeto manual; digita a resposta diretamente no sistema com visibilidade imediata.

---

## 🔑 User Stories (Backlog do MVP — Sprint 2)

| ID | User Story (INVEST) | Prioridade | Estimativa | Sprint | Critérios de Aceitação |
|:---:|:---|:---:|:---:|:---|:---:|
| **US05** | Como **aluno surdo**, quero receber sugestões de termos acadêmicos (ex.: `AULA`, `MATRICULA`) enquanto soletro, para concluir palavras rapidamente sem digitar letra por letra. | 🔴 Alta | 8 SP | 2 | - Sugestões aparecem em tempo real a partir de 2 letras digitadas.<br>- Clique no chip ou atalho `Alt+1..3` completa a palavra no texto.<br>- Adiciona espaço automaticamente após o termo selecionado. |
| **US06** | Como **aluno surdo**, quero que a frase que montei seja lida em voz alta pelo computador, para que o atendente ouvinte compreenda o que eu disse sem precisar olhar fixamente para a tela. | 🔴 Alta | 5 SP | 2 | - Acionamento pelo botão "Ouvir Frase" ou atalho.<br>- Voz sintetizada em português do Brasil com fala fluida e sem pausas robóticas.<br>- Tratamento de cancelamento de fala em caso de múltiplos cliques. |
| **US07** | Como **atendente ouvinte**, quero um campo simples para responder ao aluno digitando na tela, para que o diálogo seja mantido de forma bidirecional. | 🟡 Média | 5 SP | 2 | - Campo de texto para resposta com envio via tecla `Enter`.<br>- Balões de diálogo distintos para aluno e atendente no feed da tela.<br>- Opção de ditado por voz via microfone para o atendente. |
| **US08** | Como **usuário com baixa visão**, quero alternar para um tema de alto contraste e ampliar o tamanho da fonte, para ler os textos com conforto e acessibilidade. | 🟡 Média | 3 SP | 2 | - Botão de alternância com padrão de cores WCAG AAA (fundo escuro puro e elementos ciano/amarelo).<br>- Botões de zoom de fonte A+ e A- redimensionando todos os textos do app. |

*Capacidade planejada da equipe: 21 Story Points. Realizado: 21 Story Points.*

---

## 📊 Critérios de Aceitação Gerais do MVP 2
1. O autocompletar deve filtrar a lista de termos em menos de 10 ms no navegador sem degradação do vídeo.
2. A voz sintetizada deve funcionar de modo assíncrono sem travar a interface ou a thread de captura de vídeo do Flask.
3. As respostas digitadas pelo atendente devem ser visíveis a pelo menos 1,5 metros de distância do monitor em monitores comuns de 19 a 24 polegadas.

---

## 📈 Métricas de Validação da Sprint 2
- **Tempo Médio de Escrita de Termos Acadêmicos:** Redução de $42,5\text{ segundos}$ (soletração pura) para $7,8\text{ segundos}$ (com autocompletar e atalhos).
- **Taxa de Aceitação da Síntese de Voz:** $100\%$ de compreensão auditiva nos testes de validação com 5 servidores ouvintes.
- **Conformidade de Acessibilidade:** Contraste de cores superior a 7:1 no modo alto contraste (atendendo ao nível AAA da WCAG 2.1).

---

## 🚀 Próximos Passos (Planejado para a Sprint 3)
- Criar o **Modo Guichê de Atendimento / Mural de Expressões Frequentes** com cartões temáticos de 1 clique.
- Implementar painel de métricas da sessão e exportação de relatório para a Feira de Soluções da Fatec/Etec.
- Desenvolver guia visual interativo do alfabeto manual para suporte pedagógico à banca e novos usuários.
