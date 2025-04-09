import ast
from typing import List, Tuple, Optional
from app.models.test_models import ValidationIssue, TestValidationResponse, TestCase
from app.core.mcp_context import MCPContext


class TestValidator:
    """Validador de testes unitários."""

    def __init__(self):
        self.isolation_checker = IsolationChecker()
        self.quality_checker = QualityChecker()
        self.mcp_context = MCPContext()

    async def validate_test(
        self, test_code: str, source_code: str = None
    ) -> TestValidationResponse:
        """Valida um teste unitário."""
        issues = []

        # Parse do código
        try:
            test_tree = ast.parse(test_code)
        except SyntaxError as e:
            return TestValidationResponse(
                is_valid=False,
                issues=[
                    ValidationIssue(
                        type="syntax_error",
                        description=f"Erro de sintaxe: {str(e)}",
                        line_number=e.lineno,
                        suggestion="Corrija a sintaxe do código",
                    )
                ],
                isolation_score=0.0,
                maintainability_score=0.0,
            )

        # Validação de isolamento
        isolation_issues = self.isolation_checker.check_isolation(test_tree)
        issues.extend(isolation_issues)

        # Validação de qualidade
        quality_issues = self.quality_checker.check_quality(test_tree)
        issues.extend(quality_issues)

        # Cálculo de scores
        isolation_score = self._calculate_isolation_score(isolation_issues)
        maintainability_score = self._calculate_maintainability_score(quality_issues)

        # Extrai informações do teste para o MCP
        test_info = self._extract_test_info(test_tree)
        if test_info:
            # Armazena o resultado no contexto MCP
            await self.mcp_context.store_test_result(
                test_case=test_info, result=len(issues) == 0, issues=issues
            )

        return TestValidationResponse(
            is_valid=len(issues) == 0,
            issues=issues,
            isolation_score=isolation_score,
            maintainability_score=maintainability_score,
        )

    def _extract_test_info(self, tree: ast.AST) -> Optional[TestCase]:
        """Extrai informações do teste para o MCP."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                return TestCase(
                    name=node.name,
                    description=ast.get_docstring(node) or "No description available",
                    test_code=self._get_node_source(node),
                    assertions=self._extract_assertions(node),
                    dependencies=self._extract_dependencies(node),
                )
        return None

    def _get_node_source(self, node: ast.AST) -> str:
        """Obtém o código fonte de um nó AST."""
        return ast.unparse(node)

    def _extract_assertions(self, node: ast.AST) -> List[str]:
        """Extrai asserções de um nó AST."""
        assertions = []
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                assertions.append(ast.unparse(child))
        return assertions

    def _extract_dependencies(self, node: ast.AST) -> List[str]:
        """Extrai dependências de um nó AST."""
        dependencies = []
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for name in child.names:
                    dependencies.append(name.name)
            elif isinstance(child, ast.ImportFrom):
                dependencies.append(child.module)
        return dependencies

    def _calculate_isolation_score(self, issues: List[ValidationIssue]) -> float:
        """Calcula a pontuação de isolamento baseado nos problemas encontrados."""
        if not issues:
            return 1.0

        # Cada problema reduz a pontuação em 0.1
        return max(0.0, 1.0 - (len(issues) * 0.1))

    def _calculate_maintainability_score(self, issues: List[ValidationIssue]) -> float:
        """Calcula a pontuação de manutenibilidade baseado nos problemas encontrados."""
        if not issues:
            return 1.0

        # Cada problema reduz a pontuação em 0.1
        return max(0.0, 1.0 - (len(issues) * 0.1))


class IsolationChecker:
    """Verificador de isolamento de testes."""

    def check_isolation(self, tree: ast.AST) -> List[ValidationIssue]:
        """Verifica o isolamento do teste."""
        issues = []

        # Verifica uso de mocks
        mock_visitor = MockUsageVisitor()
        mock_visitor.visit(tree)
        if not mock_visitor.has_mocks and mock_visitor.has_external_calls:
            issues.append(
                ValidationIssue(
                    type="no_mocks",
                    description="Teste faz chamadas externas sem usar mocks",
                    line_number=None,
                    suggestion="Utilize mocks para isolar dependências externas",
                )
            )

        # Verifica estado compartilhado
        shared_state_visitor = SharedStateVisitor()
        shared_state_visitor.visit(tree)
        if shared_state_visitor.has_shared_state:
            issues.append(
                ValidationIssue(
                    type="shared_state",
                    description="Teste usa estado compartilhado",
                    line_number=shared_state_visitor.shared_state_line,
                    suggestion="Use fixtures ou setup/teardown para gerenciar estado",
                )
            )

        return issues


class QualityChecker:
    """Verificador de qualidade de testes."""

    def check_quality(self, tree: ast.AST) -> List[ValidationIssue]:
        """Verifica a qualidade do teste."""
        issues = []

        # Verifica nomenclatura
        naming_visitor = NamingConventionVisitor()
        naming_visitor.visit(tree)
        issues.extend(naming_visitor.issues)

        # Verifica asserções
        assertion_visitor = AssertionVisitor()
        assertion_visitor.visit(tree)
        if not assertion_visitor.has_assertions:
            issues.append(
                ValidationIssue(
                    type="no_assertions",
                    description="Teste não contém asserções",
                    line_number=None,
                    suggestion="Adicione asserções para verificar o comportamento esperado",
                )
            )

        # Verifica documentação
        doc_visitor = DocumentationVisitor()
        doc_visitor.visit(tree)
        if not doc_visitor.has_docstring:
            issues.append(
                ValidationIssue(
                    type="no_docstring",
                    description="Teste não possui docstring",
                    line_number=None,
                    suggestion="Adicione uma docstring descrevendo o propósito do teste",
                )
            )

        return issues


class MockUsageVisitor(ast.NodeVisitor):
    """Visitante para verificar uso de mocks."""

    def __init__(self):
        self.has_mocks = False
        self.has_external_calls = False

    def visit_Call(self, node: ast.Call):
        # Verifica se é uma chamada de mock
        if isinstance(node.func, ast.Name) and node.func.id in [
            "Mock",
            "patch",
            "MagicMock",
        ]:
            self.has_mocks = True
        # Verifica se é uma chamada externa
        elif isinstance(node.func, ast.Attribute):
            self.has_external_calls = True
        self.generic_visit(node)


class SharedStateVisitor(ast.NodeVisitor):
    """Visitante para verificar estado compartilhado."""

    def __init__(self):
        self.has_shared_state = False
        self.shared_state_line = None

    def visit_Global(self, node: ast.Global):
        self.has_shared_state = True
        self.shared_state_line = node.lineno

    def visit_ClassDef(self, node: ast.ClassDef):
        # Verifica variáveis de classe
        for item in node.body:
            if isinstance(item, ast.Assign) and not isinstance(
                item.targets[0], ast.Name
            ):
                self.has_shared_state = True
                self.shared_state_line = item.lineno


class NamingConventionVisitor(ast.NodeVisitor):
    """Visitante para verificar convenções de nomenclatura."""

    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if not node.name.startswith("test_"):
            self.issues.append(
                ValidationIssue(
                    type="naming_convention",
                    description=f"Nome da função '{node.name}' não segue convenção",
                    line_number=node.lineno,
                    suggestion="Funções de teste devem começar com 'test_'",
                )
            )


class AssertionVisitor(ast.NodeVisitor):
    """Visitante para verificar asserções."""

    def __init__(self):
        self.has_assertions = False

    def visit_Assert(self, node: ast.Assert):
        self.has_assertions = True


class DocumentationVisitor(ast.NodeVisitor):
    """Visitante para verificar documentação."""

    def __init__(self):
        self.has_docstring = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if ast.get_docstring(node):
            self.has_docstring = True
