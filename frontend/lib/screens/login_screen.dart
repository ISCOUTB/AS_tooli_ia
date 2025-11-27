import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart';
import '../utils/sso_helper_web.dart';
import 'chat_screen_pro.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _isRegisterMode = false;
  
  // Additional fields for registration
  final _emailController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _emailController.dispose();
    _fullNameController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleSSOLogin() async {
    final authProvider = context.read<AuthProvider>();
    
    try {
      // Get SSO providers
      final providers = await authProvider.getSSOProviders();
      
      if (providers.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('❌ No hay proveedores SSO disponibles'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }
      
      // Use the first provider (AS_tooli_ia)
      final provider = providers.first;
      final ssoUrl = authProvider.getSSOLoginUrl(provider.name);
      
      if (mounted) {
        // Navigate to SSO in the same window/tab
        SSOHelper.navigateToSSO(ssoUrl);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error al iniciar SSO: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final authProvider = context.read<AuthProvider>();
    bool success = false;

    if (_isRegisterMode) {
      // Register
      success = await authProvider.register(
        username: _usernameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text,
        fullName: _fullNameController.text.trim(),
      );
      
      if (mounted) {
        if (success) {
          // After successful registration, show success and switch to login
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ ¡Cuenta creada exitosamente! Ahora inicia sesión con tus credenciales.'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 4),
            ),
          );
          setState(() {
            _isRegisterMode = false;
            _passwordController.clear();
            _confirmPasswordController.clear();
          });
        } else {
          // Show error message if registration failed
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(authProvider.error ?? '❌ Error al crear la cuenta. Por favor intenta de nuevo.'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      }
    } else {
      // Login
      success = await authProvider.login(
        _usernameController.text.trim(),
        _passwordController.text,
      );
      
      if (success && mounted) {
        // Navigate to chat screen
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const ChatScreenPro()),
        );
      }
    }

    // Show error if failed
    if (!success && mounted) {
      final error = authProvider.error ?? 'Authentication failed';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error.replaceAll('Exception: ', '')),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final themeProvider = context.watch<ThemeProvider>();
    final isDark = themeProvider.themeMode == ThemeMode.dark;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isDark
                ? [
                    const Color(0xFF1E1E1E),
                    const Color(0xFF2D2D2D),
                  ]
                : [
                    const Color(0xFF0078D4),
                    const Color(0xFF0063B1),
                  ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Card(
                elevation: 8,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 400),
                  padding: const EdgeInsets.all(32.0),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Logo and Title
                        Icon(
                          Icons.smart_toy_outlined,
                          size: 64,
                          color: isDark
                              ? const Color(0xFF4CC2FF)
                              : const Color(0xFF0078D4),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'GLPI Assistant',
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _isRegisterMode ? 'Crear Cuenta' : 'Bienvenido',
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                color: Colors.grey,
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 32),

                        // Username Field
                        TextFormField(
                          controller: _usernameController,
                          decoration: InputDecoration(
                            labelText: _isRegisterMode ? 'Nombre de Usuario' : 'Usuario o Email',
                            prefixIcon: const Icon(Icons.person_outline),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            helperText: _isRegisterMode ? null : 'Puedes usar tu nombre de usuario o email',
                          ),
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) {
                              return _isRegisterMode 
                                ? 'Por favor ingresa un nombre de usuario'
                                : 'Por favor ingresa tu usuario o email';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),

                        // Email Field (only for registration)
                        if (_isRegisterMode) ...[
                          TextFormField(
                            controller: _emailController,
                            decoration: InputDecoration(
                              labelText: 'Correo Electrónico',
                              prefixIcon: const Icon(Icons.email_outlined),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            keyboardType: TextInputType.emailAddress,
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'Por favor ingresa tu correo electrónico';
                              }
                              if (!value.contains('@')) {
                                return 'Por favor ingresa un correo válido';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 16),

                          // Full Name Field
                          TextFormField(
                            controller: _fullNameController,
                            decoration: InputDecoration(
                              labelText: 'Nombre Completo',
                              prefixIcon: const Icon(Icons.badge_outlined),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'Por favor ingresa tu nombre completo';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Password Field
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          decoration: InputDecoration(
                            labelText: 'Contraseña',
                            prefixIcon: const Icon(Icons.lock_outline),
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                              onPressed: () {
                                setState(() {
                                  _obscurePassword = !_obscurePassword;
                                });
                              },
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Por favor ingresa tu contraseña';
                            }
                            if (_isRegisterMode && value.length < 8) {
                              return 'La contraseña debe tener al menos 8 caracteres';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),

                        // Confirm Password Field (only for registration)
                        if (_isRegisterMode) ...[
                          TextFormField(
                            controller: _confirmPasswordController,
                            obscureText: _obscurePassword,
                            decoration: InputDecoration(
                              labelText: 'Confirmar Contraseña',
                              prefixIcon: const Icon(Icons.lock_outline),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            validator: (value) {
                              if (value != _passwordController.text) {
                                return 'Las contraseñas no coinciden';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 24),
                        ],

                        // Submit Button
                        const SizedBox(height: 8),
                        ElevatedButton(
                          onPressed: authProvider.isLoading ? null : _handleSubmit,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: authProvider.isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : Text(
                                  _isRegisterMode ? 'Crear Cuenta' : 'Iniciar Sesión',
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                        ),
                        const SizedBox(height: 16),

                        // Toggle between login and register
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _isRegisterMode = !_isRegisterMode;
                              _formKey.currentState?.reset();
                            });
                          },
                          child: Text(
                            _isRegisterMode
                                ? '¿Ya tienes cuenta? Inicia Sesión'
                                : '¿No tienes cuenta? Regístrate',
                          ),
                        ),

                        // SSO Login (only show in login mode)
                        if (!_isRegisterMode) ...[
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Expanded(child: Divider(color: Colors.grey[400])),
                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 16),
                                child: Text(
                                  'O continuar con',
                                  style: TextStyle(color: Colors.grey[600]),
                                ),
                              ),
                              Expanded(child: Divider(color: Colors.grey[400])),
                            ],
                          ),
                          const SizedBox(height: 16),
                          OutlinedButton.icon(
                            onPressed: authProvider.isLoading ? null : _handleSSOLogin,
                            icon: const Icon(
                              Icons.business,
                              size: 20,
                            ),
                            label: const Text('Microsoft / Institucional'),
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ],

                        // Theme Toggle
                        const SizedBox(height: 8),
                        Center(
                          child: IconButton(
                            icon: Icon(
                              isDark ? Icons.light_mode : Icons.dark_mode,
                            ),
                            onPressed: () {
                              themeProvider.toggleTheme();
                            },
                            tooltip: 'Cambiar Tema',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
