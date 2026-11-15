# Assistente Técnico TOTVS Protheus (RAG)

> Projeto do curso **Instituto Hardware BR**.

Assistente virtual em Python focado em suporte técnico para configuração do **TOTVS Protheus**. Utiliza arquitetura desacoplada e injeção estrita de contexto (RAG) para responder de forma objetiva, rápida e **sem alucinações**.

## Arquitetura

- **Interface:** aplicação web em Python com chat, construída com [Streamlit](https://streamlit.io/). Abre no navegador.
- **Fidelidade à base de conhecimento:** temperatura travada em `0.0` e regras no prompt que obrigam o modelo a responder somente com o contexto fornecido.
- **Inferência (LLM):** desacoplada via API. O endereço do servidor e o modelo são definidos por variáveis de ambiente (`LLM_HOST` e `LLM_MODEL`), então o servidor pode ser local ou remoto (ex.: Google Colab via túnel) sem alterar o código.
- **Resiliência:** a chamada ao servidor tem tempo limite (5 s para conectar, 120 s para responder) e erros de conexão, timeout e resposta são tratados com mensagens claras na tela.

## ✅ Pré-requisitos

- Python 3.10 ou superior
- Um servidor de LLM em execução (local ou remoto), acessível pela rede, com um modelo instalado (ex.: `qwen2.5:7b`)

## ⚙️ Instalação e configuração

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/diegpo/hbr.git
   cd hbr
   ```

2. **Crie e ative o ambiente virtual:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/WSL/macOS
   # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente.** Copie o arquivo de exemplo e ajuste os valores:

   ```bash
   cp .env.example .env
   ```

   Conteúdo do `.env`:

   ```env
   LLM_HOST=http://localhost:11434
   LLM_MODEL=qwen2.5:7b
   ```

   | Variável    | O que é                                   |
   | ----------- | ----------------------------------------- |
   | `LLM_HOST`  | Endereço do servidor de LLM               |
   | `LLM_MODEL` | Nome do modelo que será usado nas respostas |

   > ⚠️ O arquivo `.env` não é enviado ao GitHub (está no `.gitignore`). Se o endereço do servidor mudar, basta editar o `.env`.

## ▶️ Como executar

```bash
streamlit run main.py
```

O navegador abrirá o chat (normalmente em `http://localhost:8501`). Para encerrar, pressione `Ctrl + C` no terminal.

## 🐳 Executando com Docker

```bash
docker build -t hbr .
docker run --rm -p 8080:80 --env-file .env hbr
```

Depois acesse `http://localhost:8080`.

> Dentro do container, `localhost` aponta para o próprio container. Se o servidor de LLM roda na sua máquina, use o endereço dela (ou `host.docker.internal`) no `LLM_HOST`.

## 🧪 Como testar

Com o servidor de LLM ativo, faça estas perguntas no chat:

| Tipo de pergunta | Exemplo | Resultado esperado |
| --- | --- | --- |
| Dentro da base de conhecimento | "Qual seção do appserver.ini configuro para o REST?" | Resposta direta usando apenas os dados cadastrados (`[HTTPREST]`). |
| Fora da base de conhecimento | "Como configurar o e-mail no Protheus?" | `Não tenho essa informação na minha base de conhecimento.` |
| Servidor indisponível | Coloque um `LLM_HOST` inválido no `.env` | Aviso de falha de conexão em poucos segundos, sem travar. |

## 📁 Estrutura do projeto

```text
hbr/
├── main.py            # Aplicação (interface, prompt e chamada ao servidor de LLM)
├── requirements.txt   # Dependências Python
├── Dockerfile         # Imagem para executar em container
├── .env.example       # Modelo do arquivo de variáveis de ambiente
└── README.md
```