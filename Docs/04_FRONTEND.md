# Documentación del Frontend

## 📂 Estructura del Frontend

```
frontend/
├── lib/
│   ├── main.dart                    # Punto de entrada de la aplicación
│   ├── main_simple.dart             # Versión simplificada (desarrollo)
│   ├── main_test.dart               # Versión de testing
│   │
│   ├── config/
│   │   └── api_config.dart          # Configuración de API (URLs)
│   │
│   ├── models/                      # Modelos de datos
│   │   ├── message.dart             # Modelo de mensaje de chat
│   │   ├── ticket.dart              # Modelo de ticket
│   │   └── inventory_item.dart      # Modelo de item de inventario
│   │
│   ├── providers/                   # Gestión de estado (Provider pattern)
│   │   ├── auth_provider.dart       # Estado de autenticación
│   │   ├── chat_provider.dart       # Estado del chat
│   │   └── theme_provider.dart      # Estado del tema (dark/light)
│   │
│   ├── screens/                     # Pantallas de la aplicación
│   │   ├── login_screen.dart        # Pantalla de login
│   │   ├── chat_screen.dart         # Chat básico
│   │   ├── chat_screen_pro.dart     # Chat profesional (principal)
│   │   ├── chat_screen_debug.dart   # Chat con debug
│   │   ├── conversation_history_screen.dart  # Historial de conversaciones
│   │   ├── tickets_screen.dart      # Lista de tickets
│   │   ├── ticket_detail_screen.dart         # Detalle de ticket
│   │   ├── inventory_screen.dart    # Lista de inventario
│   │   ├── inventory_detail_screen.dart      # Detalle de item
│   │   ├── settings_screen.dart     # Configuración
│   │   └── statistics_screen.dart   # Estadísticas
│   │
│   ├── services/                    # Servicios de comunicación con backend
│   │   ├── api_service.dart         # Servicio de chat/query
│   │   ├── auth_service.dart        # Servicio de autenticación
│   │   ├── ticket_service.dart      # Servicio de tickets
│   │   ├── inventory_service.dart   # Servicio de inventario
│   │   └── conversation_service.dart # Servicio de conversaciones
│   │
│   ├── theme/
│   │   └── app_theme.dart           # Tema visual de la aplicación
│   │
│   └── widgets/                     # Widgets reutilizables
│       ├── message_bubble.dart      # Burbuja de mensaje
│       ├── message_list.dart        # Lista de mensajes
│       ├── input_area.dart          # Área de entrada de texto
│       ├── suggestions_panel.dart   # Panel de sugerencias
│       └── sidebar.dart             # Menú lateral
│
├── web/                             # Archivos para web
│   ├── index.html
│   └── manifest.json
│
├── pubspec.yaml                     # Dependencias Flutter
└── devtools_options.yaml            # Configuración de DevTools
```

---

## 🚀 Punto de Entrada: main.dart

```dart
// Archivo: frontend/lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Providers para gestión de estado
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()..loadTheme()),
      ],
      child: Consumer2<ThemeProvider, AuthProvider>(
        builder: (context, themeProvider, authProvider, _) {
          return MaterialApp(
            title: 'GLPI Assistant Pro',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            // Navegación basada en autenticación
            home: authProvider.isAuthenticated 
                ? const ChatScreenPro() 
                : const LoginScreen(),
          );
        },
      ),
    );
  }
}
```

### Características Clave
- **MultiProvider**: Gestión de estado centralizada
- **Consumer**: Escucha cambios de estado
- **Autenticación**: Redirección automática según estado de login
- **Theming**: Soporte para tema claro/oscuro

---

## 🎨 Gestión de Estado: Provider Pattern

### 1. AuthProvider (auth_provider.dart)

Gestiona el estado de autenticación del usuario.

```dart
class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  
  bool _isLoading = false;
  String? _error;
  
  // Getters
  bool get isAuthenticated => _authService.isAuthenticated;
  User? get currentUser => _authService.currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Login
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();  // Notifica a los widgets que escuchan

    try {
      await _authService.login(username, password);
      _error = null;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Register
  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String fullName,
  }) async {
    // Implementación similar a login
  }

  // Logout
  Future<void> logout() async {
    await _authService.logout();
    notifyListeners();
  }
}
```

### 2. ChatProvider (chat_provider.dart)

