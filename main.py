import os
import streamlit as st
from dotenv import load_dotenv
import ollama

load_dotenv()

host_servidor = os.getenv('OLLAMA_HOST')
modelo_padrao = os.getenv('OLLAMA_MODEL')

# Desabilita verificação SSL conforme exigido no item 1.1 do guia
llm = ollama.Client(
    host=host_servidor,
    verify=False
)

CONHECIMENTO_PROTHEUS = """
Para configurar o WebService REST no Protheus:
1. Abra o arquivo appserver.ini.
2. Adicione a seção [HTTPREST] com a porta desejada, ex: Port=8084.
3. Adicione a chave [ONSTART] com jobs=HTTPJOB.
4. Reinicie o serviço do Appserver.
URL padrão de teste: http://localhost:8084/rest
"""

INSTRUCAO_SISTEMA = """
Você é um especialista em suporte cloud do Protheus.
Sua regra absoluta: responda com base ESTRITAMENTE no contexto fornecido na mensagem do usuário.
- Seja o mais direto, simples e conciso possível.
- Responda apenas o que foi perguntado, em poucas linhas ou passos curtos.
- Não faça introduções desnecessárias, não cumprimente longamente e não escreva conclusões.
- Seja polido, mas breve.
- Preserve exatamente a grafia (maiúsculas/minúsculas) de chaves, seções e parâmetros.
"""

st.title("Suporte Cloud Protheus")

pergunta = st.chat_input("Envie a sua mensagem...")

if pergunta:
    st.chat_message("user").write(pergunta)
    
    mensagem_completa = f"Contexto:\n{CONHECIMENTO_PROTHEUS}\n\nPergunta: {pergunta}"
    
    resposta = llm.chat(
        model=modelo_padrao,
        messages=[
            {"role": "system", "content": INSTRUCAO_SISTEMA},
            {"role": "user", "content": mensagem_completa}
        ]
    )
    
    st.chat_message("assistant").write(resposta['message']['content'])