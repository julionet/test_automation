"""
Ação de clique que carrega nova tela de forma assíncrona.
"""
from typing import Optional, Any
import time
import subprocess
import sys

from src.actions.base_action import BaseAction
from src.models.test_script import Action

class ClickAndWaitAction(BaseAction):
    """
    Ação de clique que aguarda explicitamente uma nova janela carregar.
    Mais robusto que ClickAsyncAction quando se sabe exatamente qual janela esperar.
    """
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique e aguarda janela específica estar pronta.
        
        Args:
            action: Definição da ação
            - control: Controle a ser clicado
            - value: Título da janela a aguardar (OBRIGATÓRIO)
            - duration: Tempo adicional de espera após janela aparecer (opcional)
            
        Returns:
            Título da janela carregada
        """
        # Log ANTES de qualquer validação
        self.logger.debug(f"Iniciando com action_type={action.action_type}, value={action.value}")
        
        # Validação com log
        if not action.value:
            error_msg = "Action 'click_and_wait' requer 'value' com o título da janela esperada"
            self.logger.error(f"Validação falhou: {error_msg}")
            raise ValueError(error_msg)
        
        expected_window_title = action.value
        additional_wait = action.duration or 0
        timeout = action.timeout or self.app_manager.timeout
        file_worker = "./src/workers/click_worker.py"
        
        self.logger.info(f"Clicando e aguardando janela '{expected_window_title}'...")
        self.logger.debug(f"Timeout: {timeout}s, Espera adicional: {additional_wait}s")

        # Executar clique em thread separada para não bloquear
        try:
            self.logger.debug(f"Iniciando processo de clique...")
            processo = self._execute_process(file_worker, action.window_title, action.control)
            self.logger.debug(f"Processo iniciado com PID: {processo.pid}")
        except Exception as e:
            self.logger.error(f"Erro ao iniciar processo de clique: {e}")
            raise
        
        time.sleep(1.0)

        # Finalizar processo de clique se ainda estiver rodando
        #if processo.poll() is None:
        #    processo.terminate()
        
        # Aguardar nova janela aparecer
        self.logger.debug(f"Aguardando janela '{expected_window_title}'...")
        if not self.app_manager.wait_window(expected_window_title, timeout=timeout):
            error_msg = f"Janela '{expected_window_title}' não foi carregada dentro de {timeout}s"
            self.logger.error(f"{error_msg}")
            raise Exception(error_msg)
        
        self.logger.info(f"✓ Janela '{expected_window_title}' carregada")
        
        # Aguardar tempo adicional se especificado (para a janela terminar de carregar)
        if additional_wait > 0:
            self.logger.info(f"Aguardando {additional_wait}s adicionais para janela estabilizar...")
            time.sleep(additional_wait)
        
        # Trazer janela para frente
        try:
            self.logger.debug(f"Trazendo janela para primeiro plano...")
            new_window = self.app_manager.get_window(title=expected_window_title)
            self.app_manager.bring_to_foreground(new_window)
            self.logger.debug(f"Janela trazida para primeiro plano")
            
            # Aguardar janela estar realmente pronta
            # new_window.wait('ready', timeout=5)
        except Exception as e:
            self.logger.warning(f"Aviso ao preparar nova janela: {e}")
        
        self.logger.info(f"✓ Ação concluída com sucesso")
        return expected_window_title
    
    def _execute_process(self, process_name, window_name, control_name):
        """
        Executa o clique em um processo completamente separado
        """
        try:
            self.logger.debug(f"Iniciando subprocess:")
            self.logger.debug(f"  - Script: {process_name}")
            self.logger.debug(f"  - Janela: {window_name}")
            self.logger.debug(f"  - Controle: {control_name}")
            
            # Inicia processo em background
            processo = subprocess.Popen(
                [sys.executable, process_name, window_name, control_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW  # Windows: sem janela
            )
            
            self.logger.debug(f"Subprocess iniciado com PID: {processo.pid}")
            return processo
        except Exception as e:
            self.logger.error(f"Erro ao iniciar subprocess: {e}")
            raise
