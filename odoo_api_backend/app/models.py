from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Union, Tuple
from datetime import date

# ----------------------------------------------------
# COMMON SCHEMAS
# ----------------------------------------------------
class UserLogin(BaseModel):
    usuario: str
    password: str

class AttachmentCreate(BaseModel):
    id: Optional[int] = Field(None, description="ID del adjunto existente en Odoo (para conservar archivos ya subidos)")
    name: str = Field(..., description="Nombre del archivo (ej: acta.pdf)")
    datas: Optional[str] = Field(None, description="Contenido en Base64 sin prefijo URI (requerido solo para archivos nuevos)")

class AttachmentResponse(BaseModel):
    id: int
    name: str
    mimetype: Optional[str] = None


# ----------------------------------------------------
# AGENTE COMUNITARIO SCHEMAS
# ----------------------------------------------------
class AgenteComunitarioBase(BaseModel):
    tipo_documento: str = Field(..., description="Tipo de documento ('01'=DNI, '03'=Carne Ext, '07'=Pasaporte, '23'=PTP)")
    numero_documento: str = Field(..., description="Número de documento de identidad")
    ape_paterno: str = Field(..., description="Apellido Paterno")
    ape_materno: Optional[str] = Field(None, description="Apellido Materno")
    nombres: str = Field(..., description="Nombres")
    telefono: Optional[str] = Field(None, description="Teléfono fijo")
    celular: Optional[str] = Field(None, description="Número de celular")
    email: Optional[str] = Field(None, description="Correo electrónico")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento en formato YYYY-MM-DD")
    direccion: str = Field(..., description="Dirección de residencia")
    es_voluntario: bool = Field(False, description="¿Es voluntario?")
    
    # ID fields (representing Many2one relations)
    diresa_id: Optional[int] = Field(None, description="ID de Diresa (renipress.diresa)")
    red_id: Optional[int] = Field(None, description="ID de Red (renipress.red)")
    establecimiento_id: Optional[int] = Field(None, description="ID de Establecimiento (renipress.eess)")
    genero_id: Optional[int] = Field(None, description="ID de Género (minsa.genero)")
    etnia_id: Optional[int] = Field(None, description="ID de Etnia (minsa.etnia)")
    seguro_id: Optional[int] = Field(None, description="ID de Seguro (minsa.seguro)")
    
    # Ubigeo
    state_id: Optional[int] = Field(None, description="ID de Departamento (res.country.state)")
    province_id: Optional[int] = Field(None, description="ID de Provincia (res.country.state)")
    district_id: Optional[int] = Field(None, description="ID de Distrito (res.country.state)")

    # Many2many: puede tener múltiples idiomas/dialectos
    dialecto_ids: Optional[List[int]] = Field(None, description="IDs de Idiomas/Dialectos (minsa.dialecto)")
    grado_instruccion_id: Optional[int] = Field(None, description="ID de Grado Instrucción (minsa.grado.instruccion)")
    nivel_agente_id: Optional[int] = Field(None, description="ID de Nivel de Agente (minsa.nivel.agente)")
    estandar_laboral_id: Optional[int] = Field(None, description="ID de Estándar Laboral (minsa.estandar.laboral)")
    operador_id: Optional[int] = Field(None, description="ID de Operador (minsa.operador.mobil)")
    # tipo_voluntariado_id: Many2one (simple)
    tipo_voluntariado_id: Optional[int] = Field(None, description="ID principal de Tipo de Voluntariado (minsa.tipo.voluntariado)")
    # tipo_voluntariado_ids: Many2many (múltiple)
    tipo_voluntariado_ids: Optional[List[int]] = Field(None, description="IDs de Tipos de Voluntariado múltiple (minsa.tipo.voluntariado)")
    foto: Optional[str] = Field(None, description="Foto del agente en formato Base64")

class AgenteComunitarioCreate(AgenteComunitarioBase):
    pass

