# Assistente Virtual TOTVS Protheus

> Projeto desenvolvido para o curso **Instituto Hardware BR**.

Assistente virtual em Python especializado em suporte técnico e infraestrutura Cloud do **TOTVS Protheus**. Utiliza arquitetura desacoplada e injeção estrita de contexto (RAG) para responder de forma objetiva, rápida e **sem alucinações**.

---

## 📑 Sumário

1. [Problema Escolhido](#1-problema-escolhido)
2. [Usuário ou Público](#2-usuário-ou-público)
3. [Justificativa para Utilizar um LLM](#3-justificativa-para-utilizar-um-llm)
4. [Funcionamento da Solução](#4-funcionamento-da-solução)
5. [Limites do Projeto](#5-limites-do-projeto)
6. [Instalação](#6-instalação)
7. [Configuração do Acesso ao LLM e Testes](#7-configuração-do-acesso-ao-llm-escolhido-e-indicação-dos-testes-reais-e-simulados)
8. [Execução](#8-execução)
9. [Exemplos de Entrada e Saída](#9-exemplos-de-entrada-e-saída)
10. [Execução dos Testes](#10-execução-dos-testes)
11. [Limitações Conhecidas](#11-limitações-conhecidas)
12. [Link para o Vídeo](#12-link-para-o-vídeo)

---

## 1. Problema Escolhido

No dia a dia de suporte técnico e administração do ERP **TOTVS Protheus**, informações críticas de configuração — como chaves do arquivo `appserver.ini`, instâncias de serviços (`HTTPJOB`), módulos (`SIGACFG`) e parâmetros (`MV_`) — ficam dispersas em dezenas de manuais operacionais. Consultar esses documentos manualmente durante um atendimento gera lentidão, e qualquer imprecisão na grafia de um parâmetro ou seção pode comprometer a disponibilidade do ambiente.

## 2. Usuário ou Público

- Analistas de suporte técnico (N1 e N2) que atendem chamados de infraestrutura e configuração Protheus.
- Administradores de ambientes Cloud TOTVS Protheus.
- Consultores de implantação que precisam validar rapidamente parâmetros padrão do sistema.

## 3. Justificativa para Utilizar um LLM

Uma busca tradicional por palavras-chave exige que o usuário saiba exatamente o nome técnico do parâmetro ou da seção antes de pesquisar. O uso de um **LLM (Large Language Model)** combinado com **RAG (Retrieval-Augmented Generation)** permite que o analista faça perguntas curtas ou em linguagem natural (como *"como configuro email?"* ou apenas *"rest"*), compreenda a intenção da solicitação, cruze múltiplos arquivos da base de conhecimento e devolva um passo a passo estruturado preservando a grafia exata dos parâmetros técnicos, sem inventar informações externas.

## 4. Funcionamento da Solução

| Componente | Tecnologia | Descrição |
|---|---|---|
| **Interface Web** | `Streamlit` | Tela de chat interativa com persistência de histórico na sessão (`st.session_state`) e barra lateral para status e recarga dinâmica dos documentos sem reiniciar a aplicação. |
| **Base de Conhecimento Desacoplada** | `pathlib` + `@st.cache_data` | Varredura recursiva (`rglob`) de arquivos `.md` e `.txt` organizados em subpastas dentro de `base_conhecimento/`, consolidando os manuais com identificação da origem de cada documento. |
| **Controle de Alucinação** | Prompt de sistema | Temperatura travada em `0.0` e diretrizes estritas que obrigam o modelo a responder exclusivamente com base nos documentos carregados, recusando perguntas fora do escopo. |
| **Inferência Desacoplada** | `Ollama` + `@st.cache_resource` | Conexão persistente em cache via API, configurada por variáveis de ambiente (`LLM_HOST` e `LLM_MODEL`), permitindo apontar para um servidor local ou remoto sem alterar o código-fonte. |
| **Resiliência** | Timeouts e exceções | Timeouts configurados (`5.0s` para conexão e `120.0s` para resposta) e tratamento explícito de exceções de rede, timeout e erros da API. |

## 5. Limites do Projeto

- **Escopo estritamente documental:** o assistente não executa comandos no servidor Protheus, não altera arquivos `.ini` diretamente e não consulta bancos de dados do ERP; atua exclusivamente como copiloto de consulta técnica.
- **Formato de entrada:** lê apenas arquivos textuais (`.md` e `.txt`) em codificação UTF-8 armazenados na pasta `base_conhecimento/`.
- **Tamanho da base na arquitetura atual:** projetado para injeção direta de contexto em manuais enxutos, sem indexação vetorial em disco nesta versão.

## 6. Instalação

### Pré-requisitos

- Python 3.10 ou superior (ou Docker)
- Servidor Ollama em execução (local ou remoto) com um modelo instalado (ex.: `qwen2.5:7b`)

### Passo a passo

**1. Clone o repositório:**

```bash
git clone https://github.com/diegpo/hbr.git
cd hbr
```

**2. Crie e ative o ambiente virtual:**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/WSL/macOS
# No Windows: .venv\Scripts\activate
```

**3. Instale as dependências:**

```bash
pip install -r requirements.txt
```

## 7. Configuração do Acesso ao LLM Escolhido e Indicação dos Testes Reais e Simulados

### Configuração das variáveis de ambiente

Crie o arquivo `.env` a partir do modelo `.env.example`:

```bash
cp .env.example .env
```

Preencha o endereço do servidor Ollama e o modelo desejado:

```env
# Para uso local (WSL/Linux/Windows):
LLM_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:7b

# Para uso no ambiente de nuvem da plataforma (Softex/HBR):
# LLM_HOST=https://llm-internal.softex:9001
```

| Variável | Descrição |
|---|---|
| `LLM_HOST` | Endereço HTTP/HTTPS do servidor Ollama |
| `LLM_MODEL` | Identificador do modelo LLM na instância |

> 🔒 **Nota de segurança:** o arquivo `.env` e os manuais operacionais internos ficam bloqueados pelo `.gitignore`, mantendo apenas o arquivo modelo `base_conhecimento/exemplo_apresentacao.md` versionado no repositório.

### Indicação dos testes reais e simulados

- **Testes reais (integrados):** executados com o servidor Ollama ativo rodando o modelo `qwen2.5:7b`, validando a leitura recursiva de manuais reais em subpastas (`base_conhecimento/configurador/` e `base_conhecimento/webservice/`), a preservação da sintaxe AdvPL/INI e o botão de recarga de cache.
- **Testes simulados (falhas e limites):** executados simulando indisponibilidade de rede (`LLM_HOST` apontando para porta inexistente), diretório `base_conhecimento/` vazio e perguntas propositalmente fora do escopo, para validar o bloqueio de alucinações e as mensagens amigáveis de erro.

## 8. Execução

### Execução local (Python / Streamlit)

```bash
streamlit run main.py
```

Acesse no navegador: <http://localhost:8501>. Para encerrar, pressione `Ctrl + C`.

### Execução via Docker (porta 80)

```bash
docker build -t 2014644alunounivespbr:latest .
docker run --rm -p 8080:80 --env-file .env 2014644alunounivespbr:latest
```

Acesse no navegador: <http://localhost:8080>.

## 9. Exemplos de Entrada e Saída

### Exemplo 1 — Pergunta curta dentro da base (WebService REST)

**Entrada:**

```text
rest
```

**Saída:**

```text
Para configurar o WebService REST no Protheus, abra o arquivo appserver.ini, adicione a seção [HTTPREST] com a porta desejada, adicione a chave [ONSTART] com jobs=HTTPJOB, e reinicie o serviço do Appserver. URL padrão de teste: http://localhost:8084/rest.
```

### Exemplo 2 — Consulta de parâmetros em subpasta (Configurador / E-mail)

**Entrada:**

```text
Como configuro um email?
```

**Saída:**

```text
Para configurar um email no Protheus, siga estes passos:
1. Acesse o módulo Configurador (SIGACFG).
2. Navegue até o menu: Ambiente > Cadastros > Parâmetros (ou Ambiente > E-mail / Proxy > Configurar E-mail).
3. Configure os parâmetros principais de envio (SMTP):
  - MV_RELSERV: Endereço do servidor SMTP e porta (ex: smtp.seudominio.com.br:587).
  - MV_RELACNT: Conta de e-mail utilizada para autenticação no servidor.
  - MV_RELPSW: Senha da conta de e-mail configurada.
  - MV_RELFROM: Endereço de e-mail que aparecerá como remetente.
  - MV_RELAUTH: Define se o servidor SMTP exige autenticação (.T. para Sim, .F. para Não).
  - MV_RELTLS: Habilita conexão segura TLS (.T. para Sim, .F. para Não).
  - MV_RELSSL: Habilita conexão segura SSL (.T. para Sim, .F. para Não).
4. Salve as alterações e realize um teste de envio pela rotina de configuração de e-mail.
```

### Exemplo 3 — Pergunta fora da base de conhecimento (bloqueio de alucinação)

**Entrada:**

```text
Pode me ajudar com um portal?
```

**Saída:**

```text
Não tenho essa informação na minha base de conhecimento.
```

### Exemplo 4 — Falha de conexão simulada (`LLM_HOST` inválido)

**Entrada:**

```text
Oi
```

**Saída:**

```text
🔌 Não consegui conectar na LLM interna. Verifique se ela está rodando e se o endereço HOST no arquivo .env está correto
```

## 10. Execução dos Testes

Para reproduzir a bateria de validação da aplicação:

1. **Teste de carga da base:** inicie a aplicação (`streamlit run main.py`) e verifique na barra lateral a mensagem verde *"Base carregada com sucesso."*.
2. **Teste de aderência ao contexto:** envie perguntas sobre tópicos documentados (ex.: *"Sabe a respeito de e-mail?"* ou *"rest"*) e confirme se os parâmetros técnicos retornam com a grafia exata.
3. **Teste de recarga dinâmica:** adicione ou edite um arquivo `.md` em `base_conhecimento/`, clique em **"Recarregar arquivos"** na barra lateral e faça uma pergunta sobre o novo conteúdo, sem reiniciar o terminal.
4. **Teste de recusa (anti-alucinação):** pergunte algo não documentado (ex.: *"Eu tenho um erro"* ou *"Como configurar portal?"*) e valide se a resposta é estritamente *"Não tenho essa informação na minha base de conhecimento."*.
5. **Teste de resiliência de rede:** altere `LLM_HOST` no `.env` para uma porta inativa (ex.: `http://localhost:9999`), reinicie a aplicação e envie uma mensagem para validar o aviso de erro em até 5 segundos.

## 11. Limitações Conhecidas

- **Crescimento da base de conhecimento (janela de contexto):** como todos os arquivos da pasta `base_conhecimento/` são concatenados e enviados integralmente a cada pergunta, bases muito extensas (acima de 20–50 manuais) podem atingir o limite de tokens (`num_ctx`) ou aumentar o tempo de resposta em modelos menores (7B). Para escalar além desse volume, será necessário implementar filtragem por ranqueamento léxico (BM25) ou busca vetorial (ChromaDB).
- **Ausência de memória conversacional na inferência:** embora a interface web exiba todo o histórico do diálogo na tela (`st.session_state`), apenas a pergunta atual e o contexto documental são enviados à API do LLM, para evitar perda de foco em modelos compactos.
- **Leitura restrita a texto puro:** documentos em PDF, Word (`.docx`) ou imagens não são processados nativamente sem conversão prévia para Markdown (`.md`) ou `.txt`.

## 12. Link para o Vídeo

🎥 **Demonstração em vídeo:** [Inserir aqui o link do vídeo publicado no YouTube / Google Drive]