# Base de Datos y Autenticación

## Arquitectura de Base de Datos

El sistema utiliza **dos bases de datos separadas**:

1. **glpi_sso** (MariaDB) - Autenticación, usuarios, conversaciones
2. **glpi** (MariaDB) - Datos de GLPI (tickets, inventario, etc.)

### Separación de Responsabilidades

```
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS SSO                        │
│                   (glpi_sso - MariaDB)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • users (usuarios del sistema)                      │   │
│  │  • sessions (tokens JWT activos)                     │   │
│  │  • refresh_tokens (tokens de refresco)               │   │
│  │  • login_attempts (intentos de login)                │   │
│  │  • conversations (conversaciones del chat)           │   │
│  │  • messages (mensajes del chat)                      │   │
│  │  • user_settings (preferencias)                      │   │
│  │  • audit_log (registro de auditoría)                 │   │
│  │  • sso_providers (proveedores OAuth)                 │   │
│  │  • sso_connections (conexiones SSO)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Backend consulta ambas DBs
                         │
┌────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS GLPI                      │
│                     (glpi - MariaDB)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • glpi_tickets (tickets de soporte)                 │  │
│  │  • glpi_computers (inventario de PCs)                │  │
│  │  • glpi_users (usuarios de GLPI)                     │  │
│  │  • glpi_entities (entidades/organizaciones)          │  │
│  │  • glpi_locations (ubicaciones)                      │  │
│  │  • + 200 tablas más de GLPI                          │  │
│  └──────────────────────────────────────────────────────┘  │
│    ACCESO VÍA API REST ÚNICAMENTE (no directo)             │
└────────────────────────────────────────────────────────────┘
```

---

## Esquema de Base de Datos: glpi_sso

### 1. Tabla: users

Almacena los usuarios del sistema.

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,     -- Hash bcrypt
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
);
```

**Campos importantes**:
- `password_hash`: Hash bcrypt del password (nunca se almacena en texto plano)
- `is_active`: Permite desactivar usuarios sin eliminarlos
- `is_admin`: Distingue administradores de usuarios normales

### 2. Tabla: sessions

Rastreo de tokens JWT activos.

```sql
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_jti VARCHAR(255) UNIQUE NOT NULL,  -- JWT ID (único)
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT FALSE,        -- Para invalidar tokens
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token_jti (token_jti),
    INDEX idx_user_id (user_id)
);
```

**Propósito**: 
- Permite invalidar tokens específicos
- Auditoría de sesiones activas
- Implementar "logout from all devices"

### 3. Tabla: refresh_tokens

Tokens de refresco para renovar access tokens expirados.

```sql
CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token_hash (token_hash)
);
```

**Flujo de tokens**:
1. Login → Access Token (30 min) + Refresh Token (7 días)
2. Access Token expira → Frontend usa Refresh Token
3. Backend valida Refresh Token → Nuevo Access Token

### 4. Tabla: login_attempts

Registro de intentos de login (seguridad).

```sql
CREATE TABLE login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    success BOOLEAN NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_ip_address (ip_address)
);
```

**Uso**:
- Detectar ataques de fuerza bruta
- Bloquear IPs sospechosas
- Auditoría de seguridad

### 5. Tabla: conversations

Conversaciones del chat (historial).

```sql
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);
```

### 6. Tabla: messages

Mensajes de cada conversación.

```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INT DEFAULT 0,                  -- Tokens consumidos (IA)
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id)
);
```

**Roles**:
- `user`: Mensaje del usuario
- `assistant`: Respuesta del bot
- `system`: Mensajes del sistema

### 7. Tabla: user_settings

Preferencias del usuario.

```sql
CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    theme VARCHAR(20) DEFAULT 'light',           -- light/dark
    language VARCHAR(10) DEFAULT 'es',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    default_view VARCHAR(50) DEFAULT 'new_conversation',
    items_per_page INT DEFAULT 20,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 8. Tabla: audit_log

Registro de auditoría de acciones.

```sql
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,              -- login, logout, query, etc.
    entity_type VARCHAR(50),                  -- ticket, computer, etc.
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_action (action)
);
```

---

## Sistema de Autenticación

### 1. Flujo de Registro

```
┌──────────────────────────────────────────────────────────────┐
│  1. Usuario envía datos de registro                          │
│     POST /api/v1/auth/register                               │
│     {                                                        │
│       "username": "jperez",                                  │
│       "email": "jperez@universidad.edu",                     │
│       "password": "SecurePass123!",                          │
│       "full_name": "Juan Pérez"                              │
│     }                                                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Backend valida datos                                     │
│     • Email único                                            │
│     • Username único                                         │
│     • Password seguro (mínimo 8 caracteres)                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Hash del password con bcrypt                             │
│     password_hash = bcrypt.hash("SecurePass123!", rounds=12) │
│     → $2b$12$Kix8...                                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Insertar en base de datos                                │
│     INSERT INTO users (username, email, password_hash, ...)  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Generar tokens JWT                                       │
│     access_token (30 min) + refresh_token (7 días)           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Devolver respuesta                                       │
│     {                                                        │
│       "access_token": "eyJhbGc...",                          │
│       "refresh_token": "8f7d2b...",                          │
│       "user": {...}                                          │
│     }                                                        │
└──────────────────────────────────────────────────────────────┘
```

