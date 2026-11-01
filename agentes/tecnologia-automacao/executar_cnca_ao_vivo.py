#!/usr/bin/env python3
"""
Mapeamento ao Vivo do Portal CNCA (CAEd Digital / MEC)
Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura
Framework Scrapling + Playwright em modo interativo (Headless = False)
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright
from scrapling.parser import Adaptor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("cnca_ao_vivo")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)


async def executar_cnca_ao_vivo():
    logger.info("=" * 80)
    logger.info(">>> INICIANDO PORTAL CNCA EM MODO AO VIVO (INTERATIVO) <<<")
    logger.info("O navegador será aberto na sua tela.")
    logger.info("Você poderá preencher suas credenciais (Gov.br ou CAEd) e resolver qualquer captcha.")
    logger.info("O Scrapling estará monitorando em segundo plano e fará o mapeamento assim que logar.")
    logger.info("=" * 80)

    apis_capturadas = []

    async with async_playwright() as p:
        # Abre o navegador visível (headless=False) preferindo o Google Chrome nativo
        launch_args = [
            "--window-size=1366,850",
            "--window-position=50,50",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check"
        ]

        try:
            logger.info("Tentando abrir com Google Chrome nativo...")
            browser = await p.chromium.launch(channel="chrome", headless=False, args=launch_args)
        except Exception as e:
            logger.warning(f"Google Chrome nativo não disponível ({e}). Usando Chromium do Playwright...")
            browser = await p.chromium.launch(headless=False, args=launch_args)

        context = await browser.new_context(
            viewport={'width': 1366, 'height': 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        page = await context.new_page()
        try:
            await page.bring_to_front()
        except Exception:
            pass

        # Injeta mock de MathJax para evitar crashes do AngularJS
        await page.add_init_script('''
            window.MathJax = window.MathJax || {
                Ajax: { config: { path: {} } },
                Hub: { Config: function(){}, Queue: function(){} },
                typeset: function(){}
            };
        ''')

        # Intercepta respostas de rede para capturar dados de APIs
        async def handle_response(response):
            url = response.url
            if any(term in url for term in ["caeddigital.net", "functions", "version.json", "api"]):
                ct = response.headers.get("content-type", "")
                if "application/json" in ct or "json" in ct:
                    try:
                        data = await response.json()
                        apis_capturadas.append({
                            "url": url,
                            "status": response.status,
                            "data": data
                        })
                    except Exception:
                        pass

        page.on("response", handle_response)

        # 1. Navega até o portal CNCA
        url_cnca = "https://criancaalfabetizada.caeddigital.net/#!/login"
        logger.info(f"Navegando para: {url_cnca}")
        try:
            await page.goto(url_cnca, wait_until="commit", timeout=60000)
        except Exception as e:
            logger.warning(f"Aviso durante navegação inicial: {e}")

        logger.info("\n" + "=" * 80)
        logger.info(">>> NAVEGADOR PRONTO NA SUA TELA <<<")
        logger.info("Por favor, digite seu usuário e senha no navegador aberto.")
        logger.info("Se necessário, clique em 'Entrar com gov.br' e resolva o desafio de segurança.")
        logger.info("Aguardando confirmação de login... (Tempo limite: 10 minutos)")
        logger.info("=" * 80 + "\n")

        # 2. Loop de monitoramento de login
        logado = False
        tempo_inicio = time.time()
        tempo_maximo = 600  # 10 minutos

        while time.time() - tempo_inicio < tempo_maximo:
            await asyncio.sleep(2.5)

            try:
                current_url = page.url
                title = await page.title()
            except Exception:
                continue

            # 1. Deve ter saído das telas de autenticação
            nao_esta_no_login = "#!/login" not in current_url.lower() and "sso.acesso.gov.br" not in current_url.lower()

            # 2. Checa localStorage por tokens de autenticação
            tem_token_ls = False
            try:
                local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
                for k, v in local_storage.items():
                    val_str = str(v)
                    if "sessiontoken" in val_str.lower() or "currentuser" in k.lower() or k.endswith(".usuario"):
                        tem_token_ls = True
                        break
            except Exception:
                local_storage = {}

            # 3. Checa elementos visuais exclusivos de sessão ativa
            tem_botao_sair = False
            tem_nome_usuario = False
            try:
                sair_el = await page.query_selector("a:has-text('Sair'), button:has-text('Sair'), a:has-text('Trocar Perfil'), button:has-text('Trocar Perfil')")
                if sair_el:
                    tem_botao_sair = True
                nome_el = await page.query_selector("button:has-text('EDUARDO'), a:has-text('EDUARDO'), button:has-text('Eduardo'), a:has-text('Eduardo'), .user-name")
                if nome_el:
                    tem_nome_usuario = True
            except Exception:
                pass

            # 4. Checa URL de área interna (Minha Página, Sistema, etc.)
            url_area_interna = any(k in current_url.lower() for k in ["minhapagina", "#!/sistema", "#!/resultados", "#!/avaliacao"])

            if nao_esta_no_login and (tem_token_ls or tem_botao_sair or tem_nome_usuario or url_area_interna):
                logger.info("\n" + "=" * 80)
                logger.info(f"[DETECTADO] Login bem-sucedido confirmado!")
                logger.info(f"URL Atual: {current_url} | Título: {title}")
                logger.info(f"Evidências: Token LS={tem_token_ls}, Botão Sair={tem_botao_sair}, Nome={tem_nome_usuario}, URL={url_area_interna}")
                logger.info("=" * 80 + "\n")
                logado = True
                break
            else:
                restante = int(tempo_maximo - (time.time() - tempo_inicio))
                logger.info(f"Aguardando login no navegador... ({restante}s restantes | URL: {current_url[:65]}...)")

        if not logado:
            logger.error("[TEMPO ESGOTADO] Tempo limite de 10 minutos atingido sem detecção de login.")
            await browser.close()
            return

        # 3. Estabilização e renderização
        logger.info("\n" + "=" * 80)
        logger.info("[SUCESSO] LOGIN CONFIRMADO!")
        logger.info("Aguardando 7 segundos para carregamento dos módulos e renderização dos cards...")
        logger.info("=" * 80 + "\n")
        await asyncio.sleep(7)

        # 4. Captura de tela do Dashboard Principal
        screenshot_path = RELATORIOS_DIR / "cnca_dashboard_aovivo.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"[CAPTURA VISUAL] Screenshot salvo em: {screenshot_path}")

        # 5. Extração de Cookies e Armazenamentos Locais
        cookies = await context.cookies()
        local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
        session_storage = await page.evaluate("() => Object.assign({}, window.sessionStorage)")

        # 6. Extração do HTML completo e Parsing com Scrapling
        page_html = await page.content()
        dump_html_path = RELATORIOS_DIR / "dump_cnca_dashboard.html"
        dump_html_path.write_text(page_html, encoding="utf-8")

        adaptor = Adaptor(page_html)

        # Extração de Cards e Módulos usando Scrapling
        cards_scrapling = []
        for card_el in adaptor.css(".card, .module-card, [class*='card'], .box, .objeto-container, mat-card"):
            txt = card_el.text.strip()
            if txt and len(txt) > 3:
                cards_scrapling.append(txt)

        # Extração de Links e Menus de Navegação
        menus_detectados = []
        for a_el in adaptor.css("a, button, [role='button']"):
            txt = a_el.text.strip()
            href = a_el.attrib.get("href", "")
            if txt and len(txt) > 2 and len(txt) < 80:
                menus_detectados.append({"texto": txt, "href": href})

        # Extração de Tabelas se houver
        tabelas_extraidas = []
        for table_el in adaptor.css("table"):
            headers = [th.text.strip() for th in table_el.css("th")]
            rows = []
            for tr in table_el.css("tr"):
                cells = [td.text.strip() for td in tr.css("td")]
                if cells:
                    rows.append(cells)
            if headers or rows:
                tabelas_extraidas.append({
                    "cabecalhos": headers,
                    "linhas": rows
                })

        # Linhas de texto estruturado
        body_text = await page.inner_text("body")
        linhas_texto = [l.strip() for l in body_text.splitlines() if l.strip()]

        # 7. Estruturação do Relatório de Sessão
        dados_sessao = {
            "portal": "CNCA - Compromisso Nacional Criança Alfabetizada (CAEd Digital / MEC)",
            "url_final": page.url,
            "titulo": await page.title(),
            "data_extracao": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "sucesso_autenticado_ao_vivo",
            "cookies": [{"name": c["name"], "domain": c["domain"], "path": c["path"]} for c in cookies],
            "local_storage_chaves": list(local_storage.keys()),
            "local_storage": {k: (str(v) if len(str(v)) < 1500 else str(v)[:1500] + "...") for k, v in local_storage.items()},
            "session_storage_chaves": list(session_storage.keys()),
            "total_apis_interceptadas": len(apis_capturadas),
            "apis_interceptadas": apis_capturadas,
            "total_cards_detectados": len(cards_scrapling),
            "cards_detectados": cards_scrapling,
            "total_menus_detectados": len(menus_detectados),
            "menus_detectados": menus_detectados[:60],
            "total_tabelas": len(tabelas_extraidas),
            "tabelas": tabelas_extraidas,
            "linhas_texto_dashboard": linhas_texto[:80]
        }

        # Salva o JSON estruturado
        sessao_json_path = RELATORIOS_DIR / "sessao_cnca.json"
        with open(sessao_json_path, "w", encoding="utf-8") as f:
            json.dump(dados_sessao, f, indent=2, ensure_ascii=False)

        dados_completos_path = RELATORIOS_DIR / "dados_completos_cnca.json"
        with open(dados_completos_path, "w", encoding="utf-8") as f:
            json.dump(dados_sessao, f, indent=2, ensure_ascii=False)

        logger.info("\n" + "=" * 80)
        logger.info(f"[CONCLUÍDO] DADOS DO CNCA EXTRAÍDOS COM SUCESSO!")
        logger.info(f"- Dashboard Screenshot: {screenshot_path}")
        logger.info(f"- Dados da Sessão: {sessao_json_path}")
        logger.info(f"- Total de APIs Interceptadas: {len(apis_capturadas)}")
        logger.info(f"- Total de Cards Mapeados: {len(cards_scrapling)}")
        logger.info(f"- Total de Menus Identificados: {len(menus_detectados)}")
        logger.info("=" * 80 + "\n")

        # Mantém a janela aberta por 4 segundos para você conferir a conclusão
        await asyncio.sleep(4)
        await browser.close()
        logger.info("[FINALIZADO] Navegador fechado com êxito.")


if __name__ == "__main__":
    asyncio.run(executar_cnca_ao_vivo())
