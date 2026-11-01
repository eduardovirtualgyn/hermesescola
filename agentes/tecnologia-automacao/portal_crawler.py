#!/usr/bin/env python3
"""
Módulo Unificado de Automação e Extração de Portais Educacionais
Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura
Desenvolvido com o framework Scrapling (D4Vinci)

Portais Mapeados e Integrados:
1. GEMUL (Aparecida): https://gemul-aparecida.com.br/login/index.asp
2. CNCA (CAEd Digital): https://criancaalfabetizada.caeddigital.net/#!/login
3. SAEGO (CAEd Digital): https://avaliacaoemonitoramentogoias.caeddigital.net/#!/login
4. Bem Comum / PARC (CAEd): https://bemcomum.caeddigital.net/
5. SIAM (SEDUC-GO): https://siam.educacao.go.gov.br/login
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
    from scrapling.fetchers import Fetcher, FetcherSession, DynamicFetcher, DynamicSession, StealthySession
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

# Dicionário canônico dos 5 portais da escola
PORTAIS_CONFIG = {
    "gemul": {
        "nome": "GEMUL (Aparecida de Goiânia)",
        "url": "https://gemul-aparecida.com.br/login/index.asp",
        "tipo": "asp_session",
        "descricao": "Sistema de Gestão Educacional Municipal (matrículas, turmas, notas, faltas e transferências)",
        "env_user": "GEMUL_USER",
        "env_pass": "GEMUL_PASSWORD"
    },
    "cnca": {
        "nome": "Criança Alfabetizada - CNCA (CAEd Digital)",
        "url": "https://criancaalfabetizada.caeddigital.net/#!/login",
        "tipo": "caed_spa",
        "descricao": "Plataforma de Avaliação da Alfabetização e Letramento (1º e 2º anos)",
        "env_user": "CAED_USER",
        "env_pass": "CAED_PASSWORD"
    },
    "saego": {
        "nome": "SAEGO (Avaliação e Monitoramento CAEd / Goiás)",
        "url": "https://avaliacaoemonitoramentogoias.caeddigital.net/#!/login",
        "tipo": "caed_spa",
        "descricao": "Sistema de Avaliação Educacional do Estado de Goiás (proficiências e diagnósticas)",
        "env_user": "CAED_USER",
        "env_pass": "CAED_PASSWORD"
    },
    "bemcomum": {
        "nome": "Associação Bem Comum / PARC (CAEd Digital)",
        "url": "https://bemcomum.caeddigital.net/",
        "tipo": "caed_spa",
        "descricao": "Plataforma do Programa de Aprendizagem em Regime de Colaboração",
        "env_user": "CAED_USER",
        "env_pass": "CAED_PASSWORD"
    },
    "siam": {
        "nome": "SIAM Educação (SEDUC-GO)",
        "url": "https://siam.educacao.go.gov.br/login",
        "tipo": "vite_spa",
        "descricao": "Sistema Integrado de Administração da Educação de Goiás (quadro funcional e gestão)",
        "env_user": "SIAM_USER",
        "env_pass": "SIAM_PASSWORD"
    }
}


class GemulHandler:
    """Manipulador para o portal ASP do GEMUL (Aparecida de Goiânia)."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.getenv("GEMUL_USER") or os.getenv("GEMUL_LOGIN") or ""
        self.password = password or os.getenv("GEMUL_PASSWORD") or os.getenv("GEMUL_SENHA") or ""
        self.base_url = "https://gemul-aparecida.com.br"
        self.session: Optional[FetcherSession] = None
        self.logged_in = False

    def check_health(self) -> Dict[str, Any]:
        url = PORTAIS_CONFIG["gemul"]["url"]
        logger.info("Testando conectividade com %s...", url)
        try:
            page = Fetcher.get(url, timeout=15)
            title = page.css("title")[0].text.strip() if page.css("title") else "GEMUL"
            return {
                "portal": "gemul",
                "nome": PORTAIS_CONFIG["gemul"]["nome"],
                "status": "online",
                "http_code": page.status,
                "url": url,
                "title": title,
                "tipo": "ASP Clássico"
            }
        except Exception as e:
            return {"portal": "gemul", "status": "offline", "erro": str(e), "url": url}

    def login(self) -> bool:
        if not self.username or not self.password:
            logger.warning("Credenciais do GEMUL não localizadas no .env (defina GEMUL_USER e GEMUL_PASSWORD)")
            return False

        clean_user = self.username.replace(".", "").replace("-", "").strip()
        clean_pass = self.password.replace(".", "").replace("-", "").strip()

        auth_url = f"{self.base_url}/gemul/portal/validaPermissao.asp" if clean_user.isnumeric() else f"{self.base_url}/login/validaUsuario.asp"

        self.session = FetcherSession()
        try:
            # 1. Carrega login para capturar cookies de sessão
            self.session.get(f"{self.base_url}/login/index.asp", timeout=15)
            # 2. Submete credenciais
            payload = {"txtLogin": clean_user, "txtSenha": clean_pass}
            resp = self.session.post(auth_url, data=payload, timeout=20)
            body = resp.text.lower()
            if "senha incorreta" in body or "usuário não localizado" in body or "invalido" in body:
                logger.error("Credenciais do GEMUL recusadas pelo servidor.")
                return False

            self.logged_in = True
            logger.info("Login efetuado com sucesso no GEMUL.")
            return True
        except Exception as e:
            logger.error("Falha no login do GEMUL: %s", e)
            return False

    def fetch(self, path_or_url: str) -> Optional[Adaptor]:
        if not self.session:
            self.session = FetcherSession()
        url = path_or_url if path_or_url.startswith("http") else urljoin(self.base_url, path_or_url)
        try:
            return self.session.get(url, timeout=25)
        except Exception as e:
            logger.error("Falha ao recuperar página %s: %s", url, e)
            return None


