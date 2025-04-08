import os,json,random
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

#pega a variável de ambiente e converte para JSON
FBKEY = json.loads(os.getenv('CONFIG_FIREBASE'))

cred = credentials.Certificate(FBKEY)
firebase_admin.initialize_app(cred)

# Conectando com o firestore da firebase
db = firestore.client()


# ROTA PRINCIPAL DE TESTE
@app.route('/')
def index():
    return 'API ON', 200

# MÉTODO GET - CHARADA ALEATÓRIA
@app.route('/charadas', methods=['GET'])
def charadarandom():
    charadas = []

    lista = db.collection('charadas').stream()

    for item in lista:
        charadas.append(item.to_dict())

    if charadas:
        return jsonify(random.choice(charadas)), 200
    else:
        return jsonify({'mensagem': 'Erro! nenhuma charada cadastrada'}), 404
    

# MÉTODO GET -  CHARADAS POR ID
@app.route('/charadas/<id>', methods=['GET'])
def busca(id):
    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get().to_dict()

    if doc:
        return jsonify(doc), 200
    else: 
        return jsonify({'mensagem':'Charada não encontrada'})
    

# MÉTODO POST - ADICIONAR CHARADA
@app.route('/charadas', methods=['POST'])
def adicionar_charada():
    dados = request.json

    if "pergunta" not in dados or "resposta" not in dados:
        return jsonify({'mensagem':'Erro - Campos pergunta e resposta são obrigatórios'}), 400
    
    # Contador
    contador_ref =  db.collection('controle_id').document('contador')
    contador_doc = contador_ref.get().to_dict()
    ultimo_id = contador_doc.get('id')
    novo_id = int(ultimo_id) + 1
    contador_ref.update({'id': novo_id}) #atualização da coleção

    db.collection('charadas').document(str(novo_id)).set({
        "id": novo_id,
        "pergunta": dados['pergunta'],
        "resposta": dados['resposta']
    })

    return jsonify({'mensagem':'Charada cadastrada com sucesso!'}),201

# MÉTODO PUT - ALTERAR CHARADA
@app.route('/charadas/<id>', methods=['PUT'])
def alterar_charada(id):
    dados = request.json

    if "pergunta" not in dados or "resposta" not in dados:
        return jsonify({'mensagem':'Erro - Campos pergunta e resposta são obrigatórios'}), 400
    
    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update({
            "pergunta": dados['pergunta'],
            "resposta": dados['resposta']
        })

        return jsonify({'mensagem':'Charada atualizada com sucesso!'}), 201
    
    else:
        return jsonify({'mensagem':'Erro - charada não encontrada'}), 404
    

    #MÉTODO DELETE - EXCLUIR CHARADA
@app.route('/charadas/<id>', methods=['DELETE'])
def excluir_charada(id):
    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({'mensagem':'Erro -  charada não encontrada!'})
    
    doc_ref.delete()
    return jsonify({'mensagem':'Charada excluida com sucesso!'})

# MÉTODO GET - LISTAR CHARADAS
@app.route('/charadas/lista', methods=['GET'])
def charadas_lista():
    charadas = []

    lista = db.collection('charadas').stream()

    for item in lista:
        charadas.append(item.to_dict())

    if charadas:
        return jsonify(charadas), 200
    else:
        return jsonify({'mensagem': 'Erro! nenhuma charada cadastrada'}), 404

if __name__ == '__main__':
    app.run()