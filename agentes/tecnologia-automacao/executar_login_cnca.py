import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("cnca_login")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

def load_env():
    env_vars = {}
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip("'\"")
    return env_vars

async def login_cnca():
    env = load_env()
    login_user = env.get("CNCA_USER", "92937934153")
    caed_pass = env.get("CAED_PASSWORD", "92937934153")
    gov_pass = env.get("CNCA_PASSWORD", "1020Nave#")

    logger.info("Iniciando autenticação no CNCA para o usuário %s...", login_user)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.add_init_script('''
            window.MathJax = window.MathJax || {
                Ajax: { config: { path: {} } },
                Hub: { Config: function(){}, Queue: function(){} }
            };
        ''')

        # 1. Carrega a página do CNCA
        logger.info("[1/4] Acessando CNCA...")
        await page.goto("https://criancaalfabetizada.caeddigital.net/#!/login", wait_until="load", timeout=60000)
        await asyncio.sleep(4)

        # 2. Localiza opção de login
        logger.info("[2/4] Abrindo formulário de autenticação...")
        # Procura link ou botão para CAEd
        caed_btn = await page.wait_for_selector("a:has-text('CAEd'), button:has-text('CAEd'), [ng-click*='caed']", timeout=15000)
        await caed_btn.click()
        await asyncio.sleep(2)

        # 3. Preenche usuário e senha
        logger.info("[3/4] Preenchendo credenciais...")
        user_input = await page.wait_for_selector("#username", timeout=15000)
        pass_input = await page.wait_for_selector("#password", timeout=15000)
        submit_btn = await page.wait_for_selector("button[type='submit'], .btn-primary", timeout=15000)

        await user_input.fill("")
        await user_input.type(login_user, delay=20)
        
        # Tenta com a senha CAEd confirmada
        await pass_input.fill("")
        await pass_input.type(caed_pass, delay=20)
        await submit_btn.click()

        # 4. Aguarda área logada
        logger.info("[4/4] Aguardando transição para a área logada...")
        await asyncio.sleep(6)

        current_url = page.url
        page_title = await page.title()
        logger.info("URL pós-login: %s | Título: %s", current_url, page_title)

        # Screenshot do painel
        shot_path = RELATORIOS_DIR / "cnca_dashboard_logado.png"
        await page.screenshot(path=str(shot_path), full_page=True)
        logger.info("[SCREENSHOT] Painel salvo em: %s", shot_path)

        # Captura de cookies e localStorage
        cookies = await context.cookies()
        local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")

        # Extrai links e menus
        links = await page.query_selector_all("a, button, .card, .menu")
        menus_detectados = []
        for l in links:
            t = (await l.inner_text()).strip()
            h = await l.get_attribute("href")
            if t and len(t) > 2 and len(t) < 60:
                menus_detectados.append(f"{t} -> {h or 'action'}")

        # Conteúdo em texto
        body_text = await page.inner_text("body")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        sessao_cnca = {
            "portal": "CNCA - Compromisso Nacional Criança Alfabetizada (CAEd Digital / MEC)",
            "url_final": current_url,
            "titulo": page_title,
            "usuario": login_user,
            "status": "sucesso" if "login" not in current_url.lower() else "verificar",
            "cookies": [{"name": c["name"], "domain": c["domain"], "path": c["path"]} for c in cookies],
            "local_storage_keys": list(local_storage.keys()),
            "local_storage": {k: str(v)[:250] for k, v in local_storage.items()},
            "menus": menus_detectados[:40],
            "linhas_conteudo": lines[:50]
        }

        output_json = RELATORIOS_DIR / "sessao_cnca.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(sessao_cnca, f, indent=2, ensure_ascii=False)
        logger.info("[OK] Sessão salva em %s", output_json)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_cnca())
