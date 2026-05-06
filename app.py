from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import datetime

app = Flask(__name__)

reportes = []
user_states = {}

@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    print(f"Recebi: {incoming_msg} de {from_number}") # Pra aparecer no log
    
    # Se usuário tá respondendo um estado anterior
    if from_number in user_states:
        estado = user_states[from_number]
        reportes.append({
            "categoria": estado.replace('aguardando_detalhes_','').upper(),
            "mensagem": request.values.get('Body', '').strip(),
            "telefone": from_number,
            "data": str(datetime.datetime.now())
        })
        del user_states[from_number]
        msg.body("✅ REGISTO CONCLUÍDO!*\n\nObrigado. A sua ocorrência foi registrada com sucesso.\n\nDigite *MENU para novo reporte.")
        return str(resp)
    
    # Comandos principais
    if incoming_msg == 'menu':
        menu = """🇦🇴 BOT CUNENE - APOIO AO CIDADÃO 🇦🇴

Sistema de reporte para problemas comunitários
Província: Cunene

📋 CATEGORIAS:
🚰 AGUA - Falta de água, poços avariados
🏥 SAUDE - Postos médicos, medicamentos  
🏫 ESCOLA - Educação, infraestrutura
⚠️ URGENTE - Emergências
📊 STATS - Ver estatísticas

Digite a palavra da categoria"""
        msg.body(menu)
    
    elif incoming_msg == 'agua':
        user_states[from_number] = 'aguardando_detalhes_agua'
        msg.body("🚰 *REGISTO - ÁGUA*\n\nDescreva o problema de água no Cunene:")
    
    elif incoming_msg == 'saude':
        user_states[from_number] = 'aguardando_detalhes_saude'
        msg.body("🏥 *REGISTO - SAÚDE*\n\nDescreva o problema de saúde:")
    
    elif incoming_msg == 'escola':
        user_states[from_number] = 'aguardando_detalhes_escola'
        msg.body("🏫 *REGISTO - ESCOLA*\n\nDescreva o problema na escola:")
    
    elif incoming_msg == 'urgente':
        user_states[from_number] = 'aguardando_detalhes_urgente'
        msg.body("⚠️ *REGISTO - URGENTE*\n\nDescreva a emergência:")
    
    elif incoming_msg == 'stats':
        total = len(reportes)
        msg.body(f"📊 ESTATÍSTICAS CUNENE*\n\nTotal de reportes: {total}\n\nDigite *MENU para voltar")
    
    else:
        msg.body("Olá! 👋\n\nDigite MENU para ver as opções do Bot Apoio Cunene 🇦🇴")
    
    print(f"Respondendo: {msg.body}") # Pra aparecer no log
    return str(resp)

@app.route("/dashboard")
def dashboard():
    return {
        "ano": 2026,
        "autor": "Osvaldo",
        "projeto": "Bot Apoio Cunene",
        "total_reportes": len(reportes),
        "estatisticas": {
            "AGUA": len([r for r in reportes if r["categoria"] == "AGUA"]),
            "SAUDE": len([r for r in reportes if r["categoria"] == "SAUDE"]),
            "ESCOLA": len([r for r in reportes if r["categoria"] == "ESCOLA"]),
            "URGENTE": len([r for r in reportes if r["categoria"] == "URGENTE"])
        },
        "ultimos_reportes": reportes[-5:]
    }
if __name__ == "__main__":
    app.run()

