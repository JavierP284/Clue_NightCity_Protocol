@echo off
echo Verificando Python...

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python no esta instalado. Por favor, instala Python desde https://www.python.org/downloads/
    pause
    exit /b
)

echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install pillow

echo Instalacion completa.
pause
