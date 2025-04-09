from fastapi import APIRouter, HTTPException, Depends
from app.models.test_models import (
    CodeAnalysisRequest,
    TestValidationRequest,
    TestAnalysisResponse,
    TestValidationResponse,
    TestFramework,
)
from app.services.test_analyzer import TestAnalyzer
from app.services.test_generator import TestGenerator
from app.services.test_validator import TestValidator
from app.core.mcp_context import MCPContext
from typing import Optional
import uuid

router = APIRouter()
analyzer = TestAnalyzer()
generator = TestGenerator()
validator = TestValidator()
mcp_context = MCPContext()


async def get_session_id(session_id: Optional[str] = None) -> str:
    """Obtém ou cria um ID de sessão."""
    if not session_id:
        session_id = str(uuid.uuid4())
        await mcp_context.create_session(session_id)
    return session_id


@router.post("/analyze", response_model=TestAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest, session_id: str = Depends(get_session_id)
):
    """
    Analisa o código fonte e sugere casos de teste.
    """
    try:
        test_suite = await analyzer.analyze_code(request.code, request.framework)

        # Armazena o contexto da análise
        for test_case in test_suite.test_cases:
            await mcp_context.learn_from_success(test_case)

        return TestAnalysisResponse(
            test_suite=test_suite,
            coverage_estimate=0.8,  # Valor exemplo, deve ser calculado
            suggestions=await mcp_context.get_test_suggestions(request.code),
            complexity_score=1.0,  # Valor exemplo, deve ser calculado
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate")
async def generate_tests(
    request: CodeAnalysisRequest, session_id: str = Depends(get_session_id)
):
    """
    Gera uma suite de testes completa para o código fornecido.
    """
    try:
        test_code = await generator.generate_test_suite(request.code, request.framework)
        return {"test_code": test_code, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate", response_model=TestValidationResponse)
async def validate_test(
    request: TestValidationRequest, session_id: str = Depends(get_session_id)
):
    """
    Valida um teste unitário e fornece sugestões de melhoria.
    """
    try:
        validation_response = await validator.validate_test(
            request.test_code, request.source_code
        )

        # Adiciona sugestões do MCP
        if validation_response.is_valid:
            suggestions = await mcp_context.get_test_suggestions(request.test_code)
            if suggestions:
                validation_response.issues.extend(
                    [
                        ValidationIssue(
                            type="suggestion",
                            description=suggestion,
                            line_number=None,
                            suggestion=suggestion,
                        )
                        for suggestion in suggestions
                    ]
                )

        return validation_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/frameworks")
async def list_frameworks():
    """
    Lista os frameworks de teste suportados.
    """
    return {"frameworks": [framework.value for framework in TestFramework]}


@router.get("/templates/{framework}")
async def get_template(
    framework: TestFramework, session_id: str = Depends(get_session_id)
):
    """
    Retorna um template básico de teste para o framework especificado.
    """
    templates = {
        TestFramework.PYTEST: """import pytest

def test_example():
    \"""
    Exemplo de teste usando pytest.
    \"""
    # Arrange
    expected = True
    
    # Act
    result = True
    
    # Assert
    assert result == expected
""",
        TestFramework.UNITTEST: """import unittest

class TestExample(unittest.TestCase):
    \"""
    Exemplo de teste usando unittest.
    \"""
    
    def setUp(self):
        pass
    
    def test_example(self):
        # Arrange
        expected = True
        
        # Act
        result = True
        
        # Assert
        self.assertEqual(result, expected)
""",
    }

    return {
        "template": templates.get(framework, "Framework não suportado"),
        "session_id": session_id,
    }


@router.get("/context/{session_id}/suggestions")
async def get_context_suggestions(session_id: str):
    """
    Obtém sugestões do contexto MCP para uma sessão específica.
    """
    try:
        await mcp_context.create_session(session_id)
        suggestions = await mcp_context.get_test_suggestions("")
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
