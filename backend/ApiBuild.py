from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/get-user/<user-id>')
def get_user(user_id):
    user_data = {
        "user_id": user_id,
        "name": "YAH",
        "email": "@gmail.com"
    }
    extra = request.args.get("extra")
    if extra:
        user_data.update(extra)
    return jsonify(user_data), 200



def run_main():
    app.run(debug=True)
