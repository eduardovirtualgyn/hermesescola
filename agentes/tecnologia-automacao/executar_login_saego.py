import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("saego_login")

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

async def login_saego():
    env = load_env()
    login_user = env.get("SAEGO_USER", "92937934153")
    password = env.get("SAEGO_PASSWORD", "92937934153")

    logger.info("Iniciando autenticação no SAEGO para o usuário %s...", login_user)

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

        intercepted_apis = []

        async def log_response(res):
            url = res.url
            if any(k in url.lower() for k in ["/portal/functions/", "auth", "login", "usuario", "perfil", "menu", "escola", "avaliacao", "saego", "token"]):
                try:
                    data = await res.json()
                    intercepted_apis.append({
                        "url": url,
                        "status": res.status,
                        "data": data
                    })
                    logger.info("API Interceptada: %s (Status %s)", url.split("?")[0], res.status)
                except Exception:
                    pass

        page.on("response", log_response)

        # 1. Carrega a tela de login do SAEGO
        logger.info("[Passo 1/4] Acessando https://avaliacaoemonitoramentogoias.caeddigital.net/#!/login...")
        await page.goto("https://avaliacaoemonitoramentogoias.caeddigital.net/#!/login", wait_until="load", timeout=60000)
        await asyncio.sleep(4)

        current_url = page.url
        page_title = await page.title()
        logger.info("URL Inicial: %s | Título: %s", current_url, page_title)

        await page.screenshot(path=str(RELATORIOS_DIR / "saego_tela_login.png"), full_page=True)

        # 2. Localiza campos de login
        logger.info("[Passo 2/4] Localizando e preenchendo campos de credenciais...")
        user_input = await page.wait_for_selector("#username, input[type='text'], input[placeholder*='Usuário']", timeout=20000)
        pass_input = await page.wait_for_selector("#password, input[type='password'], input[placeholder*='Senha']", timeout=20000)
        submit_btn = await page.wait_for_selector("button[type='submit'], input[type='submit'], .btn-primary, button:has-text('ENTRAR'), button:has-text('Entrar')", timeout=20000)

        await user_input.fill("")
        await user_input.type(login_user, delay=20)
        await pass_input.fill("")
        await pass_input.type(password, delay=20)
        await asyncio.sleep(1)

        # 3. Submissão
        logger.info("[Passo 3/4] Clicando em ENTRAR...")
        await submit_btn.click()

        # 4. Aguardar redirecionamento e carregamento da área logada
        logger.info("[Passo 4/4] Aguardando transição para a área autenticada...")
        await asyncio.sleep(8)

        current_url = page.url
        page_title = await page.title()
        logger.info("URL pós-login: %s | Título: %s", current_url, page_title)

        # Screenshot pós-login
        final_shot = RELATORIOS_DIR / "saego_dashboard_logado.png"
        await page.screenshot(path=str(final_shot), full_page=True)
        logger.info("[SCREENSHOT] Painel salvo em: %s", final_shot)

        # Captura de alertas se houver
        alerts = await page.query_selector_all(".alert, .toast, .swal2-modal, [class*='error']")
        for a in alerts:
            t = (await a.inner_text()).strip()
            if t:
                logger.info("[ALERTA NA TELA] %s", t)

        # Captura de cookies e storages
        cookies = await context.cookies()
        local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
        session_storage = await page.evaluate("() => Object.assign({}, window.sessionStorage)")

        # Menus e links
        links = await page.query_selector_all("a, button, nav, .menu")
        menus_detectados = []
        for l in links:
            t = (await l.inner_text()).strip()
            h = await l.get_attribute("href")
            if t and len(t) > 2 and len(t) < 60:
                menus_detectados.append(f"{t} -> {h or 'button'}")

        # Conteúdo em texto
        body_text = await page.inner_text("body")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        sessao_saego = {
            "portal": "SAEGO - Sistema de Avaliação Educacional do Estado de Goiás (CAEd Digital)",
            "url_final": current_url,
            "titulo": page_title,
            "usuario": login_user,
            "status": "sucesso" if "login" not in current_url.lower() else "verificar",
            "cookies": [{"name": c["name"], "domain": c["domain"], "path": c["path"]} for c in cookies],
            "local_storage_keys": list(local_storage.keys()),
            "local_storage": {k: str(v)[:250] for k, v in local_storage.items()},
            "session_storage_keys": list(session_storage.keys()),
            "apis_interceptadas": intercepted_apis,
            "menus": menus_detectados[:40],
            "linhas_conteudo": lines[:50]
        }

        output_json = RELATORIOS_DIR / "sessao_saego.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(sessao_saego, f, indent=2, ensure_ascii=False)
        logger.info("[OK] Sessão do SAEGO salva em %s", output_json)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_saego())
