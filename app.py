# ===============================================================
# FILE: app.py
# ===============================================================
import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Thêm migrate để quản lý database dễ hơn

# Lấy Database URL từ biến môi trường, rất quan trọng khi deploy
# Nếu không có, sẽ dùng một file sqlite cục bộ tên là 'dev.db'
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_secret_key_for_development_only')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1) # Render cần thay đổi này
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Khởi tạo migrate

# --- Model (Cấu trúc bảng trong Database) ---
class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    # Thêm cột clicks để đếm lượt truy cập
    clicks = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Url {self.short_code}>"

# --- Chức năng tạo mã ngắn ---
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(length))
        # Dùng SQLAlchemy để kiểm tra
        if not Url.query.filter_by(short_code=short_code).first():
            return short_code

# --- Các Route (đường dẫn) của ứng dụng ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        custom_code = request.form.get('custom_code') # Dùng .get để không bị lỗi nếu bỏ trống

        if not original_url:
            flash('Vui lòng nhập URL cần rút gọn!', 'danger')
            return redirect(url_for('index'))

        short_code = None
        if custom_code:
            # Kiểm tra xem custom_code đã tồn tại chưa
            if Url.query.filter_by(short_code=custom_code).first():
                flash(f"Mã rút gọn '{custom_code}' đã được sử dụng. Vui lòng chọn mã khác.", 'danger')
                return redirect(url_for('index'))
            short_code = custom_code
        else:
            short_code = generate_short_code()

        new_url = Url(original_url=original_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()

        short_url = request.host_url + short_code
        flash('Tạo link rút gọn thành công!', 'success')
        return render_template('index.html', short_url=short_url, original_url=original_url)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_entry = Url.query.filter_by(short_code=short_code).first()

    if url_entry:
        # Tăng số lượt click
        url_entry.clicks += 1
        db.session.commit()
        return redirect(url_entry.original_url)
    else:
        flash(f"URL không tồn tại.", 'danger')
        return redirect(url_for('index'))

# --- Lệnh tùy chỉnh để tạo DB ---
@app.cli.command('create-db')
def create_db_command():
    """Tạo các bảng trong cơ sở dữ liệu."""
    db.create_all()
    print('Database đã được tạo!')

