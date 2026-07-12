import xmlrpc.client
import ssl
from typing import List, Dict, Any, Optional
from app.config import settings

class OdooClient:
    def __init__(self):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USERNAME
        self.password = settings.ODOO_PASSWORD
        self._uid = None

    @property
    def common(self):
        try:
            # Creamos un contexto SSL relajado para evitar fallos de certificados de confianza en Windows
            context = ssl._create_unverified_context()
            transport = xmlrpc.client.SafeTransport(context=context)
            return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", transport=transport)
        except Exception:
            return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")

    @property
    def models(self):
        try:
            context = ssl._create_unverified_context()
            transport = xmlrpc.client.SafeTransport(context=context)
            return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", transport=transport)
        except Exception:
            return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def get_uid(self) -> int:
        if not self._uid:
            try:
                self._uid = self.common.authenticate(self.db, self.username, self.password, {})
                if not self._uid:
                    raise Exception("Autenticación fallida con Odoo. Verifique las credenciales.")
            except Exception as e:
                raise Exception(f"No se pudo conectar a Odoo: {str(e)}")
        return self._uid

    def authenticate_user(self, username, password) -> int:
        try:
            uid = self.common.authenticate(self.db, username, password, {})
            return uid if uid else 0
        except Exception:
            return 0

    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        uid = self.get_uid()
        try:
            return self.models.execute_kw(self.db, uid, self.password, model, method, args, kwargs)
        except Exception as e:
            raise Exception(f"Error en Odoo ORM ({model}.{method}): {str(e)}")

    def _clean_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Odoo XML-RPC devuelve False (booleano) para cualquier campo vacío.
        # Esto rompe las validaciones de Pydantic para tipos opcionales (como Optional[str]).
        # Convertimos False a None para todos los campos que no sean booleanos nativos reales.
        boolean_fields = {"es_voluntario", "active"}
        
        cleaned_list = []
        for rec in records:
            cleaned_rec = {}
            for key, val in rec.items():
                if val is False and key not in boolean_fields:
                    cleaned_rec[key] = None
                else:
                    cleaned_rec[key] = val
            cleaned_list.append(cleaned_rec)
        return cleaned_list

    # Helper CRUD Methods
    def search_read(self, model: str, domain: List[Any], fields: Optional[List[str]] = None, 
                    offset: int = 0, limit: Optional[int] = None, order: Optional[str] = None) -> List[Dict[str, Any]]:
        options = {
            "offset": offset,
        }
        if fields:
            options["fields"] = fields
        if limit:
            options["limit"] = limit
        if order:
            options["order"] = order
            
        raw_records = self.execute(model, "search_read", domain, **options)
        return self._clean_records(raw_records)

    def read(self, model: str, ids: List[int], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        options = {}
        if fields:
            options["fields"] = fields
        raw_records = self.execute(model, "read", ids, **options)
        return self._clean_records(raw_records)

    def create(self, model: str, values: Dict[str, Any]) -> int:
        return self.execute(model, "create", values)

    def write(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        return self.execute(model, "write", ids, values)

    def unlink(self, model: str, ids: List[int]) -> bool:
        return self.execute(model, "unlink", ids)

    def call_button(self, model: str, method: str, ids: List[int]) -> Any:
        # Permite ejecutar acciones/botones de Odoo como action_validar
        return self.execute(model, method, ids)

odoo_client = OdooClient()