### 2. Flujo de Login

```
┌──────────────────────────────────────────────────────────────┐
│  1. Usuario envía credenciales                               │
│     POST /api/v1/auth/login                                  │
│     {                                                        │
│       "username": "jperez",                                  │
│       "password": "SecurePass123!"                           │
│     }                                                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Buscar usuario en DB                                     │
│     SELECT * FROM users                                      │
│     WHERE username = 'jperez' OR email = 'jperez'            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Verificar password                                       │
│     bcrypt.verify("SecurePass123!", user.password_hash)      │
│     → True/False                                             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Registrar intento de login                               │
│     INSERT INTO login_attempts                               │
│     (username, ip_address, success, ...)                     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Si éxito: Generar tokens JWT                             │
│     access_token + refresh_token                             │
│     Actualizar last_login del usuario                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Devolver tokens                                          │
│     {                                                        │
│       "access_token": "eyJhbGc...",                          │
│       "refresh_token": "8f7d2b...",                          │
│       "token_type": "Bearer",                                │
│       "expires_in": 1800,                                    │
│       "user": {                                              │
│         "id": 1,                                             │
│         "username": "jperez",                                │
│         "email": "jperez@universidad.edu",                   │
│         "full_name": "Juan Pérez"                            │
│       }                                                      │
│     }                                                        │
└──────────────────────────────────────────────────────────────┘
```

### 3. Estructura de JWT Token

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1",                          // User ID
    "username": "jperez",
    "email": "jperez@universidad.edu",
    "is_admin": false,
    "exp": 1732567890,                   // Expiration timestamp
    "iat": 1732566090,                   // Issued at timestamp
    "jti": "550e8400-e29b-41d4-..."     // JWT ID (único)
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### 4. Verificación de Token

```python
# Archivo: backend/auth/jwt_auth.py

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida JWT token"""
    try:
        # 1. Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Verificar expiración (automático en jwt.decode)
        
        # 3. Verificar que no esté revocado
        jti = payload.get("jti")
        session = db.query(Session).filter(
            Session.token_jti == jti,
            Session.is_revoked == False
        ).first()
        
        if not session:
            return None  # Token revocado
        
        return payload
        
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido
```

---

## Single Sign-On (SSO)

### Proveedores Soportados

El sistema soporta OAuth 2.0 / OpenID Connect con proveedores institucionales.

### Tabla: sso_providers

```sql
CREATE TABLE sso_providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,          -- "microsoft", "google", etc.
    display_name VARCHAR(100) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_secret VARCHAR(255) NOT NULL,
    authorization_url TEXT NOT NULL,
    token_url TEXT NOT NULL,
    userinfo_url TEXT,
    scopes TEXT NOT NULL,                      -- JSON array
    tenant_id VARCHAR(255),                    -- Para Azure AD
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: sso_connections

```sql
CREATE TABLE sso_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    provider_id INT NOT NULL,
    external_user_id VARCHAR(255) NOT NULL,    -- ID del usuario en el proveedor
    access_token_encrypted TEXT,               -- Token cifrado
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMP,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES sso_providers(id),
    UNIQUE KEY unique_connection (provider_id, external_user_id)
);
```

### Flujo de SSO con Microsoft Entra ID

```
┌──────────────────────────────────────────────────────────────┐
│  1. Usuario hace clic en "Iniciar con Microsoft"             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Backend genera URL de autorización                       │
│     https://login.microsoftonline.com/{tenant}/oauth2/       │
│     v2.0/authorize?                                          │
│       client_id=xxx                                          │
│       &response_type=code                                    │
│       &redirect_uri=https://app/callback                     │
│       &scope=openid profile email                            │
│       &state=random_csrf_token                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Usuario redirigido a login de Microsoft                  │
│     Inicia sesión con credenciales institucionales           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Microsoft redirige de vuelta con código                  │
│     https://app/callback?code=AUTH_CODE&state=...            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Backend intercambia código por tokens                    │
│     POST https://login.microsoftonline.com/{tenant}/         │
│     oauth2/v2.0/token                                        │
│     Recibe: access_token, id_token, refresh_token            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Backend extrae información del usuario                   │
│     Decodifica id_token (JWT) para obtener:                  │
│     - email: jperez@unitecnologica.edu.co                    │
│     - name: Juan Pérez                                       │
│     - sub: ID único de Microsoft                             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  7. Validar dominio del email                                │
│     ⚠️ CRÍTICO: Solo @unitecnologica.edu.co                  │
│     Si dominio inválido → Rechazar                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  8. Crear o actualizar usuario en DB                         │
│     • Si usuario no existe: crear automáticamente            │
│     • Si existe: actualizar información                      │
│     • Crear/actualizar sso_connection                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  9. Generar tokens JWT propios del sistema                   │
│     access_token + refresh_token (nuestros)                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  10. Redirigir al frontend con tokens                        │
│      Usuario autenticado con SSO                             │
└──────────────────────────────────────────────────────────────┘
```

### Validación de Dominio (Seguridad Crítica)

```python
# Archivo: backend/auth/sso_service.py

