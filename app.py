from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shrikant",
        database="rental_system"
    )

# ---------------- LOGIN MANAGER ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user["id"], user["name"], user["email"], user["role"])
    return None

# ---------------- HOME + SEARCH ----------------
@app.route("/")
def index():

    city = request.args.get("city")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if city:
        cursor.execute("""
        SELECT * FROM properties
        WHERE status='active' AND city LIKE %s
        """,(f"%{city}%",))
    else:
        cursor.execute("""
        SELECT * FROM properties
        WHERE status='active'
        """)

    properties = cursor.fetchall()

    return render_template("index.html", properties=properties, city=city)
# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        cursor.execute(
            "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,%s)",
            (name,email,password,role)
        )
        db.commit()
        flash("Registered Successfully")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor(dictionary=True)

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            login_user(User(user["id"], user["name"], user["email"], user["role"]))

            if user["role"] == "owner":
                return redirect(url_for("owner_dashboard"))
            elif user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("index"))
        else:
            flash("Invalid Credentials")

    return render_template("login.html")

# ---------------- OWNER DASHBOARD ----------------
@app.route("/owner/dashboard")
@login_required
def owner_dashboard():
    if current_user.role != "owner":
        return "Unauthorized"

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM properties WHERE owner_id=%s",(current_user.id,))
    properties = cursor.fetchall()

    return render_template("owner/dashboard.html", properties=properties)

# ---------------- ADD PROPERTY ----------------
@app.route("/owner/add-property", methods=["GET","POST"])
@login_required
def add_property():

    if current_user.role != "owner":
        return "Unauthorized"

    if request.method == "POST":

        db = get_db()
        cursor = db.cursor()

        title = request.form["title"]
        price = request.form["price"]
        deposit = request.form["deposit"]   # FIXED
        city = request.form["city"]
        area = request.form["area"]
        contact_number = request.form["contact_number"]
        map_link = request.form["map_link"]

        cursor.execute("""
        INSERT INTO properties
        (owner_id,title,price,city,area,deposit,contact_number,map_link,status,payment_status)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'pending','pending')
        """,(current_user.id,title,price,city,area,deposit,contact_number,map_link))

        db.commit()

        property_id = cursor.lastrowid

        return redirect(url_for("submit_utr", property_id=property_id))

    return render_template("owner/add_property.html")
# ---------------- SUBMIT UTR ----------------
@app.route("/owner/submit-utr/<int:property_id>", methods=["GET","POST"])
@login_required
def submit_utr(property_id):
    if current_user.role != "owner":
        return "Unauthorized"

    if request.method == "POST":
        utr = request.form["utr"]

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE properties 
            SET utr_number=%s, payment_status='submitted'
            WHERE id=%s AND owner_id=%s
        """,(utr, property_id, current_user.id))

        db.commit()
        flash("UTR Submitted. Wait for Admin Approval.")
        return redirect(url_for("owner_dashboard"))

    return render_template("owner/submit_utr.html", property_id=property_id)
# edit properties
@app.route("/owner/edit-property/<int:id>", methods=["GET","POST"])
@login_required
def edit_property(id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM properties WHERE id=%s AND owner_id=%s",
        (id,current_user.id)
    )

    property = cursor.fetchone()

    if request.method == "POST":

        title = request.form["title"]
        price = request.form["price"]
        deposit = request.form["deposit"]
        city = request.form["city"]
        area = request.form["area"]
        contact_number = request.form["contact_number"]
        map_link = request.form["map_link"]

        cursor.execute("""
        UPDATE properties
        SET title=%s,
            price=%s,
            deposit=%s,
            city=%s,
            area=%s,
            contact_number=%s,
            map_link=%s
        WHERE id=%s AND owner_id=%s
        """,(title,price,deposit,city,area,contact_number,map_link,id,current_user.id))

        db.commit()

        flash("Property updated successfully")

        return redirect(url_for("owner_dashboard"))

    return render_template("owner/edit_property.html", property=property)
# delete properties
@app.route("/owner/delete-property/<int:id>")
@login_required
def delete_property(id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM properties WHERE id=%s AND owner_id=%s",
        (id,current_user.id)
    )

    db.commit()

    flash("Property deleted successfully")

    return redirect(url_for("owner_dashboard"))
# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Unauthorized"

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, u.name 
        FROM properties p 
        JOIN users u ON p.owner_id = u.id
        WHERE p.payment_status IN ('submitted','approved')
        ORDER BY p.created_at DESC
    """)

    properties = cursor.fetchall()

    return render_template("admin/dashboard.html", properties=properties)
# ---------------- APPROVE PROPERTY ----------------
@app.route("/admin/approve/<int:property_id>")
@login_required
def approve_property(property_id):
    if current_user.role != "admin":
        return "Unauthorized"

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE properties 
        SET status='active', payment_status='approved'
        WHERE id=%s
    """,(property_id,))

    db.commit()
    flash("Property Approved Successfully")
    return redirect(url_for("admin_dashboard"))

# ---------------- REJECT PROPERTY ----------------
@app.route("/admin/reject/<int:property_id>")
@login_required
def reject_property(property_id):
    if current_user.role != "admin":
        return "Unauthorized"

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE properties 
        SET status='rejected', payment_status='rejected'
        WHERE id=%s
    """,(property_id,))

    db.commit()
    flash("Property Rejected")
    return redirect(url_for("admin_dashboard"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ---------------- RUN APP ----------------
# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port, debug=True)