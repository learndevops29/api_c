from flask import Flask , request , jsonify , redirect , url_for


app =Flask(__name__)

@app.route("/alert", methods=['POST'])
def alerts():
    global data
    data = request.json
    return jsonify(data)
    print(data)
    #return redirect(url_for("display"))

@app.route("/alert_display",methods=["GET"])
def display():
    return jsonify(data)


if __name__ == "__main__":
    context = ( "/opt/controlm/emservertest/custom_scripts/openssl_cert/ctmtest.pem" , "/opt/controlm/emservertest/custom_scripts/openssl_cert/ctmtest.key")
    app.run("manitest.controlm.com", port=8445, ssl_context=context , debug=False )
