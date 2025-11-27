import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/ticket.dart';

class TicketService {
  static const String baseUrl = 'http://localhost:8000';

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

  /// Get all tickets with optional filters
  static Future<List<Ticket>> getTickets({
    String? status,
    String? priority,
    String? category,
    String? search,
  }) async {
    try {
      final headers = await _getHeaders();
      final queryParams = <String, String>{};
      
      if (status != null) queryParams['status'] = status;
      if (priority != null) queryParams['priority'] = priority;
      if (category != null) queryParams['category'] = category;
      if (search != null) queryParams['search'] = search;

      final uri = Uri.parse('$baseUrl/api/v1/tickets/')
          .replace(queryParameters: queryParams.isNotEmpty ? queryParams : null);

      print('🔍 Fetching tickets from: $uri');
      print('📋 Headers: ${headers.keys.join(", ")}');

      final response = await http.get(uri, headers: headers);

      print('📡 Response status: ${response.statusCode}');
      print('📦 Response body length: ${response.body.length}');

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        print('✅ Parsed ${data.length} tickets from response');
        return data.map((json) => Ticket.fromJson(json)).toList();
      } else {
        print('❌ Error response: ${response.body}');
        throw Exception('Failed to load tickets: ${response.body}');
      }
    } catch (e) {
      print('❌ Exception in getTickets: $e');
      throw Exception('Error loading tickets: $e');
    }
  }

  /// Get a specific ticket by ID
  static Future<Ticket> getTicket(int ticketId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/tickets/$ticketId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return Ticket.fromJson(jsonDecode(response.body));
      } else if (response.statusCode == 404) {
        throw Exception('Ticket not found');
      } else {
        throw Exception('Failed to load ticket: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading ticket: $e');
    }
  }

  /// Get ticket statistics
  static Future<Map<String, dynamic>> getTicketStats() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/tickets/stats/summary'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load stats: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading stats: $e');
    }
  }
}
