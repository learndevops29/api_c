from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/alerts', methods=['POST']) 
def alerts():
    data = request.json
    return jsonify(data)

if __name__ == "__main__":
    app.run()