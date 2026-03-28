import pandas as pd
import numpy as np


def calcular_frequencia(df, colunas_dezenas):
    serie = df[colunas_dezenas].stack().astype(int)

    frequencia = (
        serie.value_counts()
        .sort_index()
        .reset_index()
    )

    frequencia.columns = ["numero", "frequencia"]
    frequencia = frequencia.sort_values("frequencia", ascending=False).reset_index(drop=True)

    return frequencia


def calcular_atraso(df, colunas_dezenas):
    df_long = df.reset_index().melt(
        id_vars=["index"],
        value_vars=colunas_dezenas,
        value_name="numero"
    )

    df_long = df_long.rename(columns={"index": "concurso_idx"})
    df_long = df_long.sort_values("concurso_idx")

    ultimo_concurso = df_long.groupby("numero")["concurso_idx"].max().reset_index()
    ultimo_idx = df_long["concurso_idx"].max()

    ultimo_concurso["atraso"] = ultimo_idx - ultimo_concurso["concurso_idx"]
    ultimo_concurso = ultimo_concurso.sort_values("atraso", ascending=False).reset_index(drop=True)

    return ultimo_concurso


def score_pares_impares(jogo):
    pares = sum(1 for n in jogo if n % 2 == 0)

    if pares == 3:
        return 10
    elif pares in [2, 4]:
        return 7
    elif pares in [1, 5]:
        return 3
    else:
        return 0


def score_faixas(jogo):
    faixas = {
        "1-10": 0, "11-20": 0, "21-30": 0,
        "31-40": 0, "41-50": 0, "51-60": 0
    }

    for n in jogo:
        if 1 <= n <= 10:
            faixas["1-10"] += 1
        elif 11 <= n <= 20:
            faixas["11-20"] += 1
        elif 21 <= n <= 30:
            faixas["21-30"] += 1
        elif 31 <= n <= 40:
            faixas["31-40"] += 1
        elif 41 <= n <= 50:
            faixas["41-50"] += 1
        elif 51 <= n <= 60:
            faixas["51-60"] += 1

    ocupadas = sum(1 for v in faixas.values() if v > 0)
    maior_concentracao = max(faixas.values())

    if ocupadas >= 5 and maior_concentracao <= 2:
        return 10
    elif ocupadas >= 4 and maior_concentracao <= 3:
        return 7
    elif ocupadas >= 3:
        return 4
    else:
        return 0


def score_soma(jogo, media_soma, desvio_soma):
    soma = sum(jogo)
    distancia = abs(soma - media_soma)

    if distancia <= 0.5 * desvio_soma:
        return 10
    elif distancia <= 1.0 * desvio_soma:
        return 7
    elif distancia <= 1.5 * desvio_soma:
        return 4
    else:
        return 0


def score_estrategico(jogo, quentes, frios, atrasados):
    q_quentes = sum(1 for n in jogo if n in quentes)
    q_frios = sum(1 for n in jogo if n in frios)
    q_atrasados = sum(1 for n in jogo if n in atrasados)

    score = 0

    if 2 <= q_quentes <= 3:
        score += 4
    elif q_quentes in [1, 4]:
        score += 2

    if 1 <= q_frios <= 2:
        score += 3
    elif q_frios == 3:
        score += 2

    if 1 <= q_atrasados <= 2:
        score += 3
    elif q_atrasados == 3:
        score += 2

    return min(score, 10)


def penalizacao_sequencia(jogo):
    jogo_ordenado = sorted(jogo)
    sequencias = 0

    for i in range(len(jogo_ordenado) - 1):
        if jogo_ordenado[i + 1] - jogo_ordenado[i] == 1:
            sequencias += 1

    if sequencias == 0:
        return 0
    elif sequencias == 1:
        return -1
    elif sequencias == 2:
        return -3
    else:
        return -5


def obter_pesos_perfil(nome_perfil="equilibrado"):
    perfis = {
        "conservador": {
            "pares_impares": 1.5,
            "faixas": 1.5,
            "soma": 1.5,
            "estrategico": 1.0,
            "sequencia": 1.0
        },
        "equilibrado": {
            "pares_impares": 1.0,
            "faixas": 1.0,
            "soma": 1.0,
            "estrategico": 1.0,
            "sequencia": 1.0
        },
        "agressivo": {
            "pares_impares": 0.8,
            "faixas": 0.8,
            "soma": 0.7,
            "estrategico": 1.8,
            "sequencia": 1.2
        },
        "atrasados": {
            "pares_impares": 0.9,
            "faixas": 0.9,
            "soma": 0.8,
            "estrategico": 2.0,
            "sequencia": 1.0
        }
    }

    return perfis.get(nome_perfil, perfis["equilibrado"])


