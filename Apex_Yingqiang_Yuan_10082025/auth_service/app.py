import os
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("AUTH_DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("AUTH_SECRET", "change-me-auth")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

@app.post("/register")
def register():
    data = request.get_json(force=True)
    email = data.get("email","").strip().lower()
    password = data.get("password","")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 409
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "registered"}), 201

@app.post("/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email","").strip().lower()
    password = data.get("password","")
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    token = create_access_token(identity={"id": user.id, "email": user.email})
    return jsonify({"access_token": token})

@app.post("/verify")
@jwt_required()
def verify():
    ident = get_jwt_identity()
    return jsonify({"ok": True, "identity": ident})

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=port)
