# Diagnóstico e Integração: Portal GEMUL Aparecida de Goiânia
**Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura**  
**Data da Extração:** 01/11/2026  
**Status da Autenticação:** Concluída com Sucesso (Autenticado, Unidade Vinculada e Módulos Mapeados)

---

## 1. Dados Cadastrais e Perfil no GEMUL

- **Gestor:** Eduardo Rodrigues Gonçalves
- **Usuário de Acesso:** `eduardo.rodrigues`
- **ID do Usuário:** `68`
- **Cargo Oficial:** `DIRETOR(A) - INTEGRAL`
- **Matrícula Funcional:** `21057`
- **Unidade Escolar Vinculada:** **Escola Municipal Senador Albino Gonçalves Boaventura** (Código Unidade: `240`)
- **Município:** Aparecida de Goiânia – GO
- **Rede:** Secretaria Municipal de Educação (SME)

---

## 2. Comunicado Oficial Ativo no Sistema

> **Comunicado SAPE nº. 006/2026** (Superintendência de Articulação da Política Educacional):  
> *"A partir de 25/02/2026 a ferramenta de 'Lançamento de Conteúdo Programático' não estará mais disponível, sendo substituída pelo módulo 'Planejamento'. Pedimos que leiam com atenção as orientações do comunicado para o cumprimento dos prazos e fluxo de trabalho."*

---

## 3. Mapeamento dos 7 Módulos Operacionais

O GEMUL organiza a gestão da unidade escolar em 7 módulos principais:

| Módulo | Endpoint / Rota Interna | Finalidade Institucional | Agente Responsável |
| :--- | :--- | :--- | :--- |
| **Acadêmico** | `/app/academico.asp` | Gestão de notas bimestrais, frequências, fechamento de diários de classe, atas de resultados finais e conselho de classe. | **Agente 02 (Pedagógico)** e **Agente 06 (Dados)** |
| **Matrícula** | `/gemul2015/Sistema/MAT/DEFAULT.ASP` | Enturmação de alunos, confirmação de matrículas, transferências recebidas/expedidas e controle de vagas por sala. | **Agente 03 (Secretaria)** |
| **Planejamento** | `/app/planejamento.asp` | Nova ferramenta unificada (SAPE 006/2026) para registro e acompanhamento do planejamento docente e conteúdos pedagógicos. | **Agente 02 (Pedagógico)** |
| **Recursos Humanos** | `/sistema/SRH/default.asp` | Modulação docente, quadro funcional da escola, lotação, faltas, atestados e dados de servidores. | **Agente 04 (Gestão de Pessoas)** |
| **Censo Escolar** | `/login/chaveAcesso.asp` | Chave de acesso e exportação/sincronização de dados da escola para o Educacenso / MEC. | **Agente 03 (Secretaria)** e **Agente 06 (Dados)** |
| **Avap / Atividades** | `/sistema/EAD/DEFAULT.ASP` | Ambiente de atividades complementares e recursos educacionais digitais do município. | **Agente 02 (Pedagógico)** |
| **Tutoriais** | `/app/tutorial.asp` | Manuais de operação, fluxogramas e manuais de preenchimento dos sistemas da SME. | **Agente 07 (Tecnologia e Automação)** |

---

## 4. Fluxo Automatizado de Autenticação

Para garantir a operação contínua e segura da **Fábrica de Agentes**, o script [executar_login_gemul.py](file:///c:/HERMES%20ESCOLA/agentes/tecnologia-automacao/executar_login_gemul.py) realiza:
1. Envio das credenciais via `POST` seguro;
2. Navegação assíncrona para o painel de seleção de unidade (`selecionar_escola.asp`);
3. Preenchimento reativo do campo `#comboEmpresaInput` / busca dinâmica;
4. Seleção imediata de `240 - ESCOLA MUNICIPAL SENADOR ALBINO GONÇALVES BOAVENTURA`;
5. Vinculação do contrato de Direção Integral (`Matrícula 21057`);
6. Manutenção da sessão autenticada via cookies ASP e cabeçalhos oficiais.
