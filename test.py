from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/hi', methods=['GET'])
def say_hi():
    return jsonify({"message": "Hi"}), 200

@app.route('/bye', methods=['GET'])
def say_bye():
    return jsonify({"message": "Bye"}), 200

if __name__ == "__main__":
    app.run(debug=True)