Gestiona el estado del chat y las conversaciones.

```dart
class ChatProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final List<Message> _messages = [];
  bool _isLoading = false;
  bool _isConnected = false;
  String? _errorMessage;
  int? _currentConversationId;
  bool _showWelcomePanel = true;

  // Getters
  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;
  bool get isConnected => _isConnected;
  bool get showWelcomePanel => _showWelcomePanel;

  // Verificar conexión con backend
  Future<void> checkConnection({bool silent = false}) async {
    try {
      final health = await _apiService.checkHealth();
      _isConnected = health['status'] == 'healthy';
      _errorMessage = null;
    } catch (e) {
      _isConnected = false;
      _errorMessage = 'No se pudo conectar al servidor';
    }
    notifyListeners();
  }

  // Enviar mensaje
  Future<void> sendMessage(String text, {bool isQuery = true}) async {
    if (text.trim().isEmpty) return;

    // Ocultar panel de bienvenida
    _showWelcomePanel = false;

    // Agregar mensaje del usuario
    _messages.add(Message(text: text, isUser: true));
    _isLoading = true;
    notifyListeners();

    try {
      Message response;
      if (isQuery) {
        response = await _apiService.sendQuery(text, 1);
      } else {
        response = await _apiService.sendChat(text);
      }
      
      _messages.add(response);

      // Guardar en conversación
      if (_currentConversationId != null) {
        await ConversationService.addMessage(
          conversationId: _currentConversationId!,
          role: 'assistant',
          content: response.text,
        );
      }
    } catch (e) {
      _errorMessage = e.toString();
      _messages.add(Message(text: '❌ Error: $e', isUser: false));
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Limpiar chat
  Future<void> clearChat() async {
    _messages.clear();
    _errorMessage = null;
    _currentConversationId = null;
    _showWelcomePanel = true;
    notifyListeners();
    await checkConnection(silent: true);
  }

  // Cargar conversación existente
  Future<void> loadConversation(int conversationId) async {
    _isLoading = true;
    notifyListeners();

    final conversation = await ConversationService.getConversation(conversationId);
    _currentConversationId = conversationId;
    
    _messages.clear();
    final messages = conversation['messages'] as List<dynamic>;
    for (var msg in messages) {
      _messages.add(Message(
        text: msg['content'],
        isUser: msg['role'] == 'user',
      ));
    }
    
    _isLoading = false;
    notifyListeners();
  }
}
```

### 3. ThemeProvider (theme_provider.dart)

Gestiona el tema (claro/oscuro).

```dart
class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;

  ThemeMode get themeMode => _themeMode;

  void toggleTheme() {
    _themeMode = _themeMode == ThemeMode.light 
        ? ThemeMode.dark 
        : ThemeMode.light;
    _saveTheme();
    notifyListeners();
  }

  Future<void> loadTheme() async {
    // Cargar tema guardado desde SharedPreferences
  }

  Future<void> _saveTheme() async {
    // Guardar tema en SharedPreferences
  }
}
```

---

## 📡 Servicios de Comunicación

### 1. ApiService (api_service.dart)

Servicio principal para comunicación con el chatbot.

```dart
class ApiService {
  // Verificar estado del servidor
  Future<Map<String, dynamic>> checkHealth() async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}${ApiConfig.healthEndpoint}'),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Error al verificar estado del servidor');
    }
  }

  // Enviar consulta al agente IA
  Future<Message> sendQuery(String query, int userId) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}${ApiConfig.queryEndpoint}'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'query': query,
        'user_id': userId,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      
      if (data['success'] == true) {
        return Message(
          text: data['message'] ?? 'Sin respuesta',
          isUser: false,
          intention: data['intention'],
          confidence: (data['confidence'] as num?)?.toDouble(),
        );
      }
    }
    throw Exception('Error en la solicitud');
  }

  // Chat conversacional (sin consultar GLPI)
  Future<Message> sendChat(String message) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}${ApiConfig.chatEndpoint}'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'message': message}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Message(
        text: data['response'] ?? 'Sin respuesta',
        isUser: false,
      );
    }
    throw Exception('Error en el chat');
  }
}
```

### 2. AuthService (auth_service.dart)

