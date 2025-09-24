@echo off
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo Iniciando backend Tooli-IA...
cd agent
python tooli-core.py

pause