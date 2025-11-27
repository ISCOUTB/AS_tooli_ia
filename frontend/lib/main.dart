import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/theme_provider.dart';
import 'screens/chat_screen_pro.dart';
import 'screens/login_screen.dart';
import 'screens/sso_callback_screen.dart';
import 'theme/app_theme.dart';
import 'utils/sso_helper_web.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint('Flutter Error: ${details.exception}');
  };
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Check if we're returning from SSO callback
    final callbackParams = SSOHelper.getCallbackParameters();
    
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()..loadTheme()),
      ],
      child: Consumer2<ThemeProvider, AuthProvider>(
        builder: (context, themeProvider, authProvider, _) {
          // If we have callback parameters, show callback screen
          if (callbackParams != null && callbackParams.isNotEmpty) {
            return MaterialApp(
              title: 'GLPI Assistant Pro',
              debugShowCheckedModeBanner: false,
              theme: AppTheme.lightTheme,
              darkTheme: AppTheme.darkTheme,
              themeMode: themeProvider.themeMode,
              home: SSOCallbackScreen(queryParameters: callbackParams),
            );
          }
          
          // Normal app flow
          return MaterialApp(
            title: 'GLPI Assistant Pro',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            home: authProvider.isAuthenticated 
                ? const ChatScreenPro() 
                : const LoginScreen(),
          );
        },
      ),
    );
  }
}
