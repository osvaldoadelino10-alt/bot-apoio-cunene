import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google import genai
import logging

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
# No Render, configure estas chaves nas 'Environment Variables'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'SUA_CHAVE_AQUI_SE_TESTAR_LOCAL')
client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

def perguntar_ao_gemini(mensagem):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=mensagem,
            config={
                'system_instruction': (
                    "Você é o Assistente Comunitário do Cunene. "
                    "Apoie a população de Ondjiva e arredores com informações úteis. "
                    "Seja direto, educado e use termos locais de Angola."
                )
            }
        )
        return response.text
    except Exception as e:
        logging.error(f"Erro na IA: {e}")
        return "Lamento, estou com uma falha técnica agora. Tente mais tarde."

@app.route("/bot", methods=['POST'])
def bot():
    # O Twilio envia os dados como Form Data, não JSON
    pergunta_usuario = request.values.get('Body', '').lower()
    
    # Processa com a IA
    resposta_ia = perguntar_ao_gemini(pergunta_usuario)

    # Prepara a resposta no formato TwiML
    resp = MessagingResponse()
    resp.message(resposta_ia)

    return str(resp)

if __name__ == "__main__":
    # O Render exige que o bot rode na porta 10000 ou na definida pela variável PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
   

