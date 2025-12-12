from flask import Flask, request, render_template_string, redirect, url_for, flash
import secrets, time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 30

otp_store = {}

HTML_TEMPLATE = """<!doctype html>
<html><body><h2>OTP App</h2></body></html>"""  # shortened template for packaging demo

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    identifier = request.form.get("identifier","").strip()
    otp = "".join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))
    otp_store[identifier] = {"otp": otp, "ts": time.time()}
    return {"otp": otp, "expires_in": OTP_EXPIRY_SECONDS}

@app.route("/validate", methods=["POST"])
def validate():
    data = request.form
    identifier = data.get("identifier","").strip()
    otp_input = data.get("otp","").strip()
    record = otp_store.get(identifier)
    if not record:
        return {"ok": False}
    if time.time() - record["ts"] > OTP_EXPIRY_SECONDS:
        return {"ok": False, "error":"expired"}
    return {"ok": otp_input == record["otp"]}

if __name__ == "__main__":
    app.run(debug=True)
