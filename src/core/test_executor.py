"""
Executor de testes automatizados.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models.test_script import TestScript, TestCase
from src.models.test_result import (
    TestExecutionResult, TestSuiteResult, TestCaseResult,
    TestStatus
)
from src.core.app_manager import AppManager
from src.core.screenshot_manager import ScreenshotManager
from src.actions import ActionFactory
from src.utils.logger import TestLogger


class TestExecutor:
    """Executor de testes automatizados."""
    
    def __init__(self, logger: TestLogger):
        """
        Inicializa o executor.
        
        Args:
            logger: Logger para registro de eventos
        """
        self.logger = logger
        self.app_manager: Optional[AppManager] = None
        self.screenshot_manager = ScreenshotManager()
        self.action_factory = ActionFactory()
    
    def execute_script(self, test_script: TestScript) -> TestExecutionResult:
        """
        Executa um script de teste completo.
        
        Args:
            test_script: Script de teste a ser executado
            
        Returns:
            Resultado da execução
        """
        start_time = datetime.now()
        self.logger.info("="*80)
        self.logger.info(f"Iniciando execução de testes - {test_script.application.name}")
        self.logger.info(f"Versão do script: {test_script.version}")
        self.logger.info("="*80)
        
        # Criar gerenciador de aplicação
        self.app_manager = AppManager(
            app_path=test_script.application.path,
            arguments=test_script.application.arguments,
            backend=test_script.application.backend,
            startup_delay=test_script.application.startup_delay,
            timeout=test_script.application.timeout
        )
        
        # Iniciar aplicação
        try:
            self.logger.info(f"Iniciando aplicação: {test_script.application.path}")
            self.app_manager.start()
            self.logger.info("✓ Aplicação iniciada com sucesso")
        except Exception as e:
            self.logger.critical(f"✗ Falha ao iniciar aplicação: {e}")
            return self._create_error_result(test_script, start_time, str(e))
        
        # Executar suítes de teste
        suite_results = []
        try:
            for suite in test_script.test_suites:
                suite_result = self._execute_suite(suite)
                suite_results.append(suite_result)
        finally:
            # Sempre fechar aplicação
            self.logger.info("Fechando aplicação...")
            self.app_manager.close(force=True)
            self.logger.info("✓ Aplicação fechada")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = TestExecutionResult(
            application_name=test_script.application.name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            suite_results=suite_results
        )
        
        self._print_summary(result)
        
        return result
    
    def _execute_suite(self, suite) -> TestSuiteResult:
        """
        Executa uma suíte de testes.
        
        Args:
            suite: Suíte a ser executada
            
        Returns:
            Resultado da suíte
        """
        start_time = datetime.now()
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info(f"Suíte: {suite.name}")
        self.logger.info(f"Descrição: {suite.description}")
        self.logger.info("="*80)
        
        test_results = []
        
        for test_case in suite.test_cases:
            if not test_case.enabled:
                self.logger.info(f"Teste '{test_case.name}' desabilitado - pulando")
                continue
            
            test_result = self._execute_test_case(suite.name, test_case)
            test_results.append(test_result)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return TestSuiteResult(
            suite_name=suite.name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            test_results=test_results
        )
    
    def _execute_test_case(self, suite_name: str, test_case: TestCase) -> TestCaseResult:
        """
        Executa um caso de teste.
        
        Args:
            suite_name: Nome da suíte
            test_case: Caso de teste a ser executado
            
        Returns:
            Resultado do teste
        """
        start_time = datetime.now()
        self.logger.info("")
        self.logger.info("-"*80)
        self.logger.info(f"Teste: {test_case.name} (ID: {test_case.test_id})")
        self.logger.info(f"Descrição: {test_case.description}")
        if test_case.tags:
            self.logger.info(f"Tags: {', '.join(test_case.tags)}")
        self.logger.info("-"*80)
        
        # Preparar diretório de screenshots
        self.screenshot_manager.prepare_test_directory(suite_name, test_case.test_id)
        
        action_results = []
        test_status = TestStatus.PASSED
        error_message = None
        
        try:
            for i, action in enumerate(test_case.actions, 1):
                self.logger.info(f"[{i}/{len(test_case.actions)}] {action.description}")
                
                # Criar e executar ação
                action_executor = self.action_factory.create_action(
                    action.action_type,
                    self.app_manager,
                    self.screenshot_manager,
                    self.logger
                )
                
                action_result = action_executor.execute(action)
                action_results.append(action_result)
                
                # Verificar falha
                if action_result.status == TestStatus.FAILED:
                    if not action.continue_on_failure:
                        test_status = TestStatus.FAILED
                        error_message = f"Ação falhou: {action.description}"
                        break
                    else:
                        self.logger.warning("Continuando apesar da falha (continue_on_failure=true)")
                
        except Exception as e:
            test_status = TestStatus.ERROR
            error_message = f"Erro inesperado: {str(e)}"
            self.logger.error(error_message)
            
            # Capturar screenshot do erro
            try:
                self.screenshot_manager.capture_full_screen(prefix="error")
            except Exception:
                pass
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log resultado
        if test_status == TestStatus.PASSED:
            self.logger.info(f"✓ Teste APROVADO (duração: {duration:.2f}s)")
        else:
            self.logger.error(f"✗ Teste REPROVADO (duração: {duration:.2f}s)")
            if error_message:
                self.logger.error(f"  Motivo: {error_message}")
        
        return TestCaseResult(
            test_id=test_case.test_id,
            test_name=test_case.name,
            status=test_status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            action_results=action_results,
            error_message=error_message
        )
    
    def _create_error_result(self, test_script: TestScript, start_time: datetime, 
                            error: str) -> TestExecutionResult:
        """
        Cria um resultado de erro quando a aplicação não inicia.
        
        Args:
            test_script: Script de teste
            start_time: Horário de início
            error: Mensagem de erro
            
        Returns:
            Resultado indicando erro
        """
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return TestExecutionResult(
            application_name=test_script.application.name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            suite_results=[]
        )
    
    def _print_summary(self, result: TestExecutionResult):
        """
        Imprime sumário dos resultados.
        
        Args:
            result: Resultado da execução
        """
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("SUMÁRIO DA EXECUÇÃO")
        self.logger.info("="*80)
        self.logger.info(f"Aplicação: {result.application_name}")
        self.logger.info(f"Duração total: {result.duration:.2f}s")
        self.logger.info(f"Total de testes: {result.total_tests}")
        self.logger.info(f"✓ Aprovados: {result.passed_tests}")
        self.logger.info(f"✗ Reprovados: {result.failed_tests}")
        self.logger.info(f"⚠ Erros: {result.error_tests}")
        self.logger.info(f"Taxa de sucesso: {result.success_rate:.2f}%")
        self.logger.info("="*80)
    
    def save_report(self, result: TestExecutionResult, output_dir: str = "reports"):
        """
        Salva relatório de execução.
        
        Args:
            result: Resultado da execução
            output_dir: Diretório de saída
        """
        report_dir = Path(output_dir)
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório salvo em: {report_file}")
