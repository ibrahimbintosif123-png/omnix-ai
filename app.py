
from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

API_KEY = os.environ.get("OPENAI_API_KEY")

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>OMNIX AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
    background: #101323;
    color: white;
    font-family: Arial;
    text-align: center;
    padding: 20px;
}
h1 { color: #7c83ff; }
#chat {
    max-width: 600px;
    margin: auto;
    text-align: left;
}
input {
    width: 70%;
    padding: 14px;
    border-radius: 10px;
}
button {
    padding: 14px;
    background: #7777ff;
    color: white;
    border: none;
    border-radius: 10px;
}
.message {
    background: #222943;
    padding: 12px;
    margin: 10px 0;
    border-radius: 10px;
}
</style>
</head>
<body>
<h1>OMNIX AI</h1>
<p>Your personal AI assistant</p>
<div id="chat"></div>
<input id="message" placeholder="Ask OMNIX anything...">
<button onclick="sendMessage()">Send</button>
<script>
async function sendMessage() {
    const input = document.getElementById("message");
    const chat = document.getElementById("chat");
    const message = input.value.trim();
    if (!message) return;

    chat.innerHTML += '<div class="message"><b>You:</b> '
        + escapeHTML(message) + '</div>';
    input.value = "";

    const loading = document.createElement("div");
    loading.className = "message";
    loading.textContent = "OMNIX is thinking...";
    chat.appendChild(loading);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });
        const data = await response.json();
        loading.textContent = "OMNIX: " + (data.reply || data.error);
    } catch (error) {
        loading.textContent = "Connection error. Try again.";
    }
}
function escapeHTML(text) {
    return text.replace(/[&<>"']/g, c => ({
        '&':'&amp;', '<':'&lt;', '>':'&gt;',
        '"':'&quot;', "'":'&#39;'
    }[c]));
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    if not API_KEY:
        return jsonify({"error": "AI API key is not configured yet."}), 503

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are OMNIX AI, a helpful assistant."},
                    {"role": "user", "content": message}
                ]
            },
            timeout=60
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": answer})

    except requests.RequestException:
        return jsonify({"error": "AI connection failed. Please try again."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
