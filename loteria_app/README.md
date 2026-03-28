# Loteria Inteligente

Aplicativo em Streamlit para análise histórica da Mega-Sena e geração inteligente de jogos com base em:

- frequência histórica
- atraso dos números
- score ponderado
- perfis de geração
- exportação dos jogos em Excel

## Estrutura do projeto

```text
loteria_app/
│
├── app.py
├── utils.py
├── requirements.txt
├── data/
│   └── Mega-Sena.xlsx
└── assets/
    └── logo.png   # opcional
```

## Como rodar localmente

1. Crie e acesse a pasta do projeto.
2. Coloque os arquivos `app.py`, `utils.py` e `requirements.txt`.
3. Crie a pasta `data` e coloque dentro dela o arquivo `Mega-Sena.xlsx`.
4. Opcionalmente, crie a pasta `assets` e adicione um `logo.png`.
5. Instale as dependências:

```bash
pip install -r requirements.txt
```

6. Rode o app:

```bash
streamlit run app.py
```

## Como publicar no Streamlit Cloud

1. Suba os arquivos para um repositório no GitHub.
2. Verifique se a base está em `data/Mega-Sena.xlsx`.
3. No Streamlit Community Cloud, conecte o repositório.
4. Defina o arquivo principal como `app.py`.
5. Clique em deploy.

## Observações

- O app considera datas no formato brasileiro com `dayfirst=True`.
- O logo é opcional.
- A base é fixa e carregada automaticamente ao abrir o aplicativo.
