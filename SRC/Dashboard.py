import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import os
from PIL import Image

#EQUIPE
#Escala de cores para posicoes
#aba primeira
#editar data sem horario
#Comparar indices igual na planilha
#Adicionar filtro de geral para todas as partidas para comparar todos os jogos, e nao apenas o jogo a jogo

#ARQUIVO
#Enviar dash
#Colocar fotos dos jogadores

# Organizar código ( modularizar )

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Análise de Desempenho")

# Injeção de CSS para cores Azul Marinho e Azul Médio (caixas)
st.markdown(
    """
    <style>
    /* 1. Fundo Principal (O tom mais escuro) */
    .stApp {
        background-color: #001524; 
    }

    /* 2. Caixa de Informações (st.info) */
    div[data-testid="stNotification"] {
        background-color: #0A243D; /* Azul mais claro/médio */
        color: white;
        border: none;
    }

    /* 3. Caixas de Seleção (Selectbox) e Inputs */
    div[data-baseweb="select"] > div {
        background-color: #0A243D !important;
        color: white !important;
        border: 1px solid #32CD32; /* Borda verde limão para destacar */
    }

    /* 4. Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #001524;
    }

    /* 5. Títulos em Verde Limão */
    h1, h2, h3 {
        color: #32CD32 !important;
    }

    /* 6. Texto das Abas */
    .stTabs [data-baseweb="tab"] {
        color: white !important;
    }
    
    /* 7. Remover toolbar */
    header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0%;
}
    </style>
    """,
    unsafe_allow_html=True
)


