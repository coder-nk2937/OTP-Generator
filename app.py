from flask import Flask, request, render_template_string, redirect, url_for, flash
import secrets
import time
import os

app = Flask(__name__)
# allow overriding secret in env (for Vercel production)
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(16))

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 30

# NOTE: In-memory store; not suitable for production on serverless platforms.
otp_store = {}

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>OTP Generator & Validator</title>
    <style>
        body {font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0;}
        .container {width: 420px; background: white; padding: 20px 25px; margin: 60px auto; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.1);}
        h2 {margin-top: 0; text-align: center; color: #333;}
        label {font-weight: bold; color: #444;}
        input {width: 100%; padding: 8px 10px; margin: 6px 0 14px; border-radius: 5px; border: 1px solid #ccc;}
        button {width: 100%; padding: 10px; background: #4A90E2; border: none; border-radius: 5px; color: white; font-size: 16px; cursor: pointer; margin-bottom: 15px;}
        button:hover {background: #357ABD;}
        .msg {padding: 10px; border-radius: 5px; margin-top: 10px; background: #e7f3ff; border-left: 4px solid #4A90E2;}
        hr {margin: 25px 0;}
        .small {font-size: 13px; color:#666; text-align:center;}
    </style>
</head>
<body>
<div class="container">
    <h2>OTP Generator & Validator</h2>
    <p class="small">Expires in {{ expiry }} seconds</p>

    <form action="{{ url_for('generate') }}" method="post">
        <label>Identifier (email or phone)</label>
        <input name="identifier" required placeholder="you@example.com or +911234567890">
        <button type="submit">Generate OTP</button>
    </form>

    <hr>

    <form action="{{ url_for('validate') }}" method="post">
        <label>Identifier</label>
        <input name="identifier" required>

        <label>Enter OTP</label>
        <input name="otp" required maxlength="{{ length }}" placeholder="123456">

        <button type="submit">Validate OTP</button>
    </form>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for msg in messages %}
          <div class="msg">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
</div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, expiry=OTP_EXPIRY_SECONDS, length=OTP_LENGTH)

@app.route("/generate", methods=["POST"])
def generate():
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Please enter a valid identifier.")
        return redirect(url_for("index"))

    otp = "".join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))
    ts = time.time()
    otp_store[identifier] = {"otp": otp, "ts": ts}

    # For demo only: flash OTP. In production send via SMS/email.
    flash(f"OTP for {identifier}: {otp} (valid for {OTP_EXPIRY_SECONDS} seconds)")
    return redirect(url_for("index"))

@app.route("/validate", methods=["POST"])
def validate():
    identifier = request.form.get("identifier", "").strip()
    otp_input = request.form.get("otp", "").strip()

    if not identifier or not otp_input:
        flash("Both fields are required.")
        return redirect(url_for("index"))

    record = otp_store.get(identifier)
    if not record:
        flash("No OTP found for this identifier. Generate one first.")
        return redirect(url_for("index"))

    if time.time() - record["ts"] > OTP_EXPIRY_SECONDS:
        otp_store.pop(identifier, None)
        flash("OTP expired. Generate a new one.")
        return redirect(url_for("index"))

    if otp_input == record["otp"]:
        otp_store.pop(identifier, None)
        flash("OTP validation successful.")
    else:
        flash("Invalid OTP. Try again.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))