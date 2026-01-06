"""
Módulo para validação de schemas JSON.
"""
import json
from pathlib import Path
from typing import Dict, Any
from jsonschema import validate, ValidationError


class JsonValidator:
    """Validador de schemas JSON."""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Carrega um arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo JSON
            
        Returns:
            Dicionário com o conteúdo do JSON
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            json.JSONDecodeError: Se o JSON for inválido
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Valida dados contra um schema.
        
        Args:
            data: Dados a serem validados
            schema: Schema de validação
            
        Returns:
            True se válido
            
        Raises:
            ValidationError: Se a validação falhar
        """
        validate(instance=data, schema=schema)
        return True
    
    @staticmethod
    def validate_test_script(script_path: str) -> Dict[str, Any]:
        """
        Valida um script de teste.
        
        Args:
            script_path: Caminho do script de teste
            
        Returns:
            Dicionário com o script validado
            
        Raises:
            ValidationError: Se o script for inválido
        """
        script = JsonValidator.load_json(script_path)
        
        # Validações básicas
        required_fields = ["version", "application", "test_suites"]
        for field in required_fields:
            if field not in script:
                raise ValidationError(f"Campo obrigatório ausente: {field}")
        
        # Validar application
        app = script["application"]
        if "name" not in app or "path" not in app:
            raise ValidationError("Application deve ter 'name' e 'path'")
        
        # Validar test_suites
        if not script["test_suites"]:
            raise ValidationError("Deve haver pelo menos uma test_suite")
        
        for suite in script["test_suites"]:
            if "test_cases" not in suite or not suite["test_cases"]:
                raise ValidationError(f"Suite '{suite.get('name')}' deve ter test_cases")
        
        return script