class AbaDesempenho:
    METRICAS_POR_POSICAO = {
        'Zagueiro': ['ACOES', '% ACOES COM SUCESSO', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                     '% PASSES PROGRESSIVOS CONCLUIDOS',
                     'DISPUTAS', '% DISPUTAS GANHAS', 'DESARMES REALIZADOS', '% DESARMES REALIZADOS COM SUCESSO',
                     'PERDA DA BOLA', 'RETOMADA DE POSSE',
                     'BOLA RECUPERADA'],
        'Lateral': ['ACOES', '% ACOES COM SUCESSO', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                    '% PASSES PROGRESSIVOS CONCLUIDOS', 'CRUZAMENTOS',
                    'CHANCES CRIADAS', 'DISPUTAS', '% DISPUTAS GANHAS', 'DESARMES REALIZADOS',
                    '% DESARMES REALIZADOS COM SUCESSO', 'DRIBLES FEITOS',
                    '% DRIBLES FEITOS COM SUCESSO', 'PERDA DA BOLA', 'RETOMADA DE POSSE', 'BOLA RECUPERADA'],
        'Volante': ['ACOES', '% ACOES COM SUCESSO', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                    '% PASSES PROGRESSIVOS CONCLUIDOS', 'DISPUTAS',
                    '% DISPUTAS GANHAS', 'DESARMES REALIZADOS', '% DESARMES REALIZADOS COM SUCESSO', 'ACOES ULTIMO 3º',
                    '% ACOES ULTIMO 3º COM SUCESSO', 'PASSES CHAVE',
                    'CHANCES CRIADAS', 'PERDA DA BOLA', 'RETOMADA DE POSSE', 'BOLA RECUPERADA'],
        'Meia': ['ACOES', '% ACOES COM SUCESSO', 'FINALIZACOES', 'FINALIZACOES NO ALVO', 'CHANCES DE GOL',
                 'CHANCES CRIADAS', 'FALTAS', 'FALTAS SOFRIDAS',
                 'PASSES PROGRESSIVOS', '% PASSES PROGRESSIVOS CONCLUIDOS', 'ACOES ULTIMO 3º',
                 '% ACOES ULTIMO 3º COM SUCESSO', 'DRIBLES FEITOS', '% DRIBLES FEITOS COM SUCESSO',
                 'PASSES CHAVE', 'RETOMADA DE POSSE', 'PERDA DA BOLA', 'DISPUTAS', '% DISPUTAS GANHAS',
                 'BOLA RECUPERADA'],
        'Extremo': ['ACOES', '% ACOES COM SUCESSO', 'ACOES ULTIMO 3º', '% ACOES ULTIMO 3º COM SUCESSO', 'FINALIZACOES',
                    'FINALIZACOES NO ALVO', 'CHANCES DE GOL',
                    'CHANCES CRIADAS', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                    '% PASSES PROGRESSIVOS CONCLUIDOS', 'DRIBLES FEITOS',
                    '% DRIBLES FEITOS COM SUCESSO', 'PASSES CHAVE', 'CRUZAMENTOS', 'DISPUTAS', '% DISPUTAS GANHAS'],
        'Atacante': ['ACOES', '% ACOES COM SUCESSO', 'ACOES ULTIMO 3º', '% ACOES ULTIMO 3º COM SUCESSO', 'FINALIZACOES',
                     'FINALIZACOES NO ALVO',
                     'CHANCES DE GOL', 'CHANCES CRIADAS', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                     '% PASSES PROGRESSIVOS CONCLUIDOS',
                     'DRIBLES FEITOS', '% DRIBLES FEITOS COM SUCESSO', 'DISPUTAS', '% DISPUTAS GANHAS', 'PASSES CHAVE']
    }

    def __init__(self, df_partida, df_completo, atleta):
        self.df_partida = df_partida
        self.df_completo = df_completo
        self.atleta = atleta

    def render(self):
        df_atleta = self.df_partida[self.df_partida['ATLETA'] == self.atleta]

        if not df_atleta.empty:
            st.header(f"📊 Análise Individual: {self.atleta}")
            posicao_atual = df_atleta['POSICAO'].iloc[0]

            # --- 1. Gráfico de Colunas Agrupadas ---
            st.subheader(f"Comparativo de Fundamentos: {posicao_atual}")
            metricas_especificas = self.METRICAS_POR_POSICAO.get(posicao_atual, ['INDICE'])
            metricas_especificas = [m for m in metricas_especificas if m in df_atleta.columns]

            dados_atleta = df_atleta[metricas_especificas].iloc[0].to_frame().reset_index()
            dados_atleta.columns = ['Métrica', 'Valor'];
            dados_atleta['Tipo'] = self.atleta

            dados_media = self.df_partida[self.df_partida['POSICAO'] == posicao_atual][
                metricas_especificas].mean().to_frame().reset_index()
            dados_media.columns = ['Métrica', 'Valor'];
            dados_media['Tipo'] = f"Média {posicao_atual}"

            df_comparativo = pd.concat([dados_atleta, dados_media])

            fig_colunas = px.bar(df_comparativo, x='Métrica', y='Valor', color='Tipo', barmode='group', text_auto='.1f',
                                 color_discrete_map={self.atleta: '#32CD32', f"Média {posicao_atual}": '#808080'})

            fig_colunas.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            fig_colunas.update_layout(xaxis_tickangle=-45, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      font=dict(color='white'))
            st.plotly_chart(fig_colunas, use_container_width=True)

            # --- 2. Evolução Temporal ---
            st.subheader("Evolução do Índice")  # Mantemos apenas o título do Streamlit

            # Preparação dos dados (mantida)
            df_historico = self.df_completo[self.df_completo['ATLETA'] == self.atleta].sort_values('DATA').copy()
            df_historico['DATA_STR'] = df_historico['DATA'].dt.strftime('%d/%m/%Y')

            df_media_hist = self.df_completo[
                (self.df_completo['POSICAO'] == posicao_atual) &
                (self.df_completo['DATA'].isin(df_historico['DATA']))
                ].groupby('DATA')['INDICE'].mean().reset_index()
            df_media_hist['DATA_STR'] = df_media_hist['DATA'].dt.strftime('%d/%m/%Y')

            # Criamos o gráfico SEM o parâmetro title interno
            fig_evolucao = px.line(
                df_historico,
                x='DATA_STR',
                y='INDICE',
                markers=True,
                color_discrete_sequence=['#32CD32']
            )

            fig_evolucao.add_scatter(
                x=df_media_hist['DATA_STR'],
                y=df_media_hist['INDICE'],
                mode='lines+markers',
                name="Média Posição",
                line=dict(color='gray', dash='dash')
            )

            # Ajustes de Layout e Remoção do DATA_STR
            fig_evolucao.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(
                    type='category',
                    title_text='DATA',  # <--- REMOVE O "DATA_STR"
                    gridcolor='rgba(255, 255, 255, 0.1)'
                ),
                yaxis=dict(
                    title_text="ÍNDICE",
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zerolinecolor='rgba(255, 255, 255, 0.2)'
                ),
                showlegend=True,
                margin=dict(t=10)  # Reduz a margem superior já que o título agora é do Streamlit
            )

            st.plotly_chart(fig_evolucao, use_container_width=True)

            # --- SEÇÃO DE MINI GRÁFICOS DINÂMICOS (Cards) ---
            st.divider()
            st.subheader(f"Indicadores de Performance - {posicao_atual}")

            metricas_para_exibir = [m for m in metricas_especificas if m in df_historico.columns]
            cols = st.columns(2)

            for i, metrica in enumerate(metricas_para_exibir):
                with cols[i % 2]:
                    fig_mini = go.Figure()

                    # Lógica de formatação do rótulo
                    if metrica.startswith('%'):
                        texto_pontos = df_historico[metrica].apply(lambda x: f"{x:.1f}%")
                    else:
                        texto_pontos = df_historico[metrica].apply(lambda x: f"{x:.1f}")

                    # 1. Gráfico com valores na cor PRETA
                    fig_mini.add_trace(go.Scatter(
                        x=df_historico['DATA_STR'],
                        y=df_historico[metrica],
                        mode='lines+markers+text',
                        text=texto_pontos,
                        textposition="top center",
                        textfont=dict(size=11, color='black'),  # <--- Valores em PRETO
                        line=dict(color='#B22222', width=3),
                        marker=dict(symbol='square', size=8, color='#B22222'),
                        name=metrica
                    ))

                    # 2. Configuração de Layout com Grades mais Escuras
                    fig_mini.update_layout(
                        title=dict(
                            text=f"<b>{metrica}</b>",
                            x=0.5,
                            xanchor='center',
                            font=dict(size=14, color='black')
                        ),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        margin=dict(l=10, r=10, t=50, b=10),
                        height=230,
                        showlegend=False,

                        xaxis=dict(
                            showgrid=False,
                            tickfont=dict(size=10, color='gray')
                        ),

                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(0, 0, 0, 0.15)',  # <--- Grade um pouco mais escura (0.15)
                            showticklabels=False,
                            zeroline=False,
                            range=[df_historico[metrica].min() * 0.7, df_historico[metrica].max() * 1.3]
                        ),
                    )

                    # Linha de média sutil
                    valor_medio = df_historico[metrica].mean()
                    fig_mini.add_hline(y=valor_medio, line_dash="dot", line_color="rgba(0, 0, 0, 0.1)", line_width=1)

                    st.plotly_chart(fig_mini, use_container_width=True, config={'displayModeBar': False})

            # 5. Histórico Completo
            st.divider()
            st.subheader(f"Histórico de Partidas Disputadas por {self.atleta}")

            df_display = df_historico.copy()
            df_display['DATA'] = df_display['DATA_STR']  # Usa a data já formatada acima
            colunas_remover = ['NOME', 'ATLETA', 'POSICAO']
            df_display = df_display.drop(columns=colunas_remover, errors='ignore')

            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("Dados do atleta não encontrados.")


