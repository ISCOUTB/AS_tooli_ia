import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/theme_provider.dart';
import '../services/conversation_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isLoading = true;
  String? _error;
  
  // Settings values
  String _theme = 'light';
  String _language = 'es';
  bool _notificationsEnabled = true;
  String _defaultView = 'chat';
  int _itemsPerPage = 20;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final settings = await ConversationService.getUserSettings();
      
      // Validar y normalizar los valores
      String theme = settings['theme'] ?? 'light';
      if (!['light', 'dark', 'system'].contains(theme)) {
        theme = 'light';
      }
      
      String language = settings['language'] ?? 'es';
      if (!['es', 'en'].contains(language)) {
        language = 'es';
      }
      
      String defaultView = settings['default_view'] ?? 'chat';
      if (!['chat', 'history', 'statistics'].contains(defaultView)) {
        defaultView = 'chat';
      }
      
      int itemsPerPage = settings['items_per_page'] ?? 20;
      if (![10, 20, 50, 100].contains(itemsPerPage)) {
        itemsPerPage = 20;
      }
      
      setState(() {
        _theme = theme;
        _language = language;
        _notificationsEnabled = settings['notifications_enabled'] ?? true;
        _defaultView = defaultView;
        _itemsPerPage = itemsPerPage;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _saveSettings() async {
    try {
      await ConversationService.updateUserSettings(
        theme: _theme,
        language: _language,
        notificationsEnabled: _notificationsEnabled,
        defaultView: _defaultView,
        itemsPerPage: _itemsPerPage,
      );
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Configuración guardada')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configuración'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            tooltip: 'Guardar',
            onPressed: _saveSettings,
          ),
        ],
      ),
      body: _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: theme.colorScheme.error),
            const SizedBox(height: 16),
            Text('Error: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadSettings,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Appearance Section
        _buildSectionHeader('Apariencia', Icons.palette, theme),
        const SizedBox(height: 8),
        _buildThemeSelector(theme),
        
        const SizedBox(height: 24),
        
        // Language Section
        _buildSectionHeader('Idioma', Icons.language, theme),
        const SizedBox(height: 8),
        _buildLanguageSelector(theme),
        
        const SizedBox(height: 24),
        
        // Notifications Section
        _buildSectionHeader('Notificaciones', Icons.notifications, theme),
        const SizedBox(height: 8),
        _buildNotificationSettings(theme),
        
        const SizedBox(height: 24),
        
        // Display Section
        _buildSectionHeader('Visualización', Icons.display_settings, theme),
        const SizedBox(height: 8),
        _buildDisplaySettings(theme),
        
        const SizedBox(height: 32),
        
        // Save Button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _saveSettings,
            icon: const Icon(Icons.save),
            label: const Text('Guardar Cambios'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, ThemeData theme) {
    return Row(
      children: [
        Icon(icon, color: theme.colorScheme.primary),
        const SizedBox(width: 8),
        Text(
          title,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildThemeSelector(ThemeData theme) {
    final themeProvider = Provider.of<ThemeProvider>(context, listen: false);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Tema',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildThemeOption(
                    theme: theme,
                    value: 'light',
                    label: 'Claro',
                    icon: Icons.light_mode,
                    onTap: () {
                      setState(() => _theme = 'light');
                      themeProvider.setLightTheme();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildThemeOption(
                    theme: theme,
                    value: 'dark',
                    label: 'Oscuro',
                    icon: Icons.dark_mode,
                    onTap: () {
                      setState(() => _theme = 'dark');
                      themeProvider.setDarkTheme();
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildThemeOption({
    required ThemeData theme,
    required String value,
    required String label,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    final isSelected = _theme == value;
    
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(
            color: isSelected ? theme.colorScheme.primary : theme.colorScheme.outline,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(8),
          color: isSelected ? theme.colorScheme.primaryContainer.withAlpha(51) : null,
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? theme.colorScheme.primary : theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? theme.colorScheme.primary : theme.colorScheme.onSurfaceVariant,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLanguageSelector(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Idioma de la interfaz',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _language,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.language),
              ),
              items: const [
                DropdownMenuItem(value: 'es', child: Text('Español')),
                DropdownMenuItem(value: 'en', child: Text('English')),
                DropdownMenuItem(value: 'pt', child: Text('Português')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _language = value);
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationSettings(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SwitchListTile(
          title: const Text('Habilitar notificaciones'),
          subtitle: const Text('Recibe alertas sobre nuevas respuestas'),
          value: _notificationsEnabled,
          onChanged: (value) {
            setState(() => _notificationsEnabled = value);
          },
        ),
      ),
    );
  }

  Widget _buildDisplaySettings(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Vista predeterminada',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _defaultView,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.view_module),
              ),
              items: const [
                DropdownMenuItem(value: 'chat', child: Text('Chat')),
                DropdownMenuItem(value: 'history', child: Text('Historial')),
                DropdownMenuItem(value: 'statistics', child: Text('Estadísticas')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _defaultView = value);
                }
              },
            ),
            const SizedBox(height: 16),
            Text(
              'Elementos por página',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<int>(
              value: _itemsPerPage,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.numbers),
              ),
              items: const [
                DropdownMenuItem(value: 10, child: Text('10')),
                DropdownMenuItem(value: 20, child: Text('20')),
                DropdownMenuItem(value: 50, child: Text('50')),
                DropdownMenuItem(value: 100, child: Text('100')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _itemsPerPage = value);
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
