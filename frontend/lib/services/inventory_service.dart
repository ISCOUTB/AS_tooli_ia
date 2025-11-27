import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/inventory_item.dart';

class InventoryService {
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

  /// Get all inventory items with optional filters
  static Future<List<InventoryItem>> getInventory({
    String? type,
    String? status,
    String? location,
    String? search,
  }) async {
    try {
      final headers = await _getHeaders();
      final queryParams = <String, String>{};
      
      if (type != null) queryParams['type'] = type;
      if (status != null) queryParams['status'] = status;
      if (location != null) queryParams['location'] = location;
      if (search != null) queryParams['search'] = search;

      final uri = Uri.parse('$baseUrl/api/v1/inventory/')
          .replace(queryParameters: queryParams.isNotEmpty ? queryParams : null);

      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => InventoryItem.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load inventory: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading inventory: $e');
    }
  }

  /// Get a specific inventory item by ID
  static Future<InventoryItem> getInventoryItem(int itemId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/inventory/$itemId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return InventoryItem.fromJson(jsonDecode(response.body));
      } else if (response.statusCode == 404) {
        throw Exception('Item not found');
      } else {
        throw Exception('Failed to load item: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error loading item: $e');
    }
  }

  /// Get inventory statistics
  static Future<Map<String, dynamic>> getInventoryStats() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/inventory/stats'),
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
