import 'package:flutter/material.dart';
import '../models/inventory_item.dart';
import '../services/inventory_service.dart';
import 'inventory_detail_screen.dart';

class InventoryScreen extends StatefulWidget {
  const InventoryScreen({super.key});

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen> {
  List<InventoryItem> _items = [];
  List<InventoryItem> _filteredItems = [];
  bool _isLoading = true;
  String? _error;
  
  // Filters
  String? _selectedType;
  String? _selectedStatus;
  String _searchQuery = '';
  String _sortBy = 'name'; // name, type, status

  @override
  void initState() {
    super.initState();
    _loadInventory();
  }

  Future<void> _loadInventory() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final items = await InventoryService.getInventory(
        type: _selectedType,
        status: _selectedStatus,
        search: _searchQuery.isEmpty ? null : _searchQuery,
      );

      setState(() {
        _items = items;
        _applyFiltersAndSort();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _applyFiltersAndSort() {
    _filteredItems = List.from(_items);

    // Sort
    switch (_sortBy) {
      case 'name':
        _filteredItems.sort((a, b) => a.name.compareTo(b.name));
        break;
      case 'type':
        _filteredItems.sort((a, b) => a.type.compareTo(b.type));
        break;
      case 'status':
        _filteredItems.sort((a, b) => a.status.compareTo(b.status));
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventario'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: 'Filtros',
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            tooltip: 'Ordenar',
            onSelected: (value) {
              setState(() {
                _sortBy = value;
                _applyFiltersAndSort();
              });
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'name',
                child: Row(
                  children: [
                    Icon(Icons.sort_by_alpha, size: 20, color: _sortBy == 'name' ? theme.colorScheme.primary : null),
                    const SizedBox(width: 8),
                    const Text('Por Nombre'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'type',
                child: Row(
                  children: [
                    Icon(Icons.devices, size: 20, color: _sortBy == 'type' ? theme.colorScheme.primary : null),
                    const SizedBox(width: 8),
                    const Text('Por Tipo'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'status',
                child: Row(
                  children: [
                    Icon(Icons.check_circle, size: 20, color: _sortBy == 'status' ? theme.colorScheme.primary : null),
                    const SizedBox(width: 8),
                    const Text('Por Estado'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Buscar en inventario...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          setState(() {
                            _searchQuery = '';
                          });
                          _loadInventory();
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
              onSubmitted: (_) => _loadInventory(),
            ),
          ),

          // Active filters chips
          if (_selectedType != null || _selectedStatus != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Wrap(
                spacing: 8,
                children: [
                  if (_selectedType != null)
                    Chip(
                      label: Text('Tipo: ${_getTypeLabel(_selectedType!)}'),
                      onDeleted: () {
                        setState(() {
                          _selectedType = null;
                        });
                        _loadInventory();
                      },
                    ),
                  if (_selectedStatus != null)
                    Chip(
                      label: Text('Estado: ${_getStatusLabel(_selectedStatus!)}'),
                      onDeleted: () {
                        setState(() {
                          _selectedStatus = null;
                        });
                        _loadInventory();
                      },
                    ),
                ],
              ),
            ),

          // Inventory list
          Expanded(
            child: _buildBody(theme),
          ),
        ],
      ),
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
              onPressed: _loadInventory,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (_filteredItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inventory_2_outlined, size: 64, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(height: 16),
            Text(
              'No se encontraron elementos',
              style: theme.textTheme.titleMedium,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadInventory,
      child: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: 400,
          childAspectRatio: 1.4,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
        ),
        itemCount: _filteredItems.length,
        itemBuilder: (context, index) {
          final item = _filteredItems[index];
          return _buildInventoryCard(item, theme);
        },
      ),
    );
  }

  Widget _buildInventoryCard(InventoryItem item, ThemeData theme) {
    return Card(
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => InventoryDetailScreen(itemId: item.id),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _buildTypeIcon(item.type, theme),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.name,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          item.typeLabel,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildStatusBadge(item.status, theme),
                ],
              ),
              const SizedBox(height: 12),
              if ((item.manufacturer != null && item.manufacturer!.isNotEmpty) || 
                  (item.model != null && item.model!.isNotEmpty))
                Text(
                  '${item.manufacturer ?? ''} ${item.model ?? ''}',
                  style: theme.textTheme.bodyMedium,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.location_on, size: 14, color: theme.colorScheme.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      item.location ?? 'Sin ubicación',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              if (item.assignedTo != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(Icons.person, size: 14, color: theme.colorScheme.onSurfaceVariant),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        item.assignedTo!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
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
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(icon, color: color, size: 24),
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
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            _getStatusLabel(status),
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filtros'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Tipo', style: TextStyle(fontWeight: FontWeight.bold)),
              Wrap(
                spacing: 8,
                children: [
                  FilterChip(
                    label: const Text('Computadora'),
                    selected: _selectedType == 'computer',
                    onSelected: (selected) {
                      setState(() {
                        _selectedType = selected ? 'computer' : null;
                      });
                    },
                  ),
                  FilterChip(
                    label: const Text('Laptop'),
                    selected: _selectedType == 'laptop',
                    onSelected: (selected) {
                      setState(() {
                        _selectedType = selected ? 'laptop' : null;
                      });
                    },
                  ),
                  FilterChip(
                    label: const Text('Monitor'),
                    selected: _selectedType == 'monitor',
                    onSelected: (selected) {
                      setState(() {
                        _selectedType = selected ? 'monitor' : null;
                      });
                    },
                  ),
                  FilterChip(
                    label: const Text('Impresora'),
                    selected: _selectedType == 'printer',
                    onSelected: (selected) {
                      setState(() {
                        _selectedType = selected ? 'printer' : null;
                      });
                    },
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text('Estado', style: TextStyle(fontWeight: FontWeight.bold)),
              Wrap(
                spacing: 8,
                children: [
                  FilterChip(
                    label: const Text('Disponible'),
                    selected: _selectedStatus == 'available',
                    onSelected: (selected) {
                      setState(() {
                        _selectedStatus = selected ? 'available' : null;
                      });
                    },
                  ),
                  FilterChip(
                    label: const Text('En Uso'),
                    selected: _selectedStatus == 'in_use',
                    onSelected: (selected) {
                      setState(() {
                        _selectedStatus = selected ? 'in_use' : null;
                      });
                    },
                  ),
                  FilterChip(
                    label: const Text('Mantenimiento'),
                    selected: _selectedStatus == 'maintenance',
                    onSelected: (selected) {
                      setState(() {
                        _selectedStatus = selected ? 'maintenance' : null;
                      });
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _selectedType = null;
                _selectedStatus = null;
              });
              Navigator.pop(context);
              _loadInventory();
            },
            child: const Text('Limpiar'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              _loadInventory();
            },
            child: const Text('Aplicar'),
          ),
        ],
      ),
    );
  }

  String _getTypeLabel(String type) {
    switch (type) {
      case 'computer':
        return 'Computadora';
      case 'laptop':
        return 'Laptop';
      case 'monitor':
        return 'Monitor';
      case 'printer':
        return 'Impresora';
      case 'server':
        return 'Servidor';
      case 'network':
        return 'Equipo de Red';
      case 'phone':
        return 'Teléfono';
      case 'other':
        return 'Otro';
      default:
        return type;
    }
  }

  String _getStatusLabel(String status) {
    switch (status) {
      case 'available':
        return 'Disponible';
      case 'in_use':
        return 'En Uso';
      case 'maintenance':
        return 'Mantenimiento';
      case 'broken':
        return 'Averiado';
      case 'retired':
        return 'Retirado';
      default:
        return status;
    }
  }
}
