"""Gera o reunioes.json da pagina do GitHub a partir das reunioes exportadas do Artifact.

Uso: python gerar_reunioes.py <pasta com os .json exportados>
A pasta e a que a ferramenta ArtifactData grava (colecao "reunioes"), com um .json por reuniao.
Grava reunioes.json ao lado deste script. Guarda so os campos da pagina; nada de participantes, links ou IDs do Outlook.
"""
import glob
import io
import json
import os
import sys

CAMPOS = ('data', 'inicio', 'fim', 'assunto', 'local', 'organizador', 'status', 'motivo')


def main():
    if len(sys.argv) != 2:
        sys.exit('Uso: python gerar_reunioes.py <pasta com os .json exportados>')
    pasta = sys.argv[1]
    arquivos = sorted(glob.glob(os.path.join(pasta, '**', '*.json'), recursive=True))
    saida = {}
    for f in arquivos:
        with io.open(f, encoding='utf-8') as fh:
            j = json.load(fh)
        d = j['data'] if isinstance(j.get('data'), dict) else j
        if not d.get('data') or not d.get('inicio'):
            continue
        saida[os.path.splitext(os.path.basename(f))[0]] = {k: d.get(k, '') for k in CAMPOS}
    if not saida:
        sys.exit('Nenhuma reuniao encontrada em ' + pasta + '; reunioes.json nao foi alterado.')
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reunioes.json')
    with io.open(destino, 'w', encoding='utf-8', newline='') as fh:
        fh.write(json.dumps(saida, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    print(len(saida), 'reunioes gravadas em', destino)


if __name__ == '__main__':
    main()
