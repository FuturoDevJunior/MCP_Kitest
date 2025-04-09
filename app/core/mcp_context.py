from typing import Dict, List, Optional
from pydantic import BaseModel
import ast
from app.models.test_models import TestCase, TestSuite, ValidationIssue


class MCPContext:
    """Gerenciador de contexto MCP para testes."""

    def __init__(self):
        self.test_context: Dict[str, TestContext] = {}
        self.memory_store: Dict[str, MemoryItem] = {}
        self.current_session: Optional[str] = None

    async def create_session(self, session_id: str) -> None:
        """Cria uma nova sessão de teste."""
        self.test_context[session_id] = TestContext()
        self.current_session = session_id

    async def store_test_result(
        self, test_case: TestCase, result: bool, issues: List[ValidationIssue]
    ) -> None:
        """Armazena o resultado de um teste na memória."""
        if not self.current_session:
            return

        context = self.test_context[self.current_session]
        memory_item = MemoryItem(
            test_case=test_case,
            success=result,
            issues=issues,
            improvements=self._generate_improvements(issues),
        )
        context.add_memory(test_case.name, memory_item)

    async def get_test_suggestions(self, code: str) -> List[str]:
        """Gera sugestões de teste baseadas no histórico."""
        if not self.current_session:
            return []

        context = self.test_context[self.current_session]
        return context.generate_suggestions(code)

    async def learn_from_success(self, test_case: TestCase) -> None:
        """Aprende com testes bem-sucedidos."""
        if not self.current_session:
            return

        context = self.test_context[self.current_session]
        context.learn_pattern(test_case)

    def _generate_improvements(self, issues: List[ValidationIssue]) -> List[str]:
        """Gera sugestões de melhoria baseadas nos problemas encontrados."""
        improvements = []
        for issue in issues:
            if issue.type == "no_mocks":
                improvements.append("Utilize mocks para isolar dependências externas")
            elif issue.type == "shared_state":
                improvements.append("Evite estado compartilhado usando fixtures")
            elif issue.type == "naming_convention":
                improvements.append(
                    "Siga a convenção de nomenclatura 'test_*' para funções de teste"
                )
            elif issue.type == "no_assertions":
                improvements.append(
                    "Adicione asserções para validar o comportamento esperado"
                )
            elif issue.type == "no_docstring":
                improvements.append("Documente o propósito do teste com uma docstring")
        return improvements


class TestContext:
    """Contexto de teste para uma sessão."""

    def __init__(self):
        self.memories: Dict[str, MemoryItem] = {}
        self.patterns: List[TestPattern] = []

    def add_memory(self, test_name: str, memory: "MemoryItem") -> None:
        """Adiciona uma memória ao contexto."""
        self.memories[test_name] = memory

    def learn_pattern(self, test_case: TestCase) -> None:
        """Aprende um padrão de teste bem-sucedido."""
        pattern = TestPattern.from_test_case(test_case)
        if pattern not in self.patterns:
            self.patterns.append(pattern)

    def generate_suggestions(self, code: str) -> List[str]:
        """Gera sugestões baseadas em padrões aprendidos."""
        suggestions = []
        ast_tree = ast.parse(code)

        # Analisa o código em busca de padrões conhecidos
        for pattern in self.patterns:
            if pattern.matches(ast_tree):
                suggestions.append(
                    f"Considere adicionar um teste similar a '{pattern.name}' "
                    f"para validar {pattern.description}"
                )

        return suggestions


class MemoryItem(BaseModel):
    """Item de memória para armazenar resultados de teste."""

    test_case: TestCase
    success: bool
    issues: List[ValidationIssue]
    improvements: List[str]


class TestPattern:
    """Padrão de teste aprendido."""

    def __init__(self, name: str, description: str, structure: Dict):
        self.name = name
        self.description = description
        self.structure = structure

    @classmethod
    def from_test_case(cls, test_case: TestCase) -> "TestPattern":
        """Cria um padrão a partir de um caso de teste."""
        structure = {
            "has_setup": bool(test_case.setup),
            "assertion_count": len(test_case.assertions),
            "has_dependencies": bool(test_case.dependencies),
        }
        return cls(
            name=test_case.name, description=test_case.description, structure=structure
        )

    def matches(self, tree: ast.AST) -> bool:
        """Verifica se um código corresponde ao padrão."""
        # Implementação básica de correspondência de padrões
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self.structure["has_setup"] and not any(
                    isinstance(stmt, ast.FunctionDef) and stmt.name == "setUp"
                    for stmt in node.body
                ):
                    return False

                assertion_count = sum(
                    1 for stmt in ast.walk(node) if isinstance(stmt, ast.Assert)
                )
                if assertion_count < self.structure["assertion_count"]:
                    return False

        return True
