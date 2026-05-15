from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "loteria_app" / "data"
PARAMS_URL = "https://loterias.caixa.gov.br/Style%20Library/json/params.txt"
USER_AGENT = "Mozilla/5.0 (compatible; LoteriasInteligentesBot/1.0)"

DATASETS = (
    {
        "modalidade": "Lotofacil",
        "filename": "Lotofacil.xlsx",
    },
    {
        "modalidade": "Mega-Sena",
        "filename": "Mega-Sena.xlsx",
    },
    {
        "modalidade": "Quina",
        "filename": "Quina.xlsx",
    },
)


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def fetch_api_base() -> str:
    raw = fetch_bytes(PARAMS_URL)
    payload = json.loads(raw.decode("utf-8"))
    api_base = str(payload["urlapiloterias"]).rstrip("/")

    if not api_base.startswith("http"):
        raise RuntimeError(f"URL da API inválida: {api_base}")

    return api_base


def build_download_url(api_base: str, modalidade: str) -> str:
    query = urllib.parse.urlencode({"modalidade": modalidade})
    return f"{api_base}/api/resultados/download?{query}"


def validate_xlsx_bytes(content: bytes, modalidade: str) -> None:
    if not content.startswith(b"PK"):
        raise RuntimeError(f"O download de {modalidade} não retornou um XLSX válido.")

    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            nomes = set(archive.namelist())
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"O download de {modalidade} retornou um ZIP inválido.") from exc

    if "[Content_Types].xml" not in nomes or "xl/workbook.xml" not in nomes:
        raise RuntimeError(f"O arquivo de {modalidade} não parece ser um workbook do Excel.")


def write_if_changed(destination: Path, content: bytes) -> str:
    if destination.exists() and destination.read_bytes() == content:
        return "unchanged"

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return "updated"


def update_dataset(api_base: str, modalidade: str, filename: str) -> str:
    url = build_download_url(api_base, modalidade)
    content = fetch_bytes(url)
    validate_xlsx_bytes(content, modalidade)
    status = write_if_changed(DATA_DIR / filename, content)
    print(f"{modalidade}: {status} -> {filename}")
    return status


def main() -> int:
    try:
        api_base = fetch_api_base()
        print(f"API detectada: {api_base}")

        statuses = [
            update_dataset(
                api_base=api_base,
                modalidade=item["modalidade"],
                filename=item["filename"],
            )
            for item in DATASETS
        ]
    except (KeyError, OSError, urllib.error.URLError, urllib.error.HTTPError, RuntimeError, ValueError) as exc:
        print(f"Falha ao atualizar as bases: {exc}", file=sys.stderr)
        return 1

    updated = sum(1 for status in statuses if status == "updated")
    unchanged = sum(1 for status in statuses if status == "unchanged")
    print(f"Resumo: {updated} atualizado(s), {unchanged} sem mudança.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
