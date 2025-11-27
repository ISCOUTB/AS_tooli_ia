import 'package:flutter/material.dart';
import '../models/inventory_item.dart';
import '../services/inventory_service.dart';

class InventoryDetailScreen extends StatefulWidget {
  final int itemId;

  const InventoryDetailScreen({super.key, required this.itemId});

  @override
  State<InventoryDetailScreen> createState() => _InventoryDetailScreenState();
}

class _InventoryDetailScreenState extends State<InventoryDetailScreen> {
  InventoryItem? _item;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadItem();
  }

  Future<void> _loadItem() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final item = await InventoryService.getInventoryItem(widget.itemId);
      setState(() {
        _item = item;
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
        title: Text(_item != null ? _item!.name : 'Cargando...'),
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
              onPressed: _loadItem,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (_item == null) {
      return const Center(child: Text('Elemento no encontrado'));
    }

    return RefreshIndicator(
      onRefresh: _loadItem,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeaderCard(theme),
            const SizedBox(height: 16),
            _buildHardwareSection(theme),
            const SizedBox(height: 16),
            _buildDatesSection(theme),
            const SizedBox(height: 16),
            _buildAssignmentSection(theme),
            if (_item!.specifications != null && _item!.specifications!.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildSpecificationsSection(theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            _buildTypeIcon(_item!.type, theme),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _item!.name,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _item!.typeLabel,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _buildStatusBadge(_item!.status, theme),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHardwareSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.memory,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Información de Hardware',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_item!.manufacturer != null)
              _buildDetailRow('Fabricante', _item!.manufacturer!, Icons.business, theme),
            if (_item!.model != null) ...[
              const Divider(height: 24),
              _buildDetailRow('Modelo', _item!.model!, Icons.label, theme),
            ],
            if (_item!.serialNumber != null) ...[
              const Divider(height: 24),
              _buildDetailRow('Número de Serie', _item!.serialNumber!, Icons.qr_code, theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDatesSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.calendar_today,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Fechas',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_item!.purchaseDate != null)
              _buildDetailRow(
                'Fecha de Compra',
                _formatDate(_item!.purchaseDate!),
                Icons.shopping_cart,
                theme,
              ),
            if (_item!.warrantyExpiration != null) ...[
              const Divider(height: 24),
              _buildWarrantyRow(theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildWarrantyRow(ThemeData theme) {
    final warranty = _item!.warrantyExpiration!;
    final now = DateTime.now();
    final daysUntilExpiry = warranty.difference(now).inDays;
    final isExpired = daysUntilExpiry < 0;

    Color color;
    IconData icon;
    String message;

    if (isExpired) {
      color = Colors.red;
      icon = Icons.warning;
      message = 'Expirada hace ${-daysUntilExpiry} días';
    } else if (daysUntilExpiry <= 30) {
      color = Colors.orange;
      icon = Icons.alarm;
      message = daysUntilExpiry == 0 ? 'Expira hoy' : 'Expira en $daysUntilExpiry días';
    } else {
      color = Colors.green;
      icon = Icons.verified_user;
      message = 'Vigente ($daysUntilExpiry días restantes)';
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Garantía',
                  style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatDate(warranty),
                  style: theme.textTheme.bodyMedium,
                ),
                Text(
                  message,
                  style: TextStyle(
                    color: color,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
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
                  Icons.place,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Ubicación y Asignación',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_item!.location != null)
              _buildDetailRow('Ubicación', _item!.location!, Icons.location_on, theme),
            if (_item!.assignedTo != null) ...[
              const Divider(height: 24),
              _buildDetailRow('Asignado a', _item!.assignedTo!, Icons.person, theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSpecificationsSection(ThemeData theme) {
    return Card(
      child: Theme(
        data: theme.copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          leading: Icon(
            Icons.description,
            color: theme.colorScheme.primary,
          ),
          title: Text(
            'Especificaciones Técnicas',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceVariant.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _item!.specifications!.entries
                      .map((e) => '${e.key}: ${e.value}')
                      .join('\n'),
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeIcon(String type, ThemeData theme) {
    IconData icon;
    Color color;

    switch (type) {
      case 'computer':
        icon = Icons.computer;
        color = Colors.blue;
        break;
      case 'laptop':
        icon = Icons.laptop;
        color = Colors.purple;
        break;
      case 'monitor':
        icon = Icons.monitor;
        color = Colors.teal;
        break;
      case 'printer':
        icon = Icons.print;
        color = Colors.orange;
        break;
      case 'server':
        icon = Icons.dns;
        color = Colors.red;
        break;
      case 'network':
        icon = Icons.router;
        color = Colors.green;
        break;
      case 'phone':
        icon = Icons.phone_android;
        color = Colors.cyan;
        break;
      default:
        icon = Icons.devices_other;
        color = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(icon, color: color, size: 40),
    );
  }

  Widget _buildStatusBadge(String status, ThemeData theme) {
    Color color;
    IconData icon;

    switch (status) {
      case 'available':
        color = Colors.green;
        icon = Icons.check_circle;
        break;
      case 'in_use':
        color = Colors.blue;
        icon = Icons.person;
        break;
      case 'maintenance':
        color = Colors.orange;
        icon = Icons.build;
        break;
      case 'broken':
        color = Colors.red;
        icon = Icons.error;
        break;
      case 'retired':
        color = Colors.grey;
        icon = Icons.archive;
        break;
      default:
        color = Colors.grey;
        icon = Icons.help;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color, width: 2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            _item!.statusLabel,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
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

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
