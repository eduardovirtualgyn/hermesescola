# Diagnóstico e Integração: Plataforma Bem Comum (CAEd Digital / PARC)
**Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura**  
**Data da Extração:** 01/11/2026  
**Status da Autenticação:** Concluída com Sucesso (Status 200)

---

## 1. Dados Institucionais e Perfil de Acesso

- **Usuário Gestor:** Eduardo Rodrigues Gonçalves
- **CPF / Login:** `92937934153`
- **Perfil de Atuação:** Diretor(a) Escolar (ID: `1021`)
- **Unidade Escolar Vinculada:** Escola Municipal Senador Albino Gonçalves Boaventura
- **Código INEP / Censo:** `52090604`
- **Município:** Aparecida de Goiânia – GO (Código IBGE: `5201405`)
- **Regional de Ensino:** Coordenação Regional de Educação de Aparecida de Goiânia (ID: `13330100000102`)
- **Código da Rede:** `13081680200000002`

---

## 2. Arquitetura Técnica do Portal

- **Framework Web:** Single Page Application (SPA) em AngularJS com UI-Router (`#!/minhapagina`).
- **Backend / APIs:** Parse Server CAEd (`https://bemcomum.caeddigital.net/portal/functions/` e `https://api.caeddigital.net/parc/v1/`).
- **Autenticação:** Token de sessão REST (`sessionToken`) armazenado em `localStorage` sob a chave `168-parc.usuario`.
- **Desafios Superados pelo Scraper:**
  - Tratamento do MathJax inline para evitar travamento da compilação do AngularJS.
  - Seletores precisos (`#username`, `#password`, `button[type="submit"]`).
  - Navegação assíncrona tolerante a requisições de terceiros via `wait_until='commit'`.

---

## 3. Módulos e Funcionalidades Mapeadas

### A. Avaliações da Fluência em Leitura
- **Objetivo:** Identificar o padrão de fluência leitora de cada estudante (leitor fluente, leitor iniciante, não leitor) e apoiar intervenções de alfabetização na idade certa.
- **Recursos Disponíveis:**
  - Cadernos de testes oficiais.
  - Instrumentos de aplicação e registro.
  - Manuais e guias de orientação para aplicadores.
- **Rota no Portal:** `#!/avaliacao/1005/organizacao`

### B. Avaliações Orais de Matemática
- **Objetivo:** Aferir habilidades matemáticas orais e consolidação de competências numéricas do 1º ano do Ensino Fundamental.
- **Recursos Disponíveis:**
  - Organização da aplicação e cadernos.
  - Painel de Acompanhamento e sincronização dos áudios das avaliações orais.
- **Rota no Portal:** `#!/avaliacao/1007/acompanhamento`

### C. Gestão Administrativa
- **Escolas:** Visualização do cadastro da unidade e vínculo com a rede municipal.
- **Profissionais:** Acompanhamento do quadro de professores e aplicadores habilitados.
- **Rota no Portal:** `#!/administracao/profissionais` e `#!/administracao/escolas`

### D. Desenvolvimento Profissional
- Ações pedagógicas propostas e banco de boas práticas para superar dificuldades detectadas nos diagnósticos.

---

## 4. Próximos Passos na Fábrica de Agentes

1. **Agente 02 (Pedagógico):** Incorporar os instrumentos de fluência leitora e matemática às pautas de planejamento e formação continuada.
2. **Agente 06 (Inteligência de Dados):** Integrar os relatórios de sincronização e diagnósticos do PARC às planilhas da escola e ao cruzamento com notas do GEMUL.
3. **Agente 07 (Tecnologia e Automação):** Monitorar periodicamente novas janelas de avaliação através do crawler automatizado (`agentes/tecnologia-automacao/crawler_caed.py`).
