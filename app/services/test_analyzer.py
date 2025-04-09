import ast
from typing import List, Dict, Optional
from app.models.test_models import TestCase, TestSuite, TestFramework, ValidationIssue
from app.core.mcp_context import MCPContext


class TestAnalyzer:
    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()
        self.complexity_calculator = ComplexityCalculator()
        self.mcp_context = MCPContext()

    async def analyze_code(self, code: str, framework: TestFramework) -> TestSuite:
        """Analisa o código fonte e gera uma suite de testes apropriada."""
        # Análise do AST para identificar classes e métodos
        ast_tree = ast.parse(code)
        classes = self.ast_analyzer.extract_classes(ast_tree)
        functions = self.ast_analyzer.extract_functions(ast_tree)

        # Gera casos de teste para cada elemento encontrado
        test_cases = []
        imports = ["pytest", "unittest.mock"]

        # Obtém sugestões do contexto MCP
        suggestions = await self.mcp_context.get_test_suggestions(code)

        for cls in classes:
            class_tests = self._generate_class_tests(cls)
            test_cases.extend(class_tests)
            imports.extend(self._get_required_imports(cls))

            # Aprende com os testes gerados
            for test_case in class_tests:
                await self.mcp_context.learn_from_success(test_case)

        for func in functions:
            func_tests = self._generate_function_tests(func)
            test_cases.extend(func_tests)
            imports.extend(self._get_required_imports(func))

            # Aprende com os testes gerados
            for test_case in func_tests:
                await self.mcp_context.learn_from_success(test_case)

        # Aplica sugestões do MCP
        if suggestions:
            for suggestion in suggestions:
                test_cases.append(
                    TestCase(
                        name=f"test_suggested_{len(test_cases)}",
                        description=suggestion,
                        test_code="# TODO: Implementar teste sugerido\npass",
                        assertions=[],
                        dependencies=[],
                    )
                )

        return TestSuite(
            class_name=self._generate_test_class_name(classes, functions),
            description=self._generate_suite_description(classes, functions),
            test_cases=test_cases,
            imports=list(set(imports)),
            fixtures=self._generate_fixtures(classes, functions),
        )

    def _generate_test_class_name(
        self, classes: List[ast.ClassDef], functions: List[ast.FunctionDef]
    ) -> str:
        """Gera um nome apropriado para a classe de teste."""
        if classes:
            return f"Test{classes[0].name}"
        elif functions:
            return f"Test{functions[0].name.capitalize()}"
        return "TestSuite"

    def _generate_suite_description(
        self, classes: List[ast.ClassDef], functions: List[ast.FunctionDef]
    ) -> str:
        """Gera uma descrição significativa para a suite de testes."""
        elements = []
        if classes:
            elements.extend(f"classe {cls.name}" for cls in classes)
        if functions:
            elements.extend(f"função {func.name}" for func in functions)

        return f"Suite de testes para {', '.join(elements)}"

    def _generate_class_tests(self, cls: ast.ClassDef) -> List[TestCase]:
        """Gera casos de teste para uma classe."""
        test_cases = []

        # Teste de inicialização
        init_test = TestCase(
            name=f"test_{cls.name.lower()}_initialization",
            description=f"Testa a inicialização da classe {cls.name}",
            test_code=self._generate_init_test(cls),
            assertions=["assert instance is not None"],
            dependencies=[],
        )
        test_cases.append(init_test)

        # Testes para cada método
        for method in cls.body:
            if isinstance(method, ast.FunctionDef):
                test_cases.extend(self._generate_method_tests(cls.name, method))

        return test_cases

    def _generate_function_tests(self, func: ast.FunctionDef) -> List[TestCase]:
        """Gera casos de teste para uma função."""
        test_cases = []

        # Análise de parâmetros e retorno
        params = [arg.arg for arg in func.args.args]

        # Teste básico
        basic_test = TestCase(
            name=f"test_{func.name}_basic_functionality",
            description=f"Testa a funcionalidade básica de {func.name}",
            test_code=self._generate_basic_function_test(func),
            assertions=self._generate_basic_assertions(func),
            dependencies=[],
        )
        test_cases.append(basic_test)

        # Teste de casos de borda
        edge_test = TestCase(
            name=f"test_{func.name}_edge_cases",
            description=f"Testa casos de borda para {func.name}",
            test_code=self._generate_edge_case_test(func),
            assertions=self._generate_edge_case_assertions(func),
            dependencies=[],
        )
        test_cases.append(edge_test)

        return test_cases

    def _generate_init_test(self, cls: ast.ClassDef) -> str:
        """Gera código para teste de inicialização."""
        return f"""
        # Arrange
        # Act
        instance = {cls.name}()
        # Assert
        assert instance is not None
        """

    def _generate_basic_function_test(self, func: ast.FunctionDef) -> str:
        """Gera código para teste básico de função."""
        params = [arg.arg for arg in func.args.args]
        param_values = ["'test'" if i == 0 else "42" for i in range(len(params))]
        param_str = ", ".join(f"{p}={v}" for p, v in zip(params, param_values))

        return f"""
        # Arrange
        # Act
        result = {func.name}({param_str})
        # Assert
        assert result is not None
        """

    def _generate_basic_assertions(self, func: ast.FunctionDef) -> List[str]:
        """Gera asserções básicas para uma função."""
        return [
            "assert result is not None",
            "assert isinstance(result, (str, int, float, bool, list, dict))",
        ]

    def _generate_edge_case_assertions(self, func: ast.FunctionDef) -> List[str]:
        """Gera asserções para casos de borda."""
        return ["assert result is not None", "assert not isinstance(result, Exception)"]

    def _generate_edge_case_test(self, func: ast.FunctionDef) -> str:
        """Gera código para teste de casos de borda."""
        return f"""
        # Arrange
        with pytest.raises(Exception):
            # Act
            {func.name}(None)
        """

    def _get_required_imports(self, node: ast.AST) -> List[str]:
        """Identifica imports necessários baseado no código."""
        imports = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in ["pytest", "mock", "patch"]:
                    imports.add(child.id)
        return list(imports)

    def _generate_fixtures(
        self, classes: List[ast.ClassDef], functions: List[ast.FunctionDef]
    ) -> Dict[str, str]:
        """Gera fixtures necessárias para os testes."""
        fixtures = {}

        # Fixture básica para mock de dependências
        fixtures[
            "mock_dependencies"
        ] = """
        @pytest.fixture
        def mock_dependencies():
            # Setup mocks
            yield
            # Teardown
        """

        return fixtures


class ASTAnalyzer:
    """Analisador de AST para extrair informações do código."""

    def extract_classes(self, tree: ast.AST) -> List[ast.ClassDef]:
        """Extrai todas as classes do código."""
        return [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def extract_functions(self, tree: ast.AST) -> List[ast.FunctionDef]:
        """Extrai todas as funções do código."""
        return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


class ComplexityCalculator:
    """Calculadora de complexidade ciclomática."""

    def calculate_complexity(self, node: ast.AST) -> int:
        """Calcula a complexidade ciclomática de um nó AST."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity
