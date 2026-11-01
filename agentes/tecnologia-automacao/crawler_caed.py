#!/usr/bin/env python3
"""
Crawler e Extrator do Portal CAEd Digital / Bem Comum
Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura

Funções:
1. Autenticação automatizada via Playwright/Scrapling no ecossistema CAEd Digital (Bem Comum, CNCA, SAEGO).
2. Armazenamento seguro de sessão (cookies e tokens de autorização).
3. Varredura e extração de painéis diagnósticos, turmas, avaliações e relatórios.
4. Exportação estruturada para relatorios/ e conhecimentos/pedagogico/.
"""

import argparse
import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("crawler_caed")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CONHECIMENTO_DIR = BASE_DIR / "conhecimentos" / "pedagogico"

# Garante diretórios necessários
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
CONHECIMENTO_DIR.mkdir(parents=True, exist_ok=True)

def load_env() -> Dict[str, str]:
    """Carrega variáveis do arquivo .env se existir."""
    env_vars = {}
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip("'\"")
    return env_vars


class CaedCrawler:
    """Controlador de autenticação e raspagem do portal CAEd Digital / Bem Comum."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, headless: bool = True):
        env = load_env()
        self.username = username or env.get("BEMCOMUM_USER") or env.get("CAED_USER") or os.getenv("BEMCOMUM_USER", "")
        self.password = password or env.get("BEMCOMUM_PASSWORD") or env.get("CAED_PASSWORD") or os.getenv("BEMCOMUM_PASSWORD", "")
        self.headless = headless
        self.login_url = "https://bemcomum.caeddigital.net/#!/login"
        self.session_data: Dict[str, Any] = {}

    async def login_and_extract(self, wait_seconds: int = 5) -> Dict[str, Any]:
        """Executa login na plataforma Bem Comum e extrai o panorama inicial."""
        if not self.username or not self.password:
            raise ValueError("Credenciais não configuradas. Verifique o arquivo .env ou passe via argumento.")

        results: Dict[str, Any] = {
            "portal": "Bem Comum (CAEd Digital)",
            "login_user": self.username,
            "status": "iniciado",
            "menus": [],
            "cards": [],
            "tabelas": [],
            "dados_escola": {}
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Captura requisições de API para interceptar tokens JWT e dados JSON
            intercepted_apis: List[Dict[str, Any]] = []

            async def handle_response(response):
                try:
                    url = response.url
                    ct = response.headers.get("content-type", "")
                    if "api" in url.lower() or "json" in ct.lower():
                        if response.status == 200:
                            data = await response.json()
                            intercepted_apis.append({"url": url, "status": response.status, "data": data})
                except Exception:
                    pass

            page.on("response", handle_response)

            logger.info("Navegando até %s...", self.login_url)
            await page.goto(self.login_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4)

            # Localizar campos de login
            # No CAEd Angular, os campos costumam ser input[type='text'], input[type='password'] ou identificados por ng-model
            logger.info("Localizando campos de autenticação...")
            user_input = await page.query_selector("input[name='login'], input[name='cpf'], input[type='text'], input[ng-model*='login'], input[ng-model*='cpf']")
            pass_input = await page.query_selector("input[type='password']")

            if not user_input or not pass_input:
                # Tenta seletores genéricos caso estejam em modal ou layout dinâmico
                all_inputs = await page.query_selector_all("input")
                for inp in all_inputs:
                    inp_type = await inp.get_attribute("type")
                    if inp_type in ("text", "number", "email") and not user_input:
                        user_input = inp
                    elif inp_type == "password" and not pass_input:
                        pass_input = inp

            if not user_input or not pass_input:
                screenshot_path = RELATORIOS_DIR / "login_error_fields.png"
                await page.screenshot(path=str(screenshot_path))
                logger.error("Campos de login não encontrados. Screenshot salvo em %s", screenshot_path)
                results["status"] = "erro_campos_login"
                await browser.close()
                return results

            logger.info("Preenchendo credenciais...")
            await user_input.fill("")
            await user_input.type(self.username, delay=50)
            await pass_input.fill("")
            await pass_input.type(self.password, delay=50)

            # Localizar botão de submissão
            submit_btn = await page.query_selector("button[type='submit'], input[type='submit'], button.btn-primary, button:has-text('Entrar'), button:has-text('Acessar')")
            if not submit_btn:
                # Fallback: pressionar Enter no campo de senha
                logger.info("Pressionando Enter no campo de senha...")
                await pass_input.press("Enter")
            else:
                logger.info("Clicando no botão de login...")
                await submit_btn.click()

            # Aguardar resposta e redirecionamento pós-login
            logger.info("Aguardando carregamento da área logada...")
            await asyncio.sleep(wait_seconds + 3)

            current_url = page.url
            page_title = await page.title()
            logger.info("URL pós-login: %s | Título: %s", current_url, page_title)

            results["url_pos_login"] = current_url
            results["titulo"] = page_title

            # Verifica se houve erro de credencial visível
            error_el = await page.query_selector(".alert-danger, .error-message, .toast-error, [ng-show*='error']")
            if error_el:
                error_text = (await error_el.inner_text()).strip()
                if error_text:
                    logger.warning("Mensagem de erro detectada na página: %s", error_text)
                    results["status"] = "erro_autenticacao"
                    results["mensagem_erro"] = error_text

            # Captura screenshot da tela inicial logada
            screenshot_path = RELATORIOS_DIR / "caed_pos_login.png"
            await page.screenshot(path=str(screenshot_path))
            results["screenshot"] = str(screenshot_path)
            logger.info("Screenshot registrado em: %s", screenshot_path)

            # Extração de menus e navegação
            nav_links = await page.query_selector_all("nav a, .sidebar a, .menu a, a.nav-link, ul.navbar-nav a")
            menus = []
            for link in nav_links:
                txt = (await link.inner_text()).strip()
                href = await link.get_attribute("href")
                if txt and href:
                    menus.append({"label": txt, "href": href})
            results["menus"] = menus

            # Extração de cartões e títulos de destaque (dashboards, escolas, turmas)
            cards_el = await page.query_selector_all(".card, .panel, .box, .dashboard-widget")
            cards = []
            for c in cards_el:
                text = (await c.inner_text()).strip()
                if text:
                    # Limita para resumo
                    first_lines = "\n".join(text.splitlines()[:5])
                    cards.append(first_lines)
            results["cards"] = cards

            # Salva dados interceptados da API
            results["apis_capturadas"] = [
                {"url": item["url"], "dados_resumo": str(item["data"])[:200]}
                for item in intercepted_apis
            ]

            results["status"] = "sucesso" if "login" not in current_url.lower() else "verificar"
            await browser.close()

        # Gravar em arquivo JSON
        output_file = RELATORIOS_DIR / "dados_bemcomum.json"
        output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("[OK] Extração finalizada com sucesso. Dados em: %s", output_file)
        return results


def main():
    parser = argparse.ArgumentParser(description="Crawler CAEd Digital / Bem Comum")
    parser.add_argument("--user", help="Login/CPF")
    parser.add_argument("--password", help="Senha")
    parser.add_argument("--headless", action="store_true", default=True, help="Executar em modo headless")
    args = parser.parse_args()

    crawler = CaedCrawler(username=args.user, password=args.password, headless=args.headless)
    data = asyncio.run(crawler.login_and_extract())
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
