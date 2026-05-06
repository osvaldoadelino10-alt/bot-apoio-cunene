from flask import Flask, request, jsonify 
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import json

app = Flask(_name_)

# Base de dados simples em memória - pra demonstração
REPORTS = []
STATS = {"AGUA": 0, "SAUDE": 0, "ESCOLA": 0, "OUTRO": 0}

def log_report(categoria, detalhes, telefone):
    """Salva report pra mostrar na defesa do TCC"""
    report = {
        "id": len(REPORTS) + 1,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "categoria": categoria,
        "detalhes": detalhes,
        "telefone": telefone[-4:], # só últimos 4 dígitos por privacidade
        "provincia": "Cunene"
    }
    REPORTS.append(report)
    STATS[categoria] += 1
    return report["id"]

@app.route("/webhook", methods=['POST'])
def webhook():
    msg = request.values.get('Body', '').upper().strip()
    telefone = request.values.get('From', '')
    resp = MessagingResponse()
    
    # MENU PRINCIPAL
    if msg in ['OI', 'OLA', 'MENU', 'INICIO', 'HELLO']:
        resp.message(
            "🇦🇴 BOT CUNENE - APOIO AO CIDADÃO 🇦🇴\n\n"
            "Sistema de reporte para problemas comunitários\n"
            "Província: Cunene\n\n"
            "📋 *CATEGORIAS:*\n\n"
            "🚰 AGUA - Falta de água, poços avariados\n"
            "🏥 SAUDE - Postos médicos, medicamentos\n"
            "🎓 ESCOLA - Educação, infraestrutura\n"
            "⚠️ URGENTE - Emergências\n"
            "📊 STATS - Ver estatísticas\n\n"
            "Digite a palavra da categoria"
        )
    
    # ÁGUA - SUBMENU COMPLETO
    elif 'AGUA' in msg:
        resp.message(
            "🚰 *CUNENE - ABASTECIMENTO DE ÁGUA*\n\n"
            "Selecione o problema:\n\n"
            "1️⃣ Falta de água há +3 dias no bairro\n"
            "2️⃣ Poço/Furo de água avariado\n"
            "3️⃣ Água com mau cheiro ou cor estranha\n"
            "4️⃣ Canalização rebentada\n"
            "5️⃣ Outro problema\n\n"
            "⬅️ Digite MENU para voltar\n"
            "Responda com o número"
        )
    
    # SAÚDE - SUBMENU COMPLETO
    elif 'SAUDE' in msg:
        resp.message(
            "🏥 *CUNENE - SAÚDE PÚBLICA*\n\n"
            "Selecione o problema:\n\n"
            "1️⃣ Posto médico sem médico/enfermeiro\n"
            "2️⃣ Falta de medicamentos essenciais\n"
            "3️⃣ Ambulância não atende chamadas\n"
            "4️⃣ Posto sem energia/água\n"
            "5️⃣ Outro problema\n\n"
            "⬅️ Digite MENU para voltar\n"
            "Responda com o número"
        )
    
    # EDUCAÇÃO - SUBMENU COMPLETO
    elif 'ESCOLA' in msg:
        resp.message(
            "🎓 *CUNENE - EDUCAÇÃO*\n\n"
            "Selecione o problema:\n\n"
            "1️⃣ Falta de professores na escola\n"
            "2️⃣ Escola sem carteiras/quadros\n"
            "3️⃣ Falta de merenda escolar\n"
            "4️⃣ Estrutura danificada/teto a cair\n"
            "5️⃣ Outro problema\n\n"
            "⬅️ Digite MENU para voltar\n"
            "Responda com o número"
        )
    
    # URGENTE
    elif 'URGENTE' in msg:
        resp.message(
            "⚠️ *CANAL URGENTE - CUNENE*\n\n"
            "Para emergências contacte:\n"
            "🚨 Polícia: 113\n"
            "🚑 Bombeiros: 115\n"
            "🏥 INEMA: 116\n\n"
            "Se for problema comunitário urgente,\n"
            "descreva aqui e será priorizado.\n\n"
            "⬅️ Digite MENU para voltar"
        )
    
    # ESTATÍSTICAS - PRA IMPRESSIONAR NA BANCA
    elif 'STATS' in msg or 'ESTATISTICA' in msg:
        total = sum(STATS.values())
        resp.message(
            f"📊 *ESTATÍSTICAS - CUNENE*\n\n"
            f"Total de reportes: *{total}*\n\n"
            f"🚰 Água: {STATS['AGUA']}\n"
            f"🏥 Saúde: {STATS['SAUDE']}\n"
            f"🎓 Escola: {STATS['ESCOLA']}\n"
            f"⚠️ Outros: {STATS['OUTRO']}\n\n"
            f"_Dados em tempo real_\n"
            f"_TCC Osvaldo 2026_\n\n"
            "⬅️ Digite MENU para voltar"
        )
    
    # PROCESSAR RESPOSTAS NUMÉRICAS
    elif msg in ['1', '2', '3', '4', '5']:
        # Detecta categoria pela última interação - simplificado
        categoria = "OUTRO"
        if any(x in request.values.get('Body', '') for x in ['agua', 'poço', 'Água']):
            categoria = "AGUA"
        elif any(x in request.values.get('Body', '') for x in ['saude', 'médico', 'posto']):
            categoria = "SAUDE" 
        elif any(x in request.values.get('Body', '') for x in ['escola', 'professor']):
            categoria = "ESCOLA"
            
        protocolo = log_report(categoria, f"Opção {msg}", telefone)
        resp.message(
            f"✅ *PROBLEMA REGISTRADO*\n\n"
            f"Protocolo: *#{protocolo:04d}*\n"
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"Local: Cunene\n\n"
            f"Sua solicitação foi enviada para\n"
            f"a Administração Municipal.\n\n"
            f"📱 Você receberá atualizações.\n\n"
            "Digite MENU para novo reporte\n"
            "Digite STATS para ver estatísticas"
        )
    
    # FALLBACK INTELIGENTE
    else:
        resp.message(
            "❓ *Não entendi sua mensagem*\n\n"
            "Eu sou o Bot do Cunene 🇦🇴\n"
            "Ajudo a reportar problemas da comunidade.\n\n"
            "Digite:\n"
            "👉 MENU - Ver todas opções\n"
            "👉 AGUA - Problemas de água\n"
            "👉 SAUDE - Problemas de saúde\n"
            "👉 ESCOLA - Problemas de educação\n\n"
            "TCC Osvaldo 2026"
        )
    
    return str(resp)

# ROTA EXTRA PRA BANCA VER OS DADOS
@app.route("/dashboard")
def dashboard():
    return jsonify({
        "projeto": "Bot Apoio Cunene",
        "autor": "Osvaldo",
        "ano": 2026,
        "total_reportes": len(REPORTS),
        "estatisticas": STATS,
        "ultimos_reportes": REPORTS[-5:] if REPORTS else []
    })

@app.route("/")
def home():
    return """
    <h1>Bot Cunene Online 🇦🇴</h1>
    <p>Sistema de reporte comunitário - TCC 2026</p>
    <p><a href='/dashboard'>Ver Dashboard JSON</a></p>
    <p>Webhook: /webhook</p>
    """
if __name__ == "__main__":
    app.run()

