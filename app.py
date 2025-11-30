from flask import Flask, request, Response
from twilio.rest import Client
from email_parser import parse_lead_email

# -----------------------------
# CONFIG — replace with your credentials
# -----------------------------
TWILIO_ACCOUNT_SID = "AC4679a7b2c777b4a010aecdba8e0bc0f2"
TWILIO_AUTH_TOKEN  = "d2adce56cd8fd8727af845a6896d2160"
TWILIO_NUMBER      = "+14156341194"      # Your Twilio number
CONTRACTOR_PHONE   = "+2348112699123"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)

# -----------------------------
# Route to receive a new lead (simulate email)
# -----------------------------
@app.route("/call-contractor", methods=["POST"])
def call_contractor():
    # Get email text from POST request
    email_text = request.form.get("email_text")
    
    name, phone = parse_lead_email(email_text)

    if not phone:
        return {"status": "error", "message": "No customer phone found"}, 400

    # Call contractor
    contractor_call = client.calls.create(
        to=CONTRACTOR_PHONE,
        from_=TWILIO_NUMBER,
        url=f"{request.url_root}twilio-voice?name={name}&phone={phone}"
    )

    return {"status": "calling", "lead_name": name, "lead_phone": phone}

# -----------------------------
# Twilio voice instructions for contractor
# -----------------------------
@app.route("/twilio-voice", methods=["POST"])
def twilio_voice():
    name = request.args.get("name")
    phone = request.args.get("phone")

    response = f"""
    <Response>
        <Say voice="alice">New lead from {name}. Press 1 to call them now.</Say>
        <Gather action="{request.url_root}call-customer?phone={phone}" numDigits="1" timeout="5"/>
    </Response>
    """
    return Response(response, mimetype="text/xml")

# -----------------------------
# When contractor presses 1 → call customer
# -----------------------------
@app.route("/call-customer", methods=["POST"])
def call_customer():
    digit = request.form.get("Digits")
    phone = request.args.get("phone")

    if digit == "1":
        client.calls.create(
            to=phone,
            from_=TWILIO_NUMBER,
            url=f"{request.url_root}connect"
        )

    return "<Response><Say>Done.</Say></Response>"

# -----------------------------
# Connecting contractor and customer
# -----------------------------
@app.route("/connect", methods=["POST"])
def connect():
    return """
    <Response>
        <Say voice="alice">Connecting you now.</Say>
    </Response>
    """

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)