class AbaEquipe:
    def __init__(self, df_partida):
        self.df = df_partida

    def render(self):
        st.header("🏆 Comparativo da Equipe")
        metric_pos = st.selectbox("Métrica para comparar posições", ['INDICE', 'ACOES'])
        df_posicoes = self.df.groupby('POSICAO')[metric_pos].mean().sort_values(ascending=False).reset_index()
        fig_pos = px.bar(df_posicoes, x='POSICAO', y=metric_pos, color='POSICAO')
        st.plotly_chart(fig_pos)


# --- EXECUÇÃO PRINCIPAL ---
try:
    df = pd.read_excel(r"C:\Users\Calafange\PycharmProjects\Análise de Desempenho\Data\Jogos Serra.xlsx")
    # ... limpeza das colunas e data (mantido) ...

    # --- ESCUDO NO TOPO DA SIDEBAR COM REDUÇÃO DE 25% ---
    try:
        # Pega o caminho absoluto para não dar erro
        diretorio_script = os.path.dirname(os.path.abspath(__file__))
        diretorio_raiz = os.path.dirname(diretorio_script)
        caminho_escudo = os.path.join(diretorio_raiz, "IMAGES", "Escudo Serra Branca.PNG")

        if os.path.exists(caminho_escudo):
            # 1. Abrimos a imagem original com o Pillow
            img = Image.open(caminho_escudo)

            # 2. Lógica de Redimensionamento:
            # Pegamos a largura original e calculamos 75% dela (redução de 25%)
            largura_original = img.size[0]
            nova_largura = int(largura_original * 0.75)

            # 3. Exibimos na sidebar com a largura reduzida
            # Usamos o PIL apenas para abrir/processar, e o Streamlit para exibir
            st.sidebar.image(img, width=nova_largura)

    except Exception as e:
        st.sidebar.error(f"Erro ao carregar escudo: {e}")

    # 2. Agora sim, o cabeçalho de Filtros e os Seletores
    st.sidebar.header("Filtros")

    data_opcoes = df['DATA'].dt.strftime('%d/%m/%Y').unique()
    data_sel_str = st.sidebar.selectbox("Selecione a Data", data_opcoes)
    df_partida = df[df['DATA'].dt.strftime('%d/%m/%Y') == data_sel_str]

    if not df_partida.empty:
        # ... dentro do if not df_partida.empty: ...
        st.info(f"🏟️ Partida: {df_partida.iloc[0].get('ADVERSARIO', 'N/A')}")

        # --- NOVO BLOCO DE CABEÇALHO COM CAMINHO ROBUSTO ---
        col_titulo, col_imagem = st.columns([9, 1])

        tab1, tab2 = st.tabs(["👤 Desempenho Atleta", "👥 Comparativo Equipe"])

        with tab1:
            atleta_sel = st.selectbox("Selecione o Atleta", sorted(df_partida['ATLETA'].unique()), key="filtro_atleta")
            AbaDesempenho(df_partida, df, atleta_sel).render()
        with tab2:
            AbaEquipe(df_partida).render()
    else:
        st.error("Nenhum dado encontrado para esta data.")
except Exception as e:
    st.error(f"Erro crítico: {e}")