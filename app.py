"""
Bot WhatsApp com Twilio + OpenAI (Cunene)
Hospedagem: Render
Sem base de dados
"""

import os
import logging
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import openai

# ========== CONFIGURAÇÕES ==========
app = Flask(__name__)

# Variáveis de ambiente (definir no Render)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")  # Ex: whatsa+14155238886
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Inicializar cliente Twilio (para enviar mensagens assíncronas, se necessário)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

# ========== LÓGICA DO BOT ==========

def responder_com_ia(mensagem_usuario):
    """Chama a OpenAI e retorna a resposta."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "És um assistente comunitário para a província do Cunene, Angola. Respondes de forma útil, respeitosa e em português. Se não souberes, dizes que vais pesquisar."},
                {"role": "user", "content": mensagem_usuario}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Erro na IA: {e}")
        return "Desculpa, estou com dificuldades técnicas. Tenta novamente mais tarde."

def processar_mensagem(texto):
    """Processa a mensagem: menu fixo ou IA."""
    texto_lower = texto.lower().strip()

    # Menu fixo (sem gastar IA)
    if texto_lower in ("1", "informações", "cunene"):
        return ("📍 *Sobre a Província do Cunene:*\n\n"
                "Capital: Ondjiva. Região semiárida, conhecida pela cultura Ovambo e projetos de água como o Canal do Cafu.")
    
    if texto_lower in ("2", "saúde", "sintoma"):
        return ("🩺 *Orientador de Saúde (Cunene)*\n\n"
                "• Febre/dores → possível malária. Procure o centro de saúde.\n"
                "• Diarreia → soro caseiro (água, açúcar, sal).\n"
                "• Emergência: Proteção Civil 115.")

    if texto_lower in ("3", "contacto", "ajuda", "emergência"):
        return ("📞 *Contactos de Emergência:*\n"
                "Polícia: 113\n"
                "Ambulância: 115\n"
                "Hospital Geral de Ondjiva: +244 931 000 000 (simulado)")

    # Se não for comando fixo, usar IA para responder a perguntas abertas
    return responder_com_ia(texto)

# ========== ENDPOINT DO WHATSAPP (TWILIO) ==========
@app.route("/whatsapp", methods=["POST"])
def webhook():
    """Recebe mensagens do Twilio e responde."""
    numero_remetente = request.form.get('From', '').replace('whatsapp:', '')
    mensagem_usuario = request.form.get('Body', '')
    
    logging.info(f"Mensagem de {numero_remetente}: {mensagem_usuario}")
    
    # Gerar resposta
    resposta_texto = processar_mensagem(mensagem_usuario)
    
    # Construir resposta TwiML
    response = MessagingResponse()
    response.message(resposta_texto)
    return Response(str(response), mimetype='text/xml'), 200

# ========== INICIAR SERVIDOR ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
