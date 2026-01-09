"""
Ponto de entrada da aplicação de testes automatizados.
"""
import sys
import argparse

import subprocess
import sys

from src.utils.logger import TestLogger
from src.utils.json_validator import JsonValidator
from src.models.test_script import TestScript
from src.core.test_executor import TestExecutor


def main():
    """Função principal."""
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description='Executor de testes automatizados para aplicações Windows Desktop'
    )
    parser.add_argument(
        'script',
        type=str,
        default='config/test_app_script.json',
        nargs='?',
        help='Caminho para o arquivo JSON com o script de teste'
    )
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Não salvar relatório JSON'
    )
    
    args = parser.parse_args()
    
    # Inicializar logger
    logger = TestLogger()
    
    try:
        # Validar e carregar script
        logger.info(f"Carregando script de teste: {args.script}")
        script_data = JsonValidator.validate_test_script(args.script)
        test_script = TestScript.from_dict(script_data)
        logger.info("✓ Script carregado e validado com sucesso")
        
        # Executar testes
        executor = TestExecutor(logger)
        result = executor.execute_script(test_script)
        
        # Salvar relatório
        if not args.no_report:
            executor.save_report(result)
        
        # Código de saída baseado nos resultados
        if result.failed_tests > 0 or result.error_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except FileNotFoundError as e:
        logger.critical(f"Arquivo não encontrado: {e}")
        sys.exit(2)
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(3)

if __name__ == "__main__":
    main()
