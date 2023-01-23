from flask import Flask,request,abort,jsonify,session,make_response
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS,cross_origin
from config import  ApplicationConfig
from model import db,user


app = Flask(__name__)

app.config.from_object(ApplicationConfig)
bcrypt = Bcrypt(app)
server_session = Session(app)
CORS(app,supports_credentials=True)
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
         return jsonify({
            "error" :"user unauthorized"

        }),401
    users = user.query.filter_by(id = user_id).first()
    return jsonify({
        "id" : users.id,
        "email" : users.email

    })
@app.route("/register", methods=["post"])
def register_user():
    email = request.json["email"]
    password = request.json["password"]

    user_exists = user.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({
            "error" :"user already Exist"
        })
    hashed_password = bcrypt.generate_password_hash(password)

    new_user = user(email = email, password= hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id" : new_user.id,
        "email" : new_user.email

    })
@app.route("/login", methods = ["post"])

def login_user():
    email = request.json["email"]
    password = request.json["password"]

    users = user.query.filter_by(email=email).first()

    if users is None:
        return jsonify({
            "error" :"user unauthorized"
        }),401
    if not bcrypt.check_password_hash(users.password , password):
        return jsonify({
            "error" :"user unauthorized"
        }),401
    session["user_id"] = users.id

    return jsonify({
        "id" : users.id,
        "email" : users.email

    })
@app.route("/logout", methods =["POST"])
def logout_user():
    session.pop("user_id")
    return "200"

if __name__ == '__main__':
    app.run(debug=True)