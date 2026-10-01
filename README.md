# 🌮 Los Tacos · Cozinha

App interno para a equipe de cozinha de um restaurante **fictício**, o Los Tacos (Box D3).
Mostra a **ficha técnica** de cada item do cardápio, o **custo por porção**, o **CMV** e o
**preço sugerido**, com um semáforo que indica quais pratos precisam de atenção.


## Por que este projeto

Fui chef e dona de restaurante por mais de 10 anos. Ficha técnica e CMV eram feitos em planilha,
à mão, e quase nunca atualizados. Este app transforma esse processo em algo visual, que a equipe
consegue usar no dia a dia.

## O que ele faz

- Lê o cardápio e as fichas técnicas de dois arquivos CSV
- Calcula custo por porção, CMV e preço sugerido para CMV de 30%
- Velocímetro de CMV: verde (até 30%), amarelo (até 35%) e vermelho (acima)
- Mostra quais ingredientes pesam mais no custo de cada prato
- Lista o cardápio inteiro do pior para o melhor CMV
- Permite editar quantidades e preços na tela e salvar de volta nos CSVs

## Como rodar

```bash
python3 -m venv venv
source venv/bin/activate
pip install nicegui
python3 app_nicegui.py
```

Abra http://localhost:8080.

## Como o projeto evoluiu

Este foi o meu primeiro projeto em Python, construído em etapas:

1. `prato.py`: o custo de uma canja, em Python puro
2. `app.py`: a primeira interface, em Streamlit, com CMV e semáforo
3. `app_nicegui.py`: o app atual, em NiceGUI, com a identidade visual do Los Tacos

## Roadmap

| Fase | O que entra | O que o app passa a mostrar |
|---|---|---|
| ✅ 1 | Fichas técnicas | Custo, CMV e preço sugerido por prato |
| 2 | Vendas | Popularidade, margem de contribuição e matriz Stars / Plowhorses / Puzzles / Dogs |
| 3 | Compras | Evolução do custo dos ingredientes e alertas de alta |
| 4 | Estoque | Desperdício: CMV teórico × CMV real |
| 5 | SQLite | Todos os dados cruzados num banco |
| 6 | Itens críticos | Tela de alertas com o que revisar primeiro |

## Dados

O restaurante, o cardápio e as fichas técnicas são **fictícios**, criados para este projeto.

**Stack:** Python · NiceGUI · ECharts · CSV