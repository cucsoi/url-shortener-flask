# ===============================================================
# FILE: render-build.sh
# (*** NỘI DUNG ĐÃ ĐƯỢC CẬP NHẬT ***)
# ===============================================================
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Chạy lệnh create-db đã được định nghĩa trong app.py
# để tạo bảng trực tiếp, đơn giản hơn cho việc triển khai ban đầu.
python -m flask create-db
