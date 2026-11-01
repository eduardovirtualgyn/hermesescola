import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("extrator_caed")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CONHECIMENTO_DIR = BASE_DIR / "conhecimentos" / "pedagogico"
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
CONHECIMENTO_DIR.mkdir(parents=True, exist_ok=True)

ROTAS_PORTAL = [
    {"nome": "Fluência em Leitura (Organização)", "hash": "#!/avaliacao/1005/organizacao", "slug": "fluencia_organizacao"},
    {"nome": "Matemática (Organização)", "hash": "#!/avaliacao/1007/organizacao", "slug": "matematica_organizacao"},
    {"nome": "Matemática (Acompanhamento)", "hash": "#!/avaliacao/1007/acompanhamento", "slug": "matematica_acompanhamento"},
    {"nome": "Administração - Escolas", "hash": "#!/administracao/escolas", "slug": "adm_escolas"},
    {"nome": "Administração - Profissionais", "hash": "#!/administracao/profissionais", "slug": "adm_profissionais"},
    {"nome": "Desenvolvimento Profissional", "hash": "#!/desenvolvimento-profissional/boas-praticas", "slug": "boas_praticas"}
]

async def extrair():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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

        intercepted_api_calls = []

        async def on_response(res):
            url = res.url
            if any(k in url.lower() for k in ["/portal/functions/", "/parc/v1/", "/api/", "avaliacao", "turma", "resultado", "escola", "aluno"]):
                try:
                    data = await res.json()
                    intercepted_api_calls.append({
                        "url": url,
                        "status": res.status,
                        "data": data
                    })
                    logger.info("API Capturada: %s (Status %s)", url.split("?")[0], res.status)
                except Exception:
                    pass

        page.on("response", on_response)

        logger.info("[1] Autenticando na Plataforma Bem Comum...")
        await page.goto("https://bemcomum.caeddigital.net/#!/login", wait_until="commit", timeout=30000)
        
        user_input = await page.wait_for_selector("#username", timeout=25000)
        pass_input = await page.wait_for_selector("#password", timeout=25000)
        submit_btn = await page.wait_for_selector("button[type='submit'], .btn-primary.float-right", timeout=25000)

        await user_input.type("92937934153", delay=20)
        await pass_input.type("92937934153", delay=20)
        await submit_btn.click()

        # Aguardar chegada em minhapagina
        await asyncio.sleep(6)
        logger.info("Área logada com sucesso: %s", page.url)

        resultados_modulos = {}

        for rota in ROTAS_PORTAL:
            logger.info("Navegando para módulo: %s (%s)...", rota["nome"], rota["hash"])
            target_url = f"https://bemcomum.caeddigital.net/{rota['hash']}"
            await page.evaluate(f"() => location.hash = '{rota['hash']}'")
            await asyncio.sleep(5)

            # Captura screenshot
            shot_file = RELATORIOS_DIR / f"modulo_{rota['slug']}.png"
            await page.screenshot(path=str(shot_file), full_page=True)

            # Extrai tabelas HTML se existirem
            tables = await page.query_selector_all("table")
            extracted_tables = []
            for t in tables:
                rows = await t.query_selector_all("tr")
                table_data = []
                for r in rows:
                    cells = await r.query_selector_all("th, td")
                    cell_texts = [(await c.inner_text()).strip() for c in cells]
                    if any(cell_texts):
                        table_data.append(cell_texts)
                if table_data:
                    extracted_tables.append(table_data)

            # Extrai texto corrido e cards
            body_text = await page.inner_text("body")
            clean_lines = [l.strip() for l in body_text.splitlines() if l.strip() and len(l.strip()) > 2]

            resultados_modulos[rota["slug"]] = {
                "nome": rota["nome"],
                "url": page.url,
                "screenshot": str(shot_file),
                "total_tabelas": len(extracted_tables),
                "tabelas": extracted_tables,
                "resumo_texto": clean_lines[:40]
            }
            logger.info("Módulo %s processado: %d tabelas encontradas.", rota["nome"], len(extracted_tables))

        # Compilação dos dados
        dados_totais = {
            "plataforma": "Associação Bem Comum / PARC (CAEd Digital)",
            "data_extracao": "2026-11-01",
            "usuario": "92937934153",
            "nome_gestor": "EDUARDO RODRIGUES GONCALVES",
            "perfil": "Diretor(a) Escolar",
            "escola": "ESCOLA MUNICIPAL SENADOR ALBINO G BOAVENTURA",
            "codigo_inep": "52090604",
            "municipio": "APARECIDA DE GOIANIA",
            "modulos": resultados_modulos,
            "apis_interceptadas": intercepted_api_calls
        }

        output_json = RELATORIOS_DIR / "dados_completos_bemcomum.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(dados_totais, f, indent=2, ensure_ascii=False)
        logger.info("[OK] Extração total concluída e gravada em %s", output_json)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(extrair())
