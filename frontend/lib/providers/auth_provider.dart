import 'package:flutter/foundation.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  
  bool _isLoading = false;
  String? _error;
  
  bool get isAuthenticated => _authService.isAuthenticated;
  User? get currentUser => _authService.currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;

  AuthProvider() {
    _loadTokens();
  }

  Future<void> _loadTokens() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      await _authService.loadTokens();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

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

  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String fullName,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.register(
        username: username,
        email: email,
        password: password,
        fullName: fullName,
      );
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

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.logout();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  Future<List<SSOProvider>> getSSOProviders() async {
    try {
      return await _authService.getSSOProviders();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return [];
    }
  }

  String getSSOLoginUrl(String providerName) {
    return _authService.getSSOLoginUrl(providerName);
  }

  Future<bool> loginWithSSO({
    required String accessToken,
    required String refreshToken,
    required int userId,
    required String username,
    required String email,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.loginWithSSOTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
        userId: userId,
        username: username,
        email: email,
      );
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
}
