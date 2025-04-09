from typing import List, Dict, Optional
import ast
from app.models.test_models import TestCase, TestSuite, TestFramework
from app.services.test_analyzer import TestAnalyzer


class TestGenerator:
    """Gerador de testes unitários."""

    def __init__(self):
        self.analyzer = TestAnalyzer()
        self.template_engine = TestTemplateEngine()

    async def generate_test_suite(self, code: str, framework: TestFramework) -> str:
        """Gera uma suite de testes completa para o código fornecido."""
        # Analisa o código e gera a estrutura de teste
        test_suite = await self.analyzer.analyze_code(code, framework)

        # Gera o código do teste usando o template apropriado
        return self.template_engine.render_test_suite(test_suite, framework)


class TestTemplateEngine:
    """Motor de templates para geração de testes."""

    def render_test_suite(self, test_suite: TestSuite, framework: TestFramework) -> str:
        """Renderiza uma suite de testes completa."""
        if framework == TestFramework.PYTEST:
            return self._render_pytest_suite(test_suite)
        else:
            return self._render_unittest_suite(test_suite)

    def _render_pytest_suite(self, test_suite: TestSuite) -> str:
        """Renderiza uma suite de testes usando pytest."""
        imports = self._generate_imports(test_suite.imports)
        fixtures = self._generate_fixtures(test_suite.fixtures)
        test_cases = self._generate_test_cases(test_suite.test_cases)

        return f"""{imports}

{fixtures}

{test_cases}
"""

    def _render_unittest_suite(self, test_suite: TestSuite) -> str:
        """Renderiza uma suite de testes usando unittest."""
        imports = self._generate_imports(test_suite.imports + ["unittest"])

        return f"""{imports}

class {test_suite.class_name}(unittest.TestCase):
    \"""
    {test_suite.description}
    \"""
    
    def setUp(self):
        \"""Setup para cada teste.\"""
        pass
    
    def tearDown(self):
        \"""Cleanup após cada teste.\"""
        pass
    
{self._generate_unittest_test_cases(test_suite.test_cases)}
"""

    def _generate_imports(self, imports: List[str]) -> str:
        """Gera as declarações de import."""
        standard_imports = []
        third_party_imports = []
        local_imports = []

        for imp in sorted(set(imports)):
            if "." not in imp:
                if imp in ["os", "sys", "typing"]:
                    standard_imports.append(f"import {imp}")
                else:
                    third_party_imports.append(f"import {imp}")
            else:
                local_imports.append(f"from {imp}")

        result = ""
        if standard_imports:
            result += "\n".join(standard_imports) + "\n"
        if third_party_imports:
            if standard_imports:
                result += "\n"
            result += "\n".join(third_party_imports) + "\n"
        if local_imports:
            if standard_imports or third_party_imports:
                result += "\n"
            result += "\n".join(local_imports)

        return result

    def _generate_fixtures(self, fixtures: Dict[str, str]) -> str:
        """Gera o código das fixtures."""
        return "\n\n".join(fixtures.values())

    def _generate_test_cases(self, test_cases: List[TestCase]) -> str:
        """Gera o código dos casos de teste para pytest."""
        result = []

        for test_case in test_cases:
            result.append(
                f"""def {test_case.name}():
    \"""{test_case.description}\"""
{self._indent(test_case.test_code)}
"""
            )

        return "\n\n".join(result)

    def _generate_unittest_test_cases(self, test_cases: List[TestCase]) -> str:
        """Gera o código dos casos de teste para unittest."""
        result = []

        for test_case in test_cases:
            result.append(
                f"""    def {test_case.name}(self):
        \"""{test_case.description}\"""
{self._indent(self._indent(test_case.test_code))}
"""
            )

        return "\n".join(result)

    def _indent(self, code: str, level: int = 1) -> str:
        """Indenta o código pelo número especificado de níveis."""
        lines = code.strip().split("\n")
        indent = "    " * level
        return "\n".join(f"{indent}{line}" for line in lines)