class SpaHandler:
    """Manipulador para portais Single Page Applications (CAEd Digital e SIAM) via DynamicFetcher."""

    def __init__(self, portal_key: str, username: Optional[str] = None, password: Optional[str] = None):
        self.portal_key = portal_key
        self.cfg = PORTAIS_CONFIG[portal_key]
        self.username = username or os.getenv(self.cfg["env_user"]) or ""
        self.password = password or os.getenv(self.cfg["env_pass"]) or ""

    def check_health(self) -> Dict[str, Any]:
        url = self.cfg["url"]
        logger.info("Testando conectividade de %s (%s)...", self.cfg["nome"], url)
        try:
            page = Fetcher.get(url, timeout=12)
            title = page.css("title")[0].text.strip() if page.css("title") else self.cfg["nome"]
            scripts = [s.attrib.get("src") for s in page.css("script") if s.attrib.get("src")]

            return {
                "portal": self.portal_key,
                "nome": self.cfg["nome"],
                "status": "online",
                "http_code": page.status,
                "url": url,
                "title": title,
                "tipo": self.cfg["tipo"],
                "arquitetura": "SPA (Single Page App - renderizavel via DynamicFetcher)",
                "scripts_detectados": len(scripts)
            }
        except Exception as e:
            return {
                "portal": self.portal_key,
                "nome": self.cfg["nome"],
                "status": "offline/erro",
                "erro": str(e),
                "url": url
            }

    def fetch_rendered(self, url: str) -> Optional[Adaptor]:
        try:
            logger.info("Renderizando com Scrapling DynamicFetcher: %s...", url)
            return DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=30000)
        except Exception as e:
            logger.error("Erro na renderização SPA de %s: %s", url, e)
            return None


def parse_tables_from_page(page: Adaptor) -> List[Dict[str, Any]]:
    """Converte todas as tabelas HTML encontradas em dados estruturados."""
    tables = page.css("table")
    extracted_tables = []
    for idx, table in enumerate(tables):
        rows = table.css("tr")
        if not rows:
            continue
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
            for col_idx, cell in enumerate(cells):
                col_name = headers[col_idx] if col_idx < len(headers) else f"col_{col_idx}"
                row_dict[col_name] = cell.text.strip() if cell.text else ""
            data.append(row_dict)

        if data:
            extracted_tables.append({"table_index": idx, "total_linhas": len(data), "dados": data})

    return extracted_tables


def diagnostic_all() -> List[Dict[str, Any]]:
    """Executa diagnóstico completo de conectividade em todos os 5 portais."""
    print("=" * 70)
    print("DIAGNÓSTICO DA FÁBRICA DE AGENTES: 5 PORTAIS EDUCACIONAIS")
    print("=" * 70)
    results = []

    # 1. GEMUL
    gemul = GemulHandler()
    results.append(gemul.check_health())

    # 2. CAEd & SIAM
    for p_key in ["cnca", "saego", "bemcomum", "siam"]:
        handler = SpaHandler(p_key)
        results.append(handler.check_health())

    return results


def main():
    parser = argparse.ArgumentParser(description="Scrapling Portal Extractor — Fábrica de Agentes Escolares")
    parser.add_argument("--portal", choices=["gemul", "cnca", "saego", "bemcomum", "siam", "all"], default="all",
                        help="Portal alvo (gemul, cnca, saego, bemcomum, siam ou all)")
    parser.add_argument("--test", action="store_true", help="Testa conectividade e renderização do(s) portal(is)")
    parser.add_argument("--fetch", type=str, help="URL ou rota para extrair dados tabulares")
    parser.add_argument("--output", type=str, help="Arquivo de destino para salvar os dados em JSON")

    args = parser.parse_args()

    if args.portal == "all" or args.test:
        if args.portal == "all":
            results = diagnostic_all()
            output_json = json.dumps(results, indent=2, ensure_ascii=False)
            print(output_json)
            if args.output:
                Path(args.output).write_text(output_json, encoding="utf-8")
                print(f"\n[OK] Relatorio de diagnostico salvo em {args.output}")
            return
        elif args.portal == "gemul":
            handler = GemulHandler()
            res = handler.check_health()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        else:
            handler = SpaHandler(args.portal)
            res = handler.check_health()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return

    if args.fetch:
        if args.portal == "gemul":
            client = GemulHandler()
            client.login()
            page = client.fetch(args.fetch)
        else:
            spa = SpaHandler(args.portal)
            page = spa.fetch_rendered(args.fetch)

        if not page:
            print("[ERRO] Falha ao recuperar pagina.")
            return

        tables = parse_tables_from_page(page)
        res_data = {
            "portal": args.portal,
            "url": args.fetch,
            "total_tabelas": len(tables),
            "tabelas": tables
        }
        output_json = json.dumps(res_data, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(output_json, encoding="utf-8")
            print(f"[OK] Dados extraidos com sucesso e salvos em {args.output}")
        else:
            print(output_json)


if __name__ == "__main__":
    main()
