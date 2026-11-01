# Diagnóstico e Integração: Portal SAEGO (Avaliação e Monitoramento Goiás / CAEd Digital)
**Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura**  
**Código do Documento:** `DOC-PED-007`  
**Data da Extração:** 01/11/2026  
**Status da Autenticação:** Autenticado com Sucesso (Sessão Parse Ativa e Escola Vinculada)

---

## 1. Dados Institucionais e Perfil de Acesso

- **Usuário Gestor:** Eduardo Rodrigues Gonçalves
- **CPF:** `92937934153`
- **Email:** `eduardovirtualgyn@gmail.com`
- **Cargo / Perfil:** **Diretor Escolar** (ID: `901`)
- **Unidade Escolar Vinculada:** **52090604 - ESCOLA MUNICIPAL SENADOR ALBINO G BOAVENTURA**
- **Regional:** CRE-126 (Aparecida de Goiânia)
- **Município:** APARECIDA DE GOIÂNIA (Código: `5201405` / Estado: `52`)
- **Código do Programa / Registro CAEd:** `1250` (Fonte: `130-goias`)
- **Token de Sessão CAEd:** `r:e1ff4a760c5bfd295008fefdf020b501`

---

## 2. Arquitetura Técnica e Automação

O portal do SAEGO opera sob a arquitetura padronizada da plataforma **CAEd Digital**:
- **Frontend SPA:** AngularJS com UI-Router (`#!/minhapagina`).
- **Backend / BaaS:** Parse Server CAEd (`https://avaliacaoemonitoramentogoias.caeddigital.net/portal/functions/login`).
- **Desafio Técnico Resolvido:** O carregador dinâmico do MathJax com extensão `mhchem` gerava exceção não tratada em ambientes headless/crawler. Injetamos o mock preventivo `window.MathJax = { typeset: () => {} }` antes da navegação, garantindo inicialização 100% íntegra dos serviços AngularJS.
- **Script de Automação:** [executar_login_saego.py](file:///c:/HERMES%20ESCOLA/agentes/tecnologia-automacao/executar_login_saego.py)
- **Evidências Geradas:**
  - [Dashboard Logado](file:///c:/HERMES%20ESCOLA/relatorios/saego_dashboard_logado.png)
  - [Sessão e APIs Estruturadas](file:///c:/HERMES%20ESCOLA/relatorios/sessao_saego.json)

---

## 3. Mapeamento de Módulos e Cards no Painel do Diretor

O dashboard institucional do Diretor Escolar organiza os dados educacionais da E.M. Senador Albino Gonçalves Boaventura em 4 grandes eixos:

| Eixo / Seção | Card / Funcionalidade | Finalidade Pedagógica e Operacional | Agentes Responsáveis |
| :--- | :--- | :--- | :--- |
| **Desenvolvimento Profissional** | *Orientações Pedagógicas* | Ações pedagógicas propostas para subsidiar intervenções focadas nas dificuldades reveladas pelas avaliações. | **Agente 02 (Pedagógico)** |
| **Desenvolvimento Profissional** | *Cadastros* | Consulta a dados administrativos, matrizes e recursos necessários para o planejamento das aplicações. | **Agente 03 (Secretaria)** |
| **SAEGO (Somativas)** | *Organização* | Acesso a instrumentos, cadernos de provas e diretrizes oficiais de aplicação estadual. | **Agente 01 (Coordenação)** |
| **SAEGO (Somativas)** | *Resultados do SAEGO* | Diagnóstico analítico de proficiência em Língua Portuguesa e Matemática (escalas de proficiência e padrões de desempenho). | **Agente 02 (Pedagógico)** e **Agente 06 (Dados)** |
| **SAEGO (Somativas)** | *Interposição de Recursos* | Módulo de protocolo e acompanhamento de contestações ou correções de resultados de estudantes. | **Agente 01 (Coordenação)** |
| **SAEGO (Somativas)** | *Indicadores Contextuais* | Panorama socioeconômico, clima escolar e fatores associados levantados pelos questionários da escola. | **Agente 06 (Inteligência de Dados)** |
| **Avaliações Formativas** | *Organização* | Guias e matrizes para aplicação periódica ao longo dos bimestres. | **Agente 02 (Pedagógico)** |
| **Avaliações Formativas** | *Acompanhamento* | Monitoramento da taxa de participação de cada turma em tempo real para mitigar abstenção. | **Agente 02 (Pedagógico)** e **Agente 03 (Secretaria)** |
| **Fluência em Leitura** | *Organização* | Alocação de professores aplicadores e confirmação logística das turmas do 2º ano. | **Agente 01 (Coordenação)** e **Agente 04 (Gestão Pessoas)** |
| **Fluência em Leitura** | *Resultados* | Classificação de perfis de leitores (Não Leitor, Leitor de Sílabas/Palavras, Leitor de Texto sem Fluência, Leitor Fluente). | **Agente 02 (Pedagógico)** e **Agente 06 (Dados)** |

---

## 4. Articulação Sistêmica no Ecossistema da Escola

Com a autenticação e mapeamento do SAEGO, o ecossistema educacional digital da escola fecha um ciclo completo de inteligência:

```
+----------------------------------------------------------------------------------+
|               ECOSSISTEMA DE DADOS - E.M. SENADOR ALBINO G. BOAVENTURA            |
+----------------------------------------------------------------------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                                                   |
        v                                                                   v
+-----------------------+                                         +-----------------------+
|  GESTÃO LOCAL (GEMUL) |                                         | REDE ESTADUAL (SIAM)  |
| - Matrículas e Censo  |                                         | - Programa AlfaMais   |
| - Notas e Frequência  |                                         | - Janela de Avaliação |
| - Planejamento SAPE   |                                         |   (02 a 13/Nov/2026)  |
+-----------+-----------+                                         +-----------+-----------+
            |                                                                 |
            +-------------------------------+---------------------------------+
                                            |
                                            v
                    +-----------------------------------------------+
                    |       AVALIAÇÕES & PROFICIÊNCIA (CAEd)        |
                    |                                               |
                    | 1. BEM COMUM: Instrumentos da Fluência e Oral |
                    | 2. CNCA: Alinhamento Nacional (Gov.br)        |
                    | 3. SAEGO: Resultados Somativos, Formativos    |
                    |    e Indicadores Contextuais da Escola        |
                    +-----------------------------------------------+
```

1. O **SIAM (SEDUC-GO)** estabelece o cronograma e diretrizes do Programa AlfaMais Goiás.
2. O **Bem Comum (CAEd)** operacionaliza a coleta de áudios e testes de fluência em leitura e matemática oral.
3. O **GEMUL (Aparecida)** fornece a modulação docente, histórico do estudante e consolidação das notas no diário escolar.
4. O **SAEGO (CAEd/SEDUC)** sintetiza os padrões de desempenho estadual, metas de proficiência e questionários contextuais da escola.
