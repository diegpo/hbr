import os
from pathlib import Path
import httpx
import streamlit as st
from dotenv import load_dotenv
import ollama

load_dotenv()

host_servidor = os.getenv('LLM_HOST')
modelo_padrao = os.getenv('LLM_MODEL')

# Tempo máximo (em segundos) que o programa espera antes de desistir.
TIMEOUT_CONEXAO = 5.0
TIMEOUT_RESPOSTA = 120.0

# --- CACHE DO CLIENTE LLM ---
@st.cache_resource
def iniciar_cliente_llm():
    return ollama.Client(
        host=host_servidor,
        verify=False,
        timeout=httpx.Timeout(TIMEOUT_RESPOSTA, connect=TIMEOUT_CONEXAO)
    )

llm = iniciar_cliente_llm()

# --- LEITURA RECURSIVA DA BASE DE CONHECIMENTO ---
@st.cache_data
def carregar_base_conhecimento(pasta_raiz="base_conhecimento"):
    caminho = Path(pasta_raiz)
    
    # Se a pasta ainda não existir, cria automaticamente para evitar erro
    if not caminho.exists():
        caminho.mkdir(parents=True, exist_ok=True)
        return ""

    textos_coletados = []
    extensoes_validas = {".txt", ".md"}

    # rglob("*") varre a pasta raiz e TODAS as subpastas recursivamente
    for arquivo in sorted(caminho.rglob("*")):
        if arquivo.is_file() and arquivo.suffix.lower() in extensoes_validas:
            conteudo = arquivo.read_text(encoding="utf-8").strip()
            if conteudo:
                # Identifica a origem (ex: webservice/configurar_rest.md) para ajudar o modelo
                caminho_relativo = arquivo.relative_to(caminho)
                textos_coletados.append(f"--- DOCUMENTO: {caminho_relativo} ---\n{conteudo}")

    return "\n\n".join(textos_coletados)

CONHECIMENTO_PROTHEUS = carregar_base_conhecimento()

INSTRUCAO_SISTEMA = """
Você é um especialista em suporte cloud do Protheus.
Sua regra absoluta: responda com base ESTRITAMENTE no contexto fornecido na mensagem do usuário (incluindo perguntas sobre quem você é ou o que você faz).
- Seja o mais direto, simples e conciso possível.
- Responda apenas o que foi perguntado, em poucas linhas ou passos curtos.
- Não faça introduções desnecessárias, não cumprimente longamente e não escreva conclusões.
- Nunca diga "Com base no contexto" ou "De acordo com os documentos"; apenas entregue a resposta diretamente.
- Seja polido, mas breve.
- Preserve exatamente a grafia (maiúsculas/minúsculas) de chaves, seções e parâmetros.
- Use a frase "Não tenho essa informação na minha base de conhecimento." SOMENTE se a resposta for totalmente ausente (nunca a misture no final de uma resposta válida).
- Nunca use conhecimento externo, nunca invente seções, chaves ou passos e nunca dê sugestões fora do contexto.
- Se o usuário apenas cumprimentar ou pedir ajuda sem especificar o tema (ex.: 'Oi', 'Me ajude'), responda brevemente perguntando qual configuração ou dúvida do Protheus ele precisa.
"""


st.title("Suporte Cloud Protheus")

# Barra lateral útil para manutenção da base
with st.sidebar:
    st.header("Base de Conhecimento")
    if not CONHECIMENTO_PROTHEUS:
        st.warning("Nenhum arquivo .txt ou .md encontrado na pasta 'base_conhecimento'.")
    else:
        st.success("Base carregada com sucesso.")
    
    if st.button("Recarregar arquivos"):
        carregar_base_conhecimento.clear()
        st.rerun()

# --- HISTÓRICO ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

pergunta = st.chat_input("Envie a sua mensagem...")

if pergunta:
    st.chat_message("user").write(pergunta)
    st.session_state.messages.append({"role": "user", "content": pergunta})
    
    mensagem_completa = (
        f"Contexto:\n{CONHECIMENTO_PROTHEUS}\n\n"
        f"Pergunta: {pergunta}"
    )
    
    try:
        resposta = llm.chat(
            model=modelo_padrao,
            messages=[
                {"role": "system", "content": INSTRUCAO_SISTEMA},
                {"role": "user", "content": mensagem_completa}
            ],
            options={"temperature": 0.0}
        )
    except httpx.TimeoutException:
        st.error(
            "O servidor demorou demais para responder. "
            "Verifique se a llm está ativa e tente novamente."
        )
    except ConnectionError:
        st.error(
            "🔌 Não consegui conectar na LLM interna. Verifique se ela está rodando "
            "e se o endereço HOST no arquivo .env está correto "
        )
    except ollama.ResponseError as erro:
        st.error(f"O servidor respondeu com erro ({erro.status_code}): {erro.error}")
    else:
        texto_resposta = resposta['message']['content']
        st.chat_message("assistant").write(texto_resposta)
        st.session_state.messages.append({"role": "assistant", "content": texto_resposta})