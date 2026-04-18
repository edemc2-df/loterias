from __future__ import annotations

import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from utils import (
    COMPONENT_LABELS,
    LOTTERY_CONFIGS,
    PROFILE_HELP,
    PROFILE_LABELS,
    adicionar_formatacao,
    analisar_loteria,
    gerar_melhores_jogos,
    obter_pesos_perfil,
)


APP_TITLE = "Loterias Inteligentes"
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

sns.set_theme(style="whitegrid")

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def carregar_analise(lottery_key: str) -> dict[str, object]:
    return analisar_loteria(lottery_key)


def aplicar_estilo(config: dict[str, object]) -> None:
    accent = config["accent"]
    accent_soft = config["accent_soft"]
    st.markdown(
        f"""
        <style>
            :root {{
                --accent: {accent};
                --accent-soft: {accent_soft};
                --text-main: #f8fafc;
                --text-soft: #cbd5e1;
                --text-muted: #94a3b8;
                --card-dark: rgba(7, 16, 29, 0.78);
                --card-soft: rgba(255, 255, 255, 0.04);
                --border-soft: rgba(255, 255, 255, 0.09);
            }}
            .stApp {{
                background:
                    radial-gradient(circle at top left, rgba(255,255,255,0.03), transparent 28%),
                    linear-gradient(180deg, #06101d 0%, #0d1726 46%, #101826 100%);
            }}
            .main .block-container {{
                max-width: 1500px;
                padding-top: 1.2rem;
                padding-bottom: 2.5rem;
            }}
            [data-testid="stSidebar"] {{
                background:
                    radial-gradient(circle at top right, rgba(255,255,255,0.05), transparent 22%),
                    linear-gradient(180deg, #08111f 0%, #0f1725 100%);
                border-right: 1px solid var(--border-soft);
            }}
            [data-testid="stSidebar"] * {{
                color: var(--text-main);
            }}
            .hero {{
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015)),
                    linear-gradient(135deg, rgba(6,16,29,0.92), rgba(10,22,38,0.88));
                border: 1px solid var(--border-soft);
                border-radius: 28px;
                padding: 1.5rem 1.7rem;
                box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
                margin-bottom: 1rem;
            }}
            .hero-tag {{
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                background: rgba(255,255,255,0.06);
                color: var(--text-main);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 999px;
                padding: 0.35rem 0.8rem;
                font-size: 0.85rem;
                margin-bottom: 0.85rem;
            }}
            .hero-title {{
                color: var(--text-main);
                font-size: 2rem;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 0.35rem;
                font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            }}
            .hero-subtitle {{
                color: var(--text-soft);
                font-size: 1rem;
                max-width: 980px;
                margin-bottom: 0;
            }}
            .soft-card {{
                background: var(--card-soft);
                border: 1px solid var(--border-soft);
                border-radius: 24px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
            }}
            .insight-card {{
                background: var(--card-dark);
                border: 1px solid var(--border-soft);
                border-radius: 22px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
            }}
            .section-title {{
                color: var(--text-main);
                font-size: 1.08rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }}
            .section-text {{
                color: var(--text-soft);
                font-size: 0.95rem;
                line-height: 1.5;
                margin-bottom: 0;
            }}
            .number-pool {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-top: 0.75rem;
            }}
            .number-pill {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 2.2rem;
                padding: 0.42rem 0.58rem;
                border-radius: 999px;
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.06);
                color: var(--text-main);
                font-weight: 700;
                font-size: 0.88rem;
            }}
            .highlight-card {{
                background:
                    linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)),
                    linear-gradient(135deg, var(--accent), rgba(255,255,255,0.08));
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 22px;
                padding: 1rem 1.05rem;
                color: #082032;
                min-height: 145px;
            }}
            .highlight-label {{
                color: rgba(8, 32, 50, 0.72);
                font-size: 0.88rem;
                font-weight: 700;
                margin-bottom: 0.55rem;
            }}
            .highlight-value {{
                color: #081120;
                font-size: 1.12rem;
                font-weight: 800;
                line-height: 1.45;
            }}
            .highlight-sub {{
                color: rgba(8, 32, 50, 0.74);
                font-size: 0.86rem;
                margin-top: 0.55rem;
            }}
            .meta-chip {{
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 999px;
                padding: 0.34rem 0.75rem;
                color: var(--text-soft);
                font-size: 0.82rem;
                margin-right: 0.45rem;
                margin-bottom: 0.45rem;
            }}
            div[data-testid="stMetric"] {{
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 18px;
                padding: 0.85rem;
            }}
            div[data-testid="stMetricLabel"] {{
                color: var(--text-muted);
            }}
            div[data-testid="stMetricValue"] {{
                color: var(--text-main);
            }}
            .stButton > button, .stDownloadButton > button {{
                width: 100%;
                border-radius: 14px;
                min-height: 3rem;
                font-weight: 700;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.5rem;
            }}
            .stTabs [data-baseweb="tab"] {{
                border-radius: 999px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.06);
                padding: 0.6rem 1rem;
            }}
            .stTabs [aria-selected="true"] {{
                background: rgba(255,255,255,0.10) !important;
            }}
            .stRadio > div {{
                gap: 0.65rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_logo() -> None:
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.sidebar.markdown("## 🎯")


def sincronizar_pesos(chave_loteria: str, perfil: str) -> None:
    marcador = f"{chave_loteria}_perfil_pesos"
    pesos_padrao = obter_pesos_perfil(perfil)
    perfil_mudou = st.session_state.get(marcador) != perfil

    for nome_peso, valor in pesos_padrao.items():
        chave_peso = f"{chave_loteria}_peso_{nome_peso}"
        if perfil_mudou or chave_peso not in st.session_state:
            st.session_state[chave_peso] = float(valor)

    st.session_state[marcador] = perfil


def gerar_excel_download(resultado: pd.DataFrame, sheet_name: str) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        resultado.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    buffer.seek(0)
    return buffer.getvalue()


def plot_top_frequencia(frequencia: pd.DataFrame, accent: str, top_n: int = 12):
    base = frequencia.head(top_n).sort_values("frequencia", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(base["numero"].astype(str), base["frequencia"], color=accent, alpha=0.9)
    ax.set_title(f"Top {top_n} dezenas mais frequentes", fontsize=13, weight="bold")
    ax.set_xlabel("Frequência")
    ax.set_ylabel("Dezena")
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig


def plot_top_atraso(ultimo_concurso: pd.DataFrame, accent: str, top_n: int = 12):
    base = ultimo_concurso.head(top_n).sort_values("atraso", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(base["numero"].astype(str), base["atraso"], color=accent, alpha=0.88)
    ax.set_title(f"Top {top_n} dezenas mais atrasadas", fontsize=13, weight="bold")
    ax.set_xlabel("Atraso")
    ax.set_ylabel("Dezena")
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig


def plot_distribuicao_soma(soma_series: pd.Series, media_soma: float, desvio_soma: float, accent: str):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(soma_series, bins=24, color=accent, alpha=0.72, edgecolor="#0f172a")
    ax.axvline(media_soma, color="#f8fafc", linewidth=2.2, linestyle="--", label="Média histórica")
    if desvio_soma:
        ax.axvspan(media_soma - desvio_soma, media_soma + desvio_soma, color=accent, alpha=0.12)
    ax.set_title("Distribuição histórica da soma", fontsize=13, weight="bold")
    ax.set_xlabel("Soma das dezenas")
    ax.set_ylabel("Concursos")
    ax.legend(frameon=False)
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig


def plot_distribuicao_pares(distribuicao_pares: pd.DataFrame, accent: str):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(
        distribuicao_pares["pares"].astype(str),
        distribuicao_pares["concursos"],
        color=accent,
        alpha=0.88,
    )
    ax.set_title("Distribuição de pares por concurso", fontsize=13, weight="bold")
    ax.set_xlabel("Quantidade de pares")
    ax.set_ylabel("Concursos")
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig


def plot_componentes_jogo(jogo_row: pd.Series):
    componentes = pd.DataFrame(
        {
            "Componente": [
                COMPONENT_LABELS["pares_impares"],
                COMPONENT_LABELS["faixas"],
                COMPONENT_LABELS["soma"],
                COMPONENT_LABELS["estrategico"],
                COMPONENT_LABELS["sequencia"],
            ],
            "Score": [
                jogo_row["pares_impares_pond"],
                jogo_row["faixas_pond"],
                jogo_row["soma_pond"],
                jogo_row["estrategico_pond"],
                jogo_row["sequencia_pond"],
            ],
        }
    )

    cores = ["#1D9A6C" if valor >= 0 else "#EF4444" for valor in componentes["Score"]]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.barh(componentes["Componente"], componentes["Score"], color=cores, alpha=0.9)
    ax.axvline(0, color="#cbd5e1", linewidth=1)
    ax.set_title("Composição do score ponderado", fontsize=13, weight="bold")
    ax.set_xlabel("Pontos")
    ax.set_ylabel("")
    sns.despine(ax=ax, left=True)
    fig.tight_layout()
    return fig


def render_number_panel(title: str, subtitle: str, numbers: list[int]) -> str:
    badges = "".join(f"<span class='number-pill'>{numero:02d}</span>" for numero in numbers)
    return f"""
        <div class="soft-card">
            <div class="section-title">{title}</div>
            <p class="section-text">{subtitle}</p>
            <div class="number-pool">{badges}</div>
        </div>
    """


def render_meta_chips(textos: list[str]) -> str:
    chips = "".join(f"<span class='meta-chip'>{texto}</span>" for texto in textos)
    return f"<div>{chips}</div>"


if "generated_results" not in st.session_state:
    st.session_state["generated_results"] = {}


st.markdown(f"## {APP_TITLE}")
st.caption("Selecione a loteria, ajuste o perfil e gere jogos com base na análise histórica do notebook.")

lottery_key = st.radio(
    "Escolha a loteria",
    options=list(LOTTERY_CONFIGS.keys()),
    format_func=lambda chave: f"{LOTTERY_CONFIGS[chave]['icon']} {LOTTERY_CONFIGS[chave]['label']}",
    horizontal=True,
)

config = LOTTERY_CONFIGS[lottery_key]
aplicar_estilo(config)

try:
    analise = carregar_analise(lottery_key)
except FileNotFoundError as exc:
    st.error(f"Não encontrei a base esperada para {config['label']}.")
    st.info(
        "Confira se a planilha foi enviada para o repositório dentro de `loteria_app/data/` "
        "e se o nome do arquivo está correto no deploy."
    )
    st.caption(str(exc))
    st.stop()
except Exception as exc:
    st.error("Não foi possível carregar a análise histórica desta loteria.")
    st.exception(exc)
    st.stop()


mostrar_logo()
st.sidebar.markdown(f"## {APP_TITLE}")
st.sidebar.caption(f"{config['icon']} Motor configurado para {config['label']}")

perfil = st.sidebar.selectbox(
    "Perfil de geração",
    options=list(PROFILE_LABELS.keys()),
    format_func=lambda chave: PROFILE_LABELS[chave],
    key=f"{lottery_key}_perfil",
)

sincronizar_pesos(lottery_key, perfil)
st.sidebar.info(PROFILE_HELP[perfil])

qtd_jogos = st.sidebar.slider(
    "Quantidade de jogos",
    min_value=1,
    max_value=25,
    value=10,
    key=f"{lottery_key}_qtd_jogos",
)
tentativas = st.sidebar.slider(
    "Tentativas internas",
    min_value=500,
    max_value=6000,
    value=1800,
    step=100,
    key=f"{lottery_key}_tentativas",
)

with st.sidebar.expander("Ajuste fino dos pesos", expanded=False):
    st.caption("Os pesos definem quanto cada critério influencia no score final.")
    pesos = {
        "pares_impares": st.slider(
            "Pares / ímpares",
            0.5,
            2.5,
            float(st.session_state[f"{lottery_key}_peso_pares_impares"]),
            0.1,
            key=f"{lottery_key}_peso_pares_impares",
        ),
        "faixas": st.slider(
            "Faixas",
            0.5,
            2.5,
            float(st.session_state[f"{lottery_key}_peso_faixas"]),
            0.1,
            key=f"{lottery_key}_peso_faixas",
        ),
        "soma": st.slider(
            "Soma histórica",
            0.5,
            2.5,
            float(st.session_state[f"{lottery_key}_peso_soma"]),
            0.1,
            key=f"{lottery_key}_peso_soma",
        ),
        "estrategico": st.slider(
            "Mistura estratégica",
            0.5,
            3.0,
            float(st.session_state[f"{lottery_key}_peso_estrategico"]),
            0.1,
            key=f"{lottery_key}_peso_estrategico",
        ),
        "sequencia": st.slider(
            "Penalização por sequência",
            0.5,
            2.5,
            float(st.session_state[f"{lottery_key}_peso_sequencia"]),
            0.1,
            key=f"{lottery_key}_peso_sequencia",
        ),
    }

gerar = st.sidebar.button(
    f"{config['icon']} Gerar jogos",
    type="primary",
    use_container_width=True,
    key=f"{lottery_key}_gerar",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Como o motor pontua")
st.sidebar.markdown(
    """
    - equilíbrio entre pares e ímpares
    - distribuição por faixas numéricas
    - proximidade da soma histórica
    - mistura entre quentes, frios e atrasados
    - penalização para sequências longas
    """
)

if gerar:
    with st.spinner(f"Gerando jogos de {config['label']}..."):
        resultado = gerar_melhores_jogos(
            n_jogos_desejados=qtd_jogos,
            n_tentativas=tentativas,
            perfil=perfil,
            analise=analise,
            pesos=pesos,
        )

        if resultado.empty:
            st.sidebar.warning("Não foi possível gerar jogos com os parâmetros atuais.")
        else:
            resultado = adicionar_formatacao(resultado, largura=2)
            st.session_state["generated_results"][lottery_key] = {
                "resultado": resultado,
                "perfil": perfil,
                "qtd_jogos": qtd_jogos,
                "tentativas": tentativas,
                "pesos": pesos,
            }
            st.sidebar.success("Jogos atualizados.")

resultado_salvo = st.session_state["generated_results"].get(lottery_key)
faixa_soma_min = int(round(float(analise["media_soma"]) - float(analise["desvio_soma"])))
faixa_soma_max = int(round(float(analise["media_soma"]) + float(analise["desvio_soma"])))
pares_tipicos = {int(analise["qtd_dezenas"]) // 2}
if int(analise["qtd_dezenas"]) % 2 != 0:
    pares_tipicos.add((int(analise["qtd_dezenas"]) // 2) + 1)
pares_tipicos = sorted(pares_tipicos)
pares_tipicos_label = " ou ".join(str(valor) for valor in pares_tipicos)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-tag">{config['icon']} {config['label']}</div>
        <div class="hero-title">Interface única para analisar e gerar jogos com inteligência histórica</div>
        <p class="hero-subtitle">
            {config['description']} O motor usa frequência, atraso, soma histórica, equilíbrio entre pares e ímpares,
            distribuição em faixas e perfis ponderados para ranquear combinações em poucos cliques.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Concursos válidos", len(analise["df"]))
k2.metric("Última data", analise["data_ultimo"])
k3.metric("Dezenas por jogo", int(analise["qtd_dezenas"]))
k4.metric("Maior atraso", int(analise["maior_atraso"]))
k5.metric("Soma média", round(float(analise["media_soma"]), 1))

tab_panorama, tab_gerador, tab_base = st.tabs(["Panorama", "Gerador inteligente", "Base histórica"])

with tab_panorama:
    c1, c2 = st.columns([1.05, 1], gap="large")

    with c1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="section-title">Leitura rápida do histórico</div>
                <p class="section-text">
                    A base indica uma faixa típica de soma entre <strong>{faixa_soma_min}</strong> e
                    <strong>{faixa_soma_max}</strong>, com preferência histórica por <strong>{pares_tipicos_label}</strong>
                    pares e ocupação média de <strong>{round(float(analise['media_faixas_ocupadas']), 1)}</strong> faixas numéricas.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_freq = plot_top_frequencia(analise["frequencia"], str(config["accent"]))
        st.pyplot(fig_freq, use_container_width=True)
        plt.close(fig_freq)

    with c2:
        st.markdown(
            render_number_panel(
                "Pool histórico usado no gerador",
                f"O motor trabalha com {analise['reference_pool_size']} dezenas por grupo de referência.",
                analise["top_quentes"][: min(10, len(analise["top_quentes"]))],
            ),
            unsafe_allow_html=True,
        )
        fig_atraso = plot_top_atraso(analise["ultimo_concurso"], str(config["accent"]))
        st.pyplot(fig_atraso, use_container_width=True)
        plt.close(fig_atraso)

    p1, p2, p3 = st.columns(3, gap="large")
    with p1:
        st.markdown(
            render_number_panel(
                "Mais quentes",
                "Dezenas mais frequentes na base tratada.",
                analise["top_quentes"][: min(10, len(analise["top_quentes"]))],
            ),
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            render_number_panel(
                "Mais frias",
                "Dezenas menos frequentes na base tratada.",
                analise["top_frios"][: min(10, len(analise["top_frios"]))],
            ),
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            render_number_panel(
                "Mais atrasadas",
                "Dezenas com maior atraso no concurso atual.",
                analise["top_atrasados"][: min(10, len(analise["top_atrasados"]))],
            ),
            unsafe_allow_html=True,
        )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        fig_soma = plot_distribuicao_soma(
            analise["soma_series"],
            float(analise["media_soma"]),
            float(analise["desvio_soma"]),
            str(config["accent"]),
        )
        st.pyplot(fig_soma, use_container_width=True)
        plt.close(fig_soma)

    with c4:
        fig_pares = plot_distribuicao_pares(analise["distribuicao_pares"], str(config["accent"]))
        st.pyplot(fig_pares, use_container_width=True)
        plt.close(fig_pares)

with tab_gerador:
    if not resultado_salvo:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="section-title">Pronto para gerar combinações</div>
                <p class="section-text">
                    Escolha o perfil na barra lateral, ajuste a quantidade de jogos e clique em <strong>Gerar jogos</strong>.
                    O ranking será montado com base nos critérios do notebook: frequência, atraso, soma histórica,
                    faixas, equilíbrio entre pares e ímpares e penalização por sequências.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            render_meta_chips(
                [
                    f"Perfil atual: {PROFILE_LABELS[perfil]}",
                    f"{qtd_jogos} jogo(s) por rodada",
                    f"{tentativas} tentativas internas",
                    f"Soma histórica alvo: {faixa_soma_min} a {faixa_soma_max}",
                ]
            ),
            unsafe_allow_html=True,
        )
    else:
        resultado = resultado_salvo["resultado"]
        meta_textos = [
            f"Perfil usado: {PROFILE_LABELS[resultado_salvo['perfil']]}",
            f"Jogos gerados: {resultado_salvo['qtd_jogos']}",
            f"Tentativas internas: {resultado_salvo['tentativas']}",
        ]
        st.markdown(render_meta_chips(meta_textos), unsafe_allow_html=True)

        cards = st.columns(min(3, len(resultado)), gap="large")
        for idx, (_, row) in enumerate(resultado.head(3).iterrows()):
            with cards[idx]:
                st.markdown(
                    f"""
                    <div class="highlight-card">
                        <div class="highlight-label">Jogo destaque #{idx + 1}</div>
                        <div class="highlight-value">{row['jogo_formatado']}</div>
                        <div class="highlight-sub">
                            Score total: <strong>{row['score_total']}</strong><br>
                            Índice 0-100: <strong>{row['score_0_100']}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        g1, g2 = st.columns([1.2, 0.8], gap="large")

        with g1:
            st.markdown('<div class="section-title">Ranking de jogos</div>', unsafe_allow_html=True)
            exibicao = resultado[
                [
                    "jogo_formatado",
                    "score_total",
                    "score_0_100",
                    "pares",
                    "soma_total",
                    "q_quentes",
                    "q_frios",
                    "q_atrasados",
                    "sequencias",
                ]
            ].rename(
                columns={
                    "jogo_formatado": "Jogo",
                    "score_total": "Score",
                    "score_0_100": "Indice 0-100",
                    "pares": "Pares",
                    "soma_total": "Soma",
                    "q_quentes": "Quentes",
                    "q_frios": "Frios",
                    "q_atrasados": "Atrasados",
                    "sequencias": "Sequencias",
                }
            )
            st.dataframe(exibicao, use_container_width=True, hide_index=True)

            excel_bytes = gerar_excel_download(resultado, f"Jogos {config['label']}")
            st.download_button(
                label=f"Baixar jogos em Excel ({config['label']})",
                data=excel_bytes,
                file_name=f"jogos_{lottery_key}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with g2:
            opcoes_jogo = resultado["jogo_formatado"].tolist()
            jogo_escolhido = st.selectbox(
                "Raio-x do jogo",
                options=opcoes_jogo,
                index=0,
                key=f"{lottery_key}_jogo_detalhe",
            )
            jogo_row = resultado.loc[resultado["jogo_formatado"] == jogo_escolhido].iloc[0]

            d1, d2 = st.columns(2)
            d1.metric("Pares x ímpares", f"{int(jogo_row['pares'])} / {int(jogo_row['impares'])}")
            d2.metric("Soma total", int(jogo_row["soma_total"]))
            d3, d4 = st.columns(2)
            d3.metric("Faixas ocupadas", int(jogo_row["faixas_ocupadas"]))
            d4.metric("Sequências", int(jogo_row["sequencias"]))

            st.markdown(
                render_meta_chips(
                    [
                        f"Quentes no jogo: {int(jogo_row['q_quentes'])}",
                        f"Frios no jogo: {int(jogo_row['q_frios'])}",
                        f"Atrasados no jogo: {int(jogo_row['q_atrasados'])}",
                    ]
                ),
                unsafe_allow_html=True,
            )

            fig_componentes = plot_componentes_jogo(jogo_row)
            st.pyplot(fig_componentes, use_container_width=True)
            plt.close(fig_componentes)

            with st.expander("Pesos usados na última geração", expanded=False):
                st.json(resultado_salvo["pesos"])

with tab_base:
    b1, b2, b3 = st.tabs(["Frequência", "Atraso", "Base tratada"])

    with b1:
        st.dataframe(analise["frequencia"], use_container_width=True, hide_index=True)

    with b2:
        st.dataframe(analise["ultimo_concurso"], use_container_width=True, hide_index=True)

    with b3:
        st.dataframe(analise["df"].head(80), use_container_width=True, hide_index=True)
