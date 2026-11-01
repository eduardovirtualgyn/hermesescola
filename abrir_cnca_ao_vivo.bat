@echo off
title Autenticacao CNCA - Fabrica de Agentes Escolares
cls
echo =====================================================================
echo    FABRICA DE AGENTES ESCOLARES - E.M. SENADOR ALBINO G. BOAVENTURA
echo    Autenticacao ao Vivo no Portal CNCA (CAEd Digital / Gov.br)
echo =====================================================================
echo.
echo Abrindo o navegador para voce realizar o login...
echo O Scrapling ira mapear e extrair os dados assim que voce entrar!
echo.
cd /d "c:\HERMES ESCOLA"
python "agentes\tecnologia-automacao\executar_cnca_ao_vivo.py"
echo.
echo =====================================================================
echo Processo finalizado! Pressione qualquer tecla para fechar.
pause
