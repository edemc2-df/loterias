import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from utils import (
    calcular_atraso,
    calcular_frequencia,
    adicionar_formatacao,
    gerar_melhores_jogos,
    obter_pesos_perfil,
)

st.set_page_config(
    page_title="Loteria Inteligente",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CONFIGURAÇÕES
# =========================
CAMINHO_BASE = "loteria_app/data/Mega-Sena.xlsx"
CAMINHO_LOGO = "assets/logo.png"
NOME_APP = "Loteria Inteligente"
LOTERIA_NOME = "Mega-Sena"

# =========================
# ESTILO
# =========================
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #081120 0%, #0f172a 100%);
        }
        .main .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        .hero {
            background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.95) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 18px 40px rgba(0,0,0,0.22);
            margin-bottom: 1rem;
        }
        .hero-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 1rem;
            margin-bottom: 0;
        }
        .soft-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 20px;
            padding: 1rem 1rem 0.6rem 1rem;
            margin-bottom: 1rem;
        }
        .mini-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            min-height: 120px;
        }
        .mini-label {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        .mini-value {
            color: #f8fafc;
            font-size: 1.15rem;
            font-weight: 700;
            margin-top: 0.3rem;
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
            padding: 0.9rem;
            border-radius: 18px;
        }
        .stButton > button, .stDownloadButton > button {
            width: 100%;
            border-radius: 14px;
            min-height: 3rem;
            font-weight: 700;
        }
        .section-title {
            color: #f8fafc;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .section-text {
            color: #cbd5e1;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# FUNÇÕES AUXILIARES
# =========================
@st.cache_data
def carregar_base(caminho: str) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def detectar_colunas_dezenas(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if "bola" in c or "dezena" in c]


def preparar_base(df: pd.DataFrame, colunas_dezenas: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in colunas_dezenas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=colunas_dezenas).copy()


def descobrir_coluna_data(df: pd.DataFrame) -> str | None:
    candidatas = [c for c in df.columns if "data" in c or c.startswith("dt")]
    for col in candidatas:
        serie = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
        if serie.notna().sum() > 0:
            return col
    return None


def obter_data_mais_recente(df: pd.DataFrame, coluna_data: str | None) -> str:
    if not coluna_data:
        return "-"
    serie = pd.to_datetime(df[coluna_data], dayfirst=True, errors="coerce")
    if serie.notna().sum() == 0:
        return "-"
    return serie.max().strftime("%d/%m/%Y")


def gerar_excel_download(resultado: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        resultado.to_excel(writer, index=False, sheet_name="Jogos")
    buffer.seek(0)
    return buffer.getvalue()


def plot_top_frequencia(frequencia: pd.DataFrame, top_n: int = 12):
    base = frequencia.head(top_n).sort_values("frequencia", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(base["numero"].astype(str), base["frequencia"])
    ax.set_title(f"Top {top_n} números mais frequentes")
    ax.set_xlabel("Frequência")
    ax.set_ylabel("Número")
    plt.tight_layout()
    return fig


def plot_top_atraso(ultimo_concurso: pd.DataFrame, top_n: int = 12):
    base = ultimo_concurso.head(top_n).sort_values("atraso", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(base["numero"].astype(str), base["atraso"])
    ax.set_title(f"Top {top_n} números mais atrasados")
    ax.set_xlabel("Atraso")
    ax.set_ylabel("Número")
    plt.tight_layout()
    return fig


def mostrar_logo():
    caminho = Path(CAMINHO_LOGO)
    if caminho.exists():
        st.sidebar.image(str(caminho), use_container_width=True)
    else:
        st.sidebar.markdown("## 🎯")


# =========================
# SIDEBAR
# =========================
mostrar_logo()
st.sidebar.markdown(f"## {NOME_APP}")
st.sidebar.caption(f"Análise e geração de jogos para {LOTERIA_NOME}")

pagina = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Gerador de Jogos", "Base e Estatísticas"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Perfil")
perfil = st.sidebar.selectbox(
    "Perfil de geração",
    ["conservador", "equilibrado", "agressivo"],
    index=1,
)

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 1, 20, 10)
tentativas = st.sidebar.slider("Tentativas internas", 500, 5000, 1500, step=100)

st.sidebar.markdown("### Pesos do score")
pesos = obter_pesos_perfil(perfil).copy()
pesos["pares_impares"] = st.sidebar.slider("Pares/Ímpares", 0.5, 2.0, float(pesos["pares_impares"]), 0.1)
pesos["faixas"] = st.sidebar.slider("Faixas", 0.5, 2.0, float(pesos["faixas"]), 0.1)
pesos["soma"] = st.sidebar.slider("Soma", 0.5, 2.0, float(pesos["soma"]), 0.1)
pesos["estrategico"] = st.sidebar.slider("Estratégico", 0.5, 3.0, float(pesos["estrategico"]), 0.1)
pesos["sequencia"] = st.sidebar.slider("Sequência", 0.5, 2.0, float(pesos["sequencia"]), 0.1)

gerar = st.sidebar.button("🚀 Gerar jogos")

# =========================
# CARGA DA BASE
# =========================
try:
    df = carregar_base(CAMINHO_BASE)
except FileNotFoundError:
    st.error(f"Arquivo não encontrado em: {CAMINHO_BASE}")
    st.info("Crie a pasta 'data' no projeto e coloque nela o arquivo 'Mega-Sena.xlsx'.")
    st.stop()
except Exception as e:
    st.error("Não foi possível abrir a base fixa.")
    st.exception(e)
    st.stop()

colunas_dezenas = detectar_colunas_dezenas(df)
if not colunas_dezenas:
    st.error("Não encontrei colunas de dezenas. Verifique se os nomes possuem 'bola' ou 'dezena'.")
    st.stop()

df = preparar_base(df, colunas_dezenas)
if df.empty:
    st.error("Após a limpeza, não restaram linhas válidas na base.")
    st.stop()

frequencia = calcular_frequencia(df, colunas_dezenas)
ultimo_concurso = calcular_atraso(df, colunas_dezenas)
coluna_data = descobrir_coluna_data(df)
data_ultimo = obter_data_mais_recente(df, coluna_data)

df["soma_dezenas"] = df[colunas_dezenas].sum(axis=1)
media_soma = df["soma_dezenas"].mean()
desvio_soma = df["soma_dezenas"].std()

top_quentes = frequencia.head(15)["numero"].tolist()
top_frios = frequencia.tail(15)["numero"].tolist()
top_atrasados = ultimo_concurso.head(15)["numero"].tolist()

resultado = pd.DataFrame()
if gerar:
    resultado = gerar_melhores_jogos(
        n_jogos_desejados=qtd_jogos,
        n_tentativas=tentativas,
        perfil=perfil,
        media_soma=media_soma,
        desvio_soma=desvio_soma,
        quentes=top_quentes,
        frios=top_frios,
        atrasados=top_atrasados,
        pesos=pesos,
    )

    if not resultado.empty:
        resultado = adicionar_formatacao(resultado)

# =========================
# CABEÇALHO
# =========================
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">🎯 {NOME_APP}</div>
        <p class="hero-subtitle">
            Dashboard executivo, motor de score configurável e geração inteligente de jogos para <strong>{LOTERIA_NOME}</strong>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Concursos válidos", len(df))
m2.metric("Última data da base", data_ultimo)
m3.metric("Maior atraso atual", int(ultimo_concurso["atraso"].max()))
m4.metric("Média soma histórica", round(media_soma, 1))

# =========================
# PÁGINAS
# =========================
if pagina == "Dashboard":
    c1, c2 = st.columns([1.05, 1], gap="large")

    with c1:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Resumo executivo</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="section-text">
            A base histórica está carregada com <strong>{len(df)}</strong> concursos válidos. O modelo atual usa o perfil
            <strong>{perfil}</strong>, com pesos ajustáveis para equilíbrio, distribuição por faixas, soma histórica,
            componente estratégico e penalização por sequência.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        fig_freq = plot_top_frequencia(frequencia, top_n=12)
        st.pyplot(fig_freq, use_container_width=True)

    with c2:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Configuração atual</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="section-text">
            Perfil: <strong>{perfil}</strong><br>
            Quantidade de jogos: <strong>{qtd_jogos}</strong><br>
            Tentativas internas: <strong>{tentativas}</strong><br>
            Última data da base: <strong>{data_ultimo}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        fig_atraso = plot_top_atraso(ultimo_concurso, top_n=12)
        st.pyplot(fig_atraso, use_container_width=True)

    if resultado.empty:
        st.info("Use o menu lateral para ajustar os parâmetros e clique em **Gerar jogos**.")
    else:
        st.markdown("### Jogos destaque")
        cards = st.columns(min(3, len(resultado)))
        for i, (_, row) in enumerate(resultado.head(3).iterrows()):
            with cards[i]:
                st.markdown(
                    f"""
                    <div class="mini-card">
                        <div class="mini-label">Jogo destaque #{i+1}</div>
                        <div class="mini-value">{row['jogo_formatado']}</div>
                        <div class="mini-label" style="margin-top:0.55rem;">Score total: {row['score_total']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

elif pagina == "Gerador de Jogos":
    st.markdown("### Jogos recomendados")

    if resultado.empty:
        st.warning("Clique em **Gerar jogos** no menu lateral para criar as combinações.")
    else:
        st.dataframe(
            resultado[
                [
                    "jogo_formatado",
                    "score_total",
                    "pares_impares_pond",
                    "faixas_pond",
                    "soma_pond",
                    "estrategico_pond",
                    "sequencia_pond",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        excel_bytes = gerar_excel_download(resultado)
        st.download_button(
            "⬇️ Baixar jogos em Excel",
            data=excel_bytes,
            file_name="jogos_recomendados_mega_sena.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

elif pagina == "Base e Estatísticas":
    tab1, tab2, tab3 = st.tabs(["Frequência", "Atraso", "Base tratada"])

    with tab1:
        st.dataframe(frequencia, use_container_width=True, hide_index=True)

    with tab2:
        st.dataframe(ultimo_concurso, use_container_width=True, hide_index=True)
        
    with tab3:
        st.dataframe(df.head(50), use_container_width=True, hide_index=True)

st.markdown(
    """
    <hr style="margin-top: 40px;">
    <div style='text-align: center; color: #94a3b8; font-size: 14px;'>
        Desenvolvido por <strong>Ed </strong> 🚀
    </div>
    """,
    unsafe_allow_html=True
)

    
