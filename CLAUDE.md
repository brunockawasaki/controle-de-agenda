# Controle de Agenda

Instruções para o Claude neste projeto. Leia antes de agir. Atualizado em 03/11/2026.

O dono do projeto é o Bruno Kawasaki (Processos e Melhoria Contínua, Grupo Gadens). Ele não é desenvolvedor: falar em português simples, frases curtas, sem termo técnico sem explicar.

## O que é

Página HTML que registra, dia a dia, as reuniões da agenda do Outlook: **realizada**, **cancelada** (com motivo obrigatório), **remarcada** ou **prevista**. Tem calendário do mês, janela com as reuniões do dia, resumo do mês, histórico e botão "Atualizar calendário".

## Onde cada coisa fica

| Peça | O que é |
|---|---|
| Artifact do Claude | Versão principal. Guarda os registros no banco do Artifact (coleção `reunioes`) e lê o Outlook pelo conector Microsoft 365. Só o Bruno abre. |
| `index.html` | A mesma página como arquivo completo, publicada no GitHub Pages: https://brunockawasaki.github.io/controle-de-agenda/ |
| `reunioes.json` | Reuniões publicadas para a página do GitHub (só os campos da página). Atualizado pela rotina. |
| `gerar_reunioes.py` | Gera o `reunioes.json` a partir das reuniões exportadas do Artifact. |
| `gerar_planilha_mensal.py` | Gera a planilha do mês atual em `Controle Mensal`. |
| `Controle Mensal\` | Planilhas mensais (fora do git). |
| Rotina agendada | `atualizar-controle-de-agenda`, texto completo na seção "Skills" abaixo. |

## Memória do projeto (decisões e regras do Bruno)

**Como a página funciona**
- No Artifact, a página usa o banco do Artifact (compartilhado) e o botão lê o Outlook pelo conector Microsoft 365 (precisa da permissão do Bruno na primeira vez).
- No GitHub Pages não há banco nem acesso ao Outlook. A página roda em **modo local**: os registros ficam só no navegador de quem usa. O botão busca o `reunioes.json` e inclui só as reuniões **novas**, sem sobrescrever o que a pessoa marcou.
- Os registros do Artifact e os do GitHub são separados. Marcar num não muda no outro.
- Horários: o Outlook devolve em UTC; converter para Brasília (UTC-3).
- Cancelar exige motivo preenchido. Sem motivo, a página não grava.

**Regras da agenda**
- Reunião nova do Outlook entra como **Prevista**. O Claude nunca marca realizada, cancelada ou remarcada por conta própria; quem marca é o Bruno.
- Nunca alterar, sobrescrever nem apagar o que o Bruno já registrou.
- Reunião cancelada no Outlook é ignorada na carga (não entra). Reunião cancelada no Outlook que já estava na página continua lá, e o Bruno marca o cancelamento e o motivo.
- Não gravar participantes, links do Teams, IDs nem senhas de reunião, nem no banco nem no repositório.
- Chave para não duplicar reunião: data + início + assunto normalizado (minúsculas, sem acentos, só letras e números).

**Rotina e planilha**
- A rotina roda **todos os dias às 09h, 13h e 18h** (horário local) e **só com o app do Claude aberto** neste computador.
- Planilha mensal: sempre em `Controle Mensal`, **uma por mês**, atualizada no mesmo arquivo. **Nunca duplicar nem criar versão nova.**
- Só se gera a planilha do **mês atual**. A de um mês novo só nasce quando esse mês chegar (dia 1). Meses futuros não ganham planilha antes.
- A planilha é gerada a partir do Artifact. Não editar à mão: a próxima atualização sobrescreve.
- A planilha reflete o momento da última atualização. O que o Bruno marcar depois só entra na próxima rodada ou quando ele pedir.
- O botão da página **não** atualiza a planilha: a página não pode gravar arquivos no computador. A planilha é atualizada pela rotina ou quando o Bruno pede.

**GitHub**
- O repositório é **público** (necessário para o GitHub Pages no plano gratuito). Tudo que for para lá fica visível a qualquer pessoa. Os assuntos das reuniões aparecem no `reunioes.json`.
- Subir ao GitHub: o Bruno pediu "suba" a cada mudança neste projeto. Mexer só nos arquivos certos, nunca `git add .`.
- A rotina só faz `git add reunioes.json`. Nunca usar `--force`.

**Teste**
- Em 03/11/2026 a rotina rodou inteira com sucesso: incluiu 35 reuniões novas no Artifact, atualizou o `reunioes.json` e fez o push sozinha.

## Como a página é montada

- O fonte do Artifact é um fragmento HTML (título, estilo, marcação e script). O `index.html` do GitHub é o mesmo fragmento com `<!doctype html>`, `<head>` e um bloco de reinício de estilo na frente.
- Cores e estilo: tokens em `:root`, tema claro e escuro, fontes Archivo (títulos), IBM Plex Sans (texto) e IBM Plex Mono (horários), todas do Google Fonts.
- No Artifact o banco é `db` e o Outlook é `mcp` (servidor "Microsoft 365", ferramenta `outlook_calendar_search`). Fora do Artifact a página cai no modo local (`localStorage`).
- Ao editar: mudar o fragmento, publicar no Artifact (mesma URL), refazer o `index.html` do GitHub e só então subir.

## Skills

### Rotina `atualizar-controle-de-agenda`

Agendada para `0 9,13,18 * * *` (horário local). Cada execução começa sem memória desta conversa, por isso o texto é autossuficiente. Os caminhos do computador e o endereço do Artifact foram trocados por marcadores.

```
Tarefa: atualizar o "Controle de Agenda" com as reunioes novas da agenda do Outlook de Bruno Kawasaki, primeiro no Artifact e depois no GitHub. Responda em portugues simples.

Artifact: <endereco do Artifact do Controle de Agenda>
Banco do Artifact: ferramenta ArtifactData (se ela aparecer so como nome de ferramenta adiada, carregue com ToolSearch "select:ArtifactData" antes). Colecao `reunioes`. Cada documento tem os campos: data (AAAA-MM-DD), inicio (HH:MM), fim (HH:MM), assunto, local, organizador (true/false), status, motivo, outlookId.
Agenda: conector Microsoft 365, ferramenta de busca de eventos do calendario (outlook_calendar_search; se necessario, carregue as ferramentas com ToolSearch).
Pasta do repositorio GitHub: <pasta do projeto Controle de Agenda>

PARTE 1 - ARTIFACT
1. Leia TODOS os documentos existentes da colecao `reunioes` do Artifact (ArtifactData, acao list, query.limit 1000). Guarde, para cada um, a chave: data + "|" + inicio + "|" + assunto normalizado (minusculas, sem acentos, so letras e numeros), e tambem o outlookId, se existir.
2. Busque no Outlook os eventos de hoje 00:00 (horario de Brasilia, UTC-3) ate 60 dias a frente: query "*", order "oldest", limit 25, e repita com o offset indicado em nextOffset ate nao haver mais paginas.
3. Converta os horarios para Brasilia (UTC-3): o Outlook costuma devolver em UTC (timeZone "UTC"); subtraia 3 horas. Se um evento terminar em outro dia, use fim 23:59. Evento de dia inteiro: inicio 00:00 e fim 23:59.
4. Ignore eventos com isCancelled true.
5. Para cada evento cuja chave (data|inicio|assunto normalizado) NAO exista, e cujo id do Outlook NAO esteja em nenhum outlookId, crie um documento novo com ArtifactData (action batch, ate 50 por lote, op set, sem if_version): id do documento = AAAAMMDD-HHMM-<assunto em minusculas sem acentos, com letras/numeros e hifens, no maximo 40 caracteres>; se o id ja existir, acrescente -2, -3, etc. Campos: data, inicio, fim, assunto (como esta no Outlook, sem espacos extras), local, organizador (isOrganizer), status "prevista", motivo "" e outlookId (o id do evento).
   Local: "7 Pavimento SALA 1" vira "7º andar, sala 1"; "Reuniões do Microsoft Teams" vira "Teams"; se houver varios locais separados por ponto e virgula, junte com " e "; local vazio fica "".
6. NUNCA altere, sobrescreva nem apague documentos que ja existem. Eles guardam o que o usuario registrou (realizada, cancelada, remarcada e o motivo).
7. Nunca grave no banco: lista de participantes, links do Teams, ID ou senha de reuniao, corpo/descricao do evento.
8. Grave (set) o documento `config/sync` (colecao `config`, doc_id `sync`) com: em (data e hora atual em ISO), novas (quantidade de documentos criados) e origem "rotina". Se ele ja existir, leia antes e passe a version como if_version.

