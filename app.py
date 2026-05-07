import os
import sqlite3
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = Flask(__name__)

# PEGA A CHAVE QUE TU SALVOU NO RENDER
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def criar_banco():
    conn = sqlite3.connect('cunene.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (id INTEGER PRIMARY KEY, categoria TEXT, bairro TEXT, resumo TEXT, telefone TEXT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

criar_banco()

def entender_mensagem(texto):
    prompt = f"""Você é o Cunene Conectado. Analise e retorne SÓ JSON.
    Categorias: AGUA, SAUDE, ESCOLA, URGENTE, PERGUNTA, OUTRO
    Se for oi, ola, tudo bem, retorne categoria PERGUNTA e resumo saudacao.
    Bairros: Naipalala, Central, Ondjiva, Namacunde.
    Mensagem: "{texto}"
    JSON:"""
    try:
        resposta = model.generate_content(prompt)
        return eval(resposta.text)
    except:
        return {"categoria": "OUTRO", "bairro": None, "resumo": texto}

def salvar_reporte(dados, telefone):
    conn = sqlite3.connect('cunene.db')
    c = conn.cursor()
    c.execute("INSERT INTO reportes (categoria, bairro, resumo, telefone) VALUES (?, ?, ?, ?)",
              (dados['categoria'], dados['bairro'], dados['resumo'], telefone))
    conn.commit()
    conn.close()

@app.route("/webhook", methods=['POST'])
def webhook():
    texto = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    resp = MessagingResponse()
    msg = resp.message()

    dados = entender_mensagem(texto)

    if dados['categoria'] == "PERGUNTA" and dados['resumo'] == "saudacao":
        msg.body("🤖 Olá! Tudo bem por aqui 😊\n\nSou o Cunene Conectado. Me fala o problema e o bairro.\nEx: 'Falta água no Naipalala'")
        return str(resp)

    if dados['categoria'] in ['AGUA', 'SAUDE', 'ESCOLA', 'URGENTE']:
        salvar_reporte(dados, from_number)
        msg.body(f"✅ Registo feito!\nCategoria: {dados['categoria']}\nBairro: {dados['bairro'] or 'Não informado'}\n\nObrigado!")
        return str(resp)

    msg.body("Não entendi. Tenta assim:\n'Falta água no bairro Central'")
    return str(resp)

    if __name__ "__main__":
        app.run(debug=True)