```dart
class AuthService {
  static const String _baseUrl = ApiConfig.baseUrl;
  String? _accessToken;
  String? _refreshToken;
  User? _currentUser;

  bool get isAuthenticated => _accessToken != null;
  User? get currentUser => _currentUser;

  // Login
  Future<void> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/api/v1/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _accessToken = data['access_token'];
      _refreshToken = data['refresh_token'];
      _currentUser = User.fromJson(data['user']);
      
      // Guardar tokens en SharedPreferences
      await _saveTokens();
    } else {
      throw Exception('Login failed');
    }
  }

  // Logout
  Future<void> logout() async {
    _accessToken = null;
    _refreshToken = null;
    _currentUser = null;
    await _clearTokens();
  }
}
```

### 3. TicketService (ticket_service.dart)

```dart
class TicketService {
  static Future<List<Ticket>> getTickets({
    String? status,
    String? priority,
    String? search,
  }) async {
    final queryParams = <String, String>{};
    if (status != null) queryParams['status'] = status;
    if (priority != null) queryParams['priority'] = priority;
    if (search != null) queryParams['search'] = search;

    final uri = Uri.parse('${ApiConfig.baseUrl}/api/v1/tickets')
        .replace(queryParameters: queryParams);

    final response = await http.get(
      uri,
      headers: await _getAuthHeaders(),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Ticket.fromJson(json)).toList();
    }
    throw Exception('Failed to load tickets');
  }

  static Future<Ticket> getTicketById(int id) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/api/v1/tickets/$id'),
      headers: await _getAuthHeaders(),
    );

    if (response.statusCode == 200) {
      return Ticket.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to load ticket');
  }
}
```

---

## 🖼️ Pantallas Principales

### 1. ChatScreenPro (chat_screen_pro.dart)

Pantalla principal del chat con diseño profesional.

```dart
class ChatScreenPro extends StatefulWidget {
  final int? conversationIdToLoad;
  
  const ChatScreenPro({super.key, this.conversationIdToLoad});

  @override
  Widget build(BuildContext context) {
    final chatProvider = context.watch<ChatProvider>();

    return Scaffold(
      drawer: const Sidebar(),
      body: Column(
        children: [
          _buildTopBar(),
          
          // Área de mensajes o panel de bienvenida
          Expanded(
            child: chatProvider.messages.isEmpty && chatProvider.showWelcomePanel
                ? SuggestionsPanel(onSuggestionTap: _handleSuggestionTap)
                : MessageList(messages: chatProvider.messages),
          ),
          
          // Área de entrada
          InputArea(
            onSendMessage: (message) {
              chatProvider.sendMessage(message);
            },
            isLoading: chatProvider.isLoading,
          ),
        ],
      ),
    );
  }
}
```

### 2. LoginScreen (login_screen.dart)

```dart
class LoginScreen extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      body: Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _usernameController,
                  decoration: InputDecoration(labelText: 'Usuario'),
                ),
                TextField(
                  controller: _passwordController,
                  decoration: InputDecoration(labelText: 'Contraseña'),
                  obscureText: true,
                ),
                ElevatedButton(
                  onPressed: authProvider.isLoading
                      ? null
                      : () async {
                          final success = await authProvider.login(
                            _usernameController.text,
                            _passwordController.text,
                          );
                          if (success) {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const ChatScreenPro(),
                              ),
                            );
                          }
                        },
                  child: Text('Iniciar Sesión'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

### 3. TicketsScreen (tickets_screen.dart)

```dart
class TicketsScreen extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Ticket>>(
      future: TicketService.getTickets(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }

        final tickets = snapshot.data ?? [];

        return ListView.builder(
          itemCount: tickets.length,
          itemBuilder: (context, index) {
            final ticket = tickets[index];
            return ListTile(
              title: Text(ticket.title),
              subtitle: Text(ticket.status),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => TicketDetailScreen(ticketId: ticket.id),
                  ),
                );
              },
            );
          },
        );
      },
    );
  }
}
```

---

## 🧩 Widgets Reutilizables

### 1. MessageBubble (message_bubble.dart)

```dart
class MessageBubble extends StatelessWidget {
  final Message message;

  const MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser 
          ? Alignment.centerRight 
          : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: message.isUser 
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).colorScheme.surfaceVariant,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: message.isUser ? Colors.white : null,
          ),
        ),
      ),
    );
  }
}
```

### 2. InputArea (input_area.dart)

```dart
class InputArea extends StatefulWidget {
  final Function(String) onSendMessage;
  final bool isLoading;

