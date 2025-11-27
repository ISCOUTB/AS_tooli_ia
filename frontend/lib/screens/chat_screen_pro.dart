import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../providers/theme_provider.dart';
import '../widgets/message_list.dart';
import '../widgets/input_area.dart';
import '../widgets/suggestions_panel.dart';
import '../widgets/sidebar.dart';
import 'login_screen.dart';

/// Professional chat screen inspired by Microsoft Copilot
class ChatScreenPro extends StatefulWidget {
  final int? conversationIdToLoad;
  
  const ChatScreenPro({super.key, this.conversationIdToLoad});

  @override
  State<ChatScreenPro> createState() => _ChatScreenProState();
}

class _ChatScreenProState extends State<ChatScreenPro> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void initState() {
    super.initState();
    // Check connection on start or load conversation
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final chatProvider = context.read<ChatProvider>();
      if (widget.conversationIdToLoad != null) {
        chatProvider.loadConversation(widget.conversationIdToLoad!);
        // No necesitamos setState, el provider maneja el estado del panel
      } else {
        chatProvider.checkConnection(silent: true);
      }
    });
  }

  void _handleSuggestionTap(String suggestion) {
    // El provider maneja ocultar el panel cuando se envía un mensaje
    context.read<ChatProvider>().sendMessage(suggestion);
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();
    final chatProvider = context.watch<ChatProvider>();

    return Scaffold(
      key: _scaffoldKey,
      drawer: const Sidebar(),
      body: Row(
        children: [
          // Main chat area
          Expanded(
            child: Column(
              children: [
                // Top bar
                _buildTopBar(themeProvider),
                
                // Messages area
                Expanded(
                  child: chatProvider.messages.isEmpty && chatProvider.showWelcomePanel
                      ? SuggestionsPanel(
                          onSuggestionTap: _handleSuggestionTap,
                        )
                      : MessageList(
                          messages: chatProvider.messages,
                        ),
                ),
                
                // Input area
                InputArea(
                  onSendMessage: (message) {
                    // El provider maneja ocultar el panel cuando se envía un mensaje
                    chatProvider.sendMessage(message);
                  },
                  isLoading: chatProvider.isLoading,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopBar(ThemeProvider themeProvider) {
    return Container(
      height: 60,
      decoration: BoxDecoration(
        color: Theme.of(context).appBarTheme.backgroundColor,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1,
          ),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: [
            // Menu button
            IconButton(
              icon: const Icon(Icons.menu),
              onPressed: () {
                _scaffoldKey.currentState?.openDrawer();
              },
              tooltip: 'Menu',
            ),
            
            const SizedBox(width: 12),
            
            // Logo/Title
            Icon(
              Icons.support_agent,
              size: 24,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),
            Text(
              'GLPI Assistant',
              style: Theme.of(context).appBarTheme.titleTextStyle,
            ),
            
            const Spacer(),
            
            // Connection status
            Consumer<ChatProvider>(
              builder: (context, provider, child) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: provider.isConnected
                        ? Colors.green.withOpacity(0.1)
                        : Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: provider.isConnected ? Colors.green : Colors.red,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        provider.isConnected ? 'Connected' : 'Disconnected',
                        style: TextStyle(
                          fontSize: 12,
                          color: provider.isConnected ? Colors.green : Colors.red,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
            
            const SizedBox(width: 16),
            
            // Logout button
            Consumer<AuthProvider>(
              builder: (context, authProvider, _) {
                return PopupMenuButton<String>(
                  icon: const Icon(Icons.account_circle),
                  tooltip: 'Account',
                  itemBuilder: (context) => [
                    PopupMenuItem<String>(
                      value: 'profile',
                      child: Row(
                        children: [
                          const Icon(Icons.person, size: 20),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                authProvider.currentUser?.fullName ?? 'User',
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              Text(
                                authProvider.currentUser?.email ?? '',
                                style: const TextStyle(fontSize: 12, color: Colors.grey),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const PopupMenuDivider(),
                    PopupMenuItem<String>(
                      value: 'logout',
                      child: const Row(
                        children: [
                          Icon(Icons.logout, size: 20),
                          SizedBox(width: 12),
                          Text('Cerrar Sesión'),
                        ],
                      ),
                      onTap: () async {
                        // Limpiar estado del chat antes de logout
                        context.read<ChatProvider>().resetState();
                        await authProvider.logout();
                        if (context.mounted) {
                          Navigator.of(context).pushReplacement(
                            MaterialPageRoute(builder: (_) => const LoginScreen()),
                          );
                        }
                      },
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
