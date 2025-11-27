import 'package:flutter/foundation.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import '../services/conversation_service.dart';

class ChatProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final List<Message> _messages = [];
  bool _isLoading = false;
  bool _isConnected = false;
  String? _errorMessage;
  int? _currentConversationId;
  bool _showWelcomePanel = true; // Nueva variable para controlar el panel

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;
  bool get isConnected => _isConnected;
  String? get errorMessage => _errorMessage;
  int? get currentConversationId => _currentConversationId;
  bool get showWelcomePanel => _showWelcomePanel;

  // Verificar conexión al iniciar
  Future<void> checkConnection({bool silent = false}) async {
    try {
      final health = await _apiService.checkHealth();
      _isConnected = health['status'] == 'healthy';
      _errorMessage = null;
      
      // NO agregar mensajes automáticos
      // El panel de sugerencias manejará la bienvenida
    } catch (e) {
      _isConnected = false;
      _errorMessage = 'No se pudo conectar al servidor';
      // Solo mostrar error si NO está en modo silencioso
      if (!silent) {
        _messages.add(Message(
          text: '❌ Error: No se pudo conectar al servidor.\n\n'
                'Asegúrate de que el backend esté ejecutándose en:\n'
                'http://localhost:8000',
          isUser: false,
        ));
      }
    }
    notifyListeners();
  }

  // Crear una nueva conversación
  Future<void> _createNewConversation() async {
    try {
      final now = DateTime.now();
      final title = 'Conversación ${now.day}/${now.month}/${now.year} ${now.hour}:${now.minute.toString().padLeft(2, '0')}';
      
      final conversation = await ConversationService.createConversation(
        title: title,
      );
      
      _currentConversationId = conversation['id'];
      debugPrint('✅ Nueva conversación creada: ID $_currentConversationId');
    } catch (e) {
      debugPrint('⚠️ Error al crear conversación: $e');
      // No bloqueamos el chat si falla la creación de conversación
    }
  }

  // Enviar mensaje al agente
  Future<void> sendMessage(String text, {bool isQuery = true}) async {
    if (text.trim().isEmpty) return;

    // Ocultar panel de bienvenida al enviar primer mensaje
    _showWelcomePanel = false;

    // Verificar que tengamos una conversación activa
    if (_currentConversationId == null) {
      await _createNewConversation();
    }

    // Agregar mensaje del usuario
    _messages.add(Message(text: text, isUser: true));
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Guardar mensaje del usuario en la base de datos
      if (_currentConversationId != null) {
        await ConversationService.addMessage(
          conversationId: _currentConversationId!,
          role: 'user',
          content: text,
        );
      }

      Message response;
      if (isQuery) {
        // Consulta que accede a GLPI
        response = await _apiService.sendQuery(text, 1);
      } else {
        // Chat conversacional simple
        response = await _apiService.sendChat(text);
      }
      
      _messages.add(response);

      // Guardar respuesta del asistente en la base de datos
      if (_currentConversationId != null) {
        await ConversationService.addMessage(
          conversationId: _currentConversationId!,
          role: 'assistant',
          content: response.text,
        );
      }
    } catch (e) {
      _errorMessage = e.toString();
      _messages.add(Message(
        text: '❌ Error: $e',
        isUser: false,
      ));
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Limpiar chat (iniciar nueva conversación)
  Future<void> clearChat() async {
    _messages.clear();
    _errorMessage = null;
    _currentConversationId = null; // Resetear conversación actual
    _showWelcomePanel = true; // Mostrar panel de bienvenida nuevamente
    notifyListeners(); // Notificar inmediatamente para mostrar el panel
    await checkConnection(silent: true); // Verificar conexión sin agregar mensajes
  }

  // Cargar una conversación existente
  Future<void> loadConversation(int conversationId) async {
    try {
      _isLoading = true;
      notifyListeners();

      final conversation = await ConversationService.getConversation(conversationId);
      _currentConversationId = conversationId;
      
      // Limpiar mensajes actuales
      _messages.clear();
      
      // Cargar mensajes de la conversación
      final messages = conversation['messages'] as List<dynamic>;
      for (var msg in messages) {
        _messages.add(Message(
          text: msg['content'],
          isUser: msg['role'] == 'user',
        ));
      }
      
      _errorMessage = null;
      debugPrint('✅ Conversación cargada: ID $conversationId con ${messages.length} mensajes');
    } catch (e) {
      _errorMessage = 'Error al cargar conversación: $e';
      debugPrint('❌ Error al cargar conversación: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Limpiar completamente el estado al hacer logout
  void resetState() {
    _messages.clear();
    _currentConversationId = null;
    _isLoading = false;
    _isConnected = false;
    _errorMessage = null;
    notifyListeners();
    debugPrint('🔄 Estado del chat reseteado');
  }
}
