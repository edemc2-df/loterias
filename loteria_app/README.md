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

## Atualizacao automatica das bases

O repositorio agora pode atualizar automaticamente estas planilhas:

- `loteria_app/data/Lotofacil.xlsx`
- `loteria_app/data/Mega-Sena.xlsx`
- `loteria_app/data/Quina.xlsx`

Arquivos adicionados para isso:

- `scripts/update_lottery_data.py`
- `.github/workflows/update-lottery-data.yml`

Como funciona:

- o script consulta o parametro oficial da CAIXA em `https://loterias.caixa.gov.br/Style%20Library/json/params.txt`
- monta a URL oficial de download da API de resultados
- baixa as tres bases e sobrescreve apenas as que mudaram
- o GitHub Actions roda diariamente e faz commit automatico apenas quando houver diferenca

Horario do agendamento:

- `0 10 * * *` no GitHub Actions, que equivale a 10:00 UTC
- no horario de Brasilia isso costuma ser 07:00 ou 06:00, dependendo do periodo

Para disparar manualmente:

- abra a aba `Actions` no GitHub
- escolha `Atualizar bases das loterias`
- clique em `Run workflow`

## Checklist para subir no GitHub

Arquivos e pastas que devem estar no repositorio:

- `loteria_app/app.py`
- `loteria_app/utils.py`
- `loteria_app/requirements.txt`
- `loteria_app/README.md`
- `loteria_app/data/Lotofacil.xlsx`
- `loteria_app/data/Mega-Sena.xlsx`
- `loteria_app/data/Quina.xlsx`
- `scripts/update_lottery_data.py`
- `.github/workflows/update-lottery-data.yml`
- `.gitignore`

Arquivos e pastas que nao precisam subir:

- `__pycache__/`
- `*.pyc`
- `.venv/`
- `.env`

Checklist de configuracao no GitHub:

1. Suba todos os arquivos listados acima para o mesmo repositorio do app.
2. Confirme na aba `Code` que o workflow existe em `.github/workflows/update-lottery-data.yml`.
3. Abra `Settings > Actions > General`.
4. Em `Workflow permissions`, marque `Read and write permissions`.
5. Salve a configuracao.
6. Abra a aba `Actions`.
7. Rode manualmente o workflow `Atualizar bases das loterias` uma vez.
8. Verifique se ele terminou com sucesso e se nao houve erro de permissao no `git push`.
9. Depois confirme se o commit automatico apareceu no historico quando houver mudanca nas bases.

## Observacoes

- As datas sao tratadas com `dayfirst=True`.
- O logo na pasta `assets/` e opcional.
- As bases sao carregadas automaticamente a partir da pasta `data/`.
