from flask import Flask, request, jsonify, render_template, redirect, url_for 

app = Flask(__name__)
chat_log = []

API_KEY = "yQNDV9ENX9MBavPq2O0T3cUPZ8I4XZmD"

# Cipher classes
class Atbash:
    def decrypt(self, text):
        alpha = "abcdefghijklmnopqrstuvwxyz"
        rev = alpha[::-1]
        table = {a: r for a, r in zip(alpha, rev)}
        table.update({k.upper(): v.upper() for k, v in table.items()})
        return ''.join(table.get(c, c) for c in text)

class Caesar:
    def __init__(self, shift=-3):
        self.shift = shift
    def decrypt(self, text):
        alpha = "abcdefghijklmnopqrstuvwxyz"
        table = {a: alpha[(i + self.shift) % 26] for i, a in enumerate(alpha)}
        table.update({k.upper(): v.upper() for k, v in table.items()})
        return ''.join(table.get(c, c) for c in text)

class Vigenere:
    def __init__(self, key="HACKRANGERS"):
        self.key = key.upper()
    def decrypt(self, text):
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result, k = "", 0
        for c in text:
            if c.isalpha():
                p = alpha.index(c.upper())
                kp = alpha.index(self.key[k % len(self.key)])
                dec = alpha[(p - kp + 26) % 26]
                result += dec if c.isupper() else dec.lower()
                k += 1
            else:
                result += c
        return result

# Home route to display decrypted messages
@app.route('/')
def home():
    return render_template("decrypt_chat.html", messages=chat_log)
# Decryption API route
@app.route('/decrypt', methods=['POST'])
def decrypt():
    key = request.headers.get('x-api-key')
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    # Accept both form-data and JSON
    if request.is_json:
        cipher = request.json.get('cipher')
        message = request.json.get('message')
    else:
        cipher = request.form.get('cipher')
        message = request.form.get('message')

    if not cipher or not message:
        return jsonify({"error": "Missing cipher or message"}), 400

    if cipher == "Atbash":
        decrypted = Atbash().decrypt(message)
    elif cipher == "Caesar":
        decrypted = Caesar().decrypt(message)
    elif cipher == "Vigenere":
        decrypted = Vigenere().decrypt(message)
    else:
        return jsonify({"error": "Unknown cipher"}), 400

    chat_log.append({"label": cipher, "text": decrypted})
    import requests  # Ensure this is at the top of your file

# Send log to dashboard
    try:
        dashboard_payload = {
            "sender": "Decryptor",
            "receiver": "User",
            "cipher": cipher,
            "message": decrypted
        }
        requests.post("http://127.0.0.1:5002/log", json=dashboard_payload)
    except requests.exceptions.RequestException:
        pass  # Fail silently if dashboard is offline
        return jsonify({"decrypted": decrypted})