from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "ACEest Fitness DevOps Project"

@app.route("/programs")
def programs():
    return jsonify({
        "programs": [
            "Fat Loss",
            "Muscle Gain",
            "Beginner"
        ]
    })

@app.route("/health")
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)