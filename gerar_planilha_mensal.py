"""Gera a planilha mensal do Controle de Agenda, uma por mes, sempre sobrescrevendo a anterior.

Uso: python gerar_planilha_mensal.py <reunioes.json OU pasta com os .json exportados do Artifact>
(o reunioes.json ja traz os registros do Artifact e do GitHub juntos; e o que a rotina usa)
A pasta e a que a ferramenta ArtifactData grava (colecao "reunioes"), com um .json por reuniao.
Saida: Controle Mensal\\Controle de Agenda AAAA-MM - <Mes>.xlsx (uma planilha por mes; o arquivo do mes e substituido).
Gera SOMENTE a planilha do mes atual (pela data de hoje). Meses futuros nao ganham planilha antes de chegar o dia 1.
A planilha e gerada a partir do Artifact: nao editar a mao, porque a proxima atualizacao sobrescreve.
"""
import calendar
import glob
import io
import json
import os
import sys
from datetime import date, datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PASTA = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(PASTA, 'Controle Mensal')

MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
STATUS = ['prevista', 'realizada', 'cancelada', 'cancelada_sem_pendencia', 'remarcada']
ROTULO = {'prevista': 'Prevista', 'realizada': 'Realizada', 'cancelada': 'Cancelada', 'cancelada_sem_pendencia': 'Cancelada sem Pendência', 'remarcada': 'Remarcada'}

FONTE = 'Arial'
F = Font(name=FONTE, size=10)
FB = Font(name=FONTE, size=10, bold=True)
FT = Font(name=FONTE, size=14, bold=True)
FC = Font(name=FONTE, size=10, bold=True, color='FFFFFF')
CAB = PatternFill('solid', start_color='2B2F36')
FUNDO = {
    'realizada': PatternFill('solid', start_color='E2F1E8'),
    'cancelada': PatternFill('solid', start_color='F9E3E1'),
    'cancelada_sem_pendencia': PatternFill('solid', start_color='DDE9F4'),
    'remarcada': PatternFill('solid', start_color='F8ECD2'),
    'prevista': None,
}
FIM_DE_SEMANA = PatternFill('solid', start_color='F0EEEA')
FINO = Side(style='thin', color='DEDCD8')
BORDA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)


def carregar(pasta):
    reunioes = []
    fontes = []
    if os.path.isfile(pasta):
        # um reunioes.json (id -> reuniao), ja com os registros do Artifact e do GitHub juntos
        with io.open(pasta, encoding='utf-8') as fh:
            fontes = [d for d in json.load(fh).values() if isinstance(d, dict)]
    else:
        for f in sorted(glob.glob(os.path.join(pasta, '**', '*.json'), recursive=True)):
            with io.open(f, encoding='utf-8') as fh:
                j = json.load(fh)
            fontes.append(j['data'] if isinstance(j.get('data'), dict) else j)
    for d in fontes:
        if not d.get('data') or not d.get('inicio'):
            continue
        d = dict(d)
        d['status'] = d.get('status') if d.get('status') in STATUS else 'prevista'
        reunioes.append(d)
    reunioes.sort(key=lambda m: (m['data'], m['inicio'], m.get('fim', '')))
    return reunioes


def cabecalho(ws, linha, titulos):
    for i, t in enumerate(titulos, 1):
        c = ws.cell(row=linha, column=i, value=t)
        c.font, c.fill, c.border = FC, CAB, BORDA
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[linha].height = 22


