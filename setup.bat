REM ============================================
REM ETAPA 1: CRIAR AMBIENTE VIRTUAL (MELHORADO)
REM ============================================
echo ============================================================
echo [1/6] Verificando ambiente virtual...
echo ============================================================
echo.

REM Verificar se venv já existe
if exist "venv\" (
    echo AVISO: Ambiente virtual ja existe!
    echo.
    echo Opcoes:
    echo   [1] Usar o existente (recomendado)
    echo   [2] Recriar do zero (apaga e cria novo)
    echo   [3] Cancelar
    echo.
    set /p opcao=Escolha uma opcao (1/2/3): 
    
    if "!opcao!"=="1" (
        echo.
        echo OK! Usando ambiente virtual existente.
        echo.
        goto ativar_venv
    )
    
    if "!opcao!"=="2" (
        echo.
        echo Apagando ambiente virtual antigo...
        rmdir /s /q venv
        echo OK! Ambiente apagado.
        echo.
    )
    
    if "!opcao!"=="3" (
        echo.
        echo Instalacao cancelada.
        pause
        exit /b 0
    )
)

REM Criar venv (só se não existe ou foi apagado)
echo Criando ambiente virtual...
python -m venv venv

if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

echo OK! Ambiente virtual criado.
echo.

:ativar_venv
REM Continua com ativação...