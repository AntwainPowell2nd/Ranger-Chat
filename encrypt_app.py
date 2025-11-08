from flask import Flask, request, render_template, redirect
import requests 
import random
import os
print("Looking for templates in:", os.path.join(os.getcwd(), "templates")) 
print("Starting encryption app...")
app = Flask(__name__)
API_KEY = "yQNDV9ENX9MBavPq2O0T3cUPZ8I4XZmD"
DECRYPTION_URL = "http://127.0.0.1:8001/decrypt"

chat_log = [] 


# Encryption classes
class Encryption:
    def encrypt(self, plaintext):
        self.plaintext = plaintext
        raise NotImplementedError("Subclasses must implement this method.")

class Atbash(Encryption):
    def encrypt(self, plaintext):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        reverse_alphabet = alphabet[::-1]
        encrypt_map = {alphabet[i]: reverse_alphabet[i] for i in range(len(alphabet))}
        encrypt_map.update({k.upper(): v.upper() for k, v in encrypt_map.items()})
        return ''.join(encrypt_map.get(char, char) for char in plaintext)

class Caesar(Encryption):
    def __init__(self, shift=3):
        self.shift = shift

    def encrypt(self, plaintext):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        encrypt_map = {alphabet[i]: alphabet[(i + self.shift) % 26] for i in range(len(alphabet))}
        encrypt_map.update({k.upper(): v.upper() for k, v in encrypt_map.items()})
        return ''.join(encrypt_map.get(char, char) for char in plaintext)

class Vigenere(Encryption):
    def __init__(self, key="HACKRANGERS"):
        self.key = key.upper()

    def encrypt(self, plaintext):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ciphertext = ""
        key_index = 0
        for char in plaintext:
            if char.isalpha():
                is_upper = char.isupper()
                plain_char = char.upper()
                plain_pos = alphabet.index(plain_char)
                key_pos = alphabet.index(self.key[key_index % len(self.key)])
                encrypted_char = alphabet[(plain_pos + key_pos) % 26]
                ciphertext += encrypted_char if is_upper else encrypted_char.lower()
                key_index += 1
            else:
                ciphertext += char
        return ciphertext
    
# Routes

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        chat_log.clear()
    elif request.method == 'POST':
        msg = request.form['message']
        cipher = random.choice([Atbash(), Caesar(), Vigenere()])
        encrypted = cipher.encrypt(msg)

        # Log messages
        chat_log.append({"type": "sent", "label": "You", "text": encrypted})

        headers = {
            "x-api-key": API_KEY
        }

        payload = {
            "cipher": cipher.__class__.__name__,
            "message": encrypted
        }

        # Send encrypted message to decryption server (but don't display response)
        try:
            res = requests.post(DECRYPTION_URL, headers=headers, json=payload)
            if res.status_code != 200:
                chat_log.append({"type": "received", "label": "Error", "text": f"Decryption failed ({res.status_code})"})
        except requests.exceptions.RequestException as e:
            chat_log.append({"type": "received", "label": "Error", "text": f"Connection error: {str(e)}"})

    return render_template("chat.html", messages=chat_log) 

