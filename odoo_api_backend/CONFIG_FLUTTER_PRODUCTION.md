# Configuración de Producción e Integración con Flutter (Android)

Este documento detalla el cumplimiento de las tecnologías de seguridad implementadas en la API intermedia de Python y la guía paso a paso para integrarla de forma rápida y segura con tu aplicación móvil en Flutter.

---

## 🔒 Cumplimiento de Tecnologías de Seguridad

La API intermedia ha sido diseñada bajo estrictos estándares de seguridad informática para garantizar que el servidor Odoo de producción nunca quede expuesto directamente:

1. **Autenticación mediante Bearer Tokens (HTTPBearer):**
   Todos los endpoints CRUD bajo la ruta `/api/*` están protegidos por una capa de seguridad basada en tokens de autorización. Para realizar cualquier petición, la aplicación de Flutter debe enviar el header `Authorization: Bearer <API_BEARER_TOKEN>`.
   
2. **Políticas CORS Habilitadas (Cross-Origin Resource Sharing):**
   Se integró `CORSMiddleware` en FastAPI para autorizar solicitudes HTTP cruzadas. Esto es esencial para que la aplicación en Flutter (especialmente en compilaciones Flutter Web o emuladores con restricciones de red) pueda comunicarse con la API de forma fluida y sin bloqueos de navegador.

3. **Aislamiento de Credenciales (.env):**
   Las contraseñas de Odoo, credenciales de base de datos, tokens de API y URLs del servidor están completamente aisladas del código fuente. Se leen dinámicamente mediante variables de entorno desde el archivo `.env`, cumpliendo con las directivas de seguridad de desarrollo ágil de la metodología de las *12 Factor Apps*.

4. **Sanitización y Validación de Datos (Pydantic):**
   Las peticiones entrantes son analizadas y sanitizadas antes de llegar a la capa de base de datos o de comunicarse con Odoo. Esto previene inyecciones maliciosas, datos corruptos y desajustes de tipos en los parámetros XML-RPC de Odoo.

5. **Encriptación en Tránsito (HTTPS/TLS):**
   El backend se conecta al servidor Hostinger utilizando el protocolo seguro XML-RPC sobre HTTPS (`https://...`). Se recomienda que en producción el servidor de FastAPI sea desplegado detrás de un proxy inverso como Nginx o Caddy con un certificado SSL activo (Let's Encrypt).

---

## 🚀 Despliegue a Producción (FastAPI)

Para mover este backend a un servidor en producción (por ejemplo, VPS en Hostinger, Easypanel, DigitalOcean, etc.):

1. Clona el repositorio en tu servidor.
2. Crea tu entorno virtual de Python e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Edita el archivo `.env` para apuntar a la URL y base de datos de producción de Odoo:
   ```ini
   ODOO_URL=https://tu-servidor-odoo-produccion.host.com
   ODOO_DB=minsa_db_produccion
   ODOO_USERNAME=admin_produccion@correo.com
   ODOO_PASSWORD=contraseña_segura
   API_BEARER_TOKEN=token_generado_muy_largo_y_seguro
   ```
4. Levanta el servidor en producción usando Uvicorn detrás de Nginx:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

## 📱 Código de Integración en Flutter (Dart)

A continuación se detalla la clase controladora en Dart lista para copiar y pegar en tu proyecto de Flutter para realizar las llamadas CRUD.

### 1. Cliente API de Flutter (`minsa_api_client.dart`)

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class MinsaApiClient {
  // Configura la URL del API de FastAPI en producción
  static const String baseUrl = 'https://tu-api-fastapi-produccion.com/api';
  
  // Debe coincidir exactamente con el token en el archivo .env de producción
  static const String bearerToken = 'token_generado_muy_largo_y_seguro';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $bearerToken',
  };

  // --- CRUD AGENTES COMUNITARIOS ---

  // Obtener agentes comunitarios
  Future<List<dynamic>> getAgentes({String? numeroDocumento, String? name}) async {
    String query = '';
    if (numeroDocumento != null) query += '&numero_documento=$numeroDocumento';
    if (name != null) query += '&name=$name';

    final response = await http.get(
      Uri.parse('$baseUrl/agentes?limit=50$query'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al obtener agentes: ${response.body}');
    }
  }

  // Registrar un nuevo Agente Comunitario (Foto obligatoria en Base64 plano)
  Future<Map<String, dynamic>> crearAgente(Map<String, dynamic> datosAgente) async {
    final response = await http.post(
      Uri.parse('$baseUrl/agentes'),
      headers: _headers,
      body: jsonEncode(datosAgente),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al crear agente: ${response.body}');
    }
  }

  // Actualizar Agente
  Future<Map<String, dynamic>> actualizarAgente(int id, Map<String, dynamic> datosAgente) async {
    final response = await http.put(
      Uri.parse('$baseUrl/agentes/$id'),
      headers: _headers,
      body: jsonEncode(datosAgente),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al actualizar agente: ${response.body}');
    }
  }

  // --- CRUD FICHAS DE REGISTRO ---

  // Obtener Fichas
  Future<List<dynamic>> getFichas() async {
    final response = await http.get(
      Uri.parse('$baseUrl/registros?limit=50'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al obtener fichas: ${response.body}');
    }
  }

  // Crear Ficha de Registro con sus miembros (Agregar Línea)
  Future<Map<String, dynamic>> crearFicha(Map<String, dynamic> datosFicha) async {
    final response = await http.post(
      Uri.parse('$baseUrl/registros'),
      headers: _headers,
      body: jsonEncode(datosFicha),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al crear ficha: ${response.body}');
    }
  }

  // Editar Ficha de Registro
  Future<Map<String, dynamic>> actualizarFicha(int id, Map<String, dynamic> datosFicha) async {
    final response = await http.put(
      Uri.parse('$baseUrl/registros/$id'),
      headers: _headers,
      body: jsonEncode(datosFicha),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al actualizar ficha: ${response.body}');
    }
  }
}
```

---

## 📋 Estructuras de Datos JSON para Peticiones HTTP

### A. Estructura para Crear un Agente (`POST /api/agentes`)
> **Nota:** El campo `foto` debe ser un Base64 de la imagen limpio, sin el prefijo Data-URI (es decir, sin `data:image/png;base64,`).

```json
{
  "tipo_documento": "01",
  "numero_documento": "71234567",
  "ape_paterno": "Perez",
  "ape_materno": "Gomez",
  "nombres": "Juan",
  "celular": "964396353",
  "direccion": "Av. Salaverry 801, Jesús María",
  "es_voluntario": true,
  "diresa_id": 1,
  "red_id": 2,
  "establecimiento_id": 15,
  "foto": "iVBORw0KGgoAAAANSUhEUgAAADIA..."
}
```

### B. Estructura para Crear Ficha con Miembros Asociados (`POST /api/registros`)

```json
{
  "diresa_id": 1,
  "establecimiento_id": 15,
  "tipo_registro": "agente",
  "tipo_archivo": "adjunto",
  "carga_documento": [
    {
      "name": "acta_firma_agentes.pdf",
      "datas": "JVBERi0xLjQKJ..." // Base64 plano del archivo PDF o imagen
    }
  ],
  "detalle_ids": [
    {
      "agente_comunitario_id": 4, // ID del agente ya creado en Odoo
      "fecha_inicio": "2026-07-06",
      "estado": "activo"
    }
  ]
}
```
