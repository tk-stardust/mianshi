@echo off
cd /d %~dp0

if not exist "frontend\dist\index.html" (
    echo ========================================
    echo   首次运行，正在安装依赖和构建前端...
    echo   请耐心等待 3-5 分钟
    echo ========================================
    cd backend
    pip install -r requirements.txt
    cd ..\frontend
    call npm install
    call npm run build
    cd ..
)

echo ========================================
echo   启动服务中...
echo   打开 http://localhost:8000
echo   关闭此窗口即可停止服务
echo ========================================
cd backend
start "" http://localhost:8000
python main.py
pause
