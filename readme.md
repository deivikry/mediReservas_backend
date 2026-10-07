# MediReserva API

Backend del sistema de citas médicas para la Clínica MediReserva. Construido con FastAPI + PostgreSQL, con autenticación JWT, autorización por rol y autorización a nivel de dato.

**ver el archivo "pruebas_postman.docx" **

---

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **PostgreSQL** + **psycopg** — base de datos
- **Pydantic v2** — validación y schemas
- **python-jose** — JWT
- **passlib[bcrypt]** — hashing de contraseñas

---

## Estructura del proyecto

```
backend/
├── .env
├── .gitignore
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py              # wiring y create_all
    ├── config.py            # settings desde .env
    ├── database.py          # engine, SessionLocal, Base, get_db
    ├── models/              # SQLAlchemy
    │   ├── usuario.py
    │   ├── medico.py
    │   ├── horario.py
    │   └── cita.py
    ├── schemas/             # Pydantic (input/output)
    │   ├── usuario.py
    │   ├── medico.py
    │   ├── horario.py
    │   └── cita.py
    ├── services/            # lógica de negocio
    │   ├── usuario_service.py
    │   ├── horario_service.py
    │   └── cita_service.py
    ├── routers/             # endpoints
    │   ├── auth.py
    │   ├── horario_router.py
    │   ├── cita_router.py
    │   └── admin_router.py
    └── auth/
        ├── security.py      # hash + crear/decodificar tokens
        └── dependencies.py  # usuario actual + roles
```

---

## Modelo de roles

El sistema maneja **3 roles**, definidos en el enum `RolEnum` del modelo `Usuario`:

| Rol | Qué puede hacer |
|---|---|
| **paciente** | Ver y agendar **SUS** citas. Cancelar solo las suyas. No puede ver ni tocar nada de otros. |
| **medico** | Crear, listar, editar y eliminar **SU** agenda de horarios. No puede tocar la de otros médicos. |
| **admin** | Supervisar a todos los usuarios del sistema. Ver y cambiar roles. |

**Regla crítica:** el rol por defecto al registrarse es **`paciente`**. El rol se fija en el servidor, nunca se acepta desde el body. Médicos y admins se crean por vía controlada (BD / endpoint de admin).

---

## Autenticación

- **Registro:** email + password. La contraseña se hashea con bcrypt y **nunca** se devuelve en la respuesta.
- **Login:** OAuth2 form-urlencoded. Devuelve un `access_token` y un `refresh_token` (ambos JWT).
- **Access token:** corta duración (30 min). Se usa en cada petición.
- **Refresh token:** larga duración (7 días). Sirve solo para pedir un nuevo par de tokens sin re-loguear.

### Estructura del JWT

```json
{
  "sub": "1",
  "rol": "paciente",
  "type": "access",
  "exp": 1234567890
}
```

- `sub` → id del usuario (fuente de identidad de cada petición)
- `rol` → rol del usuario
- `type` → `access` o `refresh` (evita que un token se use en el lugar del otro)

---

## Códigos de error

| Código | Cuándo | Encabezado |
|---|---|---|
| **401 Unauthorized** | No sé quién eres: token ausente, inválido, expirado o tipo equivocado | `WWW-Authenticate: Bearer` |
| **403 Forbidden** | Sé quién eres, pero no te corresponde: rol incorrecto o dato ajeno | — |
| **400 Bad Request** | Regla de negocio violada (ej: email duplicado) | — |
| **404 Not Found** | Recurso no existe | — |
| **422 Unprocessable Entity** | Body mal formado (Pydantic) | — |

---

## Endpoints

### Autenticación — `/auth`

| Método | Ruta | Auth | Body | Respuesta |
|---|---|---|---|---|
| POST | `/auth/registro` | Público | `{nombre, email, password}` (JSON) | `UsuarioOut` (201) |
| POST | `/auth/login` | Público | `username`, `password` (form-urlencoded) | `Token` (200) |
| POST | `/auth/refresh` | Refresh token | `{refresh_token}` (JSON) | `Token` (200) |

**`Token`:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Horarios — `/horarios` (médico)

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| POST | `/horarios/` | **medico** | Crea un horario. El `medico_id` sale del token. |
| GET | `/horarios/mis-horarios` | **medico** | Lista solo los horarios del médico autenticado. |
| PUT | `/horarios/{id}` | **medico** | Edita un horario **solo si es suyo**. Si no, 403. |
| DELETE | `/horarios/{id}` | **medico** | Elimina un horario **solo si es suyo**. Si no, 403. |

**Body de POST / PUT:**
```json
{ "fecha_hora": "2025-12-01T10:00:00" }
```

> El `medico_id` **nunca** se envía en el body. Se obtiene cruzando el `sub` del token con la tabla `medicos`.

---

### Citas — `/citas` (paciente)

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| POST | `/citas/` | **paciente** | Agenda una cita. El `paciente_id` sale del token. |
| GET | `/citas/mis-citas` | Autenticado | Lista solo las citas del paciente autenticado. |
| PUT | `/citas/{id}/cancelar` | **paciente** | Cancela **solo si es suya**. Si no, 403. |

**Body de POST:**
```json
{
  "medico_id": 1,
  "horario_id": 1,
  "fecha_hora": "2025-12-01T10:00:00"
}
```

> El `paciente_id` **nunca** se envía en el body. Se obtiene del `sub` del token.

---

### Admin — `/admin`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| GET | `/admin/usuarios` | **admin** | Lista todos los usuarios del sistema. |
| PUT | `/admin/usuarios/{id}/rol?nuevo_rol=medico` | **admin** | Cambia el rol de un usuario. |

---

## Autorización a nivel de dato

El corazón de la seguridad de MediReserva. No basta con tener el rol correcto: hay que verificar que **el dato sea tuyo**.

### Reglas

1. **Horarios:** al editar o eliminar, se compara `horario.medico_id` con el `medico.id` del usuario del token. Si no coinciden → **403**.
2. **Citas:** al listar, se filtra por `cita.paciente_id == usuario.id` (del token). Al cancelar, se compara `cita.paciente_id` con el `sub` del token. Si no coinciden → **403**.
3. **Datos de entrada:** los campos `paciente_id` y `medico_id` **nunca** vienen del cliente; se inyectan desde el token.

### Dependencias de rol disponibles

- `obtener_usuario_actual` → valida token y devuelve el `Usuario`
- `requiere_paciente` → exige rol paciente
- `requiere_medico` → exige rol médico
- `requiere_admin` → exige rol admin
- `requiere_rol(*roles)` → versión genérica

---

## Cómo levantar el proyecto

```powershell
# 1. Crear y activar venv
py -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
# DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/medireserva_db
# SECRET_KEY=...
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_MINUTES=10080

# 4. Crear la base de datos en PostgreSQL
# CREATE DATABASE medireserva_db;

# 5. Levantar el servidor
uvicorn app.main:app --reload
```

**Swagger:** http://127.0.0.1:8000/docs

---

## Guía rápida de pruebas en Postman

### Preparación

1. Registra 3 usuarios distintos en `/auth/registro`.
2. En la BD, promueve roles:
   ```sql
   UPDATE usuarios SET rol='admin'  WHERE email='admin@test.com';
   UPDATE usuarios SET rol='medico' WHERE email='medico@test.com';
   INSERT INTO medicos (usuario_id, especialidad)
   VALUES ((SELECT id FROM usuarios WHERE email='medico@test.com'), 'Cardiología');
   ```
3. Haz login de los 3 y guarda los `access_token`.

### Casos clave

| # | Endpoint | Token | Resultado esperado |
|---|---|---|---|
| 1 | `POST /horarios/` | médico | 201 (horario creado a su nombre) |
| 2 | `POST /horarios/` | paciente | **403** |
| 3 | `PUT /horarios/{id}` | médico dueño | 200 |
| 4 | `PUT /horarios/{id}` | médico ajeno | **403** |
| 5 | `POST /citas/` | paciente | 201 (cita a su nombre) |
| 6 | `GET /citas/mis-citas` | paciente A | solo las de A |
| 7 | `PUT /citas/{id}/cancelar` | paciente B (dueño es A) | **403** |
| 8 | `POST /auth/refresh` | refresh token | nuevo par de tokens |
| 9 | `POST /auth/refresh` | access token | **401** |
| 10 | Cualquier endpoint protegido | sin token | **401** + `WWW-Authenticate: Bearer` |
| 11 | `GET /admin/usuarios` | admin | 200 (lista completa) |
| 12 | `GET /admin/usuarios` | paciente | **403** |

---

## Regla de oro

> **Todo permiso se calcula cruzando el `sub` del token con las llaves foráneas del dato.**
> Nunca se confía en el body del cliente para saber "de quién es" algo.

---

## Estado del proyecto

- [x] Parte 1 — Fundación + autenticación (registro, login, JWT)
- [x] Parte 2 — Autorización por rol + autorización a nivel de dato + refresh tokens + errores estandarizados
