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

# CSS para cores
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

            # 1. Gráfico de Colunas Agrupadas
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

            # 2. Evolução Temporal
            st.subheader("Evolução do Índice")

            # Preparação dos dados
            df_historico = self.df_completo[self.df_completo['ATLETA'] == self.atleta].sort_values('DATA').copy()
            df_historico['DATA_STR'] = df_historico['DATA'].dt.strftime('%d/%m/%Y')

            df_media_hist = self.df_completo[
                (self.df_completo['POSICAO'] == posicao_atual) &
                (self.df_completo['DATA'].isin(df_historico['DATA']))
                ].groupby('DATA')['INDICE'].mean().reset_index()
            df_media_hist['DATA_STR'] = df_media_hist['DATA'].dt.strftime('%d/%m/%Y')

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
                    title_text='DATA',
                    gridcolor='rgba(255, 255, 255, 0.1)'
                ),
                yaxis=dict(
                    title_text="ÍNDICE",
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zerolinecolor='rgba(255, 255, 255, 0.2)'
                ),
                showlegend=True,
                margin=dict(t=10)
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

                    # Formatação do rótulo
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
                        textfont=dict(size=11, color='black'),
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
                            gridcolor='rgba(0, 0, 0, 0.15)',
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
    # 1. Localizacao dos arquivos
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    diretorio_raiz = os.path.dirname(diretorio_script)

    caminho_excel = os.path.join(diretorio_raiz, "Data", "Jogos Serra.xlsx")

    # Carregamento do DataFrame
    df = pd.read_excel(caminho_excel)

    # Limpeza das colunas e data
    df.columns = [str(col).strip().upper() for col in df.columns]
    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'])
    else:
        st.error("Coluna 'DATA' não encontrada no Excel.")
        st.stop()

    # 2. ESCUDO NO TOPO DA SIDEBAR (Canto Superior Esquerdo)
    try:
        caminho_escudo = os.path.join(diretorio_raiz, "IMAGES", "Escudo Serra Branca.PNG")

        if os.path.exists(caminho_escudo):
            img = Image.open(caminho_escudo)

            # O segredo é usar int() para arredondar o resultado
            nova_largura = int(img.size * 0.75)

            # Exibe na sidebar
            st.sidebar.image(img, width=nova_largura)
        else:
            st.sidebar.warning("Escudo não encontrado na pasta IMAGES.")
    except Exception as e:
        st.sidebar.error(f"Erro ao processar imagem: {e}")

    # 3. CONFIGURAÇÃO DA SIDEBAR (Filtros únicos)
    st.sidebar.header("Filtros")

    data_opcoes = df['DATA'].dt.strftime('%d/%m/%Y').unique()
    data_sel_str = st.sidebar.selectbox("Selecione a Data", data_opcoes, key="data_principal")

    df_partida = df[df['DATA'].dt.strftime('%d/%m/%Y') == data_sel_str]

    # 4. ÁREA PRINCIPAL
    if not df_partida.empty:
        try:
            nome_adversario = df_partida['ADVERSARIO'].values
        except:
            nome_adversario = "N/A"

        st.info(f"🏟️ Partida: {nome_adversario}")

        # Tabs de navegação
        tab1, tab2 = st.tabs(["👤 Desempenho Atleta", "👥 Comparativo Equipe"])

        with tab1:
            atleta_sel = st.selectbox(
                "Selecione o Atleta",
                sorted(df_partida['ATLETA'].unique()),
                key="atleta_aba_individual"
            )
            # Renderização da aba
            AbaDesempenho(df_partida, df, atleta_sel).render()

        with tab2:
            # Renderização da aba da equipe
            AbaEquipe(df_partida).render()
    else:
        st.warning("Nenhum dado encontrado para a data selecionada.")

except FileNotFoundError:
    st.error(f"Erro: Arquivo Excel não encontrado. Verifique se a pasta 'Data' está correta no GitHub.")
except Exception as e:
    st.error(f"Erro crítico no sistema: {e}")