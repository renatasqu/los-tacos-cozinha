import streamlit as st

st.title("🍽️ Ficha técnica: canja")

# Preços dos ingredientes
preco_frango = st.number_input("Preço do frango (R$/kg)", value=19.00)
preco_arroz = st.number_input("Preço do arroz (R$/kg)", value=7.00)
preco_cenoura = st.number_input("Preço da cenoura (R$/kg)", value=6.00)
porcoes = st.number_input("Porções", value=4, min_value=1)

# Custo da receita
custo_total = 0.8 * preco_frango + 0.2 * preco_arroz + 0.2 * preco_cenoura
custo_porcao = custo_total / porcoes

st.metric("Custo por porção", f"R$ {custo_porcao:.2f}")
st.write("Custo total da receita:", round(custo_total, 2))

# Preço de venda e CMV
preco_venda = st.number_input("Preço de venda (R$)", value=32.00)
cmv = custo_porcao / preco_venda

# Preço mínimo para o CMV ficar em 30%
preco_sugerido = custo_porcao / 0.30

st.metric("CMV", f"{cmv * 100:.1f}%")
st.metric("Preço sugerido (CMV 30%)", f"R$ {preco_sugerido:.2f}")

# Semáforo
if cmv <= 0.30:
    st.success(f"CMV de {cmv * 100:.1f}%: prato redondo, custo sob controle e margem boa.")
elif cmv <= 0.35:
    st.warning(f"CMV de {cmv * 100:.1f}%: margem apertando. Confira a gramatura e o desperdício.")
else:
    st.error(f"CMV de {cmv * 100:.1f}%: prato caro de produzir. Revise preço, porção ou fornecedor.")