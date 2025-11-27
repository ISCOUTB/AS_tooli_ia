import 'package:flutter/material.dart';

class SuggestionsPanel extends StatelessWidget {
  final Function(String) onSuggestionTap;

  const SuggestionsPanel({
    Key? key,
    required this.onSuggestionTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenWidth = MediaQuery.of(context).size.width;
    final isMobile = screenWidth < 600;
    
    // Ajustar padding según tamaño de pantalla
    final horizontalPadding = isMobile ? 16.0 : 24.0;
    final verticalSpacing = isMobile ? 16.0 : 24.0;

    return Center(
      child: SingleChildScrollView(
        padding: EdgeInsets.symmetric(
          horizontal: horizontalPadding,
          vertical: verticalSpacing,
        ),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Welcome message
              Icon(
                Icons.support_agent,
                size: isMobile ? 48 : 64,
                color: theme.colorScheme.primary.withOpacity(0.8),
              ),
              SizedBox(height: isMobile ? 16 : 24),
              Text(
                'Bienvenido a GLPI Assistant',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  fontSize: isMobile ? 20 : null,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Tu compañero inteligente para la gestión de servicios de TI. Pregúntame sobre tickets, inventario, estadísticas y más.',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.textTheme.bodyLarge?.color?.withOpacity(0.7),
                  fontSize: isMobile ? 14 : null,
                ),
              ),
              SizedBox(height: isMobile ? 24 : 40),

              // Capabilities
              Text(
                'En qué puedo ayudarte:',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  fontSize: isMobile ? 16 : null,
                ),
              ),
              SizedBox(height: isMobile ? 12 : 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildCapabilityChip(
                    context,
                    icon: Icons.confirmation_number,
                    label: 'Gestión de Tickets',
                    isMobile: isMobile,
                  ),
                  _buildCapabilityChip(
                    context,
                    icon: Icons.analytics,
                    label: 'Estadísticas e Informes',
                    isMobile: isMobile,
                  ),
                  _buildCapabilityChip(
                    context,
                    icon: Icons.computer,
                    label: 'Búsqueda de Inventario',
                    isMobile: isMobile,
                  ),
                  _buildCapabilityChip(
                    context,
                    icon: Icons.search,
                    label: 'Buscar y Filtrar',
                    isMobile: isMobile,
                  ),
                  _buildCapabilityChip(
                    context,
                    icon: Icons.insights,
                    label: 'Análisis de Datos',
                    isMobile: isMobile,
                  ),
                ],
              ),
              SizedBox(height: isMobile ? 24 : 40),

              // Suggested queries
              Text(
                'Prueba preguntando:',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  fontSize: isMobile ? 16 : null,
                ),
              ),
              SizedBox(height: isMobile ? 12 : 16),
              _buildSuggestionCard(
                context,
                icon: Icons.list_alt,
                title: '¿Qué tickets disponibles hay?',
                description: 'Obtén una vista rápida de los tickets abiertos',
                isMobile: isMobile,
              ),
              const SizedBox(height: 12),
              _buildSuggestionCard(
                context,
                icon: Icons.bar_chart,
                title: 'Muéstrame las estadísticas de tickets',
                description:
                    'Visualiza análisis completos por estado, prioridad y tipo',
                isMobile: isMobile,
              ),
              const SizedBox(height: 12),
              _buildSuggestionCard(
                context,
                icon: Icons.priority_high,
                title: 'Lista todos los tickets de alta prioridad',
                description: 'Filtra tickets por nivel de prioridad',
                isMobile: isMobile,
              ),
              const SizedBox(height: 12),
              _buildSuggestionCard(
                context,
                icon: Icons.computer,
                title: '¿Cuál es el número total de computadoras de la marca HP en el inventario actual?',
                description: 'Consulta elementos específicos del inventario',
                isMobile: isMobile,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCapabilityChip(
    BuildContext context, {
    required IconData icon,
    required String label,
    required bool isMobile,
  }) {
    final theme = Theme.of(context);

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isMobile ? 12 : 16,
        vertical: isMobile ? 8 : 10,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: theme.colorScheme.primary.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: isMobile ? 16 : 18,
            color: theme.colorScheme.primary,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w500,
                fontSize: isMobile ? 12 : null,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String description,
    required bool isMobile,
  }) {
    final theme = Theme.of(context);

    return Material(
      color: theme.colorScheme.surface,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: () => onSuggestionTap(title),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: EdgeInsets.all(isMobile ? 12 : 16),
          decoration: BoxDecoration(
            border: Border.all(
              color: theme.dividerColor,
              width: 1,
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Container(
                width: isMobile ? 36 : 40,
                height: isMobile ? 36 : 40,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  icon,
                  color: theme.colorScheme.primary,
                  size: isMobile ? 20 : 24,
                ),
              ),
              SizedBox(width: isMobile ? 12 : 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      title,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        fontSize: isMobile ? 13 : null,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.textTheme.bodySmall?.color
                            ?.withOpacity(0.7),
                        fontSize: isMobile ? 11 : null,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                size: isMobile ? 14 : 16,
                color: theme.iconTheme.color?.withOpacity(0.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
