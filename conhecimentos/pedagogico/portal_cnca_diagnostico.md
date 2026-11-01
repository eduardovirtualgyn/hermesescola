# Diagnóstico e Integração: Portal CNCA (Compromisso Nacional Criança Alfabetizada)
**Fábrica de Agentes Escolares — E.M. Senador Albino Gonçalves Boaventura**  
**Data da Extração:** 01/11/2026  
**Status da Autenticação:** Mapeado com Redirecionamento Gov.br (Desafio de Segurança Interativo Detectado)

---

## 1. Dados e Estrutura de Acesso ao CNCA

- **Portal:** Compromisso Nacional Criança Alfabetizada (CNCA / MEC / CAEd Digital)
- **URL Oficial:** `https://criancaalfabetizada.caeddigital.net/#!/login`
- **Método de Autenticação Primário:** Login Único Federal (**Gov.br SSO**)
- **Credenciais Mapeadas no `.env`:**
  - `CPF / Usuário:` `92937934153`
  - `Senha Gov.br:` `1020Nave#`

---

## 2. Diagnóstico do Fluxo de Autenticação

A automação executou os seguintes passos:
1. Navegação até `https://criancaalfabetizada.caeddigital.net/#!/login` com injeção de script de compatibilidade para evitar travamentos de carregamento do AngularJS.
2. Identificação e acionamento do botão oficial **"Entrar com gov.br"**.
3. Redirecionamento bem-sucedido para o provedor de identidade federal:
   `https://sso.acesso.gov.br/login?client_id=criancaalfabetizada.caeddigital.net`
4. Preenchimento do CPF (`92937934153`) e acionamento do botão "Continuar".
5. **Detecção de Barreira de Segurança:** O sistema antifraude do Gov.br apresentou um desafio visual interativo (*hCaptcha/Arkose puzzle*: *"Selecione itens que custariam mais dinheiro do que o valor mostrado"*).

---

## 3. Alternativas e Próximos Passos Operacionais

Para concluir a extração contínua dos dados de alfabetização do 1º e 2º anos:

1. **Sessão Compartilhada CAEd (Recomendada):**  
   Os dados de avaliação da fluência leitora e letramento infantil da E.M. Senador Albino Gonçalves Boaventura encontram-se espelhados na plataforma **Bem Comum (PARC / CAEd)**, que já está **100% autenticada e integrada** pela Fábrica de Agentes com a mesma sessão do Diretor Eduardo Rodrigues Gonçalves.
2. **Autenticação em Modo Assistido (`--headed`):**  
   Podemos disparar o script com interface gráfica visível para que o gestor resolva o quebra-cabeça visual do Gov.br uma única vez, capturando os cookies de sessão de longa duração para uso headless nos dias subsequentes.
3. **Importação Direta de Cookie/Token:**  
   Possibilidade de injetar o token de autorização gerado pelo Gov.br diretamente nas requisições do crawler `crawler_caed.py`.
