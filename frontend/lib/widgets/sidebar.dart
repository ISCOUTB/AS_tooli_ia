import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/theme_provider.dart';
import '../providers/chat_provider.dart';
import '../screens/conversation_history_screen.dart';
import '../screens/statistics_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/tickets_screen.dart';
import '../screens/inventory_screen.dart';

/// Sidebar widget with navigation menu
class Sidebar extends StatelessWidget {
  const Sidebar({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final theme = Theme.of(context);

    return Drawer(
      child: Column(
        children: [
          // Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withOpacity(0.1),
              border: Border(
                bottom: BorderSide(
                  color: theme.dividerColor,
                  width: 1,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.support_agent,
                  size: 48,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 12),
                Text(
                  'Asistente GLPI',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Gestión Profesional de Servicios TI',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.textTheme.bodySmall?.color?.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),

          // Menu Items
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                _MenuItem(
                  icon: Icons.chat_bubble_outline,
                  title: 'Nueva Conversación',
                  onTap: () async {
                    final navigator = Navigator.of(context);
                    final messenger = ScaffoldMessenger.of(context);
                    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
                    
                    navigator.pop();
                    await chatProvider.clearChat();
                    messenger.showSnackBar(
                      const SnackBar(
                        content: Text('Nueva conversación iniciada'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                ),
                _MenuItem(
                  icon: Icons.history,
                  title: 'Historial de Conversaciones',
                  onTap: () {
                    final navigator = Navigator.of(context);
                    navigator.pop();
                    navigator.push(
                      MaterialPageRoute(
                        builder: (context) => const ConversationHistoryScreen(),
                      ),
                    );
                  },
                ),
                const Divider(height: 16),
                _MenuItem(
                  icon: Icons.analytics_outlined,
                  title: 'Panel de Estadísticas',
                  onTap: () {
                    final navigator = Navigator.of(context);
                    navigator.pop();
                    navigator.push(
                      MaterialPageRoute(
                        builder: (context) => const StatisticsScreen(),
                      ),
                    );
                  },
                ),
                _MenuItem(
                  icon: Icons.confirmation_number_outlined,
                  title: 'Todos los Tickets',
                  onTap: () {
                    final navigator = Navigator.of(context);
                    navigator.pop();
                    navigator.push(
                      MaterialPageRoute(
                        builder: (context) => const TicketsScreen(),
                      ),
                    );
                  },
                ),
                _MenuItem(
                  icon: Icons.computer_outlined,
                  title: 'Inventario',
                  onTap: () {
                    final navigator = Navigator.of(context);
                    navigator.pop();
                    navigator.push(
                      MaterialPageRoute(
                        builder: (context) => const InventoryScreen(),
                      ),
                    );
                  },
                ),
                const Divider(height: 16),
                _MenuItem(
                  icon: Icons.settings_outlined,
                  title: 'Configuración',
                  onTap: () {
                    final navigator = Navigator.of(context);
                    navigator.pop();
                    navigator.push(
                      MaterialPageRoute(
                        builder: (context) => const SettingsScreen(),
                      ),
                    );
                  },
                ),
                _MenuItem(
                  icon: Icons.help_outline,
                  title: 'Ayuda y Documentación',
                  onTap: () {
                    final navigator = Navigator.of(context);
                    final messenger = ScaffoldMessenger.of(context);
                    navigator.pop();
                    messenger.showSnackBar(
                      const SnackBar(
                        content: Text('Documentación de ayuda próximamente'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),

          // Footer
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  color: theme.dividerColor,
                  width: 1,
                ),
              ),
            ),
            child: Column(
              children: [
                // Theme Toggle
                ListTile(
                  leading: Icon(
                    themeProvider.isDarkMode
                        ? Icons.dark_mode
                        : Icons.light_mode,
                  ),
                  title: Text(
                    themeProvider.isDarkMode ? 'Dark Mode' : 'Light Mode',
                    style: theme.textTheme.bodyMedium,
                  ),
                  trailing: Switch(
                    value: themeProvider.isDarkMode,
                    onChanged: (value) {
                      themeProvider.toggleTheme();
                    },
                  ),
                  contentPadding: EdgeInsets.zero,
                ),
                const SizedBox(height: 8),
                // Version Info
                Text(
                  'Version 1.0.0',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.textTheme.bodySmall?.color?.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _MenuItem({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return ListTile(
      leading: Icon(icon, size: 24),
      title: Text(
        title,
        style: theme.textTheme.bodyMedium,
      ),
      onTap: () {
        debugPrint('MenuItem tapped: $title');
        onTap();
      },
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 24,
        vertical: 4,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(4),
      ),
      hoverColor: theme.colorScheme.primary.withOpacity(0.1),
    );
  }
}