PARTE 2 - EXPORTAR, PLANILHA MENSAL E GITHUB (so depois da Parte 1 ter dado certo)
9. Exporte todos os documentos da colecao `reunioes` do Artifact para arquivos: ArtifactData, acao list, colecao `reunioes`, query.limit 1000, out_dir = <pasta temporaria do usuario>\agenda-export (use o caminho completo, nao o formato abreviado com ~). Se a ferramenta recusar essa pasta, tente outra pasta dentro da pasta temporaria do usuario. Se nenhuma servir, pule a Parte 2 e diga isso no resumo.
10. PLANILHA MENSAL: rode python "<pasta do repositorio>\gerar_planilha_mensal.py" "<out_dir usado>". Ele grava, em "<pasta do repositorio>\Controle Mensal", uma planilha por mes (Controle de Agenda AAAA-MM - Mes.xlsx), SEMPRE sobrescrevendo a planilha do mes, sem criar copias ou versoes. O script gera SOMENTE a planilha do MES ATUAL (pela data de hoje): a planilha de um mes novo so nasce quando esse mes chegar (dia 1) e planilhas de meses anteriores ou futuros NAO devem ser criadas nem alteradas. Se existir planilha de mes futuro, nao a crie; avise no resumo. Nunca crie planilhas por outro caminho e nunca salve copia em outra pasta. Se o Excel estiver com o arquivo aberto e o script avisar, diga isso no resumo. Essa planilha NAO vai para o GitHub (a pasta Controle Mensal e ignorada pelo git).
11. Rode: python "<pasta do repositorio>\gerar_reunioes.py" "<out_dir usado>". Ele grava reunioes.json na pasta do repositorio (so os campos da pagina, sem outlookId).
12. Na pasta do repositorio, rode `git status --porcelain reunioes.json`. Se NAO houver mudanca, nao faca commit. Se houver: `git add reunioes.json` (SOMENTE esse arquivo; nunca `git add .` nem `git add -A`), `git commit -m "Atualiza reunioes (rotina)"` com a linha final "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" na mensagem, e `git push`. Nunca use --force, nunca altere outros arquivos e nunca mude outro repositorio.
13. Se o push for recusado ou falhar, nao tente contornar: diga o que aconteceu no resumo.

REGRAS GERAIS
- Nao envie e-mail nem mensagem a ninguem e nao altere nada no Outlook. Esta tarefa so le a agenda, grava no Artifact e atualiza o reunioes.json do repositorio.
- Termine com um resumo de uma linha: quantas reunioes novas foram incluidas no Artifact, ate que data a busca foi feita, se a planilha mensal foi atualizada e se o GitHub foi atualizado (ou por que nao). Se algo falhar, diga exatamente o que falhou.
```

### Como usar o botão "Atualizar calendário"

No Artifact, a página lê o Outlook (Microsoft 365) e inclui as reuniões novas dos próximos 60 dias, com a mesma lógica dos passos 1 a 8 da rotina. No GitHub Pages, o botão busca o `reunioes.json`.

### Pedidos que o Bruno costuma fazer

- "Atualiza a agenda": rodar os passos 1 a 8 e, se ele quiser, a Parte 2.
- "Atualiza a planilha": exportar o banco do Artifact e rodar `gerar_planilha_mensal.py`. Não criar outra planilha.
- "Suba para o github": copiar o `index.html` atualizado, `git add` só dos arquivos certos, commit e push.

## Limites conhecidos

- A rotina só roda com o app do Claude aberto. Se estiver fechado na hora, roda quando o app abrir.
- Reunião marcada depois da última rodada só aparece na próxima rodada, ou na hora no Artifact pelo botão.
- Reunião que mudou de horário no Outlook entra como reunião nova; a antiga continua na página e o Bruno marca como Remarcada.
- A página do GitHub só atualiza depois da rotina e de uns 10 minutos de espera do GitHub.
- O botão do Artifact (leitura do Outlook pela própria página) não foi testado de ponta a ponta. A rotina agendada, que faz o mesmo trabalho, foi testada e funcionou.