class SSOService:
    # Lista blanca de dominios permitidos
    REQUIRED_DOMAIN = "unitecnologica.edu.co"
    ALLOWED_DOMAINS = ["unitecnologica.edu.co"]
    
    @staticmethod
    def validate_email_domain(email: str) -> bool:
        """
        Valida que el email pertenezca al dominio institucional
        CRÍTICO: Asegura que solo personal de la universidad acceda
        """
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        is_valid = domain in SSOService.ALLOWED_DOMAINS
        
        logger.info(f" Domain validation for {email}: {'VALID' if is_valid else ' INVALID'}")
        return is_valid
```

---

## Seguridad

### 1. Hashing de Passwords

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashear password
password_hash = pwd_context.hash("MySecurePassword123!")
# → $2b$12$Kix8lt3UdDJ7niX.Cs1Hb.QWsRN3q7hSB3/vAzE8kFnN1H7Y8/Qbu

# Verificar password
is_valid = pwd_context.verify("MySecurePassword123!", password_hash)
# → True
```

### 2. Tokens JWT Seguros

- **Algoritmo**: HS256 (HMAC SHA-256)
- **Secret Key**: Mínimo 32 caracteres, aleatorio
- **Expiración**: 30 minutos (access token)
- **Refresh Token**: 7 días, rotación obligatoria

### 3. Protección CSRF

```python
# State parameter en OAuth 2.0
state = secrets.token_urlsafe(32)
# Almacenar en sesión temporalmente
# Validar en callback
```

### 4. Rate Limiting

```python
# Prevenir ataques de fuerza bruta
# Máximo 5 intentos de login por IP en 15 minutos
```

---

## Diagrama ER de Autenticación

```
┌─────────────┐          ┌─────────────────┐          ┌──────────────┐
│    users    │──────────│    sessions     │          │ refresh_     │
│             │ 1     N  │                 │          │  tokens      │
│ id (PK)     │─────────▶│ id (PK)         │          │              │
│ username    │          │ user_id (FK)    │          │ id (PK)      │
│ email       │          │ token_jti       │          │ user_id (FK) │
│ password_   │          │ expires_at      │          │ token_hash   │
│  hash       │          │ is_revoked      │          │ expires_at   │
│ is_active   │          └─────────────────┘          │ is_revoked   │
│ is_admin    │                                       └──────────────┘
└─────┬───────┘                                                │
      │ 1                                                      │
      │                                                        │ N
      │ N                                                      │
┌─────▼───────┐          ┌─────────────────┐          ┌──────▼──────┐
│conversat-   │──────────│    messages     │          │ sso_connec- │
│  ions       │ 1     N  │                 │          │  tions      │
│             │─────────▶│ id (PK)         │          │             │
│ id (PK)     │          │ conversation_id │          │ id (PK)     │
│ user_id(FK) │          │  (FK)           │          │ user_id(FK) │
│ title       │          │ role            │          │ provider_id │
│ is_archived │          │ content         │          │ external_id │
└─────────────┘          │ tokens_used     │          └─────────────┘
                         └─────────────────┘
```

---

## Resumen de Seguridad

### Implementaciones de Seguridad
- Passwords hasheados con bcrypt (12 rounds)
- JWT con HMAC SHA-256
- Refresh tokens con rotación
- Tokens revocables (sesiones)
- Validación de dominio institucional (SSO)
- Registro de intentos de login
- HTTPS requerido en producción
- CORS configurado
- SQL injection protegido (ORM SQLAlchemy)

### Conexión a Base de Datos

```python
# Archivo: backend/auth/database.py

# Configuración
DB_CONFIG = {
    "host": "20.151.72.161",
    "port": 3306,
    "user": "sso_user",
    "password": "Sso123Secure!",
    "database": "glpi_sso",
    "charset": "utf8mb4"
}

# SQLAlchemy
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## Mejores Prácticas Implementadas

1. **Separación de bases de datos**: Autenticación separada de datos de GLPI
2. **Principio de mínimo privilegio**: Usuario de DB con solo permisos necesarios
3. **Encriptación**: Passwords con bcrypt, tokens seguros
4. **Auditoría**: Logs de todos los intentos de acceso
5. **Validación**: Dominios institucionales validados (SSO)
6. **Tokens renovables**: Sistema de refresh tokens
7. **Sesiones rastreables**: Posibilidad de invalidar sesiones remotas
