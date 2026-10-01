"""Los Tacos · Cozinha: fichas técnicas do cardápio para a equipe.

Restaurante e dados fictícios. Lê dois arquivos CSV da mesma pasta:
- cardapio-los-tacos.csv  →  id, categoria, nome, descricao, preco
- fichas.csv              →  prato_id, ingrediente, qtd, un, preco

Rodar: python3 app_nicegui.py  →  http://localhost:8080
"""

import csv
from pathlib import Path

from nicegui import ui

ARQUIVO_CARDAPIO = 'cardapio-los-tacos.csv'
ARQUIVO_FICHAS = 'fichas.csv'
ARQUIVO_VENDAS = 'vendas.csv'
CMV_ALVO = 0.30

# ---------- Identidade visual do Los Tacos ----------
ROSA = '#D81B60'
ROXO = '#3B1C6E'
MOSTARDA = '#E0A33A'
MUSGO = '#4E5B31'
CINZA = '#9E9A93'
PAPEL = '#FBF5EC'
TINTA = '#231F20'


# ---------- Dados: ler e salvar os CSVs ----------
def carregar_cardapio() -> dict:
    """Lê o cardápio e junta a ficha técnica de cada prato (pelo id)."""
    cardapio = {}
    with open(ARQUIVO_CARDAPIO, encoding='utf-8') as arquivo:
        for linha in csv.DictReader(arquivo):
            cardapio[linha['id']] = {
                'categoria': linha['categoria'],
                'nome': linha['nome'],
                'descricao': linha['descricao'],
                'preco_venda': float(linha['preco']),
                'ingredientes': [],
                'vendidos': 0,
            }
    if Path(ARQUIVO_FICHAS).exists():
        with open(ARQUIVO_FICHAS, encoding='utf-8') as arquivo:
            for linha in csv.DictReader(arquivo):
                prato = cardapio.get(linha['prato_id'])
                if prato is None:  # ficha de um prato que não está no cardápio
                    continue
                prato['ingredientes'].append({
                    'nome': linha['ingrediente'],
                    'qtd': float(linha['qtd']),
                    'un': linha['un'],
                    'preco': float(linha['preco']),
                })
    if Path(ARQUIVO_VENDAS).exists():
        with open(ARQUIVO_VENDAS, encoding='utf-8') as arquivo:
            for linha in csv.DictReader(arquivo):
                if linha['prato_id'] in cardapio:
                    cardapio[linha['prato_id']]['vendidos'] = int(linha['vendidos_mes'])
    return cardapio


