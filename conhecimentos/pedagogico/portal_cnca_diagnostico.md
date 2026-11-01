# Diagnóstico e Integração: Portal CNCA (Compromisso Nacional Criança Alfabetizada)
**Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura**  
**Código do Documento:** `DOC-PED-005`  
**Data da Extração:** 01/11/2026  
**Status da Autenticação:** Autenticado com Sucesso (Gov.br SSO / Sessão Ativa / 100% Integrado)

---

## 1. Dados Institucionais e Perfil de Acesso

- **Usuário Gestor:** Eduardo Rodrigues Gonçalves
- **CPF:** `92937934153`
- **Email:** `eduardovirtualgyn@gmail.com`
- **Método de Autenticação:** Login Único Federal (**Gov.br SSO**) validado interativamente
- **Perfis Institucionais Ativos:**
  1. **Diretora ou Diretor Escolar** (Código do Perfil: `1021`)
     - Unidade Escolar Vinculada: `52090604 - ESCOLA MUNICIPAL SENADOR ALBINO GONCALVES BOAVENTURA`
     - Município: APARECIDA DE GOIÂNIA (Código: `5201405` / Estado: `52`)
     - Programa / Rede: `CD_REDE: "3"` | `FL_TEMPO_APRENDER: "1"`
  2. **Professora ou Professor** (Código do Perfil: `1072`)
     - Vínculo: `52090604`
- **Token de Sessão CAEd (Parse Server):** `r:a470229c94bba896ea3a0ff8913c1e5c` (Chave `225-alfabetizacao.usuario`)
- **Object ID Parse:** `1RNKpsdHVJ`

---

## 2. Aviso Oficial Ativo no Painel (Urgência Cadastral)

> **COMUNICADO INSTITUCIONAL DO MEC / CNCA:**  
> *"Atenção: Atualize os dados cadastrais dos estudantes com informações de cor ou raça e pertencimento ao público-alvo da educação especial."*  
> **Ação Imediata:** Acesso à rota `/#!/lista-turmas` para auditoria e regularização junto com o Agente 03 (Secretaria).

---

## 3. Módulos e Recursos Mapeados no Dashboard do CNCA

O dashboard do CNCA organiza o monitoramento da alfabetização da unidade nos seguintes eixos estruturantes:

| Módulo / Recurso | Rota / Endpoint | Finalidade Institucional | Agentes Responsáveis |
| :--- | :--- | :--- | :--- |
| **Cronograma** | `/#!/cronograma` | Acompanhamento do calendário nacional de ações, janelas de aplicação e prazos de lançamento. | **Agente 01 (Coordenação)** |
| **Novidades** | `/#!/novidades` | Informes normativos, diretrizes pedagógicas e comunicados oficiais do MEC. | **Agente 01 (Coordenação)** |
| **Profissionais** | `/#!/profissionais` | Cadastro e credenciamento de profissionais da educação para apoio às avaliações e acompanhamento. | **Agente 04 (Gestão de Pessoas)** |
| **Turmas** | `/#!/lista-turmas` | Consulta e validação das turmas participantes das avaliações formativas e atualização cadastral (raça/cor e educação especial). | **Agente 03 (Secretaria)** |
| **Avaliações** | `/#!/avaliacoes` | Acesso aos testes e materiais instrucionais e lançamento de respostas dos estudantes. | **Agente 02 (Pedagógico)** |
| **Banco de Itens** | `/#!/banco-itens` | Criação de cadernos de atividades alinhados às necessidades específicas das turmas e alunos. | **Agente 02 (Pedagógico)** |
| **Resultados** | `/#!/resultados` | Dados de participação e diagnóstico de proficiência das turmas de 1º e 2º anos nas avaliações formativas. | **Agente 02 (Pedagógico)** e **Agente 06 (Dados)** |
| **Matrizes** | `/#!/matrizes` | Matrizes curriculares e habilidades avaliadas de acordo com a etapa de alfabetização. | **Agente 02 (Pedagógico)** |
| **Monitoramento** | `/#!/monitoramento` | Indicadores de cobertura e engajamento da escola no Compromisso Criança Alfabetizada. | **Agente 06 (Inteligência de Dados)** |
| **Desenvolvimento Profissional** | `/#!/capacitacao` | Cursos e trilhas formativas em avaliação educacional para o corpo docente. | **Agente 02 (Pedagógico)** e **Agente 04 (Gestão de Pessoas)** |
| **Apoio Pedagógico** | `/#!/apoio-pedagogico` | Materiais de intervenção rápida, uso pedagógico dos resultados e boas práticas de alfabetização. | **Agente 02 (Pedagógico)** |

---

## 4. Evidências Técnicas e Artefatos da Sessão

- **Script de Autenticação ao Vivo:** [executar_cnca_ao_vivo.py](file:///c:/HERMES%20ESCOLA/agentes/tecnologia-automacao/executar_cnca_ao_vivo.py)
- **Launcher de Execução Direta:** [abrir_cnca_ao_vivo.bat](file:///c:/HERMES%20ESCOLA/abrir_cnca_ao_vivo.bat)
- **Screenshot de Alta Resolução do Dashboard:** [cnca_dashboard_aovivo.png](file:///c:/HERMES%20ESCOLA/relatorios/cnca_dashboard_aovivo.png)
- **Sessão Estruturada:** [sessao_cnca.json](file:///c:/HERMES%20ESCOLA/relatorios/sessao_cnca.json) (19 chamadas de API capturadas, incluindo `getAgregados` e `getObjetosByView`)
- **Base Completa de Dados:** [dados_completos_cnca.json](file:///c:/HERMES%20ESCOLA/relatorios/dados_completos_cnca.json)
- **Dump do HTML do Painel:** [dump_cnca_dashboard.html](file:///c:/HERMES%20ESCOLA/relatorios/dump_cnca_dashboard.html)
