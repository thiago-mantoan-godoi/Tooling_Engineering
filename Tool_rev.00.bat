@echo off
REM Ativa o ambiente virtual
call C:\Projetos\Tool\.venv\Scripts\activate.bat
"C:\Users\tgodoi01\AppData\Local\Programs\Python\Python313\Scripts\uv.exe" run "C:\Projetos\Tool\Engineering.py"
pause
