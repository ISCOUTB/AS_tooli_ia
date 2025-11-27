import 'package:flutter/material.dart';
import '../services/conversation_service.dart';

class StatisticsScreen extends StatefulWidget {
  const StatisticsScreen({super.key});

  @override
  State<StatisticsScreen> createState() => _StatisticsScreenState();
}

class _StatisticsScreenState extends State<StatisticsScreen> {
  Map<String, dynamic>? _dashboardStats;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadStatistics();
  }

  Future<void> _loadStatistics() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final stats = await ConversationService.getDashboardStatistics();
      
      setState(() {
        _dashboardStats = stats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _clearCache() async {
    try {
      await ConversationService.clearStatisticsCache();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Caché limpiado')),
        );
        _loadStatistics();
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
        title: const Text('Estadísticas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Recargar',
            onPressed: _loadStatistics,
          ),
          IconButton(
            icon: const Icon(Icons.clear_all),
            tooltip: 'Limpiar caché',
            onPressed: _clearCache,
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
              onPressed: _loadStatistics,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (_dashboardStats == null) {
      return const Center(child: Text('No hay datos disponibles'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Overview Section
          Text(
            'Resumen General',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          
          // Stats Cards
          _buildStatsGrid(theme),
          
          const SizedBox(height: 24),
          
          // Today Section
          Text(
            'Actividad de Hoy',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          
          _buildTodayStats(theme),
          
          const SizedBox(height: 24),
          
          // Additional Info
          _buildAdditionalInfo(theme),
        ],
      ),
    );
  }

  Widget _buildStatsGrid(ThemeData theme) {
    final totalConvs = _dashboardStats!['total_conversations'] ?? 0;
    final totalMsgs = _dashboardStats!['total_messages'] ?? 0;
    final avgMsgsPerConv = totalConvs > 0 ? (totalMsgs / totalConvs).toStringAsFixed(1) : '0';
    
    // Ajustar número de columnas según ancho de pantalla
    final screenWidth = MediaQuery.of(context).size.width;
    final crossAxisCount = screenWidth < 600 ? 2 : 4;
    
    return GridView.count(
      crossAxisCount: crossAxisCount,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.4, // Aumentado para dar más altura
      children: [
        _buildStatCard(
          theme: theme,
          title: 'Total Conversaciones',
          value: _dashboardStats!['total_conversations'].toString(),
          icon: Icons.forum_outlined,
          color: const Color(0xFF2196F3),
          trend: null,
        ),
        _buildStatCard(
          theme: theme,
          title: 'Total Mensajes',
          value: _dashboardStats!['total_messages'].toString(),
          icon: Icons.chat_bubble_outline,
          color: const Color(0xFF4CAF50),
          trend: null,
        ),
        _buildStatCard(
          theme: theme,
          title: 'Conversaciones Activas',
          value: _dashboardStats!['active_conversations'].toString(),
          icon: Icons.chat,
          color: const Color(0xFFFF9800),
          trend: '+${_dashboardStats!['conversations_today']}',
        ),
        _buildStatCard(
          theme: theme,
          title: 'Promedio Mensajes',
          value: avgMsgsPerConv,
          icon: Icons.analytics_outlined,
          color: const Color(0xFF9C27B0),
          trend: 'por conversación',
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required ThemeData theme,
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    String? trend,
  }) {
    return Card(
      elevation: 2,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              color.withOpacity(0.1),
              color.withOpacity(0.05),
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      title,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.w500,
                        fontSize: 11,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Icon(icon, color: color, size: 16),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      alignment: Alignment.centerLeft,
                      child: Text(
                        value,
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                    ),
                    if (trend != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        trend,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                          fontSize: 10,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTodayStats(ThemeData theme) {
    return Card(
      elevation: 3,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              theme.colorScheme.primaryContainer,
              theme.colorScheme.secondaryContainer,
            ],
          ),
        ),
        padding: const EdgeInsets.all(16),
        child: IntrinsicHeight(
          child: Row(
            children: [
              Expanded(
                child: _buildTodayStatItem(
                  theme: theme,
                  icon: Icons.auto_awesome,
                  iconColor: theme.colorScheme.primary,
                  value: _dashboardStats!['conversations_today'].toString(),
                  label: 'Conversaciones Hoy',
                  textColor: theme.colorScheme.onPrimaryContainer,
                ),
              ),
              Container(
                width: 1,
                color: Colors.white.withOpacity(0.3),
                margin: const EdgeInsets.symmetric(horizontal: 12),
              ),
              Expanded(
                child: _buildTodayStatItem(
                  theme: theme,
                  icon: Icons.send_rounded,
                  iconColor: theme.colorScheme.secondary,
                  value: _dashboardStats!['messages_today'].toString(),
                  label: 'Mensajes Enviados',
                  textColor: theme.colorScheme.onSecondaryContainer,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTodayStatItem({
    required ThemeData theme,
    required IconData icon,
    required Color iconColor,
    required String value,
    required String label,
    required Color textColor,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.9),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            size: 28,
            color: iconColor,
          ),
        ),
        const SizedBox(height: 8),
        FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            value,
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          textAlign: TextAlign.center,
          style: theme.textTheme.bodySmall?.copyWith(
            color: textColor,
            fontWeight: FontWeight.w500,
            fontSize: 11,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  Widget _buildAdditionalInfo(ThemeData theme) {
    final avgMsgs = _dashboardStats!['average_messages_per_conversation']?.toStringAsFixed(1) ?? '0.0';
    final totalTokens = _dashboardStats!['total_tokens_used'] ?? 0;
    final archivedCount = _dashboardStats!['archived_conversations'] ?? 0;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Detalles de Uso',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                _buildInfoRow(
                  theme: theme,
                  icon: Icons.show_chart,
                  iconColor: Colors.blue,
                  label: 'Promedio de mensajes por conversación',
                  value: '$avgMsgs mensajes',
                ),
                const Divider(height: 32),
                _buildInfoRow(
                  theme: theme,
                  icon: Icons.memory,
                  iconColor: Colors.purple,
                  label: 'Tokens IA utilizados',
                  value: totalTokens.toString(),
                ),
                const Divider(height: 32),
                _buildInfoRow(
                  theme: theme,
                  icon: Icons.archive_outlined,
                  iconColor: Colors.orange,
                  label: 'Conversaciones archivadas',
                  value: '$archivedCount archivadas',
                ),
                const Divider(height: 32),
                _buildInfoRow(
                  theme: theme,
                  icon: Icons.schedule,
                  iconColor: Colors.green,
                  label: 'Última actividad',
                  value: _formatLastActivity(_dashboardStats!['last_activity']),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow({
    required ThemeData theme,
    required IconData icon,
    required String label,
    required String value,
    Color? iconColor,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: (iconColor ?? theme.colorScheme.primary).withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: iconColor ?? theme.colorScheme.primary,
            size: 24,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _formatLastActivity(dynamic activity) {
    if (activity == null || activity == 'Never') {
      return 'Nunca';
    }

    try {
      final date = DateTime.parse(activity.toString());
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inMinutes < 1) {
        return 'Hace un momento';
      } else if (difference.inHours < 1) {
        return 'Hace ${difference.inMinutes} minutos';
      } else if (difference.inDays < 1) {
        return 'Hace ${difference.inHours} horas';
      } else {
        return 'Hace ${difference.inDays} días';
      }
    } catch (e) {
      return activity.toString();
    }
  }
}
