from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


APP_DIR = Path(__file__).resolve().parent

LOTTERY_CONFIGS: dict[str, dict[str, object]] = {
    "mega_sena": {
        "key": "mega_sena",
        "label": "Mega-Sena",
        "icon": "🎯",
        "description": "Analise historica com 6 dezenas entre 1 e 60.",
        "file_path": APP_DIR / "data" / "Mega-Sena.xlsx",
        "numbers_per_game": 6,
        "max_number": 60,
        "bucket_size": 10,
        "reference_pool_size": 15,
        "accent": "#1D9A6C",
        "accent_soft": "#D8F4E8",
    },
    "lotofacil": {
        "key": "lotofacil",
        "label": "Lotofacil",
        "icon": "🍀",
        "description": "Analise historica com 15 dezenas entre 1 e 25.",
        "file_path": APP_DIR / "data" / "Lotofacil.xlsx",
        "numbers_per_game": 15,
        "max_number": 25,
        "bucket_size": 5,
        "reference_pool_size": 12,
        "accent": "#E85D75",
        "accent_soft": "#FFE3E8",
    },
    "quina": {
        "key": "quina",
        "label": "Quina",
        "icon": "🔵",
        "description": "Analise historica com 5 dezenas entre 1 e 80.",
        "file_path": APP_DIR / "data" / "Quina.xlsx",
        "numbers_per_game": 5,
        "max_number": 80,
        "bucket_size": 10,
        "reference_pool_size": 15,
        "accent": "#3A76F0",
        "accent_soft": "#DDE8FF",
    },
}

PROFILE_LABELS = {
    "conservador": "Conservador",
    "equilibrado": "Equilibrado",
    "agressivo": "Agressivo",
    "atrasados": "Foco em atrasados",
}

PROFILE_HELP = {
    "conservador": "Prioriza quentes e combina linhas mais estaveis.",
    "equilibrado": "Mistura quentes, frios e atrasados com pesos balanceados.",
    "agressivo": "Aceita mais risco ao puxar frios e atrasados.",
    "atrasados": "Empurra mais dezenas em atraso para o centro da geracao.",
}

COMPONENT_LABELS = {
    "pares_impares": "Pares x impares",
    "faixas": "Distribuicao por faixas",
    "soma": "Soma historica",
    "estrategico": "Mistura estrategica",
    "sequencia": "Penalizacao por sequencia",
}


def obter_config_loteria(lottery_key: str) -> dict[str, object]:
    if lottery_key not in LOTTERY_CONFIGS:
        raise KeyError(f"Loteria desconhecida: {lottery_key}")
    return LOTTERY_CONFIGS[lottery_key]


def carregar_base(caminho: str | Path) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    df.columns = [str(col).strip().lower() for col in df.columns]
    return df


def detectar_colunas_dezenas(df: pd.DataFrame) -> list[str]:
    colunas = [col for col in df.columns if "bola" in col or "dezena" in col]
    return sorted(colunas, key=lambda col: int("".join(ch for ch in col if ch.isdigit()) or 0))


def preparar_base(df: pd.DataFrame, colunas_dezenas: list[str]) -> pd.DataFrame:
    base = df.copy()
    for col in colunas_dezenas:
        base[col] = pd.to_numeric(base[col], errors="coerce")
    return base.dropna(subset=colunas_dezenas).copy()


def descobrir_coluna_data(df: pd.DataFrame) -> str | None:
    candidatas = [col for col in df.columns if "data" in col or col.startswith("dt")]
    for col in candidatas:
        serie = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
        if serie.notna().any():
            return col
    return None


def obter_data_mais_recente(df: pd.DataFrame, coluna_data: str | None) -> str:
    if not coluna_data:
        return "-"
    serie = pd.to_datetime(df[coluna_data], dayfirst=True, errors="coerce")
    if not serie.notna().any():
        return "-"
    return serie.max().strftime("%d/%m/%Y")


def montar_faixas(max_number: int, bucket_size: int) -> list[tuple[int, int]]:
    faixas: list[tuple[int, int]] = []
    for inicio in range(1, max_number + 1, bucket_size):
        fim = min(inicio + bucket_size - 1, max_number)
        faixas.append((inicio, fim))
    return faixas


def rotulo_faixa(inicio: int, fim: int) -> str:
    return f"{inicio:02d}-{fim:02d}"


def contar_pares(jogo: list[int] | tuple[int, ...]) -> int:
    return sum(1 for numero in jogo if int(numero) % 2 == 0)


def contar_sequencias_consecutivas(jogo: list[int] | tuple[int, ...]) -> int:
    ordenado = sorted(int(numero) for numero in jogo)
    return sum(1 for idx in range(len(ordenado) - 1) if ordenado[idx + 1] - ordenado[idx] == 1)


def contar_faixas_jogo(
    jogo: list[int] | tuple[int, ...],
    faixas: list[tuple[int, int]],
) -> list[int]:
    contagens: list[int] = []
    for inicio, fim in faixas:
        contagens.append(sum(1 for numero in jogo if inicio <= int(numero) <= fim))
    return contagens


def calcular_frequencia(df: pd.DataFrame, colunas_dezenas: list[str]) -> pd.DataFrame:
    serie = df[colunas_dezenas].stack().astype(int)
    frequencia = serie.value_counts().sort_index().reset_index()
    frequencia.columns = ["numero", "frequencia"]
    frequencia["percentual"] = (
        frequencia["frequencia"] / frequencia["frequencia"].sum() * 100
    ).round(2)
    return frequencia.sort_values("frequencia", ascending=False).reset_index(drop=True)


def calcular_atraso(df: pd.DataFrame, colunas_dezenas: list[str]) -> pd.DataFrame:
    df_long = df.reset_index().melt(
        id_vars=["index"],
        value_vars=colunas_dezenas,
        value_name="numero",
    )
    df_long = df_long.rename(columns={"index": "concurso_idx"})
    df_long["numero"] = pd.to_numeric(df_long["numero"], errors="coerce")
    df_long = df_long.dropna(subset=["numero"]).copy()
    df_long["numero"] = df_long["numero"].astype(int)
    df_long = df_long.sort_values("concurso_idx")

    ultimo_concurso = df_long.groupby("numero", as_index=False)["concurso_idx"].max()
    ultimo_idx = int(df_long["concurso_idx"].max())
    ultimo_concurso["atraso"] = ultimo_idx - ultimo_concurso["concurso_idx"]

    return ultimo_concurso.sort_values("atraso", ascending=False).reset_index(drop=True)


def _round_half_up(valor: float) -> int:
    return int(math.floor(valor + 0.5))


def analisar_loteria(lottery_key: str) -> dict[str, object]:
    config = obter_config_loteria(lottery_key)
    df = carregar_base(config["file_path"])
    colunas_dezenas = detectar_colunas_dezenas(df)
    if not colunas_dezenas:
        raise ValueError("Nao encontrei colunas de dezenas na base informada.")

    base_tratada = preparar_base(df, colunas_dezenas)
    if base_tratada.empty:
        raise ValueError("Nao ha concursos validos depois da limpeza da base.")

    dezenas_df = base_tratada[colunas_dezenas].astype(int)
    frequencia = calcular_frequencia(base_tratada, colunas_dezenas)
    ultimo_concurso = calcular_atraso(base_tratada, colunas_dezenas)

    numbers_per_game = int(config["numbers_per_game"])
    max_number = int(config["max_number"])
    bucket_size = int(config["bucket_size"])
    faixas = montar_faixas(max_number, bucket_size)

    soma_series = dezenas_df.sum(axis=1)
    pares_series = dezenas_df.apply(lambda linha: contar_pares(linha.tolist()), axis=1)

    ocupacao_faixas_series = dezenas_df.apply(
        lambda linha: sum(count > 0 for count in contar_faixas_jogo(linha.tolist(), faixas)),
        axis=1,
    )
    concentracao_faixas_series = dezenas_df.apply(
        lambda linha: max(contar_faixas_jogo(linha.tolist(), faixas)),
        axis=1,
    )

    reference_pool_size = min(int(config["reference_pool_size"]), len(frequencia) // 2 or len(frequencia))
    top_quentes = frequencia.head(reference_pool_size)["numero"].astype(int).tolist()
    top_frios = (
        frequencia.tail(reference_pool_size)
        .sort_values(["frequencia", "numero"], ascending=[True, True])["numero"]
        .astype(int)
        .tolist()
    )
    top_atrasados = ultimo_concurso.head(reference_pool_size)["numero"].astype(int).tolist()

    distribuicao_pares = (
        pares_series.value_counts()
        .sort_index()
        .rename_axis("pares")
        .reset_index(name="concursos")
    )

    coluna_data = descobrir_coluna_data(base_tratada)
    data_ultimo = obter_data_mais_recente(base_tratada, coluna_data)
    maior_atraso = int(ultimo_concurso["atraso"].max()) if not ultimo_concurso.empty else 0

    return {
        "config": config,
        "df": base_tratada,
        "colunas_dezenas": colunas_dezenas,
        "frequencia": frequencia,
        "ultimo_concurso": ultimo_concurso,
        "faixas": faixas,
        "faixas_rotulos": [rotulo_faixa(inicio, fim) for inicio, fim in faixas],
        "qtd_dezenas": numbers_per_game,
        "universo": list(range(1, max_number + 1)),
        "reference_pool_size": reference_pool_size,
        "top_quentes": top_quentes,
        "top_frios": top_frios,
        "top_atrasados": top_atrasados,
        "soma_series": soma_series,
        "pares_series": pares_series,
        "ocupacao_faixas_series": ocupacao_faixas_series,
        "concentracao_faixas_series": concentracao_faixas_series,
        "distribuicao_pares": distribuicao_pares,
        "media_soma": float(soma_series.mean()),
        "desvio_soma": float(soma_series.std()) if len(soma_series) > 1 else 0.0,
        "media_pares": float(pares_series.mean()),
        "media_faixas_ocupadas": float(ocupacao_faixas_series.mean()),
        "media_concentracao_faixas": float(concentracao_faixas_series.mean()),
        "data_ultimo": data_ultimo,
        "maior_atraso": maior_atraso,
    }


def score_pares_impares(jogo: list[int]) -> int:
    pares = contar_pares(jogo)
    alvos = {len(jogo) // 2}
    if len(jogo) % 2 != 0:
        alvos.add((len(jogo) // 2) + 1)
    distancia = min(abs(pares - alvo) for alvo in alvos)

    if distancia == 0:
        return 10
    if distancia == 1:
        return 7
    if distancia == 2:
        return 4
    return 0


def score_faixas(
    jogo: list[int],
    faixas: list[tuple[int, int]],
    media_ocupadas: float,
    media_concentracao: float,
) -> int:
    contagens = contar_faixas_jogo(jogo, faixas)
    ocupadas = sum(valor > 0 for valor in contagens)
    maior_concentracao = max(contagens)
    alvo_ocupadas = _round_half_up(media_ocupadas)
    alvo_concentracao = max(1, _round_half_up(media_concentracao))

    if ocupadas >= alvo_ocupadas and maior_concentracao <= alvo_concentracao:
        return 10
    if ocupadas >= max(2, alvo_ocupadas - 1) and maior_concentracao <= alvo_concentracao + 1:
        return 7
    if ocupadas >= max(1, alvo_ocupadas - 2):
        return 4
    return 0


def score_soma(jogo: list[int], media_soma: float, desvio_soma: float) -> int:
    soma = sum(jogo)
    distancia = abs(soma - media_soma)

    if not desvio_soma:
        return 10 if distancia == 0 else 7
    if distancia <= 0.5 * desvio_soma:
        return 10
    if distancia <= 1.0 * desvio_soma:
        return 7
    if distancia <= 1.5 * desvio_soma:
        return 4
    return 0


def _score_faixa_alvo(
    contagem: int,
    minimo: int,
    maximo: int,
    pontos_cheios: int,
    pontos_parciais: int,
) -> int:
    if minimo <= contagem <= maximo:
        return pontos_cheios
    if minimo - 1 <= contagem <= maximo + 1:
        return pontos_parciais
    return 0


def score_estrategico(jogo: list[int], quentes: list[int], frios: list[int], atrasados: list[int]) -> int:
    qtd = len(jogo)
    quentes_no_jogo = sum(1 for numero in jogo if numero in quentes)
    frios_no_jogo = sum(1 for numero in jogo if numero in frios)
    atrasados_no_jogo = sum(1 for numero in jogo if numero in atrasados)

    hot_min = max(1, _round_half_up(qtd * 0.33))
    hot_max = max(hot_min, _round_half_up(qtd * 0.50))
    cold_min = max(1, _round_half_up(qtd * 0.17))
    cold_max = max(cold_min, _round_half_up(qtd * 0.33))
    late_min = max(1, _round_half_up(qtd * 0.17))
    late_max = max(late_min, _round_half_up(qtd * 0.33))

    score = 0
    score += _score_faixa_alvo(quentes_no_jogo, hot_min, hot_max, 4, 2)
    score += _score_faixa_alvo(frios_no_jogo, cold_min, cold_max, 3, 2)
    score += _score_faixa_alvo(atrasados_no_jogo, late_min, late_max, 3, 2)

    return min(score, 10)


def penalizacao_sequencia(jogo: list[int]) -> int:
    sequencias = contar_sequencias_consecutivas(jogo)
    leve = max(1, _round_half_up(len(jogo) * 0.15))
    moderado = max(leve + 1, _round_half_up(len(jogo) * 0.30))

    if sequencias == 0:
        return 0
    if sequencias <= leve:
        return -1
    if sequencias <= moderado:
        return -3
    return -5


def obter_pesos_perfil(nome_perfil: str = "equilibrado") -> dict[str, float]:
    perfis = {
        "conservador": {
            "pares_impares": 1.5,
            "faixas": 1.5,
            "soma": 1.5,
            "estrategico": 1.0,
            "sequencia": 1.0,
        },
        "equilibrado": {
            "pares_impares": 1.0,
            "faixas": 1.0,
            "soma": 1.0,
            "estrategico": 1.0,
            "sequencia": 1.0,
        },
        "agressivo": {
            "pares_impares": 0.8,
            "faixas": 0.8,
            "soma": 0.7,
            "estrategico": 1.8,
            "sequencia": 1.2,
        },
        "atrasados": {
            "pares_impares": 0.9,
            "faixas": 0.9,
            "soma": 0.8,
            "estrategico": 2.0,
            "sequencia": 1.0,
        },
    }
    return perfis.get(nome_perfil, perfis["equilibrado"]).copy()


def calcular_score_jogo(
    jogo: list[int],
    analise: dict[str, object],
    pesos: dict[str, float] | None = None,
) -> dict[str, object]:
    if pesos is None:
        pesos = obter_pesos_perfil("equilibrado")

    faixas = analise["faixas"]
    quentes = analise["top_quentes"]
    frios = analise["top_frios"]
    atrasados = analise["top_atrasados"]

    pares = contar_pares(jogo)
    soma_total = int(sum(jogo))
    sequencias = contar_sequencias_consecutivas(jogo)
    contagens_faixas = contar_faixas_jogo(jogo, faixas)
    faixas_ocupadas = sum(valor > 0 for valor in contagens_faixas)
    maior_concentracao = max(contagens_faixas)
    quentes_no_jogo = sum(1 for numero in jogo if numero in quentes)
    frios_no_jogo = sum(1 for numero in jogo if numero in frios)
    atrasados_no_jogo = sum(1 for numero in jogo if numero in atrasados)

    s1 = score_pares_impares(jogo)
    s2 = score_faixas(
        jogo,
        faixas,
        float(analise["media_faixas_ocupadas"]),
        float(analise["media_concentracao_faixas"]),
    )
    s3 = score_soma(jogo, float(analise["media_soma"]), float(analise["desvio_soma"]))
    s4 = score_estrategico(jogo, quentes, frios, atrasados)
    s5 = penalizacao_sequencia(jogo)

    s1p = s1 * pesos["pares_impares"]
    s2p = s2 * pesos["faixas"]
    s3p = s3 * pesos["soma"]
    s4p = s4 * pesos["estrategico"]
    s5p = s5 * pesos["sequencia"]
    score_total = s1p + s2p + s3p + s4p + s5p

    return {
        "jogo": sorted(int(numero) for numero in jogo),
        "pares": pares,
        "impares": len(jogo) - pares,
        "soma_total": soma_total,
        "faixas_ocupadas": faixas_ocupadas,
        "maior_concentracao_faixas": maior_concentracao,
        "sequencias": sequencias,
        "q_quentes": quentes_no_jogo,
        "q_frios": frios_no_jogo,
        "q_atrasados": atrasados_no_jogo,
        "pares_impares": s1,
        "faixas": s2,
        "soma": s3,
        "estrategico": s4,
        "penalizacao_seq": s5,
        "pares_impares_pond": round(s1p, 2),
        "faixas_pond": round(s2p, 2),
        "soma_pond": round(s3p, 2),
        "estrategico_pond": round(s4p, 2),
        "sequencia_pond": round(s5p, 2),
        "score_total": round(score_total, 2),
    }


def formatar_jogo(jogo: list[int] | tuple[int, ...], largura: int = 2) -> str:
    return " - ".join(f"{int(numero):0{largura}d}" for numero in sorted(jogo))


def normalizar_score(df_scores: pd.DataFrame) -> pd.DataFrame:
    if df_scores.empty:
        return df_scores.copy()

    base = df_scores.copy()
    min_score = float(base["score_total"].min())
    max_score = float(base["score_total"].max())

    if math.isclose(min_score, max_score):
        base["score_0_100"] = 100.0
        return base

    base["score_0_100"] = (
        (base["score_total"] - min_score) / (max_score - min_score) * 100
    ).round(2)
    return base


def adicionar_formatacao(df_scores: pd.DataFrame, largura: int = 2) -> pd.DataFrame:
    if df_scores.empty:
        return df_scores.copy()

    base = normalizar_score(df_scores)
    base["jogo_formatado"] = base["jogo"].apply(lambda jogo: formatar_jogo(jogo, largura))
    return base


def _amostrar_unicos(
    pool: list[int],
    usados: set[int],
    quantidade: int,
    rng: np.random.Generator,
) -> list[int]:
    disponiveis = [int(numero) for numero in pool if int(numero) not in usados]
    if quantidade <= 0 or not disponiveis:
        return []

    quantidade_real = min(quantidade, len(disponiveis))
    sorteados = rng.choice(disponiveis, size=quantidade_real, replace=False)
    return [int(numero) for numero in np.atleast_1d(sorteados).tolist()]


def _quantidades_por_perfil(perfil: str, qtd: int) -> list[tuple[str, int]]:
    pesos = {
        "conservador": [("quentes", 0.45), ("atrasados", 0.15)],
        "equilibrado": [("quentes", 0.30), ("frios", 0.25), ("atrasados", 0.15)],
        "agressivo": [("frios", 0.30), ("atrasados", 0.25)],
        "atrasados": [("atrasados", 0.40), ("quentes", 0.20)],
    }
    blueprint = pesos.get(perfil, [])

    quantidades: list[tuple[str, int]] = []
    restante = qtd

    for idx, (nome_pool, proporcao) in enumerate(blueprint):
        minimo = 1 if proporcao > 0 else 0
        alvo = max(minimo, _round_half_up(qtd * proporcao))
        if idx == len(blueprint) - 1:
            alvo = min(alvo, max(0, restante))
        else:
            alvo = min(alvo, max(0, restante - 1))

        quantidades.append((nome_pool, alvo))
        restante -= alvo
        if restante <= 0:
            break

    return quantidades


def gerar_jogo_por_perfil(
    perfil: str,
    analise: dict[str, object],
    rng: np.random.Generator | None = None,
) -> list[int]:
    if rng is None:
        rng = np.random.default_rng()

    universo = [int(numero) for numero in analise["universo"]]
    qtd = int(analise["qtd_dezenas"])
    pools = {
        "quentes": [int(numero) for numero in analise["top_quentes"]],
        "frios": [int(numero) for numero in analise["top_frios"]],
        "atrasados": [int(numero) for numero in analise["top_atrasados"]],
    }

    jogo: list[int] = []
    usados: set[int] = set()

    for nome_pool, quantidade in _quantidades_por_perfil(perfil, qtd):
        selecionados = _amostrar_unicos(pools.get(nome_pool, []), usados, quantidade, rng)
        jogo.extend(selecionados)
        usados.update(selecionados)

    if len(jogo) < qtd:
        faltantes = _amostrar_unicos(universo, usados, qtd - len(jogo), rng)
        jogo.extend(faltantes)

    return sorted(int(numero) for numero in jogo[:qtd])


def gerar_melhores_jogos(
    n_jogos_desejados: int,
    n_tentativas: int,
    perfil: str,
    analise: dict[str, object],
    pesos: dict[str, float] | None = None,
) -> pd.DataFrame:
    rng = np.random.default_rng()
    jogos_unicos: set[tuple[int, ...]] = set()
    resultados: list[dict[str, object]] = []

    tentativas = 0
    limite_unicos = max(n_jogos_desejados * 12, n_jogos_desejados)

    while tentativas < n_tentativas and len(jogos_unicos) < limite_unicos:
        jogo = gerar_jogo_por_perfil(perfil, analise, rng=rng)
        jogo_tuple = tuple(sorted(jogo))

        if jogo_tuple not in jogos_unicos:
            jogos_unicos.add(jogo_tuple)
            resultados.append(calcular_score_jogo(list(jogo_tuple), analise, pesos=pesos))

        tentativas += 1

    if not resultados:
        return pd.DataFrame()

    df_resultados = pd.DataFrame(resultados)
    df_resultados = df_resultados.sort_values("score_total", ascending=False).reset_index(drop=True)
    return df_resultados.head(n_jogos_desejados)