def calcular_score_jogo(jogo, media_soma, desvio_soma, quentes, frios, atrasados, pesos=None):
    if pesos is None:
        pesos = {
            "pares_impares": 1.0,
            "faixas": 1.0,
            "soma": 1.0,
            "estrategico": 1.0,
            "sequencia": 1.0
        }

    s1 = score_pares_impares(jogo)
    s2 = score_faixas(jogo)
    s3 = score_soma(jogo, media_soma, desvio_soma)
    s4 = score_estrategico(jogo, quentes, frios, atrasados)
    s5 = penalizacao_sequencia(jogo)

    s1p = s1 * pesos["pares_impares"]
    s2p = s2 * pesos["faixas"]
    s3p = s3 * pesos["soma"]
    s4p = s4 * pesos["estrategico"]
    s5p = s5 * pesos["sequencia"]

    score_total = s1p + s2p + s3p + s4p + s5p

    return {
        "jogo": sorted(jogo),
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
        "score_total": round(score_total, 2)
    }


def formatar_jogo(jogo):
    return " - ".join(f"{int(n):02d}" for n in sorted(jogo))


def adicionar_formatacao(df_scores):
    df_scores = df_scores.copy()
    df_scores["jogo_formatado"] = df_scores["jogo"].apply(formatar_jogo)
    return df_scores


def completar_jogo(jogo, universo, qtd=6):
    jogo = list(set(map(int, jogo)))

    while len(jogo) < qtd:
        faltantes = list(set(universo) - set(jogo))
        jogo.append(int(np.random.choice(faltantes)))

    return sorted(jogo)


def gerar_jogo_por_perfil(perfil, quentes, frios, atrasados, universo=range(1, 61), qtd=6):
    jogo = []

    if perfil == "conservador":
        jogo.extend(np.random.choice(quentes, size=3, replace=False))
        jogo.extend(np.random.choice(atrasados, size=1, replace=False))

    elif perfil == "equilibrado":
        jogo.extend(np.random.choice(quentes, size=2, replace=False))
        jogo.extend(np.random.choice(frios, size=2, replace=False))
        jogo.extend(np.random.choice(atrasados, size=1, replace=False))

    elif perfil == "agressivo":
        jogo.extend(np.random.choice(frios, size=2, replace=False))
        jogo.extend(np.random.choice(atrasados, size=2, replace=False))

    else:
        jogo.extend(np.random.choice(list(universo), size=qtd, replace=False))

    return completar_jogo(jogo, universo=universo, qtd=qtd)


def gerar_melhores_jogos(
    n_jogos_desejados,
    n_tentativas,
    perfil,
    media_soma,
    desvio_soma,
    quentes,
    frios,
    atrasados,
    pesos=None,
    universo=range(1, 61),
    qtd=6
):
    jogos_unicos = set()
    resultados = []
    tentativas = 0

    while tentativas < n_tentativas and len(jogos_unicos) < n_jogos_desejados * 10:
        jogo = gerar_jogo_por_perfil(
            perfil=perfil,
            quentes=quentes,
            frios=frios,
            atrasados=atrasados,
            universo=universo,
            qtd=qtd
        )

        jogo_tuple = tuple(sorted(jogo))

        if jogo_tuple not in jogos_unicos:
            jogos_unicos.add(jogo_tuple)

            avaliacao = calcular_score_jogo(
                jogo=list(jogo_tuple),
                media_soma=media_soma,
                desvio_soma=desvio_soma,
                quentes=quentes,
                frios=frios,
                atrasados=atrasados,
                pesos=pesos
            )

            resultados.append(avaliacao)

        tentativas += 1

    if not resultados:
        return pd.DataFrame()

    df_resultados = pd.DataFrame(resultados)
    df_resultados = df_resultados.sort_values("score_total", ascending=False).reset_index(drop=True)

    return df_resultados.head(n_jogos_desejados)
