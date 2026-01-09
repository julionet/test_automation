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
        if not action.value:
            raise ValueError(
                "Action 'click_and_wait' requer 'value' com o título da janela esperada"
            )
        
        expected_window_title = action.value
        additional_wait = action.duration or 0
        timeout = action.timeout or self.app_manager.timeout
        
        self.logger.info(f"Clicando e aguardando janela '{expected_window_title}'...")

        # Executar clique em thread separada para não bloquear
        processo = self._execute_process("src/workers/click_worker.py", action.window_title, action.control)
        time.sleep(timeout)

        # Finalizar processo de clique se ainda estiver rodando
        if processo.poll() is None:
            processo.terminate()
        
        # Aguardar nova janela aparecer
        if not self.app_manager.wait_window(expected_window_title, timeout=timeout):
            raise Exception(
                f"Janela '{expected_window_title}' não foi carregada dentro de {timeout}s"
            )
        
        self.logger.info(f"✓ Janela '{expected_window_title}' carregada")
        
        # Aguardar tempo adicional se especificado (para a janela terminar de carregar)
        if additional_wait > 0:
            self.logger.info(f"Aguardando {additional_wait}s adicionais para janela estabilizar...")
            time.sleep(additional_wait)
        
        # Trazer janela para frente
        try:
            new_window = self.app_manager.get_window(title=expected_window_title)
            self.app_manager.bring_to_foreground(new_window)
            
            # Aguardar janela estar realmente pronta
            new_window.wait('ready', timeout=5)
        except Exception as e:
            self.logger.warning(f"Aviso ao preparar nova janela: {e}")
        
        return expected_window_title
    
    def _execute_process(self, process_name, window_name, control_name):
        """
        Executa o clique em um processo completamente separado
        """
        # Inicia processo em background
        processo = subprocess.Popen(
            [sys.executable, process_name, window_name, control_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW  # Windows: sem janela
        )
        
        return processo
