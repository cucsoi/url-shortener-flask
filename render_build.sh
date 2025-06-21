# ===============================================================
# FILE: render-build.sh
# (Script để Render.com tự động chạy khi xây dựng ứng dụng)
# ===============================================================
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

flask db upgrade
