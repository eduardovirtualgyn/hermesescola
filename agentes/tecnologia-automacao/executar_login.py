import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Previne crash do script inline caso cdnjs demore a responder
        await page.add_init_script('''
            window.MathJax = window.MathJax || {
                Ajax: { config: { path: {} } },
                Hub: { Config: function(){}, Queue: function(){} }
            };
        ''')

        intercepted_responses = []

        async def log_response(res):
            url = res.url
            status = res.status
            if any(term in url.lower() for term in ["auth", "login", "usuario", "perfil", "menu", "escola", "municipio", "token", "sessao", "api", "turma"]):
                try:
                    data = await res.json()
                    intercepted_responses.append({
                        "url": url,
                        "status": status,
                        "data": data
                    })
                    print(f"[API RESPONSE {status}] {url}")
                except Exception:
                    pass

        page.on("response", log_response)
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}") if msg.type in ["error", "warn"] else None)

        print("[1/5] Acessando tela de login...")
        await page.goto("https://bemcomum.caeddigital.net/#!/login", wait_until="commit", timeout=30000)

        print("[2/5] Aguardando elementos do formulário de autenticação...")
        user_input = await page.wait_for_selector("#username", timeout=25000)
        pass_input = await page.wait_for_selector("#password", timeout=25000)
        submit_btn = await page.wait_for_selector("button[type='submit'], button[ng-click='login()'], .btn-primary.float-right", timeout=25000)

        if not user_input or not pass_input or not submit_btn:
            print("[ERRO] Elementos de login não encontrados!")
            return

        print("[3/5] Preenchendo credenciais...")
        await user_input.fill("")
        await user_input.type("92937934153", delay=30)
        await pass_input.fill("")
        await pass_input.type("92937934153", delay=30)
        await asyncio.sleep(1)

        print("[4/5] Clicando em ENTRAR...")
        await submit_btn.click()

        print("[5/5] Aguardando autenticação e redirecionamento...")
        # Aguarda 8 segundos para processamento e navegação
        await asyncio.sleep(8)

        current_url = page.url
        page_title = await page.title()
        print(f"\n[SUCESSO] URL Pós-Login: {current_url}")
        print(f"[SUCESSO] Título da Página: {page_title}")

        # Captura mensagens de erro/alerta se houver
        alerts = await page.query_selector_all(".alert, .toast-message, .error, .ui-notification, .swal2-modal")
        for a in alerts:
            txt = (await a.inner_text()).strip()
            if txt:
                print(f"[ALERTA NA TELA] {txt}")

        # Captura tokens no localStorage/sessionStorage
        local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
        session_storage = await page.evaluate("() => Object.assign({}, window.sessionStorage)")
        cookies = await context.cookies()

        print(f"\nLocalStorage ({len(local_storage)} chaves): {list(local_storage.keys())}")
        print(f"SessionStorage ({len(session_storage)} chaves): {list(session_storage.keys())}")
        print(f"Cookies capturados: {len(cookies)}")

        # Salva screenshot da tela após o login
        screenshot_path = Path("relatorios") / "tela_pos_login_bemcomum.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"[SCREENSHOT] Salvo em {screenshot_path}")

        # Extrai links e botões visíveis
        links = await page.query_selector_all("a[href], button")
        menus_detectados = []
        for l in links:
            txt = (await l.inner_text()).strip()
            href = await l.get_attribute("href")
            if txt and len(txt) > 2:
                menus_detectados.append(f"{txt} -> {href or 'button'}")

        print("\n--- MENUS E OPÇÕES DETECTADOS ---")
        for m in menus_detectados[:25]:
            print("  *", m)

        # Extrai conteúdo textual
        body_text = await page.inner_text("body")
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]

        # Grava os dados da sessão autenticada em arquivo JSON
        resultado_final = {
            "usuario": "92937934153",
            "url_pos_login": current_url,
            "titulo": page_title,
            "local_storage": local_storage,
            "session_storage": session_storage,
            "cookies": cookies,
            "menus": menus_detectados,
            "apis_capturadas": intercepted_responses,
            "linhas_texto": lines[:100]
        }
        output_file = Path("relatorios") / "sessao_bemcomum.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Sessão e dados salvos em {output_file}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(login())
