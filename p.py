import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your_secret_key'

# สร้างโฟลเดอร์เก็บรูปถ้ายังไม่มี
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ฟังก์ชัน login (ต้องอยู่หลังการสร้าง app)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # TODO: ตรวจสอบ username/password กับฐานข้อมูล
        # ถ้าสำเร็จให้ redirect ไปหน้า index หรือหน้าอื่น
        return redirect(url_for('index'))
    return render_template('login.html')

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db():
    conn = sqlite3.connect('summary.db')
    conn.row_factory = sqlite3.Row
    return conn

# ฟังก์ชันสร้างตารางถ้ายังไม่มี
def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            image TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS comment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER,
            text TEXT
        )''')


# หน้าแรกเป็นหน้า setting
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("setting.html")

# ฟังก์ชันเพิ่มคอมเมนต์
@app.route("/comment/<int:summary_id>", methods=["POST"])
def comment(summary_id):
    with get_db() as db:
        db.execute("INSERT INTO comment (summary_id, text) VALUES (?, ?)", (summary_id, request.form.get("comment")))
        db.commit()
    return redirect(url_for('index') + f"#post-{summary_id}")

# ฟังก์ชันลบโพสต์ (และคอมเมนต์ในโพสต์นั้น)
@app.route("/delete/<int:summary_id>", methods=["POST"])
def delete(summary_id):
    with get_db() as db:
        db.execute("DELETE FROM summary WHERE id=?", (summary_id,))
        db.execute("DELETE FROM comment WHERE summary_id=?", (summary_id,))
        db.commit()
    flash("ลบโพสต์แล้ว")
    return redirect(url_for('index'))

# ฟังก์ชันดูโพสต์เดียว (สำหรับแชร์)
@app.route("/share/<int:summary_id>")
def share(summary_id):
    with get_db() as db:
        summary = db.execute("SELECT * FROM summary WHERE id=?", (summary_id,)).fetchone()
        comments = db.execute("SELECT * FROM comment WHERE summary_id=?", (summary_id,)).fetchall()
    return render_template("share.html", summary=summary, comments=comments)


# ฟังก์ชัน register (ต้องอยู่ก่อนรันเว็บ)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # รับข้อมูลจากฟอร์ม
        username = request.form['username']
        password = request.form['password']
        # ...บันทึกข้อมูลหรือประมวลผล...
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    # ในระบบจริงควรดึง username/password จาก session/database
    current_username = 'demo_user'
    current_password = 'demo_pass'
    if request.method == 'POST':
        # รับค่าที่ผู้ใช้กรอกมาใหม่
        new_username = request.form['username']
        new_password = request.form['password']
        # TODO: บันทึก username/password ใหม่ลง database หรือ session
        flash('บันทึกการเปลี่ยนแปลงเรียบร้อยแล้ว')
        # แสดงค่าที่เปลี่ยนใหม่
        current_username = new_username
        current_password = new_password
    return render_template('setting.html', current_username=current_username, current_password=current_password)

@app.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('login'))

# เริ่มรันเว็บ
if __name__ == "__main__":
    init_db()
    app.run(port=5002)
