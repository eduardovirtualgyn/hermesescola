# Diagnóstico e Integração: Portal SIAM (SEDUC-GO / Programa AlfaMais Goiás)
**Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura**  
**Data da Extração:** 01/11/2026  
**Status da Autenticação:** Autenticado com Sucesso (Token JWT Ativo e Unidade Vinculada)

---

## 1. Dados Institucionais e Perfil de Acesso

- **Usuário Gestor:** Eduardo Rodrigues Gonçalves
- **CPF:** `92937934153`
- **Email Pessoal:** `eduardovirtualgyn@gmail.com`
- **Cargo / Perfil:** **Diretor Escola** (ID: `15`)
- **Unidade Escolar Vinculada:** **52090604 - Escola Mun. Senador Albino Gonçalves Boa Ventura**
- **Regional:** CRE-APARECIDA (ID: `126`)
- **Município:** APARECIDA DE GOIÂNIA (ID: `520301001405`)
- **Sistema Ativo:** **ALFAMAIS** (Sistema de Acompanhamento do Programa AlfaMais Goiás)
- **Token JWT de Sessão:** Armazenado e renovável via `/api/Auth`

---

## 2. Calendário Operacional e Janela de Avaliações (Novembro 2026)

O SIAM disponibiliza o cronograma oficial da SEDUC-GO diretamente no painel da escola:

* **02 a 06 de Novembro:** Realização da Formação Municipal
* **02 a 06 de Novembro:** **Aplicação da Avaliação de Fluência Leitora (Fase 1)**
* **09 a 13 de Novembro:** **Aplicação da Avaliação de Fluência Leitora (Fase 2 / Repescagem)**
* **16 de Novembro:** Prazo Final para envio do Relatório das Formações Municipais

> **Conexão Direta:** Esta janela de avaliação de fluência leitora de novembro é exatamente o que alimenta a plataforma **Bem Comum (CAEd / PARC)**, já autenticada e integrada à Fábrica de Agentes!

---

## 3. Módulos e Recursos Mapeados no SIAM

| Módulo | Endpoint / Rota | Finalidade Institucional | Agentes Responsáveis |
| :--- | :--- | :--- | :--- |
| **Início** | `/inicio` | Painel de comunicados oficiais, vídeos instrutivos e calendário da SEDUC-GO. | **Agente 01 (Coordenação)** |
| **Estudantes** | `/estudantes` | Listagem, enturmação e histórico de aprendizagem dos alunos no programa AlfaMais. | **Agente 02 (Pedagógico)** e **Agente 06 (Dados)** |
| **Escolas** | `/escolas` | Gestão de dados cadastrais, turmas participantes e metas pactuadas da unidade. | **Agente 03 (Secretaria)** |
| **Professores** | `/professores` | Acompanhamento do quadro de professores alfabetizadores e formação continuada. | **Agente 04 (Gestão de Pessoas)** |
| **Acompanhamento** | `/acompanhamento` | Monitoramento em tempo real dos índices de aprendizagem e relatórios formativos. | **Agente 02 (Pedagógico)** e **Agente 06 (Dados)** |
| **Prêmio** | `/premio` | Diretrizes, indicadores e elegibilidade ao Prêmio Leia / Reconhecimento AlfaMais. | **Agente 01 (Coordenação)** e **Agente 02 (Pedagógico)** |
| **Painel** | `/painel` | Dashboards analíticos e relatórios consolidados em nível escolar, municipal e regional. | **Agente 06 (Inteligência de Dados)** |

---

## 4. Integração Técnica

O script [executar_login_siam.py](file:///c:/HERMES%20ESCOLA/agentes/tecnologia-automacao/executar_login_siam.py) executa:
- Autenticação assíncrona contra a API REST do SIAM (`https://siam.educacao.go.gov.br/api/Auth`);
- Captura de token Bearer JWT e injeção automática no `sessionStorage` (`alfaUser`);
- Consulta automatizada das APIs de calendário (`/api/calendario/proximos-eventos`) e escolas (`/api/Escolas`);
- Exportação segura de dados estruturados para [relatorios/sessao_siam.json](file:///c:/HERMES%20ESCOLA/relatorios/sessao_siam.json).
