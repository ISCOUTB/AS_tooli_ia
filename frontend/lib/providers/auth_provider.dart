import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = false;
  String _username = '';
  String _password = '';

  bool get isAuthenticated => _isAuthenticated;
  String get username => _username;
  String get password => _password;

  Future<bool> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('http://localhost:5000/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['success']) {
        _isAuthenticated = true;
        _username = username;
        _password = password;
        notifyListeners();
        return true;
      }
    }
    return false;
  }

  void logout() {
    _isAuthenticated = false;
    _username = '';
    _password = '';
    notifyListeners();
  }
}