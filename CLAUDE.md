# Controle de Agenda

Instruções para o Claude neste projeto. Leia antes de agir. Atualizado em 03/11/2026 (registros pelo GitHub).

O dono do projeto é o Bruno Kawasaki (Processos e Melhoria Contínua, Grupo Gadens). Ele não é desenvolvedor: falar em português simples, frases curtas, sem termo técnico sem explicar.

## O que é

Página HTML que registra, dia a dia, as reuniões da agenda do Outlook: **realizada**, **cancelada** (com motivo obrigatório), **remarcada** ou **prevista**. Tem calendário do mês, janela com as reuniões do dia, resumo do mês, histórico e botão "Atualizar calendário".

## Onde cada coisa fica

| Peça | O que é |
|---|---|
| Artifact do Claude | Versão principal. Guarda os registros no banco do Artifact (coleção `reunioes`) e lê o Outlook pelo conector Microsoft 365. Só o Bruno abre. |
| `index.html` | A mesma página como arquivo completo, publicada no GitHub Pages: https://brunockawasaki.github.io/controle-de-agenda/ |
| `reunioes.json` | Reuniões e registros (status e motivo) da página do GitHub. **A página lê e grava neste arquivo** pela API do GitHub; a rotina também o atualiza. |
| `gerar_reunioes.py` | Junta o Artifact e o GitHub no `reunioes.json`: para cada reunião vale o registro com `atualizadoEm` mais recente. Também lista o que o GitHub tem de mais novo para a rotina aplicar no Artifact. |
| `gerar_planilha_mensal.py` | Gera a planilha do mês atual em `Controle Mensal`, a partir do `reunioes.json` (já com Artifact e GitHub juntos). |
| `Controle Mensal\` | Planilhas mensais (fora do git). |
| Rotina agendada | `atualizar-controle-de-agenda`, texto completo na seção "Skills" abaixo. |

## Memória do projeto (decisões e regras do Bruno)

**Como a página funciona**
- No Artifact, a página usa o banco do Artifact (compartilhado) e o botão lê o Outlook pelo conector Microsoft 365 (precisa da permissão do Bruno na primeira vez).
- No GitHub Pages não há banco nem acesso ao Outlook. Os registros (realizada, cancelada, motivo) são **gravados no `reunioes.json` do repositório pela API do GitHub** (um commit por registro). Para gravar, a pessoa cola **uma vez** um token do GitHub neste navegador (botão "Conectar ao GitHub"). Sem token, a página só mostra os dados. O botão "Atualizar calendário" recarrega os dados do GitHub.
- **O token nunca vai para o código nem para o repositório.** Fica no `localStorage` do navegador. Motivos: o repositório é público, o GitHub revoga sozinho tokens encontrados em repositório público, e quem visse o código poderia mexer em tudo. O token deve ser do tipo fine-grained, só para o repositório `controle-de-agenda`, com **Contents: Read and write**. Nunca usar o token do `gh` do Bruno (dá acesso a todos os repositórios dele).
- Artifact e GitHub têm cada um o seu registro. A rotina junta os dois a cada rodada: vale o registro com `atualizadoEm` mais recente, e o Artifact também recebe o que foi marcado pelo GitHub. Entre uma rodada e outra, um lado não vê o que foi marcado no outro.
- Horários: o Outlook devolve em UTC; converter para Brasília (UTC-3).
- Cancelar exige motivo preenchido. Sem motivo, a página não grava.
- Calendário: os **feriados nacionais** aparecem em azul claro, com o nome do feriado e "Feriado nacional" na legenda (decisão do Bruno em 04/11/2026). Só os de lei federal: Confraternização Universal, Sexta-feira Santa, Tiradentes, Dia do Trabalho, Independência, Nossa Senhora Aparecida, Finados, Proclamação da República, Dia da Consciência Negra e Natal. **Carnaval e Corpus Christi ficam de fora** (ponto facultativo). Feriado estadual ou municipal não entra. A lista é calculada no código (a Sexta-feira Santa vem da Páscoa).

**Regras da agenda**
- Reunião nova do Outlook entra como **Prevista**. O Claude nunca marca realizada, cancelada ou remarcada por conta própria; quem marca é o Bruno.
- Nunca alterar, sobrescrever nem apagar o que o Bruno já registrou. A única exceção: a rotina aplica no Artifact o registro **mais novo** vindo do GitHub.
- Status da reunião: `prevista`, `realizada`, `cancelada`, `cancelada_sem_pendencia` (botão "Cancelada sem Pendência", chamado de "Sem Pendências" no calendário) e `remarcada`. "Sem Pendências" é a reunião cancelada por não ter atividades para acompanhamento, por ter prazos mapeados e vigentes ou por todas as atividades estarem concluídas. Exige motivo, como a Cancelada, e tem contador próprio no resumo, no histórico e na planilha.
- Reunião cancelada no Outlook é ignorada na carga (não entra). Reunião cancelada no Outlook que já estava na página continua lá, e o Bruno marca o cancelamento e o motivo.
- Não gravar participantes, links do Teams, IDs nem senhas de reunião, nem no banco nem no repositório.
- **O nome da reunião vem sempre do Outlook** (decisão do Bruno em 05/11/2026). Se ele renomear a reunião no Teams (por exemplo, de "(sem assunto)" para um nome), a rotina e o botão "Atualizar calendário" trocam o nome aqui. A reunião é achada pelo `outlookId`; muda só o `assunto`, o registro (status, motivo) não muda. O `gerar_reunioes.py` também pega o assunto sempre do Artifact. Reuniões antigas sem `outlookId` ganham o id quando o Outlook as encontra pela chave.
- Chave para não duplicar reunião: data + início + assunto normalizado (minúsculas, sem acentos, só letras e números).

**Rotina e planilha**
- A rotina roda **todos os dias às 09h, 13h e 18h** (horário local) e **só com o app do Claude aberto** neste computador.
- Planilha mensal: sempre em `Controle Mensal`, **uma por mês**, atualizada no mesmo arquivo. **Nunca duplicar nem criar versão nova.**
- Só se gera a planilha do **mês atual**. A de um mês novo só nasce quando esse mês chegar (dia 1). Meses futuros não ganham planilha antes.
- A planilha é gerada a partir do `reunioes.json` (Artifact e GitHub juntos). Não editar à mão: a próxima atualização sobrescreve.
- A planilha reflete o momento da última atualização. O que o Bruno marcar depois só entra na próxima rodada ou quando ele pedir.
- O botão da página **não** atualiza a planilha: a página não pode gravar arquivos no computador. A planilha é atualizada pela rotina ou quando o Bruno pede.

**GitHub**
- O repositório é **público** (necessário para o GitHub Pages no plano gratuito). Tudo que for para lá fica visível a qualquer pessoa. Os assuntos das reuniões aparecem no `reunioes.json`.
- Subir ao GitHub: o Bruno pediu "suba" a cada mudança neste projeto. Mexer só nos arquivos certos, nunca `git add .`.
- A rotina só faz `git add reunioes.json`, antes dá `git pull --rebase` (a página grava no mesmo arquivo). Nunca usar `--force`.

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
5b. NOME SEMPRE IGUAL AO OUTLOOK: para cada evento do Outlook que NAO seja novo, (a) se o id do evento ja estiver em um documento (campo outlookId) e o assunto do evento (sem espacos extras) for DIFERENTE do assunto gravado, atualize SOMENTE o campo assunto desse documento (ArtifactData update, com if_version; nao mude status, motivo, atualizadoEm nem outros campos); (b) se a chave (data|inicio|assunto normalizado) bater com um documento que ainda NAO tem outlookId, grave SOMENTE o outlookId nele. Assim, quando o Bruno renomear a reuniao no Teams, o nome muda aqui.
6. NUNCA altere, sobrescreva nem apague documentos que ja existem. Eles guardam o que o usuario registrou (realizada, cancelada, remarcada e o motivo). A unica excecao e o passo 12 da Parte 2 (registros mais novos vindos do GitHub). Outra excecao, so no passo 5b acima: o NOME (assunto) e o outlookId.
7. Nunca grave no banco: lista de participantes, links do Teams, ID ou senha de reuniao, corpo/descricao do evento.
8. Grave (set) o documento `config/sync` (colecao `config`, doc_id `sync`) com: em (data e hora atual em ISO), novas (quantidade de documentos criados) e origem "rotina". Se ele ja existir, leia antes e passe a version como if_version.

PARTE 2 - GITHUB, PLANILHA MENSAL E ARTIFACT (so depois da Parte 1 ter dado certo)
A pagina do GitHub tambem grava registros (realizada, cancelada, motivo) no reunioes.json do repositorio. Por isso o reunioes.json e o Artifact precisam ser juntados: para cada reuniao vale o registro com "atualizadoEm" mais recente.
9. Na pasta do repositorio rode `git pull --rebase` para trazer o que a pagina gravou. Se falhar, pare a Parte 2 e diga isso no resumo (nao use --force).
10. Exporte todos os documentos da colecao `reunioes` do Artifact para arquivos: ArtifactData, acao list, colecao `reunioes`, query.limit 1000, out_dir = <pasta temporaria do usuario>\agenda-export (use o caminho completo, nao o formato abreviado com ~). Se a ferramenta recusar essa pasta, tente outra pasta dentro de <pasta temporaria do usuario>. Se nenhuma servir, pule a Parte 2 e diga isso no resumo.
11. Rode: python "<pasta do repositorio>\gerar_reunioes.py" "<out_dir usado>" "<pasta temporaria do usuario>\para_artifact.json". Ele junta Artifact e GitHub em reunioes.json (so os campos da pagina, sem outlookId) e grava em para_artifact.json o que o GitHub tem de mais novo que o Artifact.
12. APLICAR NO ARTIFACT o que veio do GitHub (unica excecao a regra 6 da Parte 1). Leia para_artifact.json. Para cada id: se _acao for "atualizar", leia o documento no Artifact e faca ArtifactData update (com if_version) so de status, motivo e atualizadoEm; se _acao for "criar", faca ArtifactData set do documento novo com data, inicio, fim, assunto, local, organizador, status, motivo e atualizadoEm. Nao mexa em nenhum outro documento. Se o arquivo estiver vazio ({}), nao ha nada a fazer.
13. PLANILHA MENSAL: rode python "<pasta do repositorio>\gerar_planilha_mensal.py" "<pasta do repositorio>\reunioes.json". Ele grava, em "<pasta do repositorio>\Controle Mensal", uma planilha por mes (Controle de Agenda AAAA-MM - Mes.xlsx), SEMPRE sobrescrevendo a planilha do mes, sem criar copias ou versoes. O script gera SOMENTE a planilha do MES ATUAL (pela data de hoje): a planilha de um mes novo so nasce quando esse mes chegar (dia 1) e planilhas de meses anteriores ou futuros NAO devem ser criadas nem alteradas. Se existir planilha de mes futuro, nao a crie; avise no resumo. Nunca crie planilhas por outro caminho e nunca salve copia em outra pasta. Se o Excel estiver com o arquivo aberto e o script avisar, diga isso no resumo. Essa planilha NAO vai para o GitHub (a pasta Controle Mensal e ignorada pelo git).
14. Na pasta do repositorio, rode `git status --porcelain reunioes.json`. Se NAO houver mudanca, nao faca commit. Se houver: `git add reunioes.json` (SOMENTE esse arquivo; nunca `git add .` nem `git add -A`), `git commit -m "Atualiza reunioes (rotina)"` com a linha final "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" na mensagem, e `git push`. Nunca use --force, nunca altere outros arquivos e nunca mude outro repositorio.
15. Se o push for recusado (a pagina pode ter gravado no meio tempo), rode `git pull --rebase` e tente `git push` mais UMA vez. Se der conflito, rode `git rebase --abort`, nao tente contornar e diga o que aconteceu no resumo.

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
- A página do GitHub lê o arquivo pela API quando há token (sem espera). Sem token, lê o arquivo publicado, que o GitHub demora uns 10 minutos para mostrar.
- Se o Bruno marcar o mesmo registro no Artifact e no GitHub entre duas rodadas, vale o que tiver `atualizadoEm` mais recente.
- Os registros gravados pelo GitHub e a lista de reuniões públicos aparecem para qualquer pessoa com o link do repositório.
- O botão do Artifact (leitura do Outlook pela própria página) não foi testado de ponta a ponta. A rotina agendada, que faz o mesmo trabalho, foi testada e funcionou.