def salvar():
    """Grava as fichas e os preços editados na tela de volta nos CSVs."""
    with open(ARQUIVO_FICHAS, 'w', encoding='utf-8', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(['prato_id', 'ingrediente', 'qtd', 'un', 'preco'])
        for prato_id, prato in CARDAPIO.items():
            for ing in prato['ingredientes']:
                escritor.writerow([prato_id, ing['nome'], ing['qtd'], ing['un'], f"{ing['preco']:.2f}"])
    with open(ARQUIVO_CARDAPIO, 'w', encoding='utf-8', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(['id', 'categoria', 'nome', 'descricao', 'preco'])
        for prato_id, prato in CARDAPIO.items():
            escritor.writerow([prato_id, prato['categoria'], prato['nome'], prato['descricao'],
                               f"{prato['preco_venda']:g}"])
    ui.notify('Fichas salvas!', type='positive')


CARDAPIO = carregar_cardapio()
estado = {'prato': next(iter(CARDAPIO)), 'venda_input': None}
campos = []  # os campos da receita que está na tela


# ---------- Contas ----------
def custo_do_prato(prato: dict) -> float:
    return sum(i['qtd'] * i['preco'] for i in prato['ingredientes'])


def cmv_do_prato(prato: dict) -> float:
    venda = prato['preco_venda']
    return custo_do_prato(prato) / venda if venda else 0


def cor_do_cmv(prato: dict) -> tuple:
    """Devolve (cor, texto do semáforo) para um prato."""
    if not prato['ingredientes']:
        return CINZA, 'Sem ficha técnica ainda: cadastre os ingredientes em fichas.csv.'
    cmv = cmv_do_prato(prato)
    if cmv <= CMV_ALVO:
        return MUSGO, 'Prato redondo: custo sob controle e margem boa.'
    if cmv <= 0.35:
        return MOSTARDA, 'Margem apertando: confira gramatura e desperdício.'
    return ROSA, 'Prato caro de produzir: revise porção, fornecedor ou preço.'


# ---------- Engenharia de cardápio (Kasavana & Smith) ----------
CLASSES = {
    'Estrela': (MUSGO, 'Star', 'Vende muito e dá boa margem: mantenha e destaque.'),
    'Burro de carga': (MOSTARDA, 'Plowhorse', 'Vende muito, margem baixa: reveja porção, fornecedor ou preço.'),
    'Quebra-cabeça': (ROXO, 'Puzzle', 'Boa margem, vende pouco: mude a posição no cardápio ou a descrição.'),
    'Cão': (ROSA, 'Dog', 'Vende pouco e dá pouca margem: reformule ou tire do cardápio.'),
}


def margem(prato: dict) -> float:
    """Margem de contribuição: o que sobra de cada venda depois do custo dos ingredientes."""
    return prato['preco_venda'] - custo_do_prato(prato)


def engenharia() -> tuple:
    """Classifica cada prato com ficha. Devolve (classes por id, corte de vendas, corte de margem)."""
    pratos = {pid: p for pid, p in CARDAPIO.items() if p['ingredientes']}
    total = sum(p['vendidos'] for p in pratos.values())
    if not pratos or not total:
        return {}, 0, 0
    corte_vendas = 0.7 * total / len(pratos)  # 70% da participação média
    corte_margem = sum(margem(p) * p['vendidos'] for p in pratos.values()) / total  # média ponderada
    classes = {}
    for pid, p in pratos.items():
        popular = p['vendidos'] >= corte_vendas
        lucrativo = margem(p) >= corte_margem
        if popular and lucrativo:
            classes[pid] = 'Estrela'
        elif popular:
            classes[pid] = 'Burro de carga'
        elif lucrativo:
            classes[pid] = 'Quebra-cabeça'
        else:
            classes[pid] = 'Cão'
    return classes, corte_vendas, corte_margem


def atualizar_matriz():
    classes, corte_vendas, corte_margem = engenharia()
    pontos = []
    for pid, classe in classes.items():
        p = CARDAPIO[pid]
        destaque = pid == estado['prato']
        pontos.append({
            'name': p['nome'],
            'value': [p['vendidos'], round(margem(p), 2)],
            'symbolSize': 22 if destaque else 13,
            'itemStyle': {'color': CLASSES[classe][0],
                          'borderColor': TINTA if destaque else 'white', 'borderWidth': 3 if destaque else 1},
        })
    serie = matriz.options['series'][0]
    serie['data'] = pontos
    serie['markLine']['data'] = [{'xAxis': round(corte_vendas)}, {'yAxis': round(corte_margem, 2)}]
    matriz.update()

    classe = classes.get(estado['prato'])
    if classe:
        cor, ingles, acao = CLASSES[classe]
        classe_label.set_text(f'{classe} ({ingles}) · {CARDAPIO[estado["prato"]]["vendidos"]} vendidos/mês')
        classe_label.style(f'background:{cor}')
        acao_label.set_text(acao)
    else:
        classe_label.set_text('Sem ficha técnica: fora da matriz')
        classe_label.style(f'background:{CINZA}')
        acao_label.set_text('')


def atualizar(_=None, inicio=False):
    """Recalcula tudo quando qualquer campo muda."""
    prato = CARDAPIO[estado['prato']]
    custos = []
    for c in campos:
        c['origem']['qtd'] = c['qtd'].value or 0  # guarda a edição no cardápio
        c['origem']['preco'] = c['preco'].value or 0
        custo = c['origem']['qtd'] * c['origem']['preco']
        c['custo'].set_text(f'R$ {custo:.2f}')
        custos.append(round(custo, 2))

    prato['preco_venda'] = estado['venda_input'].value or 0
    custo = custo_do_prato(prato)
    cmv = cmv_do_prato(prato)
    cor, texto = cor_do_cmv(prato)

    custo_label.set_text(f'R$ {custo:.2f}')
    sugerido_label.set_text(f'R$ {custo / CMV_ALVO:.2f}' if custo else '—')
    status_label.set_text(texto)
    status_label.style(f'background:{cor}')

    gauge.options['series'][0]['data'][0]['value'] = round(min(cmv * 100, 60), 1)
    gauge.update()
    barras.options['yAxis']['data'] = [c['origem']['nome'] for c in campos]
    barras.options['series'][0]['data'] = custos
    barras.update()
    atualizar_matriz()
    if not inicio:
        resumo.refresh()  # na abertura o resumo já é desenhado pronto


def trocar_prato(evento):
    estado['prato'] = evento.value
    receita.refresh()
    atualizar()


# ---------- Estilo ----------
ui.add_head_html(
    '<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue'
    '&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
)
ui.add_css(f'''
    body {{ background: {PAPEL}; color: {TINTA}; font-family: 'Inter', sans-serif; }}
    .titulo {{ font-family: 'Bebas Neue', sans-serif; letter-spacing: .03em; line-height: 1; }}
    .cartao {{ background: white; border-radius: 18px; border: 2px solid {TINTA};
              box-shadow: 5px 5px 0 {TINTA}; }}
    .faixa {{ height: 14px;
             background: linear-gradient(135deg, {ROSA} 25%, transparent 25%) -7px 0,
                         linear-gradient(225deg, {ROSA} 25%, transparent 25%) -7px 0;
             background-size: 14px 14px; background-color: {PAPEL}; }}
''')
ui.colors(primary=ROSA, secondary=ROXO)


# ---------- Partes que se redesenham ----------
@ui.refreshable
def receita():
    prato = CARDAPIO[estado['prato']]
    campos.clear()
    ui.label(prato['categoria'].upper()).classes('text-xs tracking-[0.25em] font-semibold').style(f'color:{ROSA}')
    ui.label(prato['nome']).classes('titulo text-5xl').style(f'color:{ROXO}')
    ui.label(prato['descricao']).classes('text-sm text-gray-500 italic')

    if prato['ingredientes']:
        with ui.grid(columns='1fr 105px 115px 75px').classes('w-full items-center gap-x-3 gap-y-1 mt-3'):
            for titulo in ['Ingrediente', 'Qtd', 'Preço', 'Custo']:
                ui.label(titulo).classes('text-xs uppercase tracking-wider text-gray-400 font-semibold')
            for ing in prato['ingredientes']:
                ui.label(ing['nome']).classes('font-medium')
                qtd = ui.number(value=ing['qtd'], format='%.3f', step=0.01, on_change=atualizar) \
                    .props(f'dense outlined suffix="{ing["un"]}"')
                preco = ui.number(value=ing['preco'], format='%.2f', on_change=atualizar) \
                    .props('dense outlined prefix="R$"')
                custo = ui.label().classes('text-right font-semibold')
                campos.append({'origem': ing, 'qtd': qtd, 'preco': preco, 'custo': custo})
    else:
        with ui.row().classes('w-full items-center gap-2 p-4 mt-3 rounded-xl bg-gray-100'):
            ui.icon('edit_note').classes('text-2xl text-gray-500')
            ui.label('Este item ainda não tem ficha técnica.').classes('text-gray-600')

    ui.separator().classes('my-2')
    with ui.row().classes('w-full items-center justify-between'):
        estado['venda_input'] = ui.number('Preço no cardápio', value=prato['preco_venda'], format='%.2f',
                                          on_change=atualizar).props('outlined prefix="R$"').classes('w-48')
        ui.button('Salvar fichas', icon='save', on_click=salvar).props('unelevated rounded')


@ui.refreshable
def resumo():
    # Do CMV mais alto para o mais baixo; itens sem ficha vão para o fim
    ordem = sorted(CARDAPIO.values(),
                   key=lambda p: cmv_do_prato(p) if p['ingredientes'] else -1, reverse=True)
    for prato in ordem:
        cor, _ = cor_do_cmv(prato)
        texto = f'{cmv_do_prato(prato) * 100:.1f}%' if prato['ingredientes'] else '—'
        with ui.row().classes('w-full items-center justify-between py-1 border-b border-dashed no-wrap'):
            with ui.row().classes('items-center gap-2 no-wrap'):
                ui.element('div').classes('w-3 h-3 rounded-full shrink-0').style(f'background:{cor}')
                ui.label(prato['nome']).classes('text-sm font-medium')
            ui.label(texto).classes('text-sm font-semibold').style(f'color:{cor}')


# ---------- Cabeçalho ----------
with ui.header().classes('p-0').style(f'background:{TINTA}'):
    with ui.column().classes('w-full gap-0'):
        with ui.row().classes('w-full items-center px-8 py-3 gap-4'):
            if Path('logo.png').exists():
                ui.image('logo.png').classes('w-14 h-14')
            with ui.column().classes('gap-0'):
                ui.label('LOS TACOS').classes('titulo text-4xl').style(f'color:{ROSA}')
                ui.label('COZINHA · FICHAS TÉCNICAS').classes('text-xs tracking-[0.25em] text-white/70')
            ui.space()
            ui.label('BOX D3').classes('titulo text-2xl px-3 py-1 rounded').style(f'background:white;color:{TINTA}')
        ui.element('div').classes('faixa w-full')

# ---------- Corpo ----------
with ui.column().classes('w-full max-w-6xl mx-auto px-4 pt-6 pb-10 gap-6'):

    opcoes = {pid: f"{p['categoria']} · {p['nome']}" for pid, p in CARDAPIO.items()}
    ui.select(opcoes, value=estado['prato'], label='Item do cardápio', with_input=True,
              on_change=trocar_prato).props('outlined bg-color=white').classes('w-96')

    with ui.row().classes('w-full gap-6 items-start no-wrap'):

        # Coluna esquerda: receita + cardápio inteiro
        with ui.column().classes('gap-6'):
            with ui.column().classes('cartao p-7 w-[540px] gap-1'):
                receita()
            with ui.column().classes('cartao p-5 w-[540px] gap-1'):
                ui.label('Cardápio inteiro · CMV').classes('titulo text-2xl')
                with ui.scroll_area().classes('w-full h-72'):
                    resumo()

        with ui.column().classes('flex-1 gap-6'):
            with ui.row().classes('w-full gap-6 no-wrap'):
                with ui.column().classes('cartao p-5 flex-1 items-center gap-1'):
                    ui.label('CMV').classes('titulo text-2xl self-start')
                    gauge = ui.echart({'series': [{
                        'type': 'gauge', 'min': 0, 'max': 60, 'startAngle': 200, 'endAngle': -20,
                        'axisLine': {'lineStyle': {'width': 16, 'color': [
                            [30 / 60, MUSGO], [35 / 60, MOSTARDA], [1, ROSA]]}},
                        'pointer': {'width': 5, 'length': '60%', 'itemStyle': {'color': TINTA}},
                        'anchor': {'show': True, 'size': 12, 'itemStyle': {'color': TINTA}},
                        'axisTick': {'show': False}, 'splitLine': {'show': False}, 'axisLabel': {'show': False},
                        'detail': {'formatter': '{value}%', 'fontSize': 38, 'fontFamily': 'Bebas Neue',
                                   'offsetCenter': [0, '45%'], 'color': TINTA},
                        'data': [{'value': 0}],
                    }]}).classes('w-full h-52')
                    status_label = ui.label().classes(
                        'w-full text-center text-white text-sm font-semibold px-3 py-2 rounded-xl')

                with ui.column().classes('w-56 gap-6'):
                    with ui.column().classes('cartao p-5 w-full gap-0'):
                        ui.label('Custo da porção').classes('text-xs uppercase tracking-wider text-gray-400')
                        custo_label = ui.label().classes('titulo text-5xl')
                    with ui.column().classes('cartao p-5 w-full gap-0').style(f'background:{ROXO};color:white'):
                        ui.label(f'Preço p/ CMV {CMV_ALVO:.0%}').classes(
                            'text-xs uppercase tracking-wider text-white/70')
                        sugerido_label = ui.label().classes('titulo text-5xl')

            with ui.column().classes('cartao p-5 w-full gap-1'):
                ui.label('De onde vem o custo').classes('titulo text-2xl')
                barras = ui.echart({
                    'grid': {'left': 140, 'right': 70, 'top': 5, 'bottom': 5},
                    'xAxis': {'type': 'value', 'show': False},
                    'yAxis': {'type': 'category', 'data': [], 'inverse': True,
                              'axisLine': {'show': False}, 'axisTick': {'show': False}},
                    'series': [{'type': 'bar', 'data': [], 'barWidth': 16,
                                'itemStyle': {'color': ROXO, 'borderRadius': [0, 8, 8, 0]},
                                'label': {'show': True, 'position': 'right',
                              ':formatter': 'p => "R$ " + p.value.toFixed(2)'}}],
                }).classes('w-full h-56')

    # Engenharia de cardápio: largura toda, embaixo
    with ui.column().classes('cartao p-6 w-full gap-3'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-0'):
                ui.label('Engenharia de cardápio').classes('titulo text-3xl')
                ui.label('Popularidade (vendas no mês) × margem de contribuição (preço − custo)') \
                    .classes('text-sm text-gray-500')
            with ui.column().classes('items-end gap-1'):
                classe_label = ui.label().classes('text-white text-sm font-semibold px-4 py-2 rounded-full')
                acao_label = ui.label().classes('text-sm text-gray-600')
        matriz = ui.echart({
            'grid': {'left': 60, 'right': 30, 'top': 20, 'bottom': 45},
            'tooltip': {':formatter': 'p => p.name + "<br>" + p.value[0] + " vendidos · margem R$ " + p.value[1].toFixed(2)'},
            'xAxis': {'type': 'value', 'name': 'vendidos no mês', 'nameLocation': 'middle', 'nameGap': 28,
                      'splitLine': {'show': False}},
            'yAxis': {'type': 'value', 'name': 'margem (R$)', 'splitLine': {'show': False}},
            'series': [{
                'type': 'scatter', 'data': [],
                'label': {'show': True, 'position': 'right', 'formatter': '{b}', 'fontSize': 11},
                'markLine': {'silent': True, 'symbol': 'none', 'label': {'show': False},
                             'lineStyle': {'type': 'dashed', 'color': CINZA}, 'data': []},
            }],
        }).classes('w-full h-[420px]')
        with ui.row().classes('w-full gap-6 justify-center'):
            for nome, (cor, ingles, _) in CLASSES.items():
                with ui.row().classes('items-center gap-2'):
                    ui.element('div').classes('w-3 h-3 rounded-full').style(f'background:{cor}')
                    ui.label(f'{nome} ({ingles})').classes('text-sm')

atualizar(inicio=True)  # calcula uma vez ao abrir

ui.run(title='Los Tacos · Cozinha', port=8080, favicon='🌮')
