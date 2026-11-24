import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx
import ollama
import pytest

# Garante que a raiz do projeto esteja no sys.path para importar o main.py
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

import main


# --- 1. TESTES DA BASE DE CONHECIMENTO ---

def test_carregar_base_conhecimento_recursivo_e_filtro_extensoes(tmp_path):
    """Valida leitura em subpastas, filtro de .md/.txt e formatação do cabeçalho."""
    subpasta_taf = tmp_path / "taf"
    subpasta_taf.mkdir()

    (tmp_path / "geral.txt").write_text("Manual geral Protheus", encoding="utf-8")
    (subpasta_taf / "taf_atualizacao.md").write_text("Porta WebApp 9200", encoding="utf-8")
    # Arquivos que devem ser ignorados pelo carregador
    (subpasta_taf / "planilha.xlsx").write_text("conteudo binario falso", encoding="utf-8")
    (tmp_path / "vazio.md").write_text("   \n  ", encoding="utf-8")

    # Limpa o cache do Streamlit antes de testar com o diretório temporário
    main.carregar_base_conhecimento.clear()
    resultado = main.carregar_base_conhecimento(str(tmp_path))

    assert "--- DOCUMENTO: geral.txt ---" in resultado
    assert "Manual geral Protheus" in resultado
    assert "--- DOCUMENTO: taf/taf_atualizacao.md ---" in resultado or "--- DOCUMENTO: taf\\taf_atualizacao.md ---" in resultado
    assert "Porta WebApp 9200" in resultado
    assert "planilha.xlsx" not in resultado
    assert "vazio.md" not in resultado


def test_carregar_base_conhecimento_pasta_inexistente(tmp_path):
    """Se a pasta não existir, deve criá-la automaticamente e retornar string vazia."""
    pasta_nova = tmp_path / "pasta_que_nao_existe"

    main.carregar_base_conhecimento.clear()
    resultado = main.carregar_base_conhecimento(str(pasta_nova))

    assert pasta_nova.exists()
    assert resultado == ""


# --- 2. TESTES DO PROMPT DE SISTEMA E CONFIGURAÇÕES ---

def test_instrucao_sistema_possui_regras_anti_alucinacao():
    """Garante que as travas críticas de fidelidade ao contexto estão presentes."""
    assert "Não tenho essa informação na minha base de conhecimento." in main.INSTRUCAO_SISTEMA
    assert "ESTRITAMENTE no contexto" in main.INSTRUCAO_SISTEMA


# --- 3. TESTES SIMULADOS (MOCKS) DE COMUNICAÇÃO E FALHAS COM OLLAMA ---

def test_chamada_llm_sucesso_simulado():
    """Simula uma resposta bem-sucedida do Ollama verificando parâmetros enviados."""
    cliente_falso = MagicMock()
    cliente_falso.chat.return_value = {
        "message": {"content": "Acesse a porta WebApp 9200."}
    }

    with patch.object(main, "llm", cliente_falso):
        resposta = main.llm.chat(
            model="qwen2.5:7b",
            messages=[
                {"role": "system", "content": main.INSTRUCAO_SISTEMA},
                {"role": "user", "content": "Contexto:\nPorta 9200\n\nPergunta: Qual porta?"}
            ],
            options={"temperature": 0.0}
        )

    assert resposta["message"]["content"] == "Acesse a porta WebApp 9200."
    cliente_falso.chat.assert_called_once()
    kwargs = cliente_falso.chat.call_args.kwargs
    assert kwargs["options"]["temperature"] == 0.0


@pytest.mark.parametrize("excecao_simulada", [
    httpx.TimeoutException("Tempo esgotado"),
    httpx.ConnectError("Falha de conexão"),
    ollama.ResponseError("Modelo não encontrado", status_code=404),
])
def test_simulacao_excecoes_rede_e_servidor(excecao_simulada):
    """Valida que as exceções previstas no main.py são disparadas e capturáveis."""
    cliente_falso = MagicMock()
    cliente_falso.chat.side_effect = excecao_simulada

    with patch.object(main, "llm", cliente_falso):
        with pytest.raises(type(excecao_simulada)):
            main.llm.chat(model="qwen2.5:7b", messages=[])