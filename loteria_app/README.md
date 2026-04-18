# Loterias Inteligentes

Aplicativo em Streamlit para analise historica e geracao inteligente de jogos para:

- Mega-Sena
- Lotofacil
- Quina

O motor segue a mesma linha do notebook `loterias.ipynb` e combina:

- frequencia historica
- atraso por dezena
- soma historica dos concursos
- equilibrio entre pares e impares
- distribuicao por faixas numericas
- mistura entre quentes, frios e atrasados
- perfis com pesos configuraveis

## Estrutura

```text
loteria_app/
|-- app.py
|-- utils.py
|-- requirements.txt
|-- data/
|   |-- Mega-Sena.xlsx
|   |-- Lotofacil.xlsx
|   `-- Quina.xlsx
`-- assets/
    `-- logo.png   # opcional
```

## Como rodar

1. Entre na pasta `loteria_app`.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Rode o aplicativo:

```bash
streamlit run app.py
```

Se preferir rodar a partir da raiz do repositorio:

```bash
streamlit run loteria_app/app.py
```

## O que a interface entrega

- selecao da loteria em uma unica tela
- dashboard historico com graficos e pools de referencia
- gerador de jogos com perfis e pesos configuraveis
- ranking dos melhores jogos com score detalhado
- exportacao dos jogos gerados para Excel

## Observacoes

- As datas sao tratadas com `dayfirst=True`.
- O logo na pasta `assets/` e opcional.
- As bases sao carregadas automaticamente a partir da pasta `data/`.
