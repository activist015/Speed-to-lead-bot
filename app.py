from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import re
import urllib.parse
import os

app = Flask(__name__)

# --- ENV VARIABLES ---
TWILIO_SID = os.getenv("AC4679a7b2c777b4a010aecdba8e0bc0f2")
TWILIO_AUTH = os.getenv("d2adce56cd8fd8727af845a6896d2160")
TWILIO_NUMBER = os.getenv("+14156341194")
CONTRACTOR_NUMBER = os.getenv("+2348112699123")

client = Client(TWILIO_SID, TWILIO_AUTH)


# ---------------------------------------------
#  HOME PAGE (optional)
# ---------------------------------------------
@app.route("/")
def home():
    return "Speed-to-Lead Bot is LIVE!"


# ---------------------------------------------
# 1) PARSE EMAIL + CALL CONTRACTOR
# ---------------------------------------------
@app.route("/call-contractor", methods=["POST"])
def call_contractor():

    email_text = request.form.get("email_text", "")

    # --- Extract Name ---
    name_match = re.search(r"Name[:\- ]+\s*(.+)", email_text, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else "New Lead"

    # --- Extract Phone ---
    phone_match = re.search(r"Phone[:\- ]+\s*([\+\d]+)", email_text, re.IGNORECASE)
    phone = phone_match.group(1).strip() if phone_match else ""

    if phone == "":
        return {"error": "No phone number found in email"}, 400

    # --- Encode for URL safety ---
    encoded_name = urllib.parse.quote(name)
    encoded_phone = urllib.parse.quote(phone)

    # --- Use your Railway domain (HTTPS only!) ---
    base_url = "https://speed-to-lead-bot-production.up.railway.app"

    voice_url = f"{base_url}/twilio-voice?name={encoded_name}&phone={encoded_phone}"

    # --- Place call to contractor ---
    call = client.calls.create(
        to=CONTRACTOR_NUMBER,
        from_=TWILIO_NUMBER,
        url=voice_url
    )

    return {"status": "calling", "sid": call.sid}


# ---------------------------------------------
# 2) TWILIO CALL RESPONSE (TTS)
# ---------------------------------------------
@app.route("/twilio-voice", methods=["GET", "POST"])
def twilio_voice():

    name = request.args.get("name", "New Lead")
    phone = request.args.get("phone")

    vr = VoiceResponse()

    # Message the contractor hears
    vr.say(f"You have a new lead from {name}. Press 1 to call them back now.")

    with vr.gather(num_digits=1, action=f"/connect-customer?phone={phone}", method="POST") as g:
        pass

    return Response(str(vr), mimetype="text/xml")


# ---------------------------------------------
# 3) CONNECT CONTRACTOR → CUSTOMER
# ---------------------------------------------
@app.route("/connect-customer", methods=["POST"])
def connect_customer():

    phone = request.args.get("phone")

    vr = VoiceResponse()
    vr.say("Connecting you to the customer now.")
    vr.dial(phone)

    return Response(str(vr), mimetype="text/xml")


# ---------------------------------------------
# RUN FLASK ON RAILWAY
# ---------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
