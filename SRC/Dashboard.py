import streamlit as st
import pandas as pd
import os
import base64
from PIL import Image
from Styles import apply_custom_styles
from Componentes import AbaDesempenho, AbaEquipe

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Análise de Desempenho", initial_sidebar_state="collapsed")
apply_custom_styles()

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

try:
    # 1. Identifica onde o script está (Pasta SRC)
    diretorio_script = os.path.dirname(os.path.abspath(__file__))

    # 2. Sobe um nível para a raiz do projeto (Onde ficam Data e IMAGES)
    diretorio_raiz = os.path.dirname(diretorio_script)

    # 3. Define os caminhos usando a RAIZ, não o diretorio_script
    caminho_excel = os.path.join(diretorio_raiz, "Data", "Jogos Serra.xlsx")
    caminho_escudo = os.path.join(diretorio_raiz, "IMAGES", "Escudo Serra Branca.PNG")

    #Cabeçalho
    if os.path.exists(caminho_escudo):
        def get_image_base64(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()

        img_64 = get_image_base64(caminho_escudo)

        st.markdown(
            f"""
                <div style="display: flex; 
                align-items: center;
                justify-content: center 
                gap: 600px; 
                margin-bottom: 10px;
                padding-bottom: 25px;
                margin-top: -10px;">
                    <img src="data:image/png;base64,{img_64}" width="120">
                    <h1 style="color: #32CD32; margin: 0; font-size: 48px;">ANÁLISE DE DADOS SERRA BRANCA</h1>
                </div>
                """, unsafe_allow_html=True
        )
    else:
        st.title("Análise de Desempenho Serra Branca")

    st.divider()

    # 4. Agora sim, lê o arquivo
    df = pd.read_excel(caminho_excel)

    df.columns = [str(col).strip().upper() for col in df.columns]
    df['DATA'] = pd.to_datetime(df['DATA'])

    tab1, tab2 = st.tabs(["👤 Desempenho Atleta", "👥 Comparativo Equipe"])

    tab_atleta, tab_equipe = st.columns(2)
    with tab1:
        # 1. Filtros no topo da aba (usando colunas para ficarem lado a lado)
        c1, c2 = st.columns(2)

        with c1:
            # Pega as datas únicas para o filtro
            data_opcoes = df['DATA'].dt.strftime('%d/%m/%Y').unique()
            data_sel_str = st.selectbox("📅 Selecione a Data", data_opcoes, key="data_filtro_atleta")

        # Filtra os dados da partida baseada na data escolhida
        df_partida = df[df['DATA'].dt.strftime('%d/%m/%Y') == data_sel_str]

        with c2:
            # O seletor de atleta só mostra quem jogou naquela data
            atleta_sel = st.selectbox(
                "👤 Selecione o Atleta",
                sorted(df_partida['ATLETA'].unique()),
                key="atleta_sel_final"
            )

        # Espaçador visual sutil
        st.markdown("<br>", unsafe_allow_html=True)

        if not df_partida.empty:
            # INSTANCIAÇÃO: Passamos (DataFrame da Partida, DataFrame Completo, Nome do Atleta)
            analise = AbaDesempenho(df_partida, df, atleta_sel)

            # EXECUÇÃO
            analise.render()
        else:
            st.warning("Selecione uma data válida.")

    with tab2:
        AbaEquipe(df).render()

        # 2. Banner de informação da partida (opcional, igual ao seu anterior)
        # if not df_partida.empty:
        #    adv = df_partida['ADVERSARIO'].iloc
            # st.info(f"🏟️ Partida: {adv}") # Remova o comentário se quiser o banner azul

            # 3. Chama a classe para renderizar os gráficos logo abaixo
        #    AbaDesempenho(df_partida, df, atleta_sel).render()
        #else:
        #    st.warning("Selecione uma data válida.")

except Exception as e:
    st.error(f"Erro crítico: {e}")