"""
Modelos para resultados de testes.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class TestStatus(Enum):
    """Status possíveis de um teste."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ActionResult:
    """Resultado da execução de uma ação."""
    action_type: str
    description: str
    status: TestStatus
    start_time: datetime
    end_time: datetime
    duration: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    read_value: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "action_type": self.action_type,
            "description": self.description,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "error_message": self.error_message,
            "screenshot_path": self.screenshot_path,
            "read_value": self.read_value
        }


@dataclass
class TestCaseResult:
    """Resultado da execução de um caso de teste."""
    test_id: str
    test_name: str
    status: TestStatus
    start_time: datetime
    end_time: datetime
    duration: float
    action_results: List[ActionResult] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "action_results": [ar.to_dict() for ar in self.action_results],
            "error_message": self.error_message
        }


@dataclass
class TestSuiteResult:
    """Resultado da execução de uma suíte de testes."""
    suite_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    test_results: List[TestCaseResult] = field(default_factory=list)
    
    @property
    def total_tests(self) -> int:
        """Total de testes executados."""
        return len(self.test_results)
    
    @property
    def passed_tests(self) -> int:
        """Total de testes aprovados."""
        return sum(1 for tr in self.test_results if tr.status == TestStatus.PASSED)
    
    @property
    def failed_tests(self) -> int:
        """Total de testes reprovados."""
        return sum(1 for tr in self.test_results if tr.status == TestStatus.FAILED)
    
    @property
    def error_tests(self) -> int:
        """Total de testes com erro."""
        return sum(1 for tr in self.test_results if tr.status == TestStatus.ERROR)
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "suite_name": self.suite_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "error_tests": self.error_tests,
            "test_results": [tr.to_dict() for tr in self.test_results]
        }


@dataclass
class TestExecutionResult:
    """Resultado completo da execução."""
    application_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    suite_results: List[TestSuiteResult] = field(default_factory=list)
    
    @property
    def total_tests(self) -> int:
        """Total de testes executados."""
        return sum(suite.total_tests for suite in self.suite_results)
    
    @property
    def passed_tests(self) -> int:
        """Total de testes aprovados."""
        return sum(suite.passed_tests for suite in self.suite_results)
    
    @property
    def failed_tests(self) -> int:
        """Total de testes reprovados."""
        return sum(suite.failed_tests for suite in self.suite_results)
    
    @property
    def error_tests(self) -> int:
        """Total de testes com erro."""
        return sum(suite.error_tests for suite in self.suite_results)
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso dos testes."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "application_name": self.application_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "error_tests": self.error_tests,
            "success_rate": self.success_rate,
            "suite_results": [sr.to_dict() for sr in self.suite_results]
        }
