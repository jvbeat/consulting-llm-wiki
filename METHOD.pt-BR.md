# O LLM wiki de consultoria

Este é o método por trás do repositório: uma base de conhecimento para consultor que entrega sistemas para vários clientes ao mesmo tempo, operada por um agente de IA (o Claude Code) e curada por uma pessoa. O código aqui é um kit pequeno que impõe o método. O método importa mais que o código, e pode ser adotado com qualquer agente que leia arquivos.

## O problema

Um consultor que toca a entrega de seis clientes ao mesmo tempo toma centenas de decisões por mês, quase sempre com outra pessoa. Uma regra acordada num workshop em abril é refinada por e-mail em maio, revertida pelo sponsor em junho e perguntada de novo em agosto. O conhecimento existe, espalhado em transcrições, threads e documentos que pareciam finais quando foram escritos.

Um agente de IA com acesso a esse material piora a situação antes de melhorá-la. Ele lê a nota de abril, encontra uma frase clara e responde com segurança. Nada na nota diz que a frase morreu em junho. O erro mais caro numa base de conhecimento de consultoria não é o documento que falta nem o link quebrado. O erro mais caro é a decisão antiga lida como vigente, por uma pessoa ou por um agente, e repetida ao cliente.

## A ideia

O Andrej Karpathy descreveu o LLM wiki: o material bruto entra intocado, um agente o destila num wiki, e um schema diz ao agente como mantê-lo. As operações de ingest, query e lint o mantêm em dia. Este método parte daí e acrescenta o que o trabalho com cliente exige:

- uma camada separada por cliente, para que o conhecimento de um cliente nunca responda pergunta sobre outro;
- travas de fonte, para que a afirmação morta não passe por viva;
- peso de fala, para que o brainstorm de uma reunião não seja registrado como decisão;
- templates de entregável, para que o conhecimento seja transformado em requisito, card de tarefa e status report;
- regras aplicadas por hook, porque a regra escrita em prosa é esquecida justamente quando é necessária.

O agente faz a escrituração. A pessoa decide o que importa.

## Camadas

O vault segue o PARA (projetos, áreas, recursos e arquivo), com uma caixa de entrada na frente.

```
0-Inbox/        captura rápida, varrida toda semana
1-Projects/     uma pasta por cliente: _raw, _curated, deliverables, workbook, log
2-Areas/        responsabilidades contínuas
3-Resources/    conhecimento que vale para mais de um cliente
4-Archive/      projetos encerrados
_meta/          configuração, templates, mapa de autoridade, registro de feedback
```

Cada camada tem o seu `CLAUDE.md`. O Claude Code o lê sozinho quando abre um arquivo daquela camada, então a regra específica da camada chega junto com o conteúdo. O schema é um contrato: se a sessão ainda não leu nada de uma camada, ela abre o schema antes de escrever ali.

Dentro de um projeto, `_raw/` guarda evidência e nunca é editado depois de gravado. `_curated/` guarda o que o agente destilou e a pessoa aprovou. `deliverables/` guarda o que vai para o cliente.

## Operações

Toda interação com o vault é uma destas operações.

- O ingest acontece quando chega material. O arquivo bruto é gravado primeiro, intocado. Depois o agente o lê, pesa quem disse o quê e discute as conclusões com a pessoa antes de escrever qualquer coisa na camada curada.
- O generate produz um entregável a partir do workbook, da matriz de decisões e de um template, com toda lacuna marcada como `[PENDING]` em vez de preenchida com algo plausível.
- O query responde uma pergunta a partir do estado atual e da fonte canônica daquele domínio, cita as duas e diz o que não foi conferido.
- O lint faz a manutenção. Um script confere as travas de fonte e reporta o que quebrou.

Toda operação termina com uma linha no log da camada que ela tocou, com prefixo fixo (`## [2026-10-01] ingest | transcript | Workshop de fidelidade`), para que o histórico possa ser lido com um grep.

## Travas de fonte

Elas são o núcleo do método. Cada uma fecha um caminho pelo qual uma decisão antiga é lida como vigente.

### Mapa de fonte canônica

Um projeto que passa de cerca de quinze notas curadas sempre tem duas notas sobre o mesmo assunto: a nota do workshop e a nota de arquitetura, o plano de abril e o plano de setembro. Por isso o `CLAUDE.md` do projeto abre com uma tabela que nomeia a única fonte da verdade para cada tipo de pergunta. O agente lê essa linha antes de abrir qualquer nota. O lint reprova projeto pesado sem a tabela.

### Supersessão em nível de afirmação

Tirar do caminho de leitura um documento morto resolve o caso fácil. O caso difícil é a afirmação morta dentro de um documento vivo. A linha não avisa que morreu, e o próximo leitor confia nela. Por isso a afirmação morta leva um callout com duas informações:

