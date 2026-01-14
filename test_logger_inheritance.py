"""
Script de teste para validar que o logger está funcionando em todas as classes filhas.
Execute este script para verificar se o logger está sendo herdado corretamente.
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.app_manager import AppManager
from src.core.screenshot_manager import ScreenshotManager
from src.utils.logger import TestLogger
from src.actions import ActionFactory
from src.models.test_script import Action


def test_logger_in_all_actions():
    """Testa se o logger funciona em todas as ações."""
    
    # Inicializar componentes
    logger = TestLogger()
    print("\n" + "="*60)
    print("TESTANDO LOGGER EM CLASSES HERDADAS")
    print("="*60)
    
    # Teste de logger direto em TestLogger
    logger.info("✓ TestLogger.info() funcionando")
    logger.debug("✓ TestLogger.debug() funcionando")
    
    # Agora vamos testar em ações
    print("\n" + "="*60)
    print("TESTANDO LOGGER EM ACTIONS")
    print("="*60)
    
    # Mock de app_manager e screenshot_manager (não vamos inicializar a app de verdade)
    class MockAppManager:
        def __init__(self):
            self.timeout = 10
    
    class MockScreenshotManager:
        pass
    
    app_manager = MockAppManager()
    screenshot_manager = MockScreenshotManager()
    
    # Testar cada ação
    supported_actions = ActionFactory.get_supported_actions()
    
    for action_type in supported_actions:
        try:
            action_instance = ActionFactory.create_action(
                action_type, 
                app_manager, 
                screenshot_manager, 
                logger
            )
            
            # Verificar se o logger foi atribuído
            if hasattr(action_instance, 'logger') and action_instance.logger is not None:
                print(f"\n✓ {action_type}: logger OK")
                print(f"  - Classe: {action_instance.__class__.__name__}")
                print(f"  - Has logger: {hasattr(action_instance, 'logger')}")
                print(f"  - Logger type: {type(action_instance.logger).__name__}")
                
                # Tentar logar
                try:
                    action_instance.logger.debug(f"  [DEBUG] Teste de logger em {action_instance.__class__.__name__}")
                    print(f"  [DEBUG] ✓ Debug logging OK")
                except Exception as e:
                    print(f"  [ERROR] ✗ Debug logging falhou: {e}")
            else:
                print(f"\n✗ {action_type}: logger NÃO ENCONTRADO!")
                
        except Exception as e:
            print(f"\n✗ {action_type}: Erro ao criar ação: {e}")
    
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO")
    print("="*60)
    print("\nVerifique os logs acima. Se todos mostram 'logger OK',")
    print("então o logger está funcionando em todas as classes.")
    print("\nArquivo de log: logs/test_run_*.log")


if __name__ == "__main__":
    test_logger_in_all_actions()