  const InputArea({
    required this.onSendMessage,
    required this.isLoading,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'Escribe tu mensaje...',
                border: OutlineInputBorder(),
              ),
              onSubmitted: _handleSubmit,
            ),
          ),
          SizedBox(width: 8),
          IconButton(
            icon: isLoading 
                ? CircularProgressIndicator()
                : Icon(Icons.send),
            onPressed: isLoading ? null : () => _handleSubmit(),
          ),
        ],
      ),
    );
  }
}
```

---

## 🎯 Modelos de Datos

### Message (message.dart)

```dart
class Message {
  final String text;
  final bool isUser;
  final String? intention;
  final double? confidence;
  final DateTime timestamp;

  Message({
    required this.text,
    required this.isUser,
    this.intention,
    this.confidence,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}
```

### Ticket (ticket.dart)

```dart
class Ticket {
  final int id;
  final String title;
  final String description;
  final String status;
  final String priority;
  final String? assignedTo;
  final DateTime createdAt;

  Ticket({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.priority,
    this.assignedTo,
    required this.createdAt,
  });

  factory Ticket.fromJson(Map<String, dynamic> json) {
    return Ticket(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      status: json['status'],
      priority: json['priority'],
      assignedTo: json['assigned_to'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

---

## ⚙️ Configuración

### api_config.dart

```dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  
  static const String queryEndpoint = '/api/v1/query';
  static const String chatEndpoint = '/api/v1/chat';
  static const String healthEndpoint = '/api/v1/health';
  static const String loginEndpoint = '/api/v1/auth/login';
  static const String registerEndpoint = '/api/v1/auth/register';
  static const String ticketsEndpoint = '/api/v1/tickets';
  static const String inventoryEndpoint = '/api/v1/inventory';
}
```

### pubspec.yaml

```yaml
name: glpi_assistant
description: GLPI AI Assistant

dependencies:
  flutter:
    sdk: flutter
  
  # State management
  provider: ^6.1.1
  
  # HTTP
  http: ^1.1.0
  
  # Local storage
  shared_preferences: ^2.2.2
  
  # UI
  flutter_markdown: ^0.6.18
  
  # Utils
  intl: ^0.18.1

flutter:
  uses-material-design: true
```

---

## 🎯 Flujo de Navegación

```
┌─────────────────┐
│  Splash Screen  │ (Inicial)
└────────┬────────┘
         │
         ├─► isAuthenticated?
         │
         ├─► No  → LoginScreen
         │          ├─► Login Success → ChatScreenPro
         │          └─► Register → ChatScreenPro
         │
         └─► Yes → ChatScreenPro (Home)
                    ├─► Sidebar
                    │   ├─► Tickets Screen
                    │   ├─► Inventory Screen
                    │   ├─► Statistics Screen
                    │   ├─► Conversation History
                    │   ├─► Settings
                    │   └─► Logout → LoginScreen
                    │
                    └─► Chat Interface
                        ├─► Send Message
                        ├─► View Response
                        └─► Clear Chat
```

---

## 🎨 Tema Visual

### AppTheme (app_theme.dart)

```dart
class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.light,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.dark,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.grey[900],
        foregroundColor: Colors.white,
      ),
    );
  }
}
```

---

## 🚀 Ejecución

```bash
# Desarrollo (web)
flutter run -d chrome

# Producción (web)
flutter build web

# Android
flutter run -d android

# iOS
flutter run -d ios
```

---

## 🎯 Resumen del Frontend

### Tecnologías
- **Framework**: Flutter 3.0+
- **Lenguaje**: Dart
- **Estado**: Provider pattern
- **HTTP**: http package
- **Almacenamiento**: SharedPreferences

### Arquitectura
- **Patrón MVC**: Models, Providers (Controllers), Screens (Views)
- **Servicios**: Capa de comunicación con backend
- **Widgets**: Componentes reutilizables

### Características
- ✅ Diseño profesional tipo Microsoft Copilot
- ✅ Chat en tiempo real con IA
- ✅ Gestión de tickets e inventario
- ✅ Autenticación JWT
- ✅ Tema claro/oscuro
- ✅ Responsive design
- ✅ Multiplataforma (Web, Android, iOS)
