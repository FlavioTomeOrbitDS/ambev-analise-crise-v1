import streamlit as st
import pandas as pd
import asyncio
from utils_async import process_comments
from datetime import datetime
from utils_files import *

# Funções Assíncronas
def get_event_loop():
    """Garante que um event loop esteja disponível, criando um se necessário."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if "There is no current event loop in thread" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
        raise

async def async_process_comments(df, context, api_key):
    """Processa comentários de forma assíncrona."""
    return await process_comments(df, context, api_key)

def run_async_process(df, context, api_key):
    """Executa o processamento assíncrono de comentários."""
    loop = get_event_loop()
    return loop.run_until_complete(async_process_comments(df, context, api_key))

# TABS ==================================================
def tab_conversas(tab):
    return None
    # tab.button('➕ Nova conversa',
    #             on_click=seleciona_conversa,
    #             args=('', ),
    #             use_container_width=True)
    # tab.markdown('')
    # conversas = listar_conversas()
    # for nome_arquivo in conversas:
    #     nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
    #     if len(nome_mensagem) == 30:
    #         nome_mensagem += '...'
    #     tab.button(nome_mensagem,
    #         on_click=seleciona_conversa,
    #         args=(nome_arquivo, ),
    #         disabled=nome_arquivo==st.session_state['conversa_atual'],
    #         use_container_width=True)

def tab_configuracoes(tab):
    modelo_escolhido = tab.selectbox('Selecione o modelo',
                                     ['gpt-3.5-turbo', 'gpt-4'])
    st.session_state['modelo'] = modelo_escolhido

    chave = tab.text_input('Adicione sua api key', value=st.session_state['api_key'])
    if chave != st.session_state['api_key']:
        st.session_state['api_key'] = chave
        salva_chave(chave)
        tab.success('Chave salva com sucesso')

# Função Principal
def main():
    st.set_page_config(page_title="Orbit AI", layout='centered')
    print(f"##### Executando Main...{datetime.now()}")
    
    
    inicializacao()
    tab1, tab2 = st.sidebar.tabs(['Conversas', 'Configurações'])
    tab_conversas(tab1)
    tab_configuracoes(tab2)
    
    
    st.header('Ambev Crises')

    uploaded_file = st.file_uploader("Faça o upload do arquivo Excel com os comentários", type="xlsx")
    df_texto = handle_uploaded_file(uploaded_file)
    
    
    prompt = st.chat_input('Descreva o contexto da análise...')    
    if prompt:
        if df_texto is None:
            st.error("Faça o upload do arquivo Excel!")
        else:
            api_key = st.session_state['api_key']
            results = run_async_process(df_texto, prompt, api_key)
            display_results(results)
    
        

def handle_uploaded_file(uploaded_file, limit=1000):
    """Processa o arquivo carregado e retorna um DataFrame se encontrado. limit é o tamanho maximo de textos"""
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df = df.head(limit)
        if 'Texto' in df.columns:
            st.dataframe(df)  # Mostra somente as primeiras 1000 linhas
            return df
        else:
            st.error("A coluna 'Texto' não foi encontrada no arquivo.")
    return None

def display_results(results):
    """Exibe os resultados processados."""
    if results:
        results_str = ''.join(results)
        st.write(results_str)

def inicializacao():
    """Inicializa a sessão do Streamlit, se necessário."""
    if 'mensagens' not in st.session_state:
        st.session_state['mensagens'] = []
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''
    if not 'modelo' in st.session_state:
        st.session_state.modelo = 'gpt-3.5-turbo'
    if not 'api_key' in st.session_state:
        st.session_state.api_key = le_chave()
    
    
    
    print("##### Sessão inicializada.")

if __name__ == '__main__':
    main()
