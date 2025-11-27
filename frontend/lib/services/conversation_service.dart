import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ConversationService {
  static const String baseUrl = 'http://localhost:8000';

  // =====================================================
  // CONVERSATION MODELS
  // =====================================================

  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  static Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // =====================================================
  // CONVERSATION ENDPOINTS
  // =====================================================

  /// Create a new conversation
  static Future<Map<String, dynamic>> createConversation({
    String title = 'New Conversation',
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/conversations/'),
        headers: headers,
        body: jsonEncode({'title': title}),
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to create conversation: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error creating conversation: $e');
    }
  }

  /// Get all conversations for the current user
  static Future<List<Map<String, dynamic>>> getConversations({
    int skip = 0,
    int limit = 20,
    bool includeArchived = false,
  }) async {
    try {
      final headers = await _getHeaders();
      final queryParams = {
        'skip': skip.toString(),
        'limit': limit.toString(),
        'include_archived': includeArchived.toString(),
      };
      
      final uri = Uri.parse('$baseUrl/api/v1/conversations/')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load conversations: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading conversations: $e');
    }
  }

  /// Get a specific conversation with all messages
  static Future<Map<String, dynamic>> getConversation(int conversationId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/conversations/$conversationId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 404) {
        throw Exception('Conversation not found');
      } else {
        throw Exception('Failed to load conversation: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading conversation: $e');
    }
  }

  /// Add a message to a conversation
  static Future<Map<String, dynamic>> addMessage({
    required int conversationId,
    required String role,
    required String content,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/conversations/$conversationId/messages'),
        headers: headers,
        body: jsonEncode({
          'role': role,
          'content': content,
        }),
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to add message: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error adding message: $e');
    }
  }

  /// Update conversation title or archive status
  static Future<Map<String, dynamic>> updateConversation({
    required int conversationId,
    String? title,
    bool? isArchived,
  }) async {
    try {
      final headers = await _getHeaders();
      final body = <String, dynamic>{};
      
      if (title != null) body['title'] = title;
      if (isArchived != null) body['is_archived'] = isArchived;

      final response = await http.patch(
        Uri.parse('$baseUrl/api/v1/conversations/$conversationId'),
        headers: headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to update conversation: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error updating conversation: $e');
    }
  }

  /// Delete (archive) a conversation
  static Future<void> deleteConversation(int conversationId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.delete(
        Uri.parse('$baseUrl/api/v1/conversations/$conversationId'),
        headers: headers,
      );

      if (response.statusCode != 204) {
        throw Exception('Failed to delete conversation: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error deleting conversation: $e');
    }
  }

  // =====================================================
  // USER SETTINGS ENDPOINTS
  // =====================================================

  /// Get user settings
  static Future<Map<String, dynamic>> getUserSettings() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/settings/'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load settings: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading settings: $e');
    }
  }

  /// Update user settings
  static Future<Map<String, dynamic>> updateUserSettings({
    String? theme,
    String? language,
    bool? notificationsEnabled,
    String? defaultView,
    int? itemsPerPage,
  }) async {
    try {
      final headers = await _getHeaders();
      final body = <String, dynamic>{};
      
      if (theme != null) body['theme'] = theme;
      if (language != null) body['language'] = language;
      if (notificationsEnabled != null) body['notifications_enabled'] = notificationsEnabled;
      if (defaultView != null) body['default_view'] = defaultView;
      if (itemsPerPage != null) body['items_per_page'] = itemsPerPage;

      final response = await http.put(
        Uri.parse('$baseUrl/api/v1/settings/'),
        headers: headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to update settings: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error updating settings: $e');
    }
  }

  // =====================================================
  // STATISTICS ENDPOINTS
  // =====================================================

  /// Get dashboard statistics
  static Future<Map<String, dynamic>> getDashboardStatistics() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/statistics/dashboard'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load statistics: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading statistics: $e');
    }
  }

  /// Get conversation timeline
  static Future<List<Map<String, dynamic>>> getConversationTimeline({
    int days = 30,
  }) async {
    try {
      final headers = await _getHeaders();
      final uri = Uri.parse('$baseUrl/api/v1/statistics/conversations/timeline')
          .replace(queryParameters: {'days': days.toString()});
      
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> timeline = data['timeline'];
        return timeline.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load timeline: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading timeline: $e');
    }
  }

  /// Get messages distribution by hour
  static Future<List<Map<String, dynamic>>> getMessagesByHour() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/statistics/messages/by-hour'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> distribution = data['distribution'];
        return distribution.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load distribution: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading distribution: $e');
    }
  }

  /// Clear statistics cache
  static Future<void> clearStatisticsCache() async {
    try {
      final headers = await _getHeaders();
      final response = await http.delete(
        Uri.parse('$baseUrl/api/v1/statistics/cache'),
        headers: headers,
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to clear cache: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error clearing cache: $e');
    }
  }
}
