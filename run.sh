#!/bin/bash

# Script để chạy hệ thống Multi-Agent

echo "🚀 Khởi động hệ thống Multi-Agent..."

# Thiết lập môi trường
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy. Vui lòng cài đặt Python3."
    exit 1
fi

# Cài đặt dependencies nếu chưa có
if [ ! -d "venv" ]; then
    echo "📦 Tạo virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Chạy ứng dụng
echo "🏥 Khởi động Đội Phản ứng Nhanh Kỹ thuật số..."
python3 src/app.py --interactive
