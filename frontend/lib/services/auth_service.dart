import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String baseUrl = 'http://localhost:8000/api/v1/auth';
  static const String ssoBaseUrl = 'http://localhost:8000/api/v1/sso';
  
  String? _token;
  String? _refreshToken;
  User? _currentUser;

  // Getters
  String? get token => _token;
  bool get isAuthenticated => _token != null;
  User? get currentUser => _currentUser;

  /// Login with username and password
  Future<LoginResponse> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final loginResponse = LoginResponse.fromJson(data);
        
        // Save tokens
        _token = loginResponse.accessToken;
        _refreshToken = loginResponse.refreshToken;
        _currentUser = loginResponse.user;
        
        // Persist tokens
        await _saveTokens();
        
        return loginResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Login failed');
      }
    } catch (e) {
      throw Exception('Login error: $e');
    }
  }

  /// Register new user
  Future<User> register({
    required String username,
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        
        // Handle both MessageResponse and UserResponse
        if (data.containsKey('id') && data.containsKey('username')) {
          // New format: UserResponse with user data
          return User.fromJson(data);
        } else if (data.containsKey('message') && data.containsKey('success')) {
          // Old format: MessageResponse - create a temporary user object
          // The user should login after registration anyway
          return User(
            id: 0,
            username: username,
            email: email,
            fullName: fullName,
            isAdmin: false,
            isActive: true,
          );
        } else {
          throw Exception('Unexpected response format');
        }
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Registration failed');
      }
    } catch (e) {
      throw Exception('Registration error: $e');
    }
  }

  /// Get current user info
  Future<User> getCurrentUser() async {
    if (_token == null) {
      throw Exception('Not authenticated');
    }

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _currentUser = User.fromJson(data);
        return _currentUser!;
      } else {
        throw Exception('Failed to get user info');
      }
    } catch (e) {
      throw Exception('Get user error: $e');
    }
  }

  /// Get SSO providers
  Future<List<SSOProvider>> getSSOProviders() async {
    try {
      final response = await http.get(
        Uri.parse('$ssoBaseUrl/providers'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => SSOProvider.fromJson(json)).toList();
      } else {
        throw Exception('Failed to get SSO providers');
      }
    } catch (e) {
      throw Exception('SSO providers error: $e');
    }
  }

  /// Get SSO login URL
  String getSSOLoginUrl(String providerName) {
    return '$ssoBaseUrl/login/$providerName';
  }

  /// Login with SSO tokens (from callback)
  Future<void> loginWithSSOTokens({
    required String accessToken,
    required String refreshToken,
    required int userId,
    required String username,
    required String email,
  }) async {
    _token = accessToken;
    _refreshToken = refreshToken;
    
    // Create user object
    _currentUser = User(
      id: userId,
      username: username,
      email: email,
      fullName: username,
      isAdmin: false,
      isActive: true,
    );
    
    // Save tokens
    await _saveTokens();
  }

  /// Logout
  Future<void> logout() async {
    try {
      if (_token != null) {
        await http.post(
          Uri.parse('$baseUrl/logout'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $_token',
          },
        );
      }
    } catch (e) {
      print('Logout error: $e');
    } finally {
      // Clear tokens regardless of API response
      _token = null;
      _refreshToken = null;
      _currentUser = null;
      await _clearTokens();
    }
  }

  /// Refresh access token
  Future<bool> refreshAccessToken() async {
    if (_refreshToken == null) {
      return false;
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'refresh_token': _refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _token = data['access_token'];
        await _saveTokens();
        return true;
      }
      return false;
    } catch (e) {
      print('Refresh token error: $e');
      return false;
    }
  }

  /// Load tokens from storage
  Future<void> loadTokens() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
    _refreshToken = prefs.getString('refresh_token');
    
    if (_token != null) {
      try {
        await getCurrentUser();
      } catch (e) {
        // Token might be expired, try to refresh
        final refreshed = await refreshAccessToken();
        if (refreshed) {
          await getCurrentUser();
        } else {
          await _clearTokens();
        }
      }
    }
  }

  /// Save tokens to storage
  Future<void> _saveTokens() async {
    final prefs = await SharedPreferences.getInstance();
    if (_token != null) {
      await prefs.setString('access_token', _token!);
    }
    if (_refreshToken != null) {
      await prefs.setString('refresh_token', _refreshToken!);
    }
  }

  /// Clear tokens from storage
  Future<void> _clearTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }

  /// Check health of auth service
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

/// Login Response Model
class LoginResponse {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final User user;

  LoginResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      tokenType: json['token_type'],
      expiresIn: json['expires_in'],
      user: User.fromJson(json['user']),
    );
  }
}

/// User Model
class User {
  final int id;
  final String username;
  final String email;
  final String fullName;
  final bool isAdmin;
  final bool? isActive;
  final String? createdAt;
  final String? lastLogin;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.fullName,
    required this.isAdmin,
    this.isActive,
    this.createdAt,
    this.lastLogin,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      fullName: json['full_name'],
      isAdmin: json['is_admin'] ?? false,
      isActive: json['is_active'],
      createdAt: json['created_at'],
      lastLogin: json['last_login'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'full_name': fullName,
      'is_admin': isAdmin,
      'is_active': isActive,
      'created_at': createdAt,
      'last_login': lastLogin,
    };
  }
}

/// SSO Provider model
class SSOProvider {
  final String name;
  final String providerType;
  final String? appType;
  final String redirectUri;
  final String? requiredDomain;
  final bool isActive;

  SSOProvider({
    required this.name,
    required this.providerType,
    this.appType,
    required this.redirectUri,
    this.requiredDomain,
    required this.isActive,
  });

  factory SSOProvider.fromJson(Map<String, dynamic> json) {
    return SSOProvider(
      name: json['name'],
      providerType: json['provider_type'],
      appType: json['app_type'],
      redirectUri: json['redirect_uri'],
      requiredDomain: json['required_domain'],
      isActive: json['is_active'],
    );
  }
}
