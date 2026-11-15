import os
import httpx
import streamlit as st
from dotenv import load_dotenv
import ollama

load_dotenv()

host_servidor = os.getenv('LLM_HOST')
modelo_padrao = os.getenv('LLM_MODEL')

# Tempo máximo (em segundos) que o programa espera antes de desistir.
# - CONEXAO: quanto esperar para "bater na porta" do servidor llm registrada
#   Se o servidor estiver fora do ar, descobrimos rápido (5s) em vez de esperar minutos.
# - RESPOSTA: quanto esperar o modelo gerar a resposta depois de conectado.
#   Fica mais alto porque o modelo pode demorar de verdade para "pensar".
TIMEOUT_CONEXAO = 5.0
TIMEOUT_RESPOSTA = 120.0

# Desabilita verificação SSL conforme exigido no item 1.1 do guia
llm = ollama.Client(
    host=host_servidor,
    verify=False,
    timeout=httpx.Timeout(TIMEOUT_RESPOSTA, connect=TIMEOUT_CONEXAO)
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
- Se a resposta NÃO estiver no contexto, responda somente: "Não tenho essa informação na minha base de conhecimento."
- Nunca use conhecimento externo, nunca invente seções, chaves ou passos e nunca dê sugestões fora do contexto.
"""

st.title("Suporte Cloud Protheus")

pergunta = st.chat_input("Envie a sua mensagem...")

if pergunta:
    st.chat_message("user").write(pergunta)
    
    # Repetimos a regra junto da pergunta: modelos pequenos (7B) "esquecem" mais
    # facilmente instruções que ficam só no início da conversa.
    mensagem_completa = (
        f"Contexto:\n{CONHECIMENTO_PROTHEUS}\n\n"
        f"Pergunta: {pergunta}\n\n"
        "Responda somente com base no Contexto acima. Se a resposta não estiver "
        "nele, diga exatamente: Não tenho essa informação na minha base de conhecimento."
    )
    
    # "try" = tente fazer isto. Se algo der errado, o Python pula para um "except"
    # (em vez de travar ou mostrar um erro gigante para o usuário).
    try:
        resposta = llm.chat(
            model=modelo_padrao,
            messages=[
                {"role": "system", "content": INSTRUCAO_SISTEMA},
                {"role": "user", "content": mensagem_completa}
            ],
            # temperature = "criatividade" do modelo. 0.0 = o mais fiel e previsível possível.
            options={"temperature": 0.0}
        )
    except httpx.TimeoutException:
        # Passou do tempo limite (conexão ou resposta demorou demais).
        st.error(
            "O servidor demorou demais para responder. "
            "Verifique se a llm está ativa e tente novamente."
        )
    except ConnectionError:
        # Não conseguiu nem conectar: llm desligada
        st.error(
            "🔌 Não consegui conectar na LLM interna. Verifique se ela está rodando "
            "e se o endereço HOST no arquivo .env está correto "
        )
    except ollama.ResponseError as erro:
        # O servidor respondeu, mas com erro
        st.error(f"O servidor respondeu com erro ({erro.status_code}): {erro.error}")
    else:
        # "else" só roda se o "try" funcionou sem nenhum erro.
        st.chat_message("assistant").write(resposta['message']['content'])