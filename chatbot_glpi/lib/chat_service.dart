import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final double? confidence;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.confidence,
  });
}

class ChatService extends ChangeNotifier {
  static const String _baseUrl = 'http://localhost:5000';
  
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _isConnected = false;

  List<ChatMessage> get messages => List.unmodifiable(_messages);
  bool get isLoading => _isLoading;
  bool get isConnected => _isConnected;

  ChatService() {
    _checkConnection();
  }

  Future<void> _checkConnection() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));
      
      _isConnected = response.statusCode == 200;
    } catch (e) {
      _isConnected = false;
    }
    notifyListeners();
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    _messages.add(ChatMessage(
      text: text,
      isUser: true,
      timestamp: DateTime.now(),
    ));
    
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'query': text}),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        _messages.add(ChatMessage(
          text: data['response'] ?? 'Sin respuesta',
          isUser: false,
          timestamp: DateTime.now(),
          confidence: data['confidence']?.toDouble(),
        ));
        
        _isConnected = true;
      } else {
        _messages.add(ChatMessage(
          text: 'Error: Código de estado ${response.statusCode}. ${response.body}',
          isUser: false,
          timestamp: DateTime.now(),
        ));
      }
    } catch (e) {
      _isConnected = false;
      _messages.add(ChatMessage(
        text: 'Error de conexión: Verifica que el backend esté ejecutándose.',
        isUser: false,
        timestamp: DateTime.now(),
      ));
    }

    _isLoading = false;
    notifyListeners();
  }
}