def larguras(ws, valores):
    for i, w in enumerate(valores, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def conta(itens):
    c = {s: 0 for s in STATUS}
    for m in itens:
        c[m['status']] += 1
    return c


def montar(ano, mes, itens, agora):
    wb = Workbook()
    nome_mes = MESES[mes - 1]

    # --- Resumo por dia
    ws = wb.active
    ws.title = 'Resumo por dia'
    ws['A1'] = 'Controle de Agenda - %s de %d' % (nome_mes, ano)
    ws['A1'].font = FT
    tot = conta(itens)
    ws['A2'] = 'Reuniões no mês: %d  |  Realizadas: %d  |  Canceladas: %d  |  Canceladas sem Pendência: %d  |  Remarcadas: %d  |  Previstas: %d' % (
        len(itens), tot['realizada'], tot['cancelada'], tot['cancelada_sem_pendencia'], tot['remarcada'], tot['prevista'])
    ws['A2'].font = F
    cabecalho(ws, 4, ['Data', 'Dia da semana', 'Reuniões', 'Realizadas', 'Canceladas', 'Canceladas sem Pendência', 'Remarcadas', 'Previstas'])
    por_dia = {}
    for m in itens:
        por_dia.setdefault(m['data'], []).append(m)
    linha = 5
    for dia in range(1, calendar.monthrange(ano, mes)[1] + 1):
        d = date(ano, mes, dia)
        arr = por_dia.get(d.isoformat(), [])
        c = conta(arr)
        vals = [d, DIAS[d.weekday()], len(arr), c['realizada'], c['cancelada'], c['cancelada_sem_pendencia'], c['remarcada'], c['prevista']]
        for col, v in enumerate(vals, 1):
            cel = ws.cell(row=linha, column=col, value=v)
            cel.font, cel.border = F, BORDA
            cel.alignment = Alignment(horizontal='center' if col != 2 else 'left', vertical='center')
            if d.weekday() >= 5 and not arr:
                cel.fill = FIM_DE_SEMANA
        ws.cell(row=linha, column=1).number_format = 'dd/mm/yyyy'
        if c['cancelada']:
            ws.cell(row=linha, column=5).fill = FUNDO['cancelada']
        if c['cancelada_sem_pendencia']:
            ws.cell(row=linha, column=6).fill = FUNDO['cancelada_sem_pendencia']
        if c['realizada']:
            ws.cell(row=linha, column=4).fill = FUNDO['realizada']
        linha += 1
    ws.cell(row=linha, column=1, value='Total do mês').font = FB
    for col, v in enumerate([len(itens), tot['realizada'], tot['cancelada'], tot['cancelada_sem_pendencia'], tot['remarcada'], tot['prevista']], 3):
        cel = ws.cell(row=linha, column=col, value=v)
        cel.font, cel.alignment = FB, Alignment(horizontal='center')
    for col in range(1, 9):
        ws.cell(row=linha, column=col).border = Border(top=Side(style='medium', color='2B2F36'))
    larguras(ws, [14, 16, 12, 12, 12, 16, 12, 12])
    ws.freeze_panes = 'A5'

    # --- Reunioes
    wr = wb.create_sheet('Reuniões')
    cabecalho(wr, 1, ['Data', 'Dia da semana', 'Início', 'Fim', 'Assunto', 'Local', 'Você organiza', 'Status', 'Motivo do cancelamento'])
    for i, m in enumerate(itens, 2):
        d = datetime.strptime(m['data'], '%Y-%m-%d').date()
        vals = [d, DIAS[d.weekday()], m['inicio'], m.get('fim', ''), m.get('assunto', ''), m.get('local', ''),
                'Sim' if m.get('organizador') else 'Não', ROTULO[m['status']], m.get('motivo', '')]
        for col, v in enumerate(vals, 1):
            cel = wr.cell(row=i, column=col, value=v)
            cel.font, cel.border = F, BORDA
            cel.alignment = Alignment(vertical='top', wrap_text=col in (5, 6, 9), horizontal='center' if col in (1, 3, 4, 7, 8) else 'left')
        wr.cell(row=i, column=1).number_format = 'dd/mm/yyyy'
        fundo = FUNDO[m['status']]
        if fundo:
            wr.cell(row=i, column=8).fill = fundo
    larguras(wr, [12, 14, 8, 8, 58, 24, 14, 24, 40])
    wr.freeze_panes = 'A2'
    if itens:
        wr.auto_filter.ref = 'A1:I%d' % (len(itens) + 1)

    # --- Cancelamentos
    wc = wb.create_sheet('Cancelamentos')
    cabecalho(wc, 1, ['Data', 'Início', 'Assunto', 'Situação', 'Motivo do cancelamento'])
    canc = [m for m in itens if m['status'] in ('cancelada', 'cancelada_sem_pendencia')]
    for i, m in enumerate(canc, 2):
        d = datetime.strptime(m['data'], '%Y-%m-%d').date()
        vals = [d, m['inicio'], m.get('assunto', ''), ROTULO[m['status']], m.get('motivo', '') or 'não informado']
        for col, v in enumerate(vals, 1):
            cel = wc.cell(row=i, column=col, value=v)
            cel.font, cel.border = F, BORDA
            cel.alignment = Alignment(vertical='top', wrap_text=col in (3, 5), horizontal='center' if col < 3 else 'left')
        wc.cell(row=i, column=1).number_format = 'dd/mm/yyyy'
    if not canc:
        wc.cell(row=2, column=1, value='Nenhuma reunião cancelada neste mês.').font = F
    larguras(wc, [12, 8, 58, 24, 50])
    wc.freeze_panes = 'A2'

    # --- Leia-me
    wl = wb.create_sheet('Leia-me')
    linhas = [
        ('Controle de Agenda - %s de %d' % (nome_mes, ano), FT),
        ('', F),
        ('Última atualização: %s' % agora.strftime('%d/%m/%Y %H:%M'), F),
        ('Origem: Controle de Agenda (Artifact do Claude), lido da agenda do Outlook.', F),
        ('Existe uma planilha por mês. A de cada mês é atualizada no mesmo arquivo, sem criar cópias.', F),
        ('Esta planilha é gerada automaticamente. Não edite à mão: a próxima atualização sobrescreve o que for alterado aqui.', F),
        ('Os status e os motivos são registrados na página Controle de Agenda, não nesta planilha.', F),
        ('Abas: Resumo por dia, Reuniões (todas as reuniões do mês) e Cancelamentos (com o motivo).', F),
    ]
    for i, (t, fnt) in enumerate(linhas, 1):
        c = wl.cell(row=i, column=1, value=t)
        c.font = fnt
        c.alignment = Alignment(wrap_text=True, vertical='top')
    wl.column_dimensions['A'].width = 110
    return wb


def main():
    if len(sys.argv) != 2:
        sys.exit('Uso: python gerar_planilha_mensal.py <pasta com os .json exportados>')
    reunioes = carregar(sys.argv[1])
    if not reunioes:
        sys.exit('Nenhuma reuniao encontrada em %s; nada foi alterado.' % sys.argv[1])
    os.makedirs(SAIDA, exist_ok=True)
    agora = datetime.now()
    # So o mes atual: a planilha de um mes novo nasce apenas quando esse mes chega (dia 1).
    # As planilhas de meses anteriores nao sao tocadas.
    meses = ['%04d-%02d' % (agora.year, agora.month)]
    for ym in meses:
        ano, mes = int(ym[:4]), int(ym[5:7])
        itens = [m for m in reunioes if m['data'].startswith(ym)]
        wb = montar(ano, mes, itens, agora)
        nome = 'Controle de Agenda %s - %s.xlsx' % (ym, MESES[mes - 1])
        destino = os.path.join(SAIDA, nome)
        tmp = destino + '.tmp'
        wb.save(tmp)
        try:
            os.replace(tmp, destino)
        except PermissionError:
            os.remove(tmp)
            sys.exit('Nao consegui atualizar %s: o arquivo está aberto no Excel. Feche e rode de novo.' % nome)
        print('%s: %d reunioes -> %s' % (ym, len(itens), destino))


if __name__ == '__main__':
    main()
