@echo off
REM === Paso 1: Eliminar entorno virtual si existe ===
IF EXIST env (
    echo Eliminando entorno virtual anterior...
    rmdir /s /q env
)

REM === Paso 2: Crear nuevo entorno virtual con Python 3.10 ===
echo Creando nuevo entorno virtual con Python 3.10...
py -3.10 -m venv env

REM === Paso 3: Activar el entorno virtual ===
echo Activando entorno virtual...
call env\Scripts\activate.bat

REM === Paso 4: Instalar dependencias desde requirements.txt ===
echo Instalando dependencias...
pip install -r requirements.txt

echo -----------------------------------------
echo ✅ Entorno virtual restaurado exitosamente
echo Usa el comando: call env\Scripts\activate.bat
echo para activar el entorno antes de correr tu app.
echo -----------------------------------------
pause