```markdown
> [!superseded] 2026-09-16 · replaced by [[#D4]]
> Was: tiers recalculated every quarter.
```

A data diz quando ela morreu. O link diz o que vale agora. O lint reprova o callout sem uma das duas, porque avisar que a afirmação morreu sem dizer o sucessor é pior que o silêncio: o leitor descobre que a linha está errada e não tem para onde ir. O lint também reprova a decisão que diz superar outra enquanto a outra segue sem marca, e o callout cujo sucessor não existe.

### Vigência do documento canônico

O documento canônico declara quando foi conferido contra a realidade pela última vez:

```yaml
---
canonical: integration-architecture
verified-on: 2026-10-20
---
```

A data não é a da última edição. Editar o arquivo não o torna verdadeiro. A data só muda quando alguém comparou o documento com o cliente, com o sistema ou com a matriz de decisões. O lint avisa depois de 45 dias.

### Estado atual como projeção

O log cresce pelo topo e ninguém o lê inteiro. O fato registrado em julho que ainda vale fica invisível, e o fato revertido em setembro continua lá sem marca. Por isso cada projeto mantém o `current-state.md`: o que vale hoje, por domínio, no presente, em cerca de 150 linhas. Quando algo muda, a linha é reescrita, nunca acrescentada. O lint reprova o estado atual conferido antes da última ingestão ou decisão registrada no log.

## Peso de fala

Nem tudo o que é dito numa reunião é decisão, e nem todo mundo na sala decide tudo. Antes de registrar um item como decidido, o agente o pesa em dois eixos:

- quem falou: o dono daquele domínio, um especialista sem alçada ali, alguém ainda aprendendo o assunto ou alguém de fora;
- o que foi dito: decisão, proposta, brainstorm ou dúvida. Hesitações como "acho que", "talvez" e "e se" rebaixam o item a proposta.

Só é registrada como DECIDIDA a fala de decisão do dono do domínio. Todo o resto é PROPOSTO até ser confirmado. Na dúvida, o item é rebaixado. O mapa de quem decide o quê fica em `_meta/authority-map.md` e cresce a cada reunião. A regra vale também para o dono do vault: pensar em voz alta numa reunião não é compromisso. O resumo de reunião feito por IA que lista "decisões" conta como proposta até ser conferido contra a transcrição.

## Toda resposta declara a sua base

Cada afirmação factual numa resposta tem uma de três bases: medida agora, lida na fonte agora ou não conferida. Quando a afirmação não foi conferida, isso é dito por extenso, dentro da frase. Uma palavra como "provavelmente" não é declaração.

Quando a pessoa contesta uma resposta, o agente reabre a fonte antes de responder, e a resposta começa por "Mantenho", com a evidência, ou por "Mudo", com a evidência nova. Mudar de posição sem evidência nova não é permitido. Concordar para encerrar a discussão é pior que sustentar a posição.

## O feedback é promovido a regra

Toda correção feita pela pessoa é registrada em `_meta/feedback-log.md`, com o que aconteceu, por que a correção vale e como aplicá-la. Quando o mesmo tipo de correção aparece três vezes, ele é promovido a um `CLAUDE.md`. A correção mais recente vale.

## Regras são aplicadas por hook

A lição de desenho mais importante veio de ver as regras falharem. Uma regra escrita num schema era seguida na maior parte do tempo e esquecida no pior momento: no fim de uma sessão longa, quando o commit nunca acontecia, ou no meio de um rascunho, quando a regra de escrita perdia para o hábito. A correção foi tirar da prosa toda regra que custou uma sessão e colocá-la num hook:

- o hook de início de sessão sincroniza o vault antes de qualquer escrita e reporta as travas quebradas;
- o hook de fim avisa trabalho sem commit e sem push ao final de cada turno;
- o gate de escrita confere todo markdown que o agente grava e devolve as linhas com problema.

A regra que fica num hook é aplicada sempre. A regra que fica em prosa é aplicada quando alguém se lembra dela.

## O que fica privado

O vault guarda material de cliente e precisa ficar num repositório privado. O que está público aqui é o método, o kit e um exemplo fictício. O kit em si não envia nada para fora: os hooks são executados localmente, e a única chamada a modelo é a checagem opcional de contradição, feita pela sua própria sessão do Claude Code. O Claude Code, por sua vez, envia ao provedor do modelo o que lê, nos termos da sua conta. Confira o contrato e a política de dados de cada cliente antes de arquivar o material dele no vault, e deixe dado pessoal de fora.

## De onde isso veio

O método foi construído ao longo de um ano tocando a entrega de vários clientes de Salesforce, Braze e Insider One ao mesmo tempo, numa consultoria parceira no Brasil. Cada trava existe porque a falta dela custou tempo real: uma decisão ressuscitada na frente do cliente, um status respondido a partir de uma nota velha, um brainstorm registrado como compromisso.
