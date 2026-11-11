import os
from dotenv import load_dotenv
import ollama

load_dotenv()

host_servidor = os.getenv('OLLAMA_HOST')
modelo_padrao = os.getenv('OLLAMA_MODEL')

# Conexão com o servidor remoto
llm = ollama.Client(
    host=host_servidor,
    headers={'ngrok-skip-browser-warning': 'true'}
)

# 1. Base de conhecimento documentada de exemplo
CONHECIMENTO_PROTHEUS = """
Para configurar o WebService REST no Protheus:
1. Abra o arquivo appserver.ini.
2. Adicione a seção [HTTPREST] com a porta desejada, ex: Port=8084.
3. Adicione a chave [ONSTART] com jobs=HTTPJOB.
4. Reinicie o serviço do Appserver.
URL padrão de teste: http://localhost:8084/rest
"""

# 2. Instrução do sistema fechada
INSTRUCAO_SISTEMA = """
Você é um especialista em suporte cloud do Protheus.
Sua regra absoluta: responda com base ESTRITAMENTE no contexto fornecido na mensagem do usuário.
- Seja o mais direto, simples e conciso possível.
- Responda apenas o que foi perguntado, em poucas linhas ou passos curtos.
- Não faça introduções desnecessárias, não cumprimente longamente e não escreva conclusões.
- Seja polido, mas breve.
- Preserve exatamente a grafia (maiúsculas/minúsculas) de chaves, seções e parâmetros.
"""

print(f"--- Chat iniciado com {modelo_padrao} ---")
print("Digite 'sair' a qualquer momento para encerrar.\n")

while True:
    try:
        mensagem_usuario = input("Digite aqui: ")

        if not mensagem_usuario.strip():
            continue

        if mensagem_usuario.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando o chat. Até logo!")
            break

        # 3. Monta o prompt blindado com contexto + pergunta atual
        prompt_blindado = f"""Use APENAS as informações dentro da tag <contexto> para responder à pergunta.
Se a resposta exata não estiver escrita dentro de <contexto>, responda exclusivamente: "Não tenho essa informação na minha base de conhecimento."
Não use seu conhecimento prévio da internet.

<contexto>
{CONHECIMENTO_PROTHEUS}
</contexto>

Pergunta: {mensagem_usuario}"""

        print("\nResposta da IA: ", end="", flush=True)

        # Ilusão para modelos que executam localmente para teste
        stream = llm.chat(
            model=modelo_padrao,
            messages=[
                {'role': 'system', 'content': INSTRUCAO_SISTEMA},
                {'role': 'user', 'content': prompt_blindado}
            ],
            options={
                'temperature': 0.0  # Trava a criatividade para evitar alucinações
            },
            stream=True
        )

        for chunk in stream:
            print(chunk['message']['content'], end="", flush=True)

        print("\n" + "-" * 40 + "\n")

    except KeyboardInterrupt:
        print("\nEncerrando o chat...")
        break
    except Exception as erro:
        print(f"\nErro de conexão: {erro}\n")