import streamlit as st
import pandas as pd
from datetime import datetime
import os

ARQ_PEDIDOS = "pedidos.xlsx"
ARQ_USUARIOS = "usuarios.xlsx"
ARQ_LOG = "acessos.xlsx"

st.set_page_config(page_title="Painel de Colheita", layout="wide")
st.title("🌱 Painel de Colheita")

# ================= LOGIN =================

if "logado" not in st.session_state:
    st.session_state.logado = False

def registrar_acesso(usuario):
    if os.path.exists(ARQ_LOG):
        log = pd.read_excel(ARQ_LOG)
    else:
        log = pd.DataFrame(columns=["Usuario", "DataHora"])

    log.loc[len(log)] = [usuario, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
    log.to_excel(ARQ_LOG, index=False)

if not st.session_state.logado:
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuarios = pd.read_excel(ARQ_USUARIOS)
        valido = usuarios[
            (usuarios["usuario"] == usuario) &
            (usuarios["senha"] == senha)
        ]

        if not valido.empty:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.perfil = valido.iloc[0]["perfil"]
            registrar_acesso(usuario)
            st.success("Login realizado com sucesso")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

# ================= PAINEL =================

st.sidebar.success(f"Logado como: {st.session_state.usuario}")

df = pd.read_excel(ARQ_PEDIDOS)

st.subheader("📋 Pedidos")
st.dataframe(df, use_container_width=True)

st.subheader("📊 Resumo por Produto")
resumo = df.groupby("Produto")["Quantidade"].sum().reset_index()
st.dataframe(resumo, use_container_width=True)

# ================= ADMIN =================

if st.session_state.perfil == "admin":
    st.subheader("✏️ Área do Administrador")

    with st.form("novo_pedido"):
        data = st.text_input("Data (dd/mm/aaaa)", datetime.now().strftime("%d/%m/%Y"))
        categoria = st.text_input("Categoria", "Hidroponia")
        produto = st.text_input("Produto")
        quantidade = st.number_input("Quantidade", min_value=0)
        status = st.selectbox("Status", ["Total", "Parcial", "Sem colheita"])

        if st.form_submit_button("Adicionar Pedido"):
            df.loc[len(df)] = [data, categoria, produto, quantidade, status]
            df.to_excel(ARQ_PEDIDOS, index=False)
            st.success("Pedido adicionado com sucesso")
            st.rerun()

    st.subheader("👁️ Histórico de Acessos")
    if os.path.exists(ARQ_LOG):
        st.dataframe(pd.read_excel(ARQ_LOG), use_container_width=True)

else:
    st.info("🔒 Acesso somente para visualização")
