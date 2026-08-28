"""
01_download_dados.py

Baixa os datasets de Contratações do TCE-ES (Controle Externo)
disponibilizados na plataforma CKAN do Governo do Espírito Santo
(dados.es.gov.br).

Como rodar:
    cd TCC/prototipo
    python -m venv venv
    venv\\Scripts\\activate        (Windows)
    pip install -r requirements.txt
    python scripts/01_download_dados.py
"""

import requests
from pathlib import Path

# Pasta onde os CSVs brutos serão salvos
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# URLs diretas dos recursos no CKAN (dados.es.gov.br)
# Origem: dataset "[TCEES] Contratações - Controle Externo"
# https://dados.es.gov.br/dataset/tcees-contratacoes
RECURSOS = {
    "instrumentos_contratuais_alteracoes": (
        "https://dados.es.gov.br/dataset/29ac71a3-dcec-42c8-9b9c-a9bba39e0c53"
        "/resource/ed499bd8-a17d-47a4-bbd1-a239351895e2"
        "/download/instrumentoscontratuaisalteracaomedicao.csv"
    ),
    # TODO: preencher com as URLs dos outros recursos (clicando em "Explorar"
    # -> "Baixar" em cada um, igual fizemos com o primeiro):
    # "instrumentos_contratuais": "https://dados.es.gov.br/dataset/.../download/...",
    # "contratacoes": "https://dados.es.gov.br/dataset/.../download/...",
}

HEADERS = {
    # Alguns portais CKAN bloqueiam requisições sem User-Agent de navegador
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def baixar_csv(nome: str, url: str) -> Path:
    destino = RAW_DIR / f"{nome}.csv"
    print(f"Baixando '{nome}'...")
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    destino.write_bytes(resp.content)
    tamanho_mb = len(resp.content) / (1024 * 1024)
    print(f"  -> salvo em {destino} ({tamanho_mb:.2f} MB)")
    return destino


def inspecionar_csv(caminho: Path) -> None:
    """Mostra as primeiras linhas e colunas do CSV baixado.

    Arquivos de dados abertos de governos brasileiros frequentemente vêm
    em Latin-1/CP1252 (não UTF-8) e usam ';' como separador. Este método
    tenta várias combinações até uma funcionar, lendo só uma amostra
    (nrows), já que o arquivo completo pode ter mais de 1 GB.
    """
    import pandas as pd

    print(f"\nInspecionando {caminho.name}...")

    tentativas = [
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin-1"},
        {"sep": ";", "encoding": "cp1252"},
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin-1"},
    ]

    df = None
    for tentativa in tentativas:
        try:
            df = pd.read_csv(caminho, nrows=50, **tentativa)
            print(f"  Sucesso com sep='{tentativa['sep']}' encoding='{tentativa['encoding']}'")
            break
        except Exception as e:
            print(f"  [!] Falhou com {tentativa}: {type(e).__name__}")

    if df is None:
        print("  [ERRO] Nenhuma combinação de separador/encoding funcionou.")
        print("  Envie as primeiras linhas do CSV (abra com Notepad) para eu investigar.")
        return

    print(f"\n  Colunas encontradas ({len(df.columns)}):")
    for col in df.columns:
        print(f"    - {col}")
    print(f"\n  Prévia (5 primeiras linhas):")
    print(df.head())


def main():
    caminhos_baixados = []
    for nome, url in RECURSOS.items():
        try:
            caminho = baixar_csv(nome, url)
            caminhos_baixados.append(caminho)
        except requests.HTTPError as e:
            print(f"  [ERRO] Falha ao baixar '{nome}': {e}")
        except requests.RequestException as e:
            print(f"  [ERRO] Problema de conexão em '{nome}': {e}")

    for caminho in caminhos_baixados:
        inspecionar_csv(caminho)

    print("\nConcluído. Confira os arquivos em data/raw/.")
    print("Copie as colunas impressas acima e me envie de volta — ")
    print("assim ajusto o próximo script (modelagem do banco MySQL) certinho.")


if __name__ == "__main__":
    main()