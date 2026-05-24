import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

# ==========================================
# 1. VARIÁVEIS DE AMBIENTE (GROQ & TELEGRAM)
# ==========================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") # Adiciona esta variável no Render

# Inicializa OpenAI para usar a infraestrutura da Groq
client = None
if GROQ_API_KEY:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

app = Flask(__name__)

# ==========================================
# 2. A BÍBLIA DE ONDJIVA (Base Embutida do TCC)
# ==========================================
CONTEXTO_ONDJIVA = """
Tu és o Bot_cunene, o assistente oficial e inteligente da Administração de Ondjiva, província do Cunene.
O teu objetivo é informar os cidadãos, receber denúncias e reportagens comunitárias.

### REGRAS DE OURO:
1. Se não tiveres a informação na tua base de dados abaixo, diz: "Lamento, não possuo essa informação oficial no momento. Sugiro que se dirija aos serviços da Administração."
2. Se o utilizador quiser fazer uma reportagem ou denúncia, agradece, pede detalhes (o que aconteceu, local, data) e diz que a informação foi registada para análise.
3. Sê formal, direto, prestativo e educado.

---
### 1. ADMINISTRAÇÃO E LOCALIZAÇÃO
- Capital da província do Cunene: Ondjiva.
- Governo Provincial, Jardim Provincial, Palácio, Tribunal, Delegacia Provincial, AGT e Tribuna: Centro da Cidade.
- Administração Provincial e Aeroporto Provincial: Bairro Kaculuvale.
- Comando Provincial da Polícia: Centro da Cidade.
- Mediateca Lucas: Pesquisa e internet.

### 2. BAIRROS E COMANDOS
- Bairros: Kafitu (1/2), Onahumba (1/2/3), Castilhos, Kaculuvale, Caxila (1/2/3), Pioneiro Zeca, Bangula, Muhongo, Naipalala, Ekuma.
- Comandos Policiais: 
  - Municipal e Investigação: Castilhos.
  - Guarda Fronteira: Cafitu.
  - Bombeiros e Viação Trânsito: Naipalala.
  - Esquadras: Kaculuvale and Onahumba.

### 3. SAÚDE
- Hospitais Principais:
  - Hospital Provincial (EKUMA): Bairro Ekuma.
  - Hospital Central Simeone Mucunde: Bairro Naipalala.
  - Hospital Municipal: Centro da Cidade.
  - Hospital Adicional: Onahumba.

### 4. EDUCAÇÃO
- Faculdades: Rei Luhuna (Muhongo), Mandume (Naipalala).
- Institutos/Colégios (Resumo):
  - ITSO (Saúde): Ekuma.
  - Eiffel, Oulondelo, Instituto ITSO, IMPO (Pedagogia), Colégio Bolet Salú, Colégio Pitágoras, Colégio Arcanjo: Naipalala.
  - Cesmo, Colégio Ednans, Colégio Popiene, Marco Lendros: Kaculuvale.
  - Complexo Abcunene: Caxila 3.
- Escolas Primárias/1º Ciclo: Cow-Boy (Castilhos), Centralidade, Ocapale (Kaculuvale), Rei Nande (Naipalala), E.P. 122 (Zeca), 4 de Janeiro (Kafitu1), e outras nos bairros Kafitu2, Onahumba e Zeca.

### 5. SERVIÇOS E COMÉRCIO
- Bancos: 
  - Centro: BAI. 
  - Bangula: BCI, BPC, Banco Sol, Banco Económico. 
  - Zeca: BFA, BIC. 
  - Castilhos: BCA. 
  - Naipalala: BPC2, Atlântico.
- Supermercados: Shoprite e AngoMarte (Castilhos).
- Lazer/Restaurantes: Lodge (Naipalala), Cumbuessa (Zeca), Moreira (Caxila 2), Skiva (Caxila 3), Vila Ocapale. Brothers (Bangula/Zeca), Fórmula (Zeca), Rodrigão (Zeca), Rosmélia (Castilhos), Kaculuvale.

### 6. DESPORTO
- Estádios: Onze de Novembro (Castilhos) e Campo da Centralidade.
"""

# ==========================================
# 3. FUNÇÃO DE ENVIAR MENSAGEM (TELEGRAM API)
# ==========================================
def enviar_mensagem_telegram(chat_id, texto):
    if not TELEGRAM_TOKEN:
        print("🚨 Falta a credencial TELEGRAM_TOKEN no Render!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown" # Permite usar o negrito *texto* e itálico _texto_ no Telegram
    }
    
    resposta = requests.post(url, json=payload)
    print(f"📤 Resposta enviada ao Telegram. Status: {resposta.status_code}")

# ==========================================
# 4. PROCESSAMENTO DO BOT (FILTROS + GROQ)
# ==========================================
def processar_texto(user_text):
    texto_baixo = user_text.lower()
    
    # --- FILTRO 1: EMERGÊNCIA ---
    if any(palavra in texto_baixo for palavra in ["emergencia", "emergência", "socorro", "policia", "bombeiros"]):
        return (
            "🚨 *ALERTA DE EMERGÊNCIA IMEDIATA!* 🚨\n\n"
            "Se estás numa situação de perigo real no Cunene, liga de imediato:\n"
            "🚓 *Polícia Nacional:* 113\n"
            "👨‍🚒 *Bombeiros:* 115\n\n"
            "Procura um local seguro!"
        )
    
    # --- FILTRO 2: REPORTAGEM ---
    elif "reportagem" in texto_baixo:
        relato = user_text.lower().replace("reportagem", "").strip()
        if not relato:
            return "🚨 Escreve a palavra *Reportagem* seguida da descrição do problema (Ex: Reportagem falta de luz no bairro X)."
        return f"✅ *Ocorrência Registada!*\n\nO teu relato:\n_{relato}_\n\nFoi guardado e será reencaminhado para a Administração Municipal. Obrigado!"

    # --- FILTRO 3: GROQ/OPENAI ---
    else:
        try:
            if not client:
                return "🚨 Erro: API da IA não configurada."
                
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.1,
                messages=[
                    {"role": "system", "content": CONTEXTO_ONDJIVA},
                    {"role": "user", "content": user_text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Erro na IA: {e}"

# ==========================================
# 5. ROTA DO FLASK (WEBHOOK DO TELEGRAM)
# ==========================================
@app.route('/', methods=['GET'])
def home():
    return "Servidor do Bot de Telegram do Cunene Ativo!", 200

# O Telegram envia tudo para esta rota via POST (não precisa da validação GET da Meta)
@app.route('/telegram', methods=['POST'])
def receber_mensagens_telegram():
    body = request.get_json()

    # Verifica se a estrutura JSON contém uma mensagem de texto válida
    if "message" in body and "text" in body["message"]:
        chat_id = body["message"]["chat"]["id"]
        texto_recebido = body["message"]["text"]
        
        print(f"📥 Recebido do Telegram (Chat ID {chat_id}): {texto_recebido}")
        
        # Processa o texto usando os mesmos filtros e IA
        resposta_final = processar_texto(texto_recebido)
        
        # Envia de volta para o utilizador no Telegram
        enviar_mensagem_telegram(chat_id, resposta_final)
                    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
