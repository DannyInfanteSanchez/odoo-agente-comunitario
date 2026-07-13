from fastapi import FastAPI, HTTPException, Depends, Security, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any
from datetime import date
import os
import traceback

from app.config import settings
from app.odoo_client import odoo_client
from app.models import (
    AgenteComunitarioCreate,
    AgenteComunitarioUpdate,
    AgenteComunitarioResponse,
    AttachmentResponse,
    RegistroCreate,
    RegistroUpdate,
    RegistroResponse,
    RegistroDetalleResponse,
    DiresaResponse,
    RedResponse,
    MicroredResponse,
    EessResponse,
    UserLogin
)

# Inicializar FastAPI con información del MINSA
app = FastAPI(
    title="MINSA - Odoo Agente Comunitario CRUD API",
    description="API intermedia tipo CRUD en Python para interactuar con los servicios de Odoo 14 desde aplicaciones móviles (Flutter) y web.",
    version="1.0.0"
)

# Registrar errores detalladamente en un archivo de log local
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"❌ Exception en {request.method} {request.url.path}: {str(exc)}\n"
    error_msg += "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    
    # Escribir en error.log
    with open("error.log", "a", encoding="utf-8") as f:
        f.write("\n" + "="*50 + "\n" + error_msg + "\n" + "="*50 + "\n")
        
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno en la API intermedia: {str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_msg = f"⚠️ HTTPException en {request.method} {request.url.path} [{exc.status_code}]: {exc.detail}\n"
    
    # Escribir en error.log
    with open("error.log", "a", encoding="utf-8") as f:
        f.write("\n" + "="*50 + "\n" + error_msg + "\n" + "="*50 + "\n")
        
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Habilitar CORS para permitir consumo desde Flutter Web y navegadores
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por dominios específicos en producción si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def get_dashboard():
    """
    Sirve la interfaz gráfica interactiva de pruebas.
    """
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

def extract_many2one_id(relation):
    if not relation:
        return None
    if isinstance(relation, (list, tuple)) and len(relation) > 0:
        return relation[0]
    if isinstance(relation, int):
        return relation
    return None

@app.post("/login", tags=["Autenticación"])
@app.post("/api/login", tags=["Autenticación"])
def login_user(login_data: UserLogin):
    """
    Autentica un usuario contra la base de datos de Odoo usando XML-RPC.
    Determina su rol dinámico y relaciones geográficas (DIRESA, Red, Establecimiento).
    """
    username = login_data.usuario.strip()
    password = login_data.password.strip()

    # Intentar autenticar contra Odoo
    uid = odoo_client.authenticate_user(username, password)

    if uid > 0:
        # Autenticación exitosa en Odoo.
        # Obtener datos geográficos y de grupos del usuario.
        try:
            user_data = odoo_client.search_read(
                model="res.users",
                domain=[("id", "=", uid)],
                fields=[
                    "diresa_id", 
                    "red_id", 
                    "establecimiento_id",
                    "es_grupo_admin",
                    "es_grupo_establecimiento",
                    "login"
                ],
                limit=1
            )
            
            if user_data:
                user = user_data[0]
                diresa_id = extract_many2one_id(user.get("diresa_id"))
                red_id = extract_many2one_id(user.get("red_id"))
                est_id = extract_many2one_id(user.get("establecimiento_id"))
                user_login = str(user.get("login", "")).strip().lower()
                
                # Determinar rol:
                is_admin = user.get("es_grupo_admin", False)
                is_renipress = user.get("es_grupo_establecimiento", False)
                
                # Bypass explícito de seguridad para el usuario de pruebas o base
                if user_login == "koboscg@gmail.com":
                    rol_id = "agente"
                elif is_admin:
                    rol_id = "ambos"
                elif is_renipress or est_id is not None:
                    rol_id = "agente"
                else:
                    rol_id = "ambos" # Default seguro
            else:
                diresa_id = None
                red_id = None
                est_id = None
                rol_id = "ambos"
                if username.lower() == "koboscg@gmail.com":
                    rol_id = "agente"
        except Exception as e:
            # Fallback en caso de error de lectura de campos
            diresa_id = None
            red_id = None
            est_id = None
            rol_id = "agente" if username.lower() == "koboscg@gmail.com" else "ambos"

        return {
            "error": 0,
            "mensaje": "Autenticación exitosa",
            "resultado": {
                "token": settings.API_BEARER_TOKEN,
                "usuario_id": uid,
                "rol_id": rol_id,
                "diresa_id": diresa_id,
                "red_id": red_id,
                "establecimiento_id": est_id
            }
        }
    else:
        # Falló
        return {
            "error": 1,
            "mensaje": "Usuario o clave incorrectos en Odoo.",
            "resultado": None
        }

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifica que la petición incluya el Bearer token correcto especificado en la configuración.
    """
    token = credentials.credentials
    if token != settings.API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización inválido o ausente."
        )
    return token

# Endpoint público de bypass para simular la consulta RENIEC de Odoo
@app.post("/api/reniec-bypass")
def reniec_bypass(payload: dict = None):
    """
    Retorna una respuesta exitosa (HTTP 200) simulada para evitar que la validación de Odoo 
    se caiga al intentar hacer consultas a un API de RENIEC inexistente o desconfigurado.
    """
    return {
        "coResultado": "0000",
        "datosPersona": {
            "apPrimer": "VALIDADO",
            "apSegundo": "SISTEMA",
            "prenombres": "AGENTE"
        }
    }

# Endpoints de Salud Pública / Estado
@app.get("/health", tags=["Salud"])
def health_check():
    """
    Verifica el estado del API de Python y la conectividad XML-RPC con Odoo.
    """
    try:
        uid = odoo_client.get_uid()
        return {
            "status": "online",
            "odoo_connected": True,
            "odoo_uid": uid
        }
    except Exception as e:
        return {
            "status": "degraded",
            "odoo_connected": False,
            "error": str(e)
        }


# =====================================================================
# ENDPOINTS: AGENTE COMUNITARIO (minsa.agente.comunitario)
# =====================================================================
@app.get("/api/agentes", response_model=List[AgenteComunitarioResponse], tags=["Agentes Comunitarios"])
def get_agentes(
    numero_documento: Optional[str] = None,
    tipo_documento: Optional[str] = None,
    name: Optional[str] = None,
    es_voluntario: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
    token: str = Depends(verify_token)
):
    """
    Obtiene un listado de agentes comunitarios aplicando filtros opcionales.
    """
    domain = []
    if numero_documento:
        domain.append(("numero_documento", "=", numero_documento))
    if tipo_documento:
        domain.append(("tipo_documento", "=", tipo_documento))
    if name:
        domain.append(("name", "ilike", name))
    if es_voluntario is not None:
        domain.append(("es_voluntario", "=", es_voluntario))
        
    try:
        fields = [
            "id", "name", "tipo_documento", "numero_documento", "ape_paterno", "ape_materno",
            "nombres", "telefono", "celular", "email", "fecha_nacimiento", "edad", "direccion",
            "es_voluntario", "diresa_id", "red_id", "establecimiento_id", "genero_id", "etnia_id",
            "seguro_id", "dialecto_ids", "grado_instruccion_id", "nivel_agente_id", "estandar_laboral_id",
            "operador_id", "tipo_voluntariado_id", "tipo_voluntariado_ids", "foto"
        ]
        records = odoo_client.search_read(
            model="minsa.agente.comunitario",
            domain=domain,
            fields=fields,
            offset=offset,
            limit=limit,
            order="name asc"
        )
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agentes/{agente_id}", response_model=AgenteComunitarioResponse, tags=["Agentes Comunitarios"])
def get_agente_by_id(agente_id: int, token: str = Depends(verify_token)):
    """
    Obtiene los detalles de un agente comunitario específico por su ID.
    """
    try:
        fields = [
            "id", "name", "tipo_documento", "numero_documento", "ape_paterno", "ape_materno",
            "nombres", "telefono", "celular", "email", "fecha_nacimiento", "edad", "direccion",
            "es_voluntario", "diresa_id", "red_id", "establecimiento_id", "genero_id", "etnia_id",
            "seguro_id", "dialecto_id", "grado_instruccion_id", "nivel_agente_id", "estandar_laboral_id",
            "operador_id", "tipo_voluntariado_id", "foto"
        ]
        records = odoo_client.read("minsa.agente.comunitario", [agente_id], fields=fields)
        if not records:
            raise HTTPException(status_code=404, detail=f"Agente comunitario con ID {agente_id} no encontrado.")
        return records[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agentes", status_code=status.HTTP_201_CREATED, tags=["Agentes Comunitarios"])
def create_agente(agente: AgenteComunitarioCreate, token: str = Depends(verify_token)):
    """
    Crea un nuevo agente comunitario en Odoo. 
    Nota: Odoo validará las restricciones de base de datos como el documento único y ejecutará el alta en RENIEC si es DNI.
    """
    values = agente.model_dump(exclude_none=True)
    
    # Manejar formatos de fecha
    if "fecha_nacimiento" in values and isinstance(values["fecha_nacimiento"], date):
        values["fecha_nacimiento"] = values["fecha_nacimiento"].strftime("%Y-%m-%d")
    
    # Convertir Many2many a comandos Odoo: (6, 0, [ids])
    if "dialecto_ids" in values:
        values["dialecto_ids"] = [(6, 0, values["dialecto_ids"])]
    if "tipo_voluntariado_ids" in values:
        values["tipo_voluntariado_ids"] = [(6, 0, values["tipo_voluntariado_ids"])]
        
    try:
        new_id = odoo_client.create("minsa.agente.comunitario", values)
        return {"id": new_id, "message": "Agente comunitario creado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/agentes/{agente_id}", tags=["Agentes Comunitarios"])
def update_agente(agente_id: int, agente: AgenteComunitarioUpdate, token: str = Depends(verify_token)):
    """
    Actualiza los datos de un agente comunitario existente.
    """
    values = agente.model_dump(exclude_none=True)
    if not values:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un campo para actualizar.")
        
    if "fecha_nacimiento" in values and isinstance(values["fecha_nacimiento"], date):
        values["fecha_nacimiento"] = values["fecha_nacimiento"].strftime("%Y-%m-%d")
    
    # Convertir Many2many a comandos Odoo: (6, 0, [ids]) para reemplazar la lista completa
    if "dialecto_ids" in values:
        values["dialecto_ids"] = [(6, 0, values["dialecto_ids"])]
    if "tipo_voluntariado_ids" in values:
        values["tipo_voluntariado_ids"] = [(6, 0, values["tipo_voluntariado_ids"])]
        
    try:
        # Verificar existencia
        exists = odoo_client.search_read("minsa.agente.comunitario", [("id", "=", agente_id)], ["id"])
        if not exists:
            raise HTTPException(status_code=404, detail=f"Agente comunitario con ID {agente_id} no encontrado.")
            
        success = odoo_client.write("minsa.agente.comunitario", [agente_id], values)
        return {"success": success, "message": "Agente comunitario actualizado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/agentes/{agente_id}", tags=["Agentes Comunitarios"])
def delete_agente(agente_id: int, token: str = Depends(verify_token)):
    """
    Archiva (o elimina lógicamente) un agente comunitario de Odoo.
    En Odoo, el método unlink para esta clase generalmente realiza write({'active': False}).
    """
    try:
        exists = odoo_client.search_read("minsa.agente.comunitario", [("id", "=", agente_id)], ["id"])
        if not exists:
            raise HTTPException(status_code=404, detail=f"Agente comunitario con ID {agente_id} no encontrado.")
            
        success = odoo_client.unlink("minsa.agente.comunitario", [agente_id])
        return {"success": success, "message": "Agente comunitario eliminado o archivado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================================
# ENDPOINTS: REGISTRO DE FICHAS (minsa.registro y minsa.registro.detalle)
# =====================================================================
@app.get("/api/registros", response_model=List[RegistroResponse], tags=["Registro de Fichas"])
def get_registros(
    tipo_registro: Optional[str] = None,
    estado: Optional[str] = None,
    establecimiento_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    token: str = Depends(verify_token)
):
    """
    Retorna la lista de fichas de registros registradas en el sistema.
    """
    domain = []
    if tipo_registro:
        domain.append(("tipo_registro", "=", tipo_registro))
    if estado:
        domain.append(("estado", "=", estado))
    if establecimiento_id:
        domain.append(("establecimiento_id", "=", establecimiento_id))
        
    try:
        fields = [
            "id", "name", "diresa_id", "establecimiento_id", "red_id", "ubigeo", "renipress",
            "tipo_registro", "tipo_archivo", "url_documento", "cantidad_detalle", "estado",
            "create_date", "valida_date", "revalida_date", "evalua_revalida", "detalle_ids"
        ]
        records = odoo_client.search_read(
            model="minsa.registro",
            domain=domain,
            fields=fields,
            offset=offset,
            limit=limit,
            order="create_date desc"
        )
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _fetch_attachment_metadata(attachment_ids: list) -> list:
    """
    Helper: dado una lista de IDs de ir.attachment, devuelve su metadata (id, name, mimetype).
    """
    if not attachment_ids:
        return []
    try:
        records = odoo_client.read("ir.attachment", attachment_ids, fields=["id", "name", "mimetype"])
        return [{"id": r["id"], "name": r.get("name", "archivo"), "mimetype": r.get("mimetype")} for r in records]
    except Exception:
        # Fallback: devolver solo los IDs si falla la lectura
        return [{"id": aid, "name": f"archivo_{aid}", "mimetype": None} for aid in attachment_ids]


@app.get("/api/registros/{registro_id}", response_model=RegistroResponse, tags=["Registro de Fichas"])
def get_registro_by_id(registro_id: int, token: str = Depends(verify_token)):
    """
    Obtiene los detalles de una ficha de registro en específico, trayendo la información completa
    de cada uno de sus miembros detallados en el One2many (`detalle_ids`) y los archivos adjuntos.
    """
    try:
        fields = [
            "id", "name", "diresa_id", "establecimiento_id", "red_id", "ubigeo", "renipress",
            "tipo_registro", "tipo_archivo", "url_documento", "cantidad_detalle", "estado",
            "create_date", "valida_date", "revalida_date", "evalua_revalida", "detalle_ids",
            "carga_documento"
        ]
        records = odoo_client.read("minsa.registro", [registro_id], fields=fields)
        if not records:
            raise HTTPException(status_code=404, detail=f"Ficha de registro con ID {registro_id} no encontrada.")
            
        registro = records[0]

        # --- Enriquecer adjuntos de nivel Ficha ---
        carga_doc_ids = registro.get("carga_documento", []) or []
        if carga_doc_ids:
            registro["carga_documento"] = _fetch_attachment_metadata(carga_doc_ids)
        else:
            registro["carga_documento"] = []
        
        # --- Enriquecer detalles (miembros) ---
        detalle_ids = registro.get("detalle_ids", [])
        if detalle_ids:
            detalle_fields = [
                "id", "registro_id", "agente_comunitario_id", "tipo_documento", "numero_documento",
                "name", "celular", "fecha_inicio", "fecha_fin", "observacion", "estado",
                "carga_documento"
            ]
            detalles_completos = odoo_client.read("minsa.registro.detalle", detalle_ids, fields=detalle_fields)
            # Enriquecer adjuntos de cada detalle
            for det in detalles_completos:
                det_doc_ids = det.get("carga_documento", []) or []
                if det_doc_ids:
                    det["carga_documento"] = _fetch_attachment_metadata(det_doc_ids)
                else:
                    det["carga_documento"] = []
            registro["detalle_ids"] = detalles_completos
        else:
            registro["detalle_ids"] = []
            
        return registro
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/registros", status_code=status.HTTP_201_CREATED, tags=["Registro de Fichas"])
def create_registro(registro: RegistroCreate, token: str = Depends(verify_token)):
    """
    Crea una nueva ficha de registro con su respectivo listado de agentes/miembros asociados.
    """
    values = registro.model_dump(exclude_none=True)
    
    # Preparar el comando relacional de Odoo para el One2many (detalle_ids).
    # Odoo usa el formato (0, 0, {valores}) para crear registros relacionados.
    detalles_odoo = []
    if "detalle_ids" in values:
        for det in values["detalle_ids"]:
            # Dar formato a las fechas dentro del detalle si existen
            if "fecha_inicio" in det and isinstance(det["fecha_inicio"], date):
                det["fecha_inicio"] = det["fecha_inicio"].strftime("%Y-%m-%d")
            if "fecha_fin" in det and isinstance(det["fecha_fin"], date):
                det["fecha_fin"] = det["fecha_fin"].strftime("%Y-%m-%d")
            
            # Formatear documentos adjuntos dentro del detalle si existen
            if "carga_documento" in det:
                docs_det = []
                for doc in det["carga_documento"]:
                    docs_det.append((0, 0, {
                        "name": doc["name"],
                        "datas": doc["datas"]
                    }))
                det["carga_documento"] = docs_det
                
            detalles_odoo.append((0, 0, det))
            
    values["detalle_ids"] = detalles_odoo

    # Preparar documentos adjuntos (Many2many ir.attachment)
    documentos_odoo = []
    if "carga_documento" in values:
        for doc in values["carga_documento"]:
            documentos_odoo.append((0, 0, {
                "name": doc["name"],
                "datas": doc["datas"]
            }))
    values["carga_documento"] = documentos_odoo
    
    try:
        new_id = odoo_client.create("minsa.registro", values)
        return {"id": new_id, "message": "Ficha de registro creada exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/registros/{registro_id}", tags=["Registro de Fichas"])
def update_registro(registro_id: int, registro: RegistroUpdate, token: str = Depends(verify_token)):
    """
    Actualiza una ficha de registro en Odoo, resolviendo adiciones, ediciones y eliminaciones de miembros en el One2many.
    """
    values = registro.model_dump(exclude_none=True)
    
    # 1. Resolver relación One2many (detalle_ids)
    if "detalle_ids" in values:
        try:
            current_record = odoo_client.read("minsa.registro", [registro_id], fields=["detalle_ids"])
            existing_ids = current_record[0].get("detalle_ids", []) if current_record else []
        except Exception:
            existing_ids = []
            
        incoming_details = values["detalle_ids"]
        incoming_ids = [d["id"] for d in incoming_details if d.get("id")]
        
        detalles_odoo = []
        
        # Eliminar las líneas que ya no se envían
        for old_id in existing_ids:
            if old_id not in incoming_ids:
                detalles_odoo.append((2, old_id, False))
                
        # Insertar / Actualizar las líneas entrantes
        for det in incoming_details:
            if "fecha_inicio" in det and isinstance(det["fecha_inicio"], date):
                det["fecha_inicio"] = det["fecha_inicio"].strftime("%Y-%m-%d")
            if "fecha_fin" in det and isinstance(det["fecha_fin"], date):
                det["fecha_fin"] = det["fecha_fin"].strftime("%Y-%m-%d")

            line_id = det.pop("id", None)


            if "carga_documento" in det and det["carga_documento"]:
                docs_det = []
                # Obtener adjuntos existentes del detalle si es línea existente
                existing_det_att_ids = set()
                if line_id:
                    try:
                        det_rec = odoo_client.read("minsa.registro.detalle", [line_id], fields=["carga_documento"])
                        existing_det_att_ids = set(det_rec[0].get("carga_documento", []) if det_rec else [])
                    except Exception:
                        pass

                incoming_keep_det_ids = set()
                for doc in det["carga_documento"]:
                    doc_id = doc.get("id")
                    if doc_id:
                        incoming_keep_det_ids.add(doc_id)
                        if doc_id not in existing_det_att_ids:
                            docs_det.append((4, doc_id, 0))
                    else:
                        if doc.get("datas"):
                            docs_det.append((0, 0, {
                                "name": doc["name"],
                                "datas": doc["datas"]
                            }))

                # Desvincular los que ya no están
                for old_det_att_id in existing_det_att_ids:
                    if old_det_att_id not in incoming_keep_det_ids:
                        docs_det.append((3, old_det_att_id, 0))

                det["carga_documento"] = docs_det
            else:
                det.pop("carga_documento", None)

            if line_id:
                # Odoo Command 1: update existing line
                detalles_odoo.append((1, line_id, det))
            else:
                # Odoo Command 0: create new line
                detalles_odoo.append((0, 0, det))
                
        values["detalle_ids"] = detalles_odoo

    # 2. Documentos adjuntos de nivel superior (Many2many) — Smart Merge
    if "carga_documento" in values:
        # Obtener IDs actuales de adjuntos en Odoo
        try:
            current_record = odoo_client.read("minsa.registro", [registro_id], fields=["carga_documento"])
            existing_att_ids = set(current_record[0].get("carga_documento", []) if current_record else [])
        except Exception:
            existing_att_ids = set()

        incoming_docs = values["carga_documento"]
        incoming_keep_ids = set()
        documentos_odoo = []

        for doc in incoming_docs:
            doc_id = doc.get("id")
            if doc_id:
                # Archivo existente que se quiere conservar
                incoming_keep_ids.add(doc_id)
                # Solo enlazar si no estaba ya (por seguridad)
                if doc_id not in existing_att_ids:
                    documentos_odoo.append((4, doc_id, 0))
            else:
                # Archivo nuevo: crear
                if doc.get("datas"):
                    documentos_odoo.append((0, 0, {
                        "name": doc["name"],
                        "datas": doc["datas"]
                    }))

        # Desvincular los que ya no están
        for old_id in existing_att_ids:
            if old_id not in incoming_keep_ids:
                documentos_odoo.append((3, old_id, 0))

        values["carga_documento"] = documentos_odoo

    try:
        odoo_client.write("minsa.registro", [registro_id], values)
        return {"success": True, "message": f"Ficha de registro #{registro_id} actualizada exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================================
# ACCIONES DE WORKFLOW DE REGISTRO (BOTONES)
# =====================================================================
@app.post("/api/registros/{registro_id}/validar", tags=["Acciones de Workflow"])
def action_validar_registro(registro_id: int, token: str = Depends(verify_token)):
    """
    Ejecuta el botón 'Validar' en Odoo para cambiar el estado de la ficha (de borrador a Validado Red, o a Validado Diresa).
    """
    try:
        odoo_client.call_button("minsa.registro", "action_validar", [registro_id])
        return {"success": True, "message": "Ficha validada exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/registros/{registro_id}/borrador", tags=["Acciones de Workflow"])
def action_borrador_registro(registro_id: int, token: str = Depends(verify_token)):
    """
    Mueve la ficha de registro de vuelta a estado 'Borrador'.
    """
    try:
        odoo_client.call_button("minsa.registro", "action_borrador", [registro_id])
        return {"success": True, "message": "Ficha devuelta a borrador exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/attachments/{attachment_id}", tags=["Archivos Adjuntos"])
def get_attachment(attachment_id: int, token: str = Depends(verify_token)):
    """
    Obtiene los datos de un archivo adjunto por su ID (incluyendo contenido base64).
    """
    try:
        records = odoo_client.read("ir.attachment", [attachment_id], fields=["id", "name", "mimetype", "datas"])
        if not records:
            raise HTTPException(status_code=404, detail=f"Adjunto con ID {attachment_id} no encontrado.")
        return records[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/registros/{registro_id}/revalidar", tags=["Acciones de Workflow"])
def action_revalidar_registro(registro_id: int, token: str = Depends(verify_token)):
    """
    Ejecuta el botón 'Revalidar' para actualizar la fecha de revalidación.
    """
    try:
        odoo_client.call_button("minsa.registro", "action_revalidar", [registro_id])
        return {"success": True, "message": "Ficha revalidada correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================================
# ENDPOINTS: TABLAS MAESTRAS / RENIPRESS (DIRESA, RED, MICRORED, EESS)
# =====================================================================
@app.get("/api/diresas", response_model=List[DiresaResponse], tags=["Tablas Maestras"])
def get_diresas(limit: int = 100, token: str = Depends(verify_token)):
    """
    Obtiene el listado de DIRESA (Dirección Regional de Salud).
    """
    try:
        return odoo_client.search_read(
            model="renipress.diresa",
            domain=[("active", "=", True)],
            fields=["id", "name", "codigo_diresa"],
            limit=limit,
            order="name asc"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/redes", response_model=List[RedResponse], tags=["Tablas Maestras"])
def get_redes(
    diresa_id: Optional[int] = None,
    limit: int = 100,
    token: str = Depends(verify_token)
):
    """
    Obtiene el listado de Redes de Salud.
    """
    domain = [("active", "=", True)]
    if diresa_id:
        domain.append(("diresa_id", "=", diresa_id))
    try:
        return odoo_client.search_read(
            model="renipress.red",
            domain=domain,
            fields=["id", "name", "codigo_red", "diresa_id"],
            limit=limit,
            order="name asc"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/microredes", response_model=List[MicroredResponse], tags=["Tablas Maestras"])
def get_microredes(
    red_id: Optional[int] = None,
    limit: int = 100,
    token: str = Depends(verify_token)
):
    """
    Obtiene el listado de Micro Redes de Salud.
    """
    domain = [("active", "=", True)]
    if red_id:
        domain.append(("red_id", "=", red_id))
    try:
        return odoo_client.search_read(
            model="renipress.microred",
            domain=domain,
            fields=["id", "name", "codigo_microred", "red_id"],
            limit=limit,
            order="name asc"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/establecimientos", response_model=List[EessResponse], tags=["Tablas Maestras"])
def get_establecimientos(
    search: Optional[str] = None,
    diresa_id: Optional[int] = None,
    red_id: Optional[int] = None,
    limit: int = 100,
    token: str = Depends(verify_token)
):
    """
    Obtiene el listado de Establecimientos de Salud (IPRESS / RENIPRESS).
    """
    domain = [("active", "=", True)]
    if diresa_id:
        domain.append(("diresa_id", "=", diresa_id))
    if red_id:
        domain.append(("red_id", "=", red_id))
    if search:
        domain.append("|")
        domain.append(("codigo_eess", "ilike", search))
        domain.append(("name", "ilike", search))
        
    try:
        return odoo_client.search_read(
            model="renipress.eess",
            domain=domain,
            fields=["id", "name", "codigo_eess", "direccion", "microred_id", "red_id", "diresa_id", "categoria", "condicion"],
            limit=limit,
            order="name asc"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auxiliar/{model_name}", tags=["Tablas Auxiliares"])
def get_auxiliar_model(model_name: str, token: str = Depends(verify_token)):
    """
    Retorna el listado (id, name) de cualquier tabla auxiliar configurada en Odoo
    para poblar los dropdowns dinámicos en el front-end.
    """
    try:
        model_map = {
            "operadores": "minsa.operador.mobil",
            "generos": "minsa.genero",
            "etnias": "minsa.etnia",
            "seguros": "minsa.seguro",
            "dialectos": "minsa.dialecto",
            "grados": "minsa.grado.instruccion",
            "voluntariados": "minsa.tipo.voluntariado",
            "niveles": "minsa.nivel.agente",
            "estandares": "minsa.estandar.laboral"
        }
        odoo_model = model_map.get(model_name)
        if not odoo_model:
            raise HTTPException(status_code=400, detail="Modelo auxiliar no válido")
            
        return odoo_client.search_read(
            model=odoo_model,
            domain=[("active", "=", True)] if model_name != "dialectos" and model_name != "estandares" else [],
            fields=["id", "name"],
            limit=200,
            order="name asc"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ubigeos", tags=["Tablas Maestras"])
def get_ubigeos():
    """
    Retorna el listado de Departamentos, Provincias y Distritos desde Odoo 14.
    Clasifica de manera exacta usando las relaciones state_id y province_id de Odoo.
    """
    try:
        # Consultar todos los ubigeos peruanos en res.country.state
        raw_states = odoo_client.search_read(
            model="res.country.state",
            domain=[("country_id.code", "=", "PE")],
            fields=["id", "name", "code", "state_id", "province_id"],
            limit=5000
        )

        departamentos = []
        provincias = []
        distritos = []

        for s in raw_states:
            # Extraer IDs de relaciones
            state_val = s.get("state_id")
            prov_val = s.get("province_id")
            
            dep_id = state_val[0] if isinstance(state_val, (list, tuple)) else state_val
            prov_id = prov_val[0] if isinstance(prov_val, (list, tuple)) else prov_val

            # CLASIFICACIÓN NATVA ODOO:
            # 1. Departamento: No tiene state_id ni province_id
            if dep_id is None and prov_id is None:
                departamentos.append({
                    "id": s["id"],
                    "nombre": s["name"].upper()
                })
            
            # 2. Provincia: Tiene state_id (departamento) pero no province_id
            elif dep_id is not None and prov_id is None:
                provincias.append({
                    "id": s["id"],
                    "nombre": s["name"].upper(),
                    "departamento_id": dep_id
                })
            
            # 3. Distrito: Tiene province_id (provincia) y state_id (departamento)
            elif dep_id is not None and prov_id is not None:
                distritos.append({
                    "id": s["id"],
                    "nombre": s["name"].upper(),
                    "provincia_id": prov_id
                })

        return {
            "departamentos": departamentos,
            "provincias": provincias,
            "distritos": distritos
        }

    except Exception as e:
        # Failover robusto para que la aplicación móvil no falle
        return {
            "departamentos": [],
            "provincias": [],
            "distritos": []
        }



