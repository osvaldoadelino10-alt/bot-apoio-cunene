from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Configurações da Meta
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

def enviar_mensagem_oficial(numero_destino, texto):
    """Envia mensagem de texto via API Cloud Oficial do WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def enviar_para_administracao(numero_cidadao, texto_reportagem):
    """
    Simula o envio em tempo real dos dados para a Administração Municipal.
    No TCC, podes explicar que isto dispara uma API para o sistema interno deles
    ou envia um e-mail/alerta estruturado para os técnicos da administração.
    """
    print("\n=======================================================")
    print(f"🚨 PROTOCOLO ENVIADO PARA A ADMINISTRAÇÃO MUNICIPAL 🚨")
    print(f"Origem do Cidadão: {numero_cidadao}")
    print(f"Relato do Problema: {texto_reportagem}")
    print("=======================================================\n")
    # Aqui futuramente entraria um requests.post("https://api.administracaocunene.gov.ao/reportagens", ...)

def processar_cerebro_do_bot(numero, texto_usuario):
    """Lógica principal com os novos fluxos de Saúde, Contactos e Administração"""
    texto_minusculo = texto_usuario.lower().strip()
    
    # ----------------------------------------------------
    # MENU 1: Informações Gerais sobre o Cunene
    # ----------------------------------------------------
    if texto_minusculo == "1" or "cunene" in texto_minusculo:
        resposta = (
            "📍 *Sobre a Província do Cunene:*\n\n"
            "Situada no sul de Angola, a sua capital é Ondjiva. É conhecida pela sua forte "
            "cultura pastoral tradicional e pela resiliência do seu povo face às secas cíclicas. "
            "Projetos estruturantes como o Canal do Cafu ajudam a mitigar a escassez de água na região."
        )

    # ----------------------------------------------------
    # MENU 2: Envio de Reportagem para a Administração
    # ----------------------------------------------------
    elif "reportagem" in texto_minusculo or "problema" in texto_minusculo:
        # Verifica se o utilizador enviou apenas a palavra ou já o texto descritivo
        if len(texto_usuario.split()) < 2:
            resposta = "🚨 Para registares o teu problema, escreve a palavra *Reportagem* seguida do teu relato.\n\n*Exemplo:* Reportagem Falta de iluminação pública na rua direita do mercado de Ondjiva."
        else:
            # Captura tudo o que vem depois da palavra "Reportagem"
            relato = texto_usuario.replace("Reportagem", "").replace("reportagem", "").strip()
            
            # Executa a função que envia os dados para a Administração Municipal
            enviar_para_administracao(numero, relato)
            
            resposta = (
                "✅ *Reportagem Registada com Sucesso!*\n\n"
                "As tuas informações foram enviadas e guardadas diretamente no sistema de triagem da *Administração Municipal*.\n\n"
                "Obrigado por exerceres a tua cidadania e ajudar no desenvolvimento do Cunene!"
            )

    # ----------------------------------------------------
    # MENU 3: Orientador de Saúde Básico
    # ----------------------------------------------------
    elif texto_minusculo == "3" or "saude" in texto_minusculo or "sintoma" in texto_minusculo:
        resposta = (
            "🩺 *Orientador de Saúde Básico (Cunene)*\n\n"
            "Este é um canal informativo, não substitui uma consulta médica. Se tens sintomas, vê as orientações:\n\n"
            "🦟 *Febre Alta/Dores de Cabeça (Suspeita de Malária):* Hidrata-te bastante e dirige-te imediatamente ao centro de saúde mais próximo para fazer o teste da gota espessa.\n\n"
            "💧 *Diarreia/Vómitos (Desidratação):* Inicia o soro caseiro (1 litro de água fervida ou filtrada + 1 colher de sopa de açúcar + 1 colher de café de sal). Se persistir, procura o hospital.\n\n"
            "⚠️ *Caso de Urgência:* Dirige-te ao Hospital Geral de Ondjiva."
        )

    # ----------------------------------------------------
    # MENU 4: Contactos de Emergência (Polícia e Hospitais)
    # ----------------------------------------------------
    elif texto_minusculo == "4" or "contacto" in texto_minusculo or "ajuda" in texto_minusculo:
        resposta = (
            "📞 *Lista de Contactos de Emergência do Cunene*:\n\n"
            "🚓 *Polícia Nacional (Cunene):*\n"
            "• Terminal Geral: 113\n"
            "• Comando Provincial do Cunene: +244 923 166 113 (Simulado)\n\n"
            "🏥 *Hospitais e Centros de Saúde:*\n"
            "• Hospital Geral do Cunene (Ondjiva): +244 931 000 000 (Simulado)\n"
            "• Banco de Urgência Pediatria: +244 945 000 000 (Simulado)\n"
            "• Ambulância/Proteção Civil: 115\n\n"
            "💡 _Guarda estes números no teu telemóvel para situações de aflição._"
        )

    # ----------------------------------------------------
    # MENSAGEM PADRÃO / MENU PRINCIPAL
    # ----------------------------------------------------
    else:
        resposta = (
            "👋 Olá! Bem-vindo ao *Portal Digital do Cidadão - Província do Cunene*.\n\n"
            "Este sistema está interligado com os serviços provinciais. Escolhe uma opção digitando o número correspondente:\n\n"
            "1️⃣ *Informações:* Saber mais sobre a província do Cunene.\n"
            "2️⃣ *Reportagem:* Enviar uma denúncia ou problema para a *Administração Municipal* (Escreve: _Reportagem [teu texto]_).\n"
            "3️⃣ *Saúde:* Guia de orientação para problemas básicos de saúde.\n"
            "4️⃣ *Contactos:* Lista telefónica da Polícia e Hospitais da província."
        )
        
    enviar_mensagem_oficial(numero, resposta)

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Token inválido", 403
    return "Requisição inválida", 400

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.get_json()
    try:
        if "messages" in dados["entry"][0]["changes"][0]["value"]:
            mensagem_obj = dados["entry"][0]["changes"][0]["value"]["messages"][0]
            numero_cliente = mensagem_obj["from"]
            texto_recebido = mensagem_obj["text"]["body"]
            
            processar_cerebro_do_bot(numero_cliente, texto_recebido)
    except:
        pass

    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
