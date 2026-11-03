"""Junta os registros do Artifact e do GitHub no reunioes.json (o arquivo que a pagina do GitHub le e grava).

Uso: python gerar_reunioes.py <pasta com os .json exportados do Artifact> [arquivo para_artifact.json]

- A pasta e a que a ferramenta ArtifactData grava (colecao "reunioes"), com um .json por reuniao.
- Cada reuniao tem, no Artifact e no GitHub, os campos da pagina e "atualizadoEm" (quando foi marcada).
  Para cada reuniao vence o lado com "atualizadoEm" MAIS RECENTE. Reuniao que so existe de um lado e incluida.
- Grava reunioes.json ao lado deste script (so campos da pagina; nada de participantes, links ou IDs do Outlook).
- Com o segundo argumento, grava nele o que o GitHub tem de mais novo que o Artifact (para a rotina aplicar no Artifact).
"""
import glob
import io
import json
import os
import sys

CAMPOS = ('data', 'inicio', 'fim', 'assunto', 'local', 'organizador', 'status', 'motivo', 'atualizadoEm')
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reunioes.json')


def limpa(d):
    return {k: d.get(k, '') for k in CAMPOS}


def le_artifact(pasta):
    saida = {}
    for f in sorted(glob.glob(os.path.join(pasta, '**', '*.json'), recursive=True)):
        with io.open(f, encoding='utf-8') as fh:
            j = json.load(fh)
        d = j['data'] if isinstance(j.get('data'), dict) else j
        if not d.get('data') or not d.get('inicio'):
            continue
        saida[os.path.splitext(os.path.basename(f))[0]] = limpa(d)
    return saida


def le_github():
    if not os.path.exists(DESTINO):
        return {}
    with io.open(DESTINO, encoding='utf-8') as fh:
        atual = json.load(fh)
    return {i: limpa(d) for i, d in atual.items() if isinstance(d, dict)}


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit('Uso: python gerar_reunioes.py <pasta exportada> [para_artifact.json]')
    artifact = le_artifact(sys.argv[1])
    if not artifact:
        sys.exit('Nenhuma reuniao encontrada em ' + sys.argv[1] + '; reunioes.json nao foi alterado.')
    github = le_github()

    final, para_artifact = {}, {}
    for i in sorted(set(artifact) | set(github)):
        a, g = artifact.get(i), github.get(i)
        if a and not g:
            final[i] = a
        elif g and not a:
            final[i] = g
            para_artifact[i] = dict(g, _acao='criar')
        else:
            # mesma reuniao nos dois lados: vence o registro mais recente
            if (g.get('atualizadoEm') or '') > (a.get('atualizadoEm') or ''):
                final[i] = g
                if any(g[k] != a[k] for k in ('status', 'motivo')):
                    para_artifact[i] = dict(g, _acao='atualizar')
            else:
                final[i] = a

    with io.open(DESTINO, 'w', encoding='utf-8', newline='') as fh:
        fh.write(json.dumps(final, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    print(len(final), 'reunioes gravadas em', DESTINO)

    if len(sys.argv) == 3:
        with io.open(sys.argv[2], 'w', encoding='utf-8', newline='') as fh:
            fh.write(json.dumps(para_artifact, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
        print(len(para_artifact), 'reunioes do GitHub mais novas que o Artifact ->', sys.argv[2])


if __name__ == '__main__':
    main()
