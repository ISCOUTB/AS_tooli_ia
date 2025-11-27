import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/message.dart';

class ApiService {
  // Verificar estado del servidor
  Future<Map<String, dynamic>> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.healthEndpoint}'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al verificar estado del servidor');
      }
    } catch (e) {
      throw Exception('No se pudo conectar al servidor: $e');
    }
  }

  // Enviar consulta al agente IA
  Future<Message> sendQuery(String query, int userId) async {
    try {
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
        } else {
          return Message(
            text: data['message'] ?? 'Error al procesar la consulta',
            isUser: false,
          );
        }
      } else {
        throw Exception('Error en la solicitud: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error al enviar consulta: $e');
    }
  }

  // Chat conversacional (sin consultar GLPI)
  Future<Message> sendChat(String message) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.chatEndpoint}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Message(
          text: data['response'] ?? 'Sin respuesta',
          isUser: false,
        );
      } else {
        throw Exception('Error en el chat: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error al enviar mensaje: $e');
    }
  }
}