class AgenteComunitarioUpdate(BaseModel):
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    ape_paterno: Optional[str] = None
    ape_materno: Optional[str] = None
    nombres: Optional[str] = None
    telefono: Optional[str] = None
    celular: Optional[str] = None
    email: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    es_voluntario: Optional[bool] = None
    
    diresa_id: Optional[int] = None
    red_id: Optional[int] = None
    establecimiento_id: Optional[int] = None
    genero_id: Optional[int] = None
    etnia_id: Optional[int] = None
    seguro_id: Optional[int] = None
    
    state_id: Optional[int] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None

    # Many2many
    dialecto_ids: Optional[List[int]] = None
    grado_instruccion_id: Optional[int] = None
    nivel_agente_id: Optional[int] = None
    estandar_laboral_id: Optional[int] = None
    operador_id: Optional[int] = None
    tipo_voluntariado_id: Optional[int] = None
    tipo_voluntariado_ids: Optional[List[int]] = None
    foto: Optional[str] = None

class AgenteComunitarioResponse(BaseModel):
    id: int
    name: str
    tipo_documento: str
    numero_documento: str
    ape_paterno: Optional[str] = None
    ape_materno: Optional[str] = None
    nombres: Optional[str] = None
    telefono: Optional[str] = None
    celular: Optional[str] = None
    email: Optional[str] = None
    fecha_nacimiento: Optional[Union[str, date]] = None
    edad: Optional[int] = None
    direccion: Optional[str] = None
    es_voluntario: bool
    
    # Many2one fields return [id, name_display] in Odoo, so we model them as Union[Tuple[int, str], int, None]
    diresa_id: Optional[Union[Tuple[int, str], int]] = None
    red_id: Optional[Union[Tuple[int, str], int]] = None
    establecimiento_id: Optional[Union[Tuple[int, str], int]] = None
    genero_id: Optional[Union[Tuple[int, str], int]] = None
    etnia_id: Optional[Union[Tuple[int, str], int]] = None
    seguro_id: Optional[Union[Tuple[int, str], int]] = None
    # Many2many: Odoo devuelve lista de IDs
    dialecto_ids: Optional[List[int]] = None
    grado_instruccion_id: Optional[Union[Tuple[int, str], int]] = None
    nivel_agente_id: Optional[Union[Tuple[int, str], int]] = None
    estandar_laboral_id: Optional[Union[Tuple[int, str], int]] = None
    operador_id: Optional[Union[Tuple[int, str], int]] = None
    tipo_voluntariado_id: Optional[Union[Tuple[int, str], int]] = None
    tipo_voluntariado_ids: Optional[List[int]] = None
    foto: Optional[str] = None


# ----------------------------------------------------
# REGISTRO DETALLE SCHEMAS
# ----------------------------------------------------
class RegistroDetalleBase(BaseModel):
    agente_comunitario_id: int = Field(..., description="ID del Agente Comunitario (minsa.agente.comunitario)")
    fecha_inicio: Optional[date] = Field(None, description="Fecha de inicio de actividad YYYY-MM-DD")
    fecha_fin: Optional[date] = Field(None, description="Fecha de fin de actividad YYYY-MM-DD")
    observacion: Optional[str] = Field(None, description="Observaciones")
    estado: str = Field("activo", description="Estado ('activo', 'noactivo')")
    carga_documento: Optional[List[AttachmentCreate]] = Field(default=[], description="Documento adjunto al detalle")

class RegistroDetalleCreate(RegistroDetalleBase):
    pass

class RegistroDetalleResponse(BaseModel):
    id: int
    registro_id: Optional[Union[Tuple[int, str], int]] = None
    agente_comunitario_id: Optional[Union[Tuple[int, str], int]] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    name: Optional[str] = None
    celular: Optional[str] = None
    fecha_inicio: Optional[Union[str, date]] = None
    fecha_fin: Optional[Union[str, date]] = None
    observacion: Optional[str] = None
    estado: str
    carga_documento: List[Union[AttachmentResponse, Tuple[int, str], int]] = []


