import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("gemul_modulos")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CONHECIMENTO_DIR = BASE_DIR / "conhecimentos" / "secretaria"
CONHECIMENTO_DIR.mkdir(parents=True, exist_ok=True)

async def mapear_modulos():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        logger.info("[1/3] Efetuando login e seleção da escola...")
        await page.goto("https://gemul-aparecida.com.br/login/index.asp", wait_until="domcontentloaded")
        await page.type("#txtLogin", "eduardo.rodrigues", delay=10)
        await page.type("#txtSenha", "280381", delay=10)
        await page.click("button, input[type=submit]")
        await asyncio.sleep(4)

        search_input = await page.wait_for_selector("input#busca, input#comboEmpresaInput, input[type=text]", timeout=15000)
        await search_input.click()
        await search_input.type("albino", delay=40)
        await asyncio.sleep(2)

        item = await page.wait_for_selector("text=/ESCOLA MUNICIPAL SENADOR ALBINO/i", timeout=15000)
        await item.click()
        await asyncio.sleep(4)

        logger.info("[2/3] Painel de módulos carregado: %s", page.url)

        # Mapear os 7 cards de módulos
        modulos_detectados = []
        cards = await page.query_selector_all(".card, a, button, div[onclick], div.col-md-2, div.col-sm-4, div.item")
        
        for c in cards:
            txt = (await c.inner_text()).strip()
            onclick = await c.get_attribute("onclick")
            href = await c.get_attribute("href")
            classes = await c.get_attribute("class")
            
            # Filtra os 7 módulos principais conhecidos
            if any(nome in txt for nome in ["Tutoriais", "Acadêmico", "Censo Escolar", "Avap/Atividades", "Matrícula", "Planejamento", "Recursos Humanos"]):
                # Pega a linha principal do nome
                nome_modulo = next(nome for nome in ["Tutoriais", "Acadêmico", "Censo Escolar", "Avap/Atividades", "Matrícula", "Planejamento", "Recursos Humanos"] if nome in txt)
                modulos_detectados.append({
                    "modulo": nome_modulo,
                    "texto_completo": txt,
                    "onclick": onclick,
                    "href": href,
                    "class": classes
                })

        # Remove duplicados mantendo a ordem
        vistos = set()
        modulos_unicos = []
        for m in modulos_detectados:
            if m["modulo"] not in vistos:
                vistos.add(m["modulo"])
                modulos_unicos.append(m)

        logger.info("[3/3] Total de módulos mapeados: %d", len(modulos_unicos))
        for m in modulos_unicos:
            logger.info("  * Módulo: %s | OnClick: %s | Href: %s", m["modulo"], m["onclick"], m["href"])

        # Captura dados de sessão e cookies
        cookies = await context.cookies()

        resultado_gemul = {
            "sistema": "GEMUL - Sistema de Gestão Educacional Municipal de Aparecida",
            "url_painel": page.url,
            "titulo": await page.title(),
            "usuario": "eduardo.rodrigues",
            "nome_completo": "EDUARDO RODRIGUES GONÇALVES",
            "id_usuario": 68,
            "cargo": "DIRETOR(A) - INTEGRAL",
            "matricula": "21057",
            "escola": "ESCOLA MUNICIPAL SENADOR ALBINO G. BOAVENTURA",
            "comunicado_vigente": "Comunicado SAPE nº. 006/2026 - Lançamento de Conteúdo Programático substituído pelo módulo Planejamento",
            "modulos": modulos_unicos,
            "cookies": [{"name": c["name"], "domain": c["domain"], "path": c["path"]} for c in cookies]
        }

        output_file = RELATORIOS_DIR / "sessao_gemul.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado_gemul, f, indent=2, ensure_ascii=False)
        logger.info("[OK] Sessão do GEMUL gravada em: %s", output_file)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(mapear_modulos())
