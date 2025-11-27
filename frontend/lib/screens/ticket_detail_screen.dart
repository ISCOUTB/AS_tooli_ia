import 'package:flutter/material.dart';
import '../models/ticket.dart';
import '../services/ticket_service.dart';

class TicketDetailScreen extends StatefulWidget {
  final int ticketId;

  const TicketDetailScreen({super.key, required this.ticketId});

  @override
  State<TicketDetailScreen> createState() => _TicketDetailScreenState();
}

class _TicketDetailScreenState extends State<TicketDetailScreen> {
  Ticket? _ticket;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadTicket();
  }

  Future<void> _loadTicket() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final ticket = await TicketService.getTicket(widget.ticketId);
      setState(() {
        _ticket = ticket;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(_ticket != null ? 'Ticket #${_ticket!.id}' : 'Cargando...'),
      ),
      body: _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
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
              onPressed: _loadTicket,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (_ticket == null) {
      return const Center(child: Text('Ticket no encontrado'));
    }

    return RefreshIndicator(
      onRefresh: _loadTicket,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatusBanner(theme),
            const SizedBox(height: 24),
            _buildHeaderSection(theme),
            const SizedBox(height: 24),
            _buildDescriptionSection(theme),
            const SizedBox(height: 24),
            _buildDetailsSection(theme),
            const SizedBox(height: 24),
            _buildAssignmentSection(theme),
            if (_ticket!.dueDate != null) ...[
              const SizedBox(height: 24),
              _buildDueDateSection(theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBanner(ThemeData theme) {
    Color backgroundColor;
    Color textColor;
    IconData icon;

    switch (_ticket!.status) {
      case 'new':
        backgroundColor = Colors.blue;
        textColor = Colors.white;
        icon = Icons.fiber_new;
        break;
      case 'assigned':
        backgroundColor = Colors.purple;
        textColor = Colors.white;
        icon = Icons.assignment_ind;
        break;
      case 'in_progress':
        backgroundColor = Colors.orange;
        textColor = Colors.white;
        icon = Icons.autorenew;
        break;
      case 'pending':
        backgroundColor = Colors.amber;
        textColor = Colors.black87;
        icon = Icons.pending;
        break;
      case 'solved':
        backgroundColor = Colors.green;
        textColor = Colors.white;
        icon = Icons.check_circle;
        break;
      case 'closed':
        backgroundColor = Colors.grey;
        textColor = Colors.white;
        icon = Icons.cancel;
        break;
      default:
        backgroundColor = Colors.grey;
        textColor = Colors.white;
        icon = Icons.info;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: textColor, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Estado: ${_ticket!.statusLabel}',
                  style: TextStyle(
                    color: textColor,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Prioridad: ${_ticket!.priorityLabel}',
                  style: TextStyle(
                    color: textColor.withOpacity(0.9),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          _buildPriorityIcon(_ticket!.priority, textColor),
        ],
      ),
    );
  }

  Widget _buildPriorityIcon(String priority, Color color) {
    int count;
    switch (priority) {
      case 'very_high':
        count = 5;
        break;
      case 'high':
        count = 4;
        break;
      case 'medium':
        count = 3;
        break;
      case 'low':
        count = 2;
        break;
      case 'very_low':
        count = 1;
        break;
      default:
        count = 3;
    }

    return Column(
      children: List.generate(
        5,
        (index) => Icon(
          Icons.arrow_drop_up,
          color: index < count ? color : color.withOpacity(0.3),
          size: 16,
        ),
      ).reversed.toList(),
    );
  }

  Widget _buildHeaderSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _ticket!.title,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Ticket #${_ticket!.id}',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDescriptionSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.description,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Descripción',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              _ticket!.description,
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailsSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.info_outline,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Detalles',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildDetailRow('Categoría', _ticket!.category, Icons.category, theme),
            const Divider(height: 24),
            _buildDetailRow('Fecha de Creación', _formatDateTime(_ticket!.createdAt), Icons.calendar_today, theme),
            if (_ticket!.updatedAt != null) ...[
              const Divider(height: 24),
              _buildDetailRow('Última Actualización', _formatDateTime(_ticket!.updatedAt!), Icons.update, theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAssignmentSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.people,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Asignación',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildDetailRow('Solicitante', _ticket!.requesterName, Icons.person, theme),
            if (_ticket!.assignedTo != null) ...[
              const Divider(height: 24),
              _buildDetailRow('Asignado a', _ticket!.assignedTo!, Icons.assignment_ind, theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDueDateSection(ThemeData theme) {
    final dueDate = _ticket!.dueDate!;
    final now = DateTime.now();
    final isOverdue = dueDate.isBefore(now);
    final daysUntilDue = dueDate.difference(now).inDays;

    Color cardColor;
    IconData icon;
    String message;

    if (isOverdue) {
      cardColor = Colors.red;
      icon = Icons.warning;
      message = 'Vencido hace ${-daysUntilDue} días';
    } else if (daysUntilDue <= 2) {
      cardColor = Colors.orange;
      icon = Icons.alarm;
      message = daysUntilDue == 0 ? 'Vence hoy' : 'Vence en $daysUntilDue días';
    } else {
      cardColor = Colors.green;
      icon = Icons.schedule;
      message = 'Vence en $daysUntilDue días';
    }

    return Card(
      color: cardColor.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(icon, color: cardColor, size: 32),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Fecha Límite',
                    style: TextStyle(
                      color: cardColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _formatDateTime(dueDate),
                    style: theme.textTheme.bodyMedium,
                  ),
                  Text(
                    message,
                    style: TextStyle(
                      color: cardColor,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, IconData icon, ThemeData theme) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _formatDateTime(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