# ----------------------------------------------------
# REGISTRO SCHEMAS
# ----------------------------------------------------
class RegistroBase(BaseModel):
    name: Optional[str] = Field(None, description="Nombre del comité (opcional si es de tipo agente)")
    diresa_id: int = Field(..., description="ID de la DIRESA (renipress.diresa)")
    establecimiento_id: int = Field(..., description="ID del Establecimiento RENIPRESS (renipress.eess)")
    tipo_registro: str = Field("agente", description="Tipo de registro ('agente' o 'comite')")
    tipo_archivo: str = Field("adjunto", description="Tipo de archivo ('adjunto', 'url')")
    url_documento: Optional[str] = Field(None, description="URL del documento si aplica")


class RegistroCreate(RegistroBase):
    # En Odoo se puede enviar la creación de líneas relacionales usando el comando tuples:
    # (0, 0, values) para crear un nuevo registro detalle relacionado
    detalle_ids: List[RegistroDetalleCreate] = Field(default=[], description="Lista de miembros/detalles a asociar")
    carga_documento: List[AttachmentCreate] = Field(default=[], description="Lista de documentos adjuntos obligatorios")

class RegistroDetalleUpdate(BaseModel):
    id: Optional[int] = Field(None, description="ID del registro detalle de Odoo")
    agente_comunitario_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    observacion: Optional[str] = None
    estado: str = "activo"
    carga_documento: Optional[List[AttachmentCreate]] = None

class RegistroUpdate(BaseModel):
    name: Optional[str] = None
    diresa_id: Optional[int] = None
    establecimiento_id: Optional[int] = None
    tipo_registro: Optional[str] = None
    tipo_archivo: Optional[str] = None
    url_documento: Optional[str] = None
    detalle_ids: Optional[List[RegistroDetalleUpdate]] = None
    carga_documento: Optional[List[AttachmentCreate]] = None

class RegistroResponse(BaseModel):
    id: int
    name: Optional[str] = None
    diresa_id: Optional[Union[Tuple[int, str], int]] = None
    establecimiento_id: Optional[Union[Tuple[int, str], int]] = None
    red_id: Optional[Union[Tuple[int, str], int]] = None
    ubigeo: Optional[str] = None
    renipress: Optional[str] = None
    tipo_registro: str
    tipo_archivo: str
    url_documento: Optional[str] = None
    cantidad_detalle: int
    estado: str
    create_date: Optional[str] = None
    valida_date: Optional[str] = None
    revalida_date: Optional[str] = None
    evalua_revalida: int
    # Odoo one2many returns a list of integer IDs by default or we can read them separately
    detalle_ids: List[Union[RegistroDetalleResponse, int]] = []
    carga_documento: List[Union[AttachmentResponse, Tuple[int, str], int]] = []


# ----------------------------------------------------
# MASTER DATA / RENIPRESS SCHEMAS
# ----------------------------------------------------
class DiresaResponse(BaseModel):
    id: int
    name: str
    codigo_diresa: str

class RedResponse(BaseModel):
    id: int
    name: str
    codigo_red: str
    diresa_id: Optional[Union[Tuple[int, str], int]] = None

class MicroredResponse(BaseModel):
    id: int
    name: str
    codigo_microred: str
    red_id: Optional[Union[Tuple[int, str], int]] = None

class EessResponse(BaseModel):
    id: int
    name: str
    codigo_eess: str
    direccion: Optional[str] = None
    microred_id: Optional[Union[Tuple[int, str], int]] = None
    red_id: Optional[Union[Tuple[int, str], int]] = None
    diresa_id: Optional[Union[Tuple[int, str], int]] = None
    categoria: Optional[str] = None
    condicion: Optional[str] = None
