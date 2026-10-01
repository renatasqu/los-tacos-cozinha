# Ficha técnica da canja: custo por porção

# Frango: 0,8 kg a R$ 19,00 o kg
preco_frango = 19.00
custo_frango = 0.8 * preco_frango

# Arroz: 0,2 kg a R$ 7,00 o kg
preco_arroz = 7.00
custo_arroz = 0.2 * preco_arroz

# Cenoura: 0,2 kg a R$ 6,00 o kg
preco_cenoura = 6.00
custo_cenoura = 0.2 * preco_cenoura

# Soma o custo de todos os ingredientes
custo_total = custo_frango + custo_arroz + custo_cenoura

# A receita rende 4 porções
porcoes = 4
custo_porcao = custo_total / porcoes

# Mostra os resultados, arredondados em 2 casas
print("Custo total da receita:", round(custo_total, 2))
print("Custo por porção:", round(custo_porcao, 2))