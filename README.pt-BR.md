# consulting-llm-wiki

Um LLM wiki para consultor que entrega para vários clientes ao mesmo tempo. O Claude Code cuida da escrituração, você faz a curadoria, e uma decisão antiga deixa de passar por decisão vigente.

[English](README.md) · [O método](METHOD.pt-BR.md)

## Por que existe

Um consultor que toca seis projetos toma centenas de decisões por mês, e boa parte delas é refinada, revertida ou substituída depois. Um agente de IA que lê o vault encontra a nota de abril, confia nela e a repete ao cliente em agosto. O erro mais caro numa base de conhecimento de consultoria não é o documento que falta. O erro mais caro é a decisão morta lida como viva.

Este repositório parte da ideia do [LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) do Karpathy e acrescenta o que a entrega para cliente exige: uma camada por cliente, travas de fonte conferidas por um lint, peso de fala na ingestão de reunião, templates de entregável e hooks que aplicam as regras em vez de depender da memória de alguém.

## O que muda

- **Travas de fonte:** a afirmação morta leva `[!superseded]` com data e link para o que a substituiu, a decisão que supera outra precisa marcar a antiga, o documento canônico declara quando foi conferido contra a realidade, e cada projeto mantém um estado atual que precisa ser reconferido depois de cada ingestão. O lint reprova quando qualquer uma delas quebra.
- **Peso de fala:** na ingestão de reunião, cada item é pesado por quem falou (o dono do domínio, um especialista, alguém aprendendo o assunto) e pelo tipo de fala (decisão, proposta, brainstorm). Só é registrada como DECIDIDA a fala de decisão do dono do domínio.
- **Uma camada por cliente:** a evidência bruta, o conhecimento curado e os entregáveis ficam dentro de cada projeto, com um mapa de fonte canônica que diz ao agente qual nota é a verdade para cada tipo de pergunta.
- **Entregáveis:** há templates de requisitos, card de tarefa, nota de reunião e status report, gerados a partir da matriz de decisões com `[PENDING]` onde falta insumo.
- **Regras como hooks:** o vault sincroniza antes de a sessão escrever, avisa trabalho sem push quando ela termina e confere todo markdown que o agente grava contra a sua régua de escrita (os pacotes em inglês e em português do Brasil vêm junto).

## Como começar

Instale o plugin no Claude Code:

```
/plugin marketplace add jvbeat/consulting-llm-wiki
/plugin install consulting-llm-wiki@consulting-llm-wiki
```

Depois peça ao Claude para criar o seu vault:

```
crie meu vault em ~/consulting-vault
```

A skill `new-vault` copia o template, grava o marcador `.llm-wiki`, que liga os hooks só naquela pasta, e inicializa o git. Mantenha o vault em repositório privado, porque ele vai guardar material de cliente. Para escrever em português, coloque `"writing_packs": ["pt-BR"]` no `_meta/llm-wiki.json`.

Sem o plugin, execute `python3 scripts/new_vault.py ~/consulting-vault` e copie as skills que quiser para `.claude/skills/`.

## As travas funcionando

O repositório traz um cliente fictício, a Northwind Grocers, com quatro problemas plantados de propósito. O comando `python3 scripts/lint.py examples/northwind-vault` encontra os quatro: o callout de supersessão sem data nem sucessor, a decisão D5 que supera a D2 sem marcar a D2, o estado atual conferido antes da última ingestão e o documento de integração conferido há mais de 45 dias.

O estado atual do exemplo ainda diz que os pontos nunca expiram, embora a decisão D5 tenha estabelecido validade de doze meses. É exatamente a resposta que um agente daria ao cliente. O lint sai com código 1, então o mesmo comando pode barrar um job de CI.

## O que tem aqui

| Peça | O que faz |
|---|---|
| `skills/new-vault` | Cria o vault ou acrescenta um projeto de cliente. |
| `skills/ingest` | Arquiva transcrição, e-mail ou documento, pesa quem disse o quê e registra decisões com supersessão. |
| `skills/query` | Responde a partir do estado atual e das fontes canônicas, declarando o que não foi conferido. |
| `skills/generate` | Monta entregáveis a partir da matriz de decisões e dos templates. |
| `skills/lint` | Executa o lint das travas de fonte e explica como corrigir cada achado. |
| `hooks` | Sincronização e relatório das travas no início da sessão, aviso de commit no fim e gate de escrita em todo markdown gravado. |
| `scripts/check_contradiction.py` | Pergunta a um modelo pequeno quais decisões anteriores a nova torna falsas, antes de ela ser registrada. |
| `template/` | O esqueleto do vault, com os schemas de camada, o template de projeto e os templates de entregável. |
| `METHOD.pt-BR.md` | O método, escrito para ser adotado com qualquer agente. |

Os hooks só agem dentro de uma pasta que tem o marcador `.llm-wiki`, então o plugin nunca toca nos seus outros repositórios.

## Créditos

A ideia do LLM wiki é do [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). A checagem de contradição segue o prompt de deduplicação de arestas do [Graphiti](https://github.com/getzep/graphiti). A estrutura de pastas é o PARA, do Tiago Forte.

Feito por [João Victor Beato](https://github.com/jvbeat), Delivery Lead na DDGroup, a partir de um ano tocando a entrega de Salesforce, Braze e Insider One para vários clientes ao mesmo tempo.

## Licença

MIT
