"""
Modelos para scripts de teste.
"""
from dataclasses import dataclass
from typing import List, Optional, Any, Dict


@dataclass
class Application:
    """Configuração da aplicação a ser testada."""
    name: str
    path: str
    arguments: str = ""
    startup_delay: int = 3
    backend: str = "uia"
    timeout: int = 10
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Application':
        """Cria uma instância a partir de um dicionário."""
        return Application(
            name=data["name"],
            path=data["path"],
            arguments=data.get("arguments", ""),
            startup_delay=data.get("startup_delay", 3),
            backend=data.get("backend", "uia"),
            timeout=data.get("timeout", 10)
        )


@dataclass
class Action:
    """Ação a ser executada no teste."""
    action_type: str
    description: str
    class_type: Optional[str] = None
    control: Optional[str] = None
    window_title: Optional[str] = None
    value: Optional[str] = None
    duration: Optional[int] = None
    timeout: Optional[int] = None
    screenshot_on_success: bool = False
    screenshot_on_failure: bool = True
    continue_on_failure: bool = False
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Action':
        """Cria uma instância a partir de um dicionário."""
        return Action(
            action_type=data["type"],
            description=data["description"],
            class_type=data.get("class"),
            control=data.get("control"),
            window_title=data.get("window_title"),
            value=data.get("value"),
            duration=data.get("duration"),
            timeout=data.get("timeout"),
            screenshot_on_success=data.get("screenshot_on_success", False),
            screenshot_on_failure=data.get("screenshot_on_failure", True),
            continue_on_failure=data.get("continue_on_failure", False)
        )


@dataclass
class TestCase:
    """Caso de teste."""
    test_id: str
    name: str
    description: str
    actions: List[Action]
    enabled: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestCase':
        """Cria uma instância a partir de um dicionário."""
        return TestCase(
            test_id=data["id"],
            name=data["name"],
            description=data["description"],
            actions=[Action.from_dict(a) for a in data["actions"]],
            enabled=data.get("enabled", True),
            tags=data.get("tags", [])
        )


@dataclass
class TestSuite:
    """Suíte de testes."""
    name: str
    description: str
    test_cases: List[TestCase]
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestSuite':
        """Cria uma instância a partir de um dicionário."""
        return TestSuite(
            name=data["name"],
            description=data["description"],
            test_cases=[TestCase.from_dict(tc) for tc in data["test_cases"]]
        )


@dataclass
class TestScript:
    """Script completo de teste."""
    version: str
    application: Application
    test_suites: List[TestSuite]
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestScript':
        """Cria uma instância a partir de um dicionário."""
        return TestScript(
            version=data["version"],
            application=Application.from_dict(data["application"]),
            test_suites=[TestSuite.from_dict(ts) for ts in data["test_suites"]]
        )
