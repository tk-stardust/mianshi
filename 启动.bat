@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 创建虚拟环境（首次）
if not exist ".venv\Scripts\python.exe" (
    echo ========================================
    echo   正在创建虚拟环境...
    echo ========================================
    python -m venv .venv
)

:: 激活虚拟环境
call "%CD%\.venv\Scripts\activate.bat"

if not exist "%CD%\frontend\dist\index.html" (
    echo ========================================
    echo   首次运行，正在安装依赖和构建前端...
    echo   请耐心等待 3-5 分钟
    echo ========================================
    pip install -r "%CD%\backend\requirements.txt"
    cd /d "%CD%\frontend"
    call npm install
    call npm run build
    cd /d "%CD%\.."
)

echo ========================================
echo   启动服务中...
echo   打开 http://localhost:8000
echo   关闭此窗口即可停止服务
echo ========================================
cd /d "%CD%\backend"
start "" http://localhost:8000
python main.py
pause
