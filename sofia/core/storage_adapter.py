"""
🌸 Sofia - Storage Adapter para Azure Blob
Compatível com storage local (fallback) e Azure Blob Storage
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

# Configuração
USE_AZURE_BLOB = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "") != ""
AZURE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "sofia-memoria")

if USE_AZURE_BLOB:
    try:
        from azure.storage.blob import BlobServiceClient, ContainerClient
        print("☁️ Azure Blob Storage ativado")
    except ImportError:
        print("⚠️ azure-storage-blob não instalado, usando storage local")
        USE_AZURE_BLOB = False


class StorageAdapter:
    """Adapter para armazenamento local ou Azure Blob"""
    
    def __init__(self):
        self.use_cloud = USE_AZURE_BLOB
        
        if self.use_cloud:
            self._init_azure()
        else:
            self._init_local()
    
    def _init_azure(self):
        """Inicializa Azure Blob Storage"""
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        
        # Criar container se não existir
        try:
            self.container_client = self.blob_service.get_container_client(AZURE_CONTAINER)
            if not self.container_client.exists():
                self.container_client.create_container()
                print(f"✅ Container '{AZURE_CONTAINER}' criado")
        except Exception as e:
            print(f"❌ Erro ao conectar Azure Blob: {e}")
            self.use_cloud = False
            self._init_local()
    
    def _init_local(self):
        """Inicializa storage local"""
        self.local_dir = Path(".sofia_data")
        self.local_dir.mkdir(exist_ok=True)
        print(f"💾 Usando storage local: {self.local_dir.absolute()}")
    
    def save(self, filename: str, data: Any) -> bool:
        """
        Salva dados (dict ou string)
        
        Args:
            filename: Nome do arquivo (ex: 'memoria.json')
            data: Dados a salvar (dict será convertido para JSON)
        
        Returns:
            bool: True se sucesso
        """
        try:
            # Converter dict para JSON string
            if isinstance(data, dict):
                content = json.dumps(data, ensure_ascii=False, indent=2)
            else:
                content = str(data)
            
            if self.use_cloud:
                return self._save_azure(filename, content)
            else:
                return self._save_local(filename, content)
        except Exception as e:
            print(f"❌ Erro ao salvar {filename}: {e}")
            return False
    
    def load(self, filename: str, default: Any = None) -> Optional[Any]:
        """
        Carrega dados
        
        Args:
            filename: Nome do arquivo
            default: Valor padrão se arquivo não existir
        
        Returns:
            Dict ou string dos dados, ou default se erro
        """
        try:
            if self.use_cloud:
                content = self._load_azure(filename)
            else:
                content = self._load_local(filename)
            
            if content is None:
                return default
            
            # Tentar parsear como JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar {filename}: {e}")
            return default
    
    def exists(self, filename: str) -> bool:
        """Verifica se arquivo existe"""
        try:
            if self.use_cloud:
                blob_client = self.container_client.get_blob_client(filename)
                return blob_client.exists()
            else:
                return (self.local_dir / filename).exists()
        except Exception:
            return False
    
    def delete(self, filename: str) -> bool:
        """Deleta arquivo"""
        try:
            if self.use_cloud:
                blob_client = self.container_client.get_blob_client(filename)
                blob_client.delete_blob()
            else:
                (self.local_dir / filename).unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar {filename}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """Lista arquivos (com prefixo opcional)"""
        try:
            if self.use_cloud:
                blobs = self.container_client.list_blobs(name_starts_with=prefix)
                return [blob.name for blob in blobs]
            else:
                if prefix:
                    return [f.name for f in self.local_dir.glob(f"{prefix}*")]
                else:
                    return [f.name for f in self.local_dir.glob("*")]
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return []
    
    # Métodos internos
    
    def _save_azure(self, filename: str, content: str) -> bool:
        """Salva no Azure Blob"""
        blob_client = self.container_client.get_blob_client(filename)
        blob_client.upload_blob(content, overwrite=True)
        print(f"☁️ Salvo no Azure: {filename}")
        return True
    
    def _save_local(self, filename: str, content: str) -> bool:
        """Salva localmente"""
        filepath = self.local_dir / filename
        filepath.write_text(content, encoding='utf-8')
        print(f"💾 Salvo localmente: {filename}")
        return True
    
    def _load_azure(self, filename: str) -> Optional[str]:
        """Carrega do Azure Blob"""
        blob_client = self.container_client.get_blob_client(filename)
        if not blob_client.exists():
            return None
        download_stream = blob_client.download_blob()
        return download_stream.readall().decode('utf-8')
    
    def _load_local(self, filename: str) -> Optional[str]:
        """Carrega localmente"""
        filepath = self.local_dir / filename
        if not filepath.exists():
            return None
        return filepath.read_text(encoding='utf-8')


# Singleton global
storage = StorageAdapter()

# Funções de conveniência
def save(filename: str, data: Any) -> bool:
    """Salva dados"""
    return storage.save(filename, data)

def load(filename: str, default: Any = None) -> Optional[Any]:
    """Carrega dados"""
    return storage.load(filename, default)

def exists(filename: str) -> bool:
    """Verifica se existe"""
    return storage.exists(filename)

def delete(filename: str) -> bool:
    """Deleta arquivo"""
    return storage.delete(filename)

def list_files(prefix: str = "") -> list:
    """Lista arquivos"""
    return storage.list_files(prefix)
