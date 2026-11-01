#!/usr/bin/env python3
"""
Módulo de Integração e Leitura de Portais Educacionais
Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura
Utiliza a biblioteca Scrapling (D4Vinci) para conexões furtivas, gerenciamento
de sessões e extração adaptativa de dados do GEMUL, SIAM, CNCA e afins.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

try:
    from scrapling.fetchers import Fetcher, FetcherSession, DynamicSession, StealthySession
    from scrapling.parser import Adaptor
except ImportError:
    print("[ERRO] Scrapling não encontrado. Instale com: pip install \"scrapling[all]\"")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("portal_crawler")

GEMUL_BASE_URL = "https://gemul-aparecida.com.br"
GEMUL_LOGIN_URL = f"{GEMUL_BASE_URL}/login/index.asp"
GEMUL_AUTH_NUMERIC_URL = f"{GEMUL_BASE_URL}/gemul/portal/validaPermissao.asp"
GEMUL_AUTH_TEXT_URL = f"{GEMUL_BASE_URL}/login/validaUsuario.asp"


class GemulClient:
    """Cliente para automação e extração de dados do GEMUL via Scrapling."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.getenv("GEMUL_USER") or os.getenv("GEMUL_LOGIN") or ""
        self.password = password or os.getenv("GEMUL_PASSWORD") or os.getenv("GEMUL_SENHA") or ""
        self.session: Optional[FetcherSession] = None
        self.logged_in = False

    def test_connection(self) -> Dict[str, Any]:
        """Testa a conectividade com o portal GEMUL."""
        try:
            logger.info("Testando conectividade com %s...", GEMUL_LOGIN_URL)
            page = Fetcher.get(GEMUL_LOGIN_URL, timeout=15)
            forms = page.css("form")
            title_el = page.css("title")
            title_text = title_el[0].text.strip() if title_el and title_el[0].text else "GEMUL"
            return {
                "status": "online",
                "http_code": page.status,
                "url": GEMUL_LOGIN_URL,
                "forms_detected": len(forms),
                "title": title_text
            }
        except Exception as e:
            logger.error("Falha ao conectar ao GEMUL: %s", e)
            return {
                "status": "error",
                "error": str(e),
                "url": GEMUL_LOGIN_URL
            }

    def login(self) -> bool:
        """Realiza autenticação no portal GEMUL mantendo sessão de cookies ativa."""
        if not self.username or not self.password:
            logger.warning("Credenciais do GEMUL não informadas (defina GEMUL_USER e GEMUL_PASSWORD no .env)")
            return False

        clean_user = self.username.replace(".", "").replace("-", "").strip()
        clean_pass = self.password.replace(".", "").replace("-", "").strip()

        # Determina o endpoint conforme a regra do validaCampo() do GEMUL
        if clean_user.isnumeric():
            auth_url = GEMUL_AUTH_NUMERIC_URL
        else:
            auth_url = GEMUL_AUTH_TEXT_URL

        logger.info("Iniciando sessão Scrapling para autenticação no GEMUL...")
        self.session = FetcherSession()

        # 1. Carrega a página inicial de login para capturar cookies iniciais (ASPSESSIONID)
        try:
            self.session.get(GEMUL_LOGIN_URL, timeout=15)
        except Exception as e:
            logger.error("Erro ao carregar página de login: %s", e)
            return False

        # 2. Executa o POST de autenticação com formulário padrão
        payload = {
            "txtLogin": clean_user,
            "txtSenha": clean_pass
        }

        try:
            logger.info("Enviando credenciais para %s...", auth_url)
            resp = self.session.post(auth_url, data=payload, timeout=20)
            text_body = resp.text.lower()

            # Verificações de recusa ou sucesso
            if "senha incorreta" in text_body or "usuário não localizado" in text_body or "invalido" in text_body:
                logger.error("Falha de autenticação no GEMUL: usuário ou senha recusados.")
                self.logged_in = False
                return False

            logger.info("Autenticação realizada com sucesso no GEMUL (HTTP %s).", resp.status)
            self.logged_in = True
            return True
        except Exception as e:
            logger.error("Erro durante o POST de login: %s", e)
            self.logged_in = False
            return False

    def fetch_page(self, path_or_url: str) -> Optional[Adaptor]:
        """Recupera uma página interna do GEMUL com a sessão autenticada."""
        if not self.session:
            self.session = FetcherSession()

        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            url = path_or_url
        else:
            url = urljoin(GEMUL_BASE_URL, path_or_url)

        try:
            logger.info("Recuperando página: %s...", url)
            response = self.session.get(url, timeout=25)
            return response
        except Exception as e:
            logger.error("Falha ao recuperar %s: %s", url, e)
            return None

    @staticmethod
    def parse_table_to_data(table_element) -> List[Dict[str, str]]:
        """Converte uma tabela HTML em lista de dicionários estruturados."""
        rows = table_element.css("tr")
        if not rows:
            return []

        # Tenta obter cabeçalhos de th ou da primeira tr
        headers = []
        header_cells = rows[0].css("th, td")
        for cell in header_cells:
            headers.append(cell.text.strip() if cell.text else f"col_{len(headers)}")

        data = []
        for r in rows[1:]:
            cells = r.css("td")
            if not cells:
                continue
            row_dict = {}
            for idx, cell in enumerate(cells):
                col_name = headers[idx] if idx < len(headers) else f"col_{idx}"
                row_dict[col_name] = cell.text.strip() if cell.text else ""
            data.append(row_dict)

        return data


def main():
    parser = argparse.ArgumentParser(description="Scrapling Portal Extractor para Fábrica de Agentes Escolares")
    parser.add_argument("--portal", choices=["gemul", "siam", "cnca"], default="gemul", help="Portal alvo")
    parser.add_argument("--test", action="store_true", help="Testa apenas a conectividade com o portal")
    parser.add_argument("--login", action="store_true", help="Testa o login com as credenciais salvas no ambiente")
    parser.add_argument("--fetch", type=str, help="URL ou caminho relativo para extração de página")
    parser.add_argument("--output", type=str, help="Caminho para salvar o resultado (JSON ou Markdown)")

    args = parser.parse_args()

    if args.portal == "gemul":
        client = GemulClient()
        if args.test:
            result = client.test_connection()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        if args.login:
            success = client.login()
            if success:
                print("✅ Login efetuado com sucesso no GEMUL!")
            else:
                print("❌ Não foi possível realizar o login. Verifique as credenciais no .env.")
            return

        if args.fetch:
            if not client.logged_in:
                client.login()
            page = client.fetch_page(args.fetch)
            if not page:
                print("❌ Falha na extração da página.")
                return

            tables = page.css("table")
            print(f"Página obtida com sucesso. Tabelas encontradas: {len(tables)}")
            extracted = []
            for idx, t in enumerate(tables):
                data = client.parse_table_to_data(t)
                if data:
                    extracted.append({"table_index": idx, "rows": data})

            output_content = json.dumps(extracted, indent=2, ensure_ascii=False)
            if args.output:
                Path(args.output).write_text(output_content, encoding="utf-8")
                print(f"Dados salvos em {args.output}")
            else:
                print(output_content)


if __name__ == "__main__":
    main()
