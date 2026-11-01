import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("siam_login")

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

async def login_siam():
    env = load_env()
    login_user = env.get("SIAM_USER", "92937934153")
    password = env.get("SIAM_PASSWORD", "1020Manager#")

    logger.info("Iniciando autenticação no SIAM SEDUC-GO para o usuário %s...", login_user)

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

        # Interceptação de respostas de API
        intercepted_apis = []

        async def log_response(res):
            url = res.url
            if any(k in url.lower() for k in ["auth", "login", "usuario", "perfil", "menu", "token", "sessao", "api"]):
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

        # 1. Acesso à página do SIAM
        logger.info("[Passo 1/4] Acessando https://siam.educacao.go.gov.br/login...")
        await page.goto("https://siam.educacao.go.gov.br/login", wait_until="networkidle", timeout=45000)
        await asyncio.sleep(3)

        current_url = page.url
        page_title = await page.title()
        logger.info("URL Inicial: %s | Título: %s", current_url, page_title)

        # Screenshot inicial
        await page.screenshot(path=str(RELATORIOS_DIR / "siam_tela_login.png"), full_page=True)
        logger.info("Screenshot inicial salvo em relatorios/siam_tela_login.png")

        # 2. Inspecionar inputs
        inputs = await page.query_selector_all("input")
        logger.info("Total de inputs na tela: %d", len(inputs))
        user_input = None
        pass_input = None
        for i, inp in enumerate(inputs):
            inp_id = await inp.get_attribute("id")
            inp_type = await inp.get_attribute("type")
            inp_name = await inp.get_attribute("name")
            placeholder = await inp.get_attribute("placeholder")
            logger.info("  Input %d: id=%s, name=%s, type=%s, placeholder=%s", i, inp_id, inp_name, inp_type, placeholder)
            if inp_type in ["text", "tel", "number", "email"] or (placeholder and any(p in placeholder.lower() for p in ["cpf", "usuário", "login"])):
                if not user_input:
                    user_input = inp
            elif inp_type == "password":
                pass_input = inp

        # 3. Preenchimento de credenciais
        if user_input and pass_input:
            logger.info("[Passo 2/4] Preenchendo campos de login e senha...")
            await user_input.fill("")
            await user_input.type(login_user, delay=30)
            await pass_input.fill("")
            await pass_input.type(password, delay=30)
            await asyncio.sleep(1)

            # Localizar botão de submissão
            submit_btn = await page.query_selector("button[type='submit'], input[type='submit'], button:has-text('Entrar'), button:has-text('Acessar'), .btn-primary")
            logger.info("[Passo 3/4] Submetendo credenciais...")
            if submit_btn:
                await submit_btn.click()
            else:
                await pass_input.press("Enter")

            # Aguardar resposta e redirecionamento
            await asyncio.sleep(8)
        else:
            logger.warning("Campos padrão de usuário/senha não identificados de imediato.")

        # 4. Análise da página pós-login
        current_url = page.url
        page_title = await page.title()
        logger.info("[Passo 4/4] URL pós-login: %s | Título: %s", current_url, page_title)

        # Screenshot pós-login
        final_shot = RELATORIOS_DIR / "siam_pos_login.png"
        await page.screenshot(path=str(final_shot), full_page=True)
        logger.info("[SCREENSHOT] Painel salvo em: %s", final_shot)

        # Captura de alertas/erros se houver
        alerts = await page.query_selector_all(".alert, .toast, .swal2-modal, [class*='error'], [class*='alerta']")
        for a in alerts:
            t = (await a.inner_text()).strip()
            if t:
                logger.info("[ALERTA NA TELA] %s", t)

        # Captura de cookies e localStorage
        cookies = await context.cookies()
        local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
        session_storage = await page.evaluate("() => Object.assign({}, window.sessionStorage)")

        # Extração de menus e opções
        links = await page.query_selector_all("a, button, nav, .menu, .sidebar")
        menus_detectados = []
        for l in links:
            t = (await l.inner_text()).strip()
            h = await l.get_attribute("href")
            if t and len(t) > 2 and len(t) < 60:
                menus_detectados.append(f"{t} -> {h or 'button'}")

        body_text = await page.inner_text("body")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        sessao_siam = {
            "portal": "SIAM - Sistema Integrado de Administração da Educação (SEDUC-GO)",
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

        output_json = RELATORIOS_DIR / "sessao_siam.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(sessao_siam, f, indent=2, ensure_ascii=False)
        logger.info("[OK] Sessão do SIAM gravada em: %s", output_json)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_siam())
