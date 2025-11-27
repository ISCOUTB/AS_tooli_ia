import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'chat_screen_pro.dart';

/// SSO Callback Screen
/// This screen handles the redirect from SSO provider with authentication tokens
class SSOCallbackScreen extends StatefulWidget {
  final Map<String, String> queryParameters;

  const SSOCallbackScreen({
    super.key,
    required this.queryParameters,
  });

  @override
  State<SSOCallbackScreen> createState() => _SSOCallbackScreenState();
}

class _SSOCallbackScreenState extends State<SSOCallbackScreen> {
  bool _isProcessing = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _processCallback();
  }

  Future<void> _processCallback() async {
    try {
      // Extract tokens from URL parameters
      final accessToken = widget.queryParameters['access_token'];
      final refreshToken = widget.queryParameters['refresh_token'];
      final userId = widget.queryParameters['user_id'];
      final username = widget.queryParameters['username'];
      final email = widget.queryParameters['email'];

      if (accessToken == null || refreshToken == null) {
        throw Exception('Missing authentication tokens');
      }

      // Save tokens using auth provider
      final authProvider = context.read<AuthProvider>();
      await authProvider.loginWithSSO(
        accessToken: accessToken,
        refreshToken: refreshToken,
        userId: int.tryParse(userId ?? '0') ?? 0,
        username: username ?? '',
        email: email ?? '',
      );

      // Navigate to chat screen
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const ChatScreenPro()),
        );
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: _isProcessing
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 24),
                  Text(
                    'Completando inicio de sesión...',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ],
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Colors.red,
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Error al iniciar sesión',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      _error ?? 'Error desconocido',
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Volver'),
                  ),
                ],
              ),
      ),
    );
  }
}
