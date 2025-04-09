from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class TestFramework(str, Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"


class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Código fonte a ser analisado")
    framework: TestFramework = Field(
        default=TestFramework.PYTEST, description="Framework de teste a ser utilizado"
    )
    file_path: Optional[str] = Field(None, description="Caminho do arquivo (opcional)")


class TestCase(BaseModel):
    name: str = Field(..., description="Nome do caso de teste")
    description: str = Field(..., description="Descrição do que o teste verifica")
    setup: Optional[str] = Field(None, description="Código de setup necessário")
    test_code: str = Field(..., description="Código do teste")
    assertions: List[str] = Field(..., description="Lista de asserções do teste")
    dependencies: List[str] = Field(
        default_list=[], description="Dependências necessárias"
    )


class TestSuite(BaseModel):
    class_name: str = Field(..., description="Nome da classe de teste")
    description: str = Field(..., description="Descrição da suite de testes")
    test_cases: List[TestCase] = Field(..., description="Lista de casos de teste")
    imports: List[str] = Field(..., description="Imports necessários")
    fixtures: Dict[str, str] = Field(
        default_factory=dict, description="Fixtures necessárias"
    )


class TestAnalysisResponse(BaseModel):
    test_suite: TestSuite
    coverage_estimate: float = Field(..., description="Estimativa de cobertura")
    suggestions: List[str] = Field(..., description="Sugestões de melhoria")
    complexity_score: float = Field(..., description="Pontuação de complexidade")


class TestValidationRequest(BaseModel):
    test_code: str = Field(..., description="Código do teste a ser validado")
    source_code: Optional[str] = Field(None, description="Código fonte relacionado")
    framework: TestFramework = Field(default=TestFramework.PYTEST)


class ValidationIssue(BaseModel):
    type: str = Field(..., description="Tipo do problema")
    description: str = Field(..., description="Descrição do problema")
    line_number: Optional[int] = Field(None, description="Número da linha")
    suggestion: str = Field(..., description="Sugestão de correção")


class TestValidationResponse(BaseModel):
    is_valid: bool = Field(..., description="Indica se o teste é válido")
    issues: List[ValidationIssue] = Field(
        default_factory=list, description="Problemas encontrados"
    )
    isolation_score: float = Field(..., description="Pontuação de isolamento")
    maintainability_score: float = Field(
        ..., description="Pontuação de manutenibilidade"
    )
