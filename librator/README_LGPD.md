# 🔒 Privacidade e LGPD no Librator

Este documento explica como o **Librator** (Tradutor de Libras para texto) trata dados pessoais e como o projeto se relaciona com a **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)**.

> ⚠️ Este texto é uma análise técnica feita pela equipe, **não um parecer jurídico**. Se o sistema for usado de fato em uma escola ou por terceiros, consulte o orientador ou o encarregado de dados da instituição.

---

## 1. Que dados o sistema usa?

| Dado | Origem | Tratamento |
|---|---|---|
| Imagem da webcam (vídeo) | Usuário, em tempo real | Usada apenas para detectar a mão e reconhecer a letra ou o número |
| 21 pontos de referência da mão (*landmarks*) | Extraídos pelo MediaPipe | Coordenadas numéricas; são o que alimenta o classificador |
| Dataset de treino (`landmarks_dataset.csv`) | Coletado pela própria equipe | Contém coordenadas dos landmarks e o rótulo da letra, sem nome nem imagem |
| Texto digitado na aba "Texto → Libras" | Usuário | Enviado ao widget oficial VLibras (gov.br) para gerar a tradução |

## 2. Por que o risco é baixo (e onde exige atenção)

- **Landmarks não são imagens.** Coordenadas de pontos da mão, sem rosto ou fundo, dificilmente identificam alguém por si sós.
- **A finalidade é reconhecer gestos, não pessoas.** O sistema não faz identificação nem autenticação biométrica.
- **A imagem da câmera é o ponto sensível.** Rosto, mãos e fundo são dados pessoais se forem gravados ou enviados a algum lugar. Por isso o princípio central do projeto é **não armazenar nem transmitir frames**.
- **Dado biométrico é dado sensível** quando vinculado a uma pessoa (art. 5º, II). Como o sistema não vincula os landmarks a ninguém, a tendência é ficar fora dessa categoria, e a equipe documenta isso de propósito.

## 3. Princípios da LGPD aplicados ao projeto

| Princípio | Como o Librator o atende |
|---|---|
| **Finalidade** | Os dados servem só para traduzir sinais estáticos de Libras em texto |
| **Adequação** | O tratamento é compatível com a finalidade informada ao usuário |
| **Necessidade (minimização)** | Só os 21 landmarks são usados; nenhuma imagem entra no dataset |
| **Transparência** | A interface deve informar, de forma clara, que a câmera é usada para reconhecer gestos |
| **Segurança** | Sem armazenamento de vídeo; HTTPS caso o sistema seja publicado |
| **Prevenção** | Sem logs, analytics ou cookies que guardem dados do usuário |

## 4. Base legal e exceção acadêmica

A LGPD não se aplica ao tratamento feito exclusivamente para **fins acadêmicos**, mas **os arts. 7º e 11 continuam valendo** nesse caso. Ou seja, é preciso ter uma base legal. No Librator:

- **Dataset:** foi montado pela equipe, e cada integrante que contribuiu com amostras consentiu com o uso (declaração simples, registrada pela equipe).
- **Usuários em testes:** o uso da câmera depende de **consentimento informado**. A permissão do navegador não substitui o aviso de privacidade na interface.
- **Menores de idade:** se o sistema for testado com alunos menores, o art. 14 exige tratamento no melhor interesse da criança e **consentimento de um dos pais ou responsável**.

## 5. Terceiros: VLibras

A aba "Texto → Libras" usa o **widget oficial do governo (VLibras)**. O texto digitado é processado por esse serviço, que é de terceiros. Por isso:

- o usuário deve ser avisado de que o texto é enviado ao VLibras;
- o Librator **não deve registrar** os textos digitados;
- recomenda-se não digitar dados pessoais (nome, CPF etc.) nessa aba.

## 6. Boas práticas no repositório

- Não versionar fotos, vídeos nem prints de pessoas.
- O dataset deve conter apenas coordenadas e rótulos.
- O modelo treinado (`libras_rf_model.pkl`) contém apenas parâmetros do classificador, não dados dos contribuintes.
- Manter o README técnico consistente com o código. Hoje ele cita `MLPClassifier`, mas o sistema usa **Random Forest**.

## 7. ✅ Checklist antes da apresentação

- [ ] Confirmar no código (`app.py` e rotas que recebem vídeo) que **nenhum frame é salvo em disco ou enviado a terceiros**
- [ ] Confirmar que o script de coleta grava **só landmarks e rótulo**
- [ ] Adicionar **aviso de privacidade** visível antes de ativar a câmera
- [ ] Registrar o **consentimento** de quem contribuiu com o dataset
- [ ] Informar na interface o envio de texto ao **VLibras**
- [ ] Se houver teste com menores, obter **autorização dos responsáveis**
- [ ] Verificar que não há logs, cookies ou analytics coletando dados

## 8. Referência

- [Lei nº 13.709/2018 (LGPD), texto compilado no Planalto](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709compilado.htm)

---

*Equipe Librator: Wenderson Candido, Samuel Domingos, Pedro Vieira e Pietro Oliveira.*
