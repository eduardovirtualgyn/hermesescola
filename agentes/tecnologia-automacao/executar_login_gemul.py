import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("gemul_ano")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"

async def test_ano():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        logger.info("[1/4] Login inicial...")
        await page.goto("https://gemul-aparecida.com.br/login/index.asp", wait_until="domcontentloaded")
        await page.type("#txtLogin", "eduardo.rodrigues", delay=10)
        await page.type("#txtSenha", "280381", delay=10)
        await page.click("button, input[type='submit']")
        await asyncio.sleep(4)

        logger.info("[2/4] Selecionando unidade: Escola Municipal Senador Albino...")
        target_school = await page.wait_for_selector("text=/albino/i", timeout=15000)
        await target_school.click()
        await asyncio.sleep(4)

        logger.info("[3/4] Página após selecionar escola: %s (Título: %s)", page.url, await page.title())
        await page.screenshot(path=str(RELATORIOS_DIR / "gemul_seleciona_ano.png"), full_page=True)

        body_text = await page.inner_text("body")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]
        logger.info("Conteúdo de selecionaAno.asp:")
        for l in lines[:20]:
            logger.info("  | %s", l)

        # Checar opções de ano letivo (links, botões, selects)
        anos_links = await page.query_selector_all("a, button, select, input[type='radio']")
        logger.info("Total de elementos interativos: %d", len(anos_links))
        
        # Procurar ano 2026 ou o mais recente (2025/2026)
        ano_2026 = await page.query_selector("text=/2026/i")
        ano_recente = ano_2026 or await page.query_selector("text=/2025/i") or await page.query_selector("a[href*='ano']")

        if ano_recente:
            txt = (await ano_recente.inner_text()).strip()
            logger.info("[4/4] Clicando no ano letivo: '%s'...", txt)
            await ano_recente.click()
            await asyncio.sleep(5)

        logger.info("URL no Dashboard do GEMUL: %s", page.url)
        logger.info("Título do Dashboard: %s", await page.title())

        # Screenshot do Dashboard Geral da escola
        dash_shot = RELATORIOS_DIR / "gemul_dashboard_albino.png"
        await page.screenshot(path=str(dash_shot), full_page=True)
        logger.info("[SCREENSHOT] Dashboard final salvo em: %s", dash_shot)

        # Extrair menus principais do GEMUL
        final_body = await page.inner_text("body")
        final_lines = [l.strip() for l in final_body.splitlines() if l.strip()]

        menus_gemul = []
        links = await page.query_selector_all("a[href], .menu a, nav a, ul li a")
        for l in links:
            t = (await l.inner_text()).strip()
            h = await l.get_attribute("href")
            if t and len(t) > 2 and len(t) < 50:
                menus_gemul.append(f"{t} -> {h}")

        cookies = await context.cookies()

        resumo = {
            "sistema": "GEMUL - Sistema de Gestão Educacional Municipal de Aparecida",
            "url_dashboard": page.url,
            "titulo": await page.title(),
            "usuario": "eduardo.rodrigues",
            "escola": "240 - ESCOLA MUNICIPAL SENADOR ALBINO GONÇALVES BOAVENTURA",
            "ano_letivo_selecionado": txt if ano_recente else "padrão",
            "total_cookies": len(cookies),
            "cookies": cookies,
            "menus_disponiveis": menus_gemul[:50],
            "linhas_conteudo": final_lines[:60]
        }

        output_json = RELATORIOS_DIR / "sessao_gemul.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(resumo, f, indent=2, ensure_ascii=False)
        logger.info("[OK] Sessão e mapeamento gravados em: %s", output_json)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ano())
