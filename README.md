# hbr
Curso Instituto hardware br.

# Assistente Técnico TOTVS Protheus (RAG)

Assistente virtual em Python focado em suporte técnico para configuração do TOTVS Protheus. Utiliza arquitetura desacoplada e injeção estrita de contexto (RAG) para responder de forma objetiva, rápida e sem alucinações.

## Arquitetura

- **Cliente:** Aplicação CLI em Python com streaming de resposta (`stream=True`) e temperatura travada em `0.0` para máxima fidelidade à base de conhecimento.
- **Inferência (LLM):** Desacoplada via API. Na configuração atual para desenvolvimento e testes, utiliza o [Ollama](https://ollama.com/) rodando localmente ou remotamente (ex: Google Colab via túnel Ngrok). Como a lógica de RAG e as regras de contexto são independentes do motor de inferência, o projeto pode ser facilmente adaptado para outros provedores de LLM (OpenAI, Gemini API, Groq, LM Studio, etc.).

## Pré-requisitos

- Python 3.10 ou superior
- Instância do **Ollama** em execução (local ou remota para testes) com um modelo instalado (ex: `qwen2.5:7b` ou `llama3.2:3b`).

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/diegpo/hbr.git](https://github.com/diegpo/hbr.git)
   cd hbr

    Crie e ative o ambiente virtual:
    Bash

    python3 -m venv venv
    source venv/bin/activate  # Linux/WSL/macOS
    # No Windows: venv\Scripts\activate

    Instale as dependências:
    Bash

    pip install -r requirements.txt

    Configure as variáveis de ambiente:
    Crie um arquivo .env na raiz do projeto com o endereço do seu servidor Ollama e o modelo desejado:
    Snippet de código

    OLLAMA_HOST=http://localhost:11434
    OLLAMA_MODEL=qwen2.5:7b

    
Como Testar

    Certifique-se de que o servidor Ollama está ativo e acessível.

    Execute o script principal:
    Bash

    python main.py

    Teste o comportamento do assistente fazendo perguntas no terminal:

        Pergunta dentro da base de conhecimento: "Qual seção do appserver.ini configuro para o REST?" -> Deve responder de forma direta usando apenas os dados cadastrados.

        Pergunta fora da base de conhecimento: "Como configurar o e-mail no Protheus?" -> Deve recusar responder ("Não tenho essa informação na minha base de conhecimento."), validando o bloqueio contra alucinações.

    Digite sair ou pressione Ctrl + C para encerrar.