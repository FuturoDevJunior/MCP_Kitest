# MCP Test Assistant

[![CI/CD](https://github.com/yourusername/mcpteste/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/mcpteste/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourusername/mcpteste/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/mcpteste)
[![Documentation Status](https://github.com/yourusername/mcpteste/workflows/docs/badge.svg)](https://yourusername.github.io/mcpteste/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

📚 [Documentação Completa](https://yourusername.github.io/mcpteste/)

Um servidor MCP (Memory, Computation, Protocol) especializado em auxiliar desenvolvedores a criar testes unitários de qualidade, seguindo as melhores práticas e princípios SOLID.

## 🌟 Características

- 🔍 Análise automática de código fonte
- ✨ Geração inteligente de testes unitários
- 🎯 Validação de qualidade e isolamento
- 🧠 Aprendizado contínuo através do protocolo MCP
- 📝 Sugestões personalizadas baseadas em contexto
- 🔄 Suporte a múltiplos frameworks (pytest e unittest)

## 🚀 Tecnologias

- Python 3.8+
- FastAPI
- Pydantic
- AST (Abstract Syntax Tree)
- pytest
- unittest

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mcp-test-assistant.git
cd mcp-test-assistant
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute o servidor:
```bash
uvicorn main:app --reload
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Endpoints Principais

#### 1. Análise de Código
```http
POST /api/v1/tests/analyze
```
Analisa o código fonte e sugere casos de teste.

#### 2. Geração de Testes
```http
POST /api/v1/tests/generate
```
Gera uma suite de testes completa.

#### 3. Validação de Testes
```http
POST /api/v1/tests/validate
```
Valida a qualidade e isolamento dos testes.

## 💡 Exemplos de Uso

### 1. Analisando um Código

```python
import requests

code = """
def soma(a: int, b: int) -> int:
    return a + b
"""

response = requests.post(
    "http://localhost:8000/api/v1/tests/analyze",
    json={
        "code": code,
        "framework": "pytest"
    }
)

print(response.json())
```

### 2. Gerando Testes

```python
response = requests.post(
    "http://localhost:8000/api/v1/tests/generate",
    json={
        "code": code,
        "framework": "pytest"
    }
)

print(response.json()["test_code"])
```

## 🧪 Executando os Testes

```bash
# Executa todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Gera relatório HTML de cobertura
pytest --cov=app --cov-report=html tests/
```

## 📊 Métricas de Qualidade

O sistema avalia os testes com base em:

- Isolamento (mocks, fixtures)
- Nomenclatura
- Documentação
- Asserções
- Complexidade
- Manutenibilidade

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 🎯 Roadmap

- [ ] Suporte a mais frameworks de teste
- [ ] Integração com CI/CD
- [ ] Interface web
- [ ] Análise de cobertura em tempo real
- [ ] Sugestões baseadas em ML
- [ ] Plugins para IDEs

## 📞 Suporte

- Abra uma issue
- Envie um pull request
- Contribua com a documentação

## ⭐ Agradecimentos

- Comunidade Python
- Contribuidores
- Usuários que fornecem feedback # MCP_Kitest
