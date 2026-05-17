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
    calcular_combinacoes_cobertas,
    gerar_melhores_jogos,
    obter_pesos_perfil,
    preparar_analise_aposta,
)


APP_TITLE = "Loterias Inteligentes"
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"
GENERATION_MODE_LABELS = {
    "score": "Score maximo",
    "cobertura": "Modo cobertura",
}
GENERATION_MODE_HELP = {
    "score": "Prioriza os jogos individualmente mais bem pontuados.",
    "cobertura": "Aceita pequenas perdas de score para reduzir a repeticao entre os jogos.",
}

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
    st.markdown(
        f"""
        <style>
            :root {{
                --accent: {accent};
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
                font-size: 1.08rem;
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_logo() -> None:
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.sidebar.markdown("## LOT")


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
    ax.set_xlabel("Frequencia")
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
    ax.axvline(media_soma, color="#f8fafc", linewidth=2.2, linestyle="--", label="Media alvo")
    if desvio_soma:
        ax.axvspan(media_soma - desvio_soma, media_soma + desvio_soma, color=accent, alpha=0.12)
    ax.set_title("Distribuicao historica da soma", fontsize=13, weight="bold")
    ax.set_xlabel("Soma das dezenas sorteadas")
    ax.set_ylabel("Concursos")
    ax.legend(frameon=False)
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig


def plot_distribuicao_pares(distribuicao_pares: pd.DataFrame, accent: str):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(distribuicao_pares["pares"].astype(str), distribuicao_pares["concursos"], color=accent, alpha=0.88)
    ax.set_title("Distribuicao de pares por concurso", fontsize=13, weight="bold")
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
    ax.set_title("Composicao do score ponderado", fontsize=13, weight="bold")
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


def formatar_inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def obter_resultado_compativel(
    resultado_salvo: dict[str, object] | None,
    qtd_dezenas: int,
    modo_selecao: str,
    intensidade_cobertura: float,
) -> dict[str, object] | None:
    if not resultado_salvo:
        return None
    if resultado_salvo.get("qtd_dezenas") != qtd_dezenas:
        return None
    if resultado_salvo.get("modo_selecao") != modo_selecao:
        return None
    if resultado_salvo.get("intensidade_cobertura") != intensidade_cobertura:
        return None
    return resultado_salvo


if "generated_results" not in st.session_state:
    st.session_state["generated_results"] = {}


st.markdown(f"## {APP_TITLE}")
st.caption("Selecione a loteria, ajuste o perfil e gere jogos com base na analise historica.")

lottery_key = st.radio(
    "Escolha a loteria",
    options=list(LOTTERY_CONFIGS.keys()),
    format_func=lambda chave: f"{LOTTERY_CONFIGS[chave]['icon']} {LOTTERY_CONFIGS[chave]['label']}",
    horizontal=True,
)

config = LOTTERY_CONFIGS[lottery_key]
aplicar_estilo(config)

try:
    analise_base = carregar_analise(lottery_key)
except FileNotFoundError as exc:
    st.error(f"Nao encontrei a base esperada para {config['label']}.")
    st.info("Confira se a planilha foi enviada para o repositorio dentro de `loteria_app/data/`.")
    st.caption(str(exc))
    st.stop()
except Exception as exc:
    st.error("Nao foi possivel carregar a analise historica desta loteria.")
    st.exception(exc)
    st.stop()

mostrar_logo()
st.sidebar.markdown(f"## {APP_TITLE}")
st.sidebar.caption(f"{config['icon']} Motor configurado para {config['label']}")

perfil = st.sidebar.selectbox(
    "Perfil de geracao",
    options=list(PROFILE_LABELS.keys()),
    format_func=lambda chave: PROFILE_LABELS[chave],
    key=f"{lottery_key}_perfil",
)

sincronizar_pesos(lottery_key, perfil)
st.sidebar.info(PROFILE_HELP[perfil])

qtd_dezenas_min = int(analise_base["qtd_dezenas_min"])
qtd_dezenas_max = int(analise_base["qtd_dezenas_max"])
qtd_dezenas_sorteio = int(analise_base["qtd_dezenas_sorteio"])

if qtd_dezenas_min != qtd_dezenas_max:
    qtd_dezenas = st.sidebar.slider(
        "Dezenas por aposta",
        min_value=qtd_dezenas_min,
        max_value=qtd_dezenas_max,
        value=qtd_dezenas_sorteio,
        key=f"{lottery_key}_qtd_dezenas",
    )
else:
    qtd_dezenas = qtd_dezenas_sorteio
    st.sidebar.caption(f"Dezenas por aposta: {qtd_dezenas} (fixo nesta loteria)")

modo_selecao = st.sidebar.selectbox(
    "Estrategia de montagem",
    options=list(GENERATION_MODE_LABELS.keys()),
    format_func=lambda chave: GENERATION_MODE_LABELS[chave],
    key=f"{lottery_key}_modo_selecao",
)
st.sidebar.caption(GENERATION_MODE_HELP[modo_selecao])

intensidade_cobertura = 1.0
if modo_selecao == "cobertura":
    intensidade_cobertura = st.sidebar.slider(
        "Intensidade da cobertura",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        key=f"{lottery_key}_intensidade_cobertura",
    )

analise_aposta = preparar_analise_aposta(analise_base, qtd_dezenas)
combinacoes_cobertas = calcular_combinacoes_cobertas(qtd_dezenas, qtd_dezenas_sorteio)
if qtd_dezenas > qtd_dezenas_sorteio:
    st.sidebar.caption(
        f"Cobertura combinatoria: {formatar_inteiro(combinacoes_cobertas)} combinacoes de {qtd_dezenas_sorteio} dezenas."
    )

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
    st.caption("Os pesos definem quanto cada criterio influencia no score final.")
    pesos = {
        "pares_impares": st.slider(
            "Pares / impares",
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
            "Soma historica",
            0.5,
            2.5,
            float(st.session_state[f"{lottery_key}_peso_soma"]),
            0.1,
            key=f"{lottery_key}_peso_soma",
        ),
        "estrategico": st.slider(
            "Mistura estrategica",
            0.5,
            3.0,
            float(st.session_state[f"{lottery_key}_peso_estrategico"]),
            0.1,
            key=f"{lottery_key}_peso_estrategico",
        ),
        "sequencia": st.slider(
            "Penalizacao por sequencia",
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
    - equilibrio entre pares e impares
    - distribuicao por faixas numericas
    - proximidade da soma historica
    - mistura entre quentes, frios e atrasados
    - penalizacao para sequencias longas
    """
)

if gerar:
    with st.spinner(f"Gerando jogos de {config['label']}..."):
        resultado = gerar_melhores_jogos(
            n_jogos_desejados=qtd_jogos,
            n_tentativas=tentativas,
            perfil=perfil,
            analise=analise_aposta,
            pesos=pesos,
            modo_selecao=modo_selecao,
            intensidade_cobertura=intensidade_cobertura,
        )

        if resultado.empty:
            st.sidebar.warning("Nao foi possivel gerar jogos com os parametros atuais.")
        else:
            resultado = adicionar_formatacao(resultado, largura=2)
            st.session_state["generated_results"][lottery_key] = {
                "resultado": resultado,
                "perfil": perfil,
                "qtd_jogos": qtd_jogos,
                "tentativas": tentativas,
                "qtd_dezenas": qtd_dezenas,
                "modo_selecao": modo_selecao,
                "intensidade_cobertura": intensidade_cobertura,
                "combinacoes_cobertas": combinacoes_cobertas,
                "pesos": pesos,
            }
            st.sidebar.success("Jogos atualizados.")

resultado_salvo = obter_resultado_compativel(
    st.session_state["generated_results"].get(lottery_key),
    qtd_dezenas=qtd_dezenas,
    modo_selecao=modo_selecao,
    intensidade_cobertura=intensidade_cobertura,
)

faixa_soma_min = int(round(float(analise_aposta["media_soma"]) - float(analise_aposta["desvio_soma"])))
faixa_soma_max = int(round(float(analise_aposta["media_soma"]) + float(analise_aposta["desvio_soma"])))
pares_tipicos = {int(analise_aposta["qtd_dezenas"]) // 2}
if int(analise_aposta["qtd_dezenas"]) % 2 != 0:
    pares_tipicos.add((int(analise_aposta["qtd_dezenas"]) // 2) + 1)
pares_tipicos_label = " ou ".join(str(valor) for valor in sorted(pares_tipicos))

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-tag">{config['icon']} {config['label']}</div>
        <div class="hero-title">Interface unica para analisar e gerar jogos com inteligencia historica</div>
        <p class="hero-subtitle">
            {config['description']} O motor usa frequencia, atraso, soma historica,
            distribuicao em faixas e perfis ponderados para montar apostas de forma pratica.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Concursos validos", len(analise_base["df"]))
k2.metric("Ultima data", analise_base["data_ultimo"])
k3.metric("Dezenas por jogo", int(analise_aposta["qtd_dezenas"]))
k4.metric("Maior atraso", int(analise_base["maior_atraso"]))
k5.metric("Soma alvo", round(float(analise_aposta["media_soma"]), 1))

tab_panorama, tab_gerador, tab_base = st.tabs(["Panorama", "Gerador inteligente", "Base historica"])

with tab_panorama:
    c1, c2 = st.columns([1.05, 1], gap="large")

    with c1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="section-title">Leitura rapida do historico</div>
                <p class="section-text">
                    A base indica uma faixa tipica de soma entre <strong>{faixa_soma_min}</strong> e
                    <strong>{faixa_soma_max}</strong>, com preferencia por <strong>{pares_tipicos_label}</strong> pares
                    e ocupacao media de <strong>{round(float(analise_aposta['media_faixas_ocupadas']), 1)}</strong> faixas
                    para apostas de <strong>{int(analise_aposta['qtd_dezenas'])}</strong> dezenas.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_freq = plot_top_frequencia(analise_base["frequencia"], str(config["accent"]))
        st.pyplot(fig_freq, use_container_width=True)
        plt.close(fig_freq)

    with c2:
        st.markdown(
            render_number_panel(
                "Pool historico usado no gerador",
                f"O motor trabalha com {analise_base['reference_pool_size']} dezenas por grupo de referencia.",
                analise_base["top_quentes"][: min(10, len(analise_base["top_quentes"]))],
            ),
            unsafe_allow_html=True,
        )
        fig_atraso = plot_top_atraso(analise_base["ultimo_concurso"], str(config["accent"]))
        st.pyplot(fig_atraso, use_container_width=True)
        plt.close(fig_atraso)

    p1, p2, p3 = st.columns(3, gap="large")
    with p1:
        st.markdown(
            render_number_panel(
                "Mais quentes",
                "Dezenas mais frequentes na base tratada.",
                analise_base["top_quentes"][: min(10, len(analise_base["top_quentes"]))],
            ),
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            render_number_panel(
                "Mais frias",
                "Dezenas menos frequentes na base tratada.",
                analise_base["top_frios"][: min(10, len(analise_base["top_frios"]))],
            ),
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            render_number_panel(
                "Mais atrasadas",
                "Dezenas com maior atraso no concurso atual.",
                analise_base["top_atrasados"][: min(10, len(analise_base["top_atrasados"]))],
            ),
            unsafe_allow_html=True,
        )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        fig_soma = plot_distribuicao_soma(
            analise_base["soma_series"],
            float(analise_aposta["media_soma"]),
            float(analise_aposta["desvio_soma"]),
            str(config["accent"]),
        )
        st.pyplot(fig_soma, use_container_width=True)
        plt.close(fig_soma)

    with c4:
        fig_pares = plot_distribuicao_pares(analise_base["distribuicao_pares"], str(config["accent"]))
        st.pyplot(fig_pares, use_container_width=True)
        plt.close(fig_pares)

with tab_gerador:
    chips_atuais = [
        f"Perfil atual: {PROFILE_LABELS[perfil]}",
        f"Dezenas por aposta: {qtd_dezenas}",
        f"Estrategia: {GENERATION_MODE_LABELS[modo_selecao]}",
        f"{qtd_jogos} jogo(s) por rodada",
    ]
    if qtd_dezenas > qtd_dezenas_sorteio:
        chips_atuais.append(
            f"Cobertura teorica: {formatar_inteiro(combinacoes_cobertas)} combinacoes de {qtd_dezenas_sorteio}"
        )

    if not resultado_salvo:
        st.markdown(
            """
            <div class="insight-card">
                <div class="section-title">Pronto para gerar combinacoes</div>
                <p class="section-text">
                    Escolha o perfil na barra lateral, ajuste a quantidade de dezenas, defina a estrategia
                    e clique em <strong>Gerar jogos</strong>. O ranking combina score historico com opcao de cobertura
                    para reduzir repeticoes entre as apostas.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(render_meta_chips(chips_atuais), unsafe_allow_html=True)
    else:
        resultado = resultado_salvo["resultado"]
        meta_textos = [
            f"Perfil usado: {PROFILE_LABELS[resultado_salvo['perfil']]}",
            f"Dezenas usadas: {resultado_salvo['qtd_dezenas']}",
            f"Estrategia usada: {GENERATION_MODE_LABELS[resultado_salvo['modo_selecao']]}",
            f"Jogos gerados: {resultado_salvo['qtd_jogos']}",
            f"Tentativas internas: {resultado_salvo['tentativas']}",
        ]
        if resultado_salvo["qtd_dezenas"] > qtd_dezenas_sorteio:
            meta_textos.append(
                "Cobertura teorica: "
                f"{formatar_inteiro(int(resultado_salvo['combinacoes_cobertas']))} combinacoes de {qtd_dezenas_sorteio}"
            )
        st.markdown(render_meta_chips(meta_textos), unsafe_allow_html=True)

        cards = st.columns(min(3, len(resultado)), gap="large")
        for indice, (_, row) in enumerate(resultado.head(3).iterrows()):
            subtitulo = f"Score total: {row['score_total']}<br>Indice 0-100: {row['score_0_100']}"
            if "score_cobertura" in resultado.columns:
                subtitulo += f"<br>Score cobertura: {row['score_cobertura']}"
            with cards[indice]:
                st.markdown(
                    f"""
                    <div class="highlight-card">
                        <div class="highlight-label">Jogo destaque #{indice + 1}</div>
                        <div class="highlight-value">{row['jogo_formatado']}</div>
                        <div class="highlight-sub">{subtitulo}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        g1, g2 = st.columns([1.2, 0.8], gap="large")
        with g1:
            st.markdown('<div class="section-title">Ranking de jogos</div>', unsafe_allow_html=True)
            colunas = [
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
            renomear = {
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
            if "score_cobertura" in resultado.columns:
                colunas.extend(["score_cobertura", "sobreposicao_maxima"])
                renomear["score_cobertura"] = "Score cobertura"
                renomear["sobreposicao_maxima"] = "Sobreposicao max"

            exibicao = resultado[colunas].rename(columns=renomear)
            st.dataframe(exibicao, use_container_width=True, hide_index=True)

            nome_arquivo = f"jogos_{lottery_key}_{qtd_dezenas}dezenas.xlsx"
            excel_bytes = gerar_excel_download(resultado, f"Jogos {config['label']}")
            st.download_button(
                label=f"Baixar jogos em Excel ({config['label']})",
                data=excel_bytes,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with g2:
            jogo_escolhido = st.selectbox(
                "Raio-x do jogo",
                options=resultado["jogo_formatado"].tolist(),
                index=0,
                key=f"{lottery_key}_jogo_detalhe",
            )
            jogo_row = resultado.loc[resultado["jogo_formatado"] == jogo_escolhido].iloc[0]

            d1, d2 = st.columns(2)
            d1.metric("Pares x impares", f"{int(jogo_row['pares'])} / {int(jogo_row['impares'])}")
            d2.metric("Soma total", int(jogo_row["soma_total"]))
            d3, d4 = st.columns(2)
            d3.metric("Faixas ocupadas", int(jogo_row["faixas_ocupadas"]))
            d4.metric("Sequencias", int(jogo_row["sequencias"]))

            chips_jogo = [
                f"Quentes no jogo: {int(jogo_row['q_quentes'])}",
                f"Frios no jogo: {int(jogo_row['q_frios'])}",
                f"Atrasados no jogo: {int(jogo_row['q_atrasados'])}",
            ]
            if "sobreposicao_maxima" in resultado.columns:
                chips_jogo.append(f"Sobreposicao maxima: {int(jogo_row['sobreposicao_maxima'])}")
            st.markdown(render_meta_chips(chips_jogo), unsafe_allow_html=True)

            fig_componentes = plot_componentes_jogo(jogo_row)
            st.pyplot(fig_componentes, use_container_width=True)
            plt.close(fig_componentes)

            with st.expander("Pesos usados na ultima geracao", expanded=False):
                st.json(resultado_salvo["pesos"])

with tab_base:
    b1, b2, b3 = st.tabs(["Frequencia", "Atraso", "Base tratada"])
    with b1:
        st.dataframe(analise_base["frequencia"], use_container_width=True, hide_index=True)
    with b2:
        st.dataframe(analise_base["ultimo_concurso"], use_container_width=True, hide_index=True)
    with b3:
        st.dataframe(analise_base["df"].head(80), use_container_width=True, hide_index=True)
