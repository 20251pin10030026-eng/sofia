@echo off
echo ========================================
echo  TESTE DE BIBLIOTECAS - SOFIA
echo ========================================
echo.

echo Testando PyPDF2...
D:\A.I_GitHUB\.venv\Scripts\python.exe -c "import PyPDF2; print('  [OK] PyPDF2 versao:', PyPDF2.__version__)" 2>nul || echo   [ERRO] PyPDF2 nao encontrado!

echo Testando Pillow...
D:\A.I_GitHUB\.venv\Scripts\python.exe -c "import PIL; print('  [OK] Pillow disponivel')" 2>nul || echo   [ERRO] Pillow nao encontrado!

echo Testando pytesseract...
D:\A.I_GitHUB\.venv\Scripts\python.exe -c "import pytesseract; print('  [OK] pytesseract disponivel')" 2>nul || echo   [ERRO] pytesseract nao encontrado!

echo Testando numpy...
D:\A.I_GitHUB\.venv\Scripts\python.exe -c "import numpy; print('  [OK] numpy versao:', numpy.__version__)" 2>nul || echo   [ERRO] numpy nao encontrado!

echo.
echo ========================================
echo  TESTE COMPLETO!
echo ========================================
echo.
echo Se todas as bibliotecas estao [OK], reinicie o servidor:
echo   1. Ctrl+C para parar o servidor
echo   2. python api.py para reiniciar
echo.
pause
