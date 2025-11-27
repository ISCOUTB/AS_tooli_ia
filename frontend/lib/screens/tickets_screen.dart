import 'package:flutter/material.dart';
import '../models/ticket.dart';
import '../services/ticket_service.dart';
import 'ticket_detail_screen.dart';

class TicketsScreen extends StatefulWidget {
  const TicketsScreen({super.key});

  @override
  State<TicketsScreen> createState() => _TicketsScreenState();
}

class _TicketsScreenState extends State<TicketsScreen> {
  List<Ticket> _tickets = [];
  List<Ticket> _filteredTickets = [];
  bool _isLoading = true;
  String? _error;
  
  // Filters
  String? _selectedStatus;
  String? _selectedPriority;
  String _searchQuery = '';
  String _sortBy = 'date'; // date, priority, status
  bool _sortAscending = false; // false = descendente, true = ascendente

  @override
  void initState() {
    super.initState();
    _loadTickets();
  }

  Future<void> _loadTickets() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Cargar TODOS los tickets sin filtros del servidor
      final tickets = await TicketService.getTickets();

      setState(() {
        _tickets = tickets;
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
    // Empezar con todos los tickets
    _filteredTickets = List.from(_tickets);

    // Aplicar filtro de búsqueda
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      _filteredTickets = _filteredTickets.where((ticket) {
        return ticket.title.toLowerCase().contains(query) ||
               ticket.description.toLowerCase().contains(query) ||
               ticket.id.toString().contains(query);
      }).toList();
    }

    // Aplicar filtro de estado
    if (_selectedStatus != null) {
      _filteredTickets = _filteredTickets.where((ticket) {
        return ticket.status == _selectedStatus;
      }).toList();
    }

    // Aplicar filtro de prioridad
    if (_selectedPriority != null) {
      _filteredTickets = _filteredTickets.where((ticket) {
        return ticket.priority == _selectedPriority;
      }).toList();
    }

    // Ordenar
    switch (_sortBy) {
      case 'date':
        _filteredTickets.sort((a, b) => 
          _sortAscending 
            ? a.createdAt.compareTo(b.createdAt)
            : b.createdAt.compareTo(a.createdAt)
        );
        break;
      case 'priority':
        final priorityOrder = {'very_high': 5, 'high': 4, 'medium': 3, 'low': 2, 'very_low': 1};
        _filteredTickets.sort((a, b) {
          final aPriority = priorityOrder[a.priority] ?? 0;
          final bPriority = priorityOrder[b.priority] ?? 0;
          return _sortAscending 
            ? aPriority.compareTo(bPriority)
            : bPriority.compareTo(aPriority);
        });
        break;
      case 'status':
        _filteredTickets.sort((a, b) => 
          _sortAscending
            ? a.status.compareTo(b.status)
            : b.status.compareTo(a.status)
        );
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Todos los Tickets'),
        actions: [
          // Botón para cambiar orden ascendente/descendente
          IconButton(
            icon: Icon(_sortAscending ? Icons.arrow_upward : Icons.arrow_downward),
            onPressed: () {
              setState(() {
                _sortAscending = !_sortAscending;
                _applyFiltersAndSort();
              });
            },
            tooltip: _sortAscending ? 'Orden Ascendente' : 'Orden Descendente',
          ),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: 'Filtros',
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            tooltip: 'Ordenar Por',
            onSelected: (value) {
              setState(() {
                _sortBy = value;
                _applyFiltersAndSort();
              });
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'date',
                child: Row(
                  children: [
                    Icon(Icons.calendar_today, size: 20, color: _sortBy == 'date' ? theme.colorScheme.primary : null),
                    const SizedBox(width: 8),
                    const Text('Por Fecha'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'priority',
                child: Row(
                  children: [
                    Icon(Icons.priority_high, size: 20, color: _sortBy == 'priority' ? theme.colorScheme.primary : null),
                    const SizedBox(width: 8),
                    const Text('Por Prioridad'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'status',
                child: Row(
                  children: [
                    Icon(Icons.info_outline, size: 20, color: _sortBy == 'status' ? theme.colorScheme.primary : null),
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
                hintText: 'Buscar por ID, título o descripción...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          setState(() {
                            _searchQuery = '';
                            _applyFiltersAndSort();
                          });
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                helperText: 'La búsqueda se aplica en tiempo real',
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                  _applyFiltersAndSort(); // Aplicar búsqueda en tiempo real
                });
              },
            ),
          ),

          // Active filters chips
          if (_selectedStatus != null || _selectedPriority != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Wrap(
                spacing: 8,
                children: [
                  if (_selectedStatus != null)
                    Chip(
                      label: Text('Estado: ${_getStatusLabel(_selectedStatus!)}'),
                      onDeleted: () {
                        setState(() {
                          _selectedStatus = null;
                        });
                        _loadTickets();
                      },
                    ),
                  if (_selectedPriority != null)
                    Chip(
                      label: Text('Prioridad: ${_getPriorityLabel(_selectedPriority!)}'),
                      onDeleted: () {
                        setState(() {
                          _selectedPriority = null;
                        });
                        _loadTickets();
                      },
                    ),
                ],
              ),
            ),

          // Tickets list
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
              onPressed: _loadTickets,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (_filteredTickets.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox_outlined, size: 64, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(height: 16),
            Text(
              'No se encontraron tickets',
              style: theme.textTheme.titleMedium,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadTickets,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _filteredTickets.length,
        itemBuilder: (context, index) {
          final ticket = _filteredTickets[index];
          return _buildTicketCard(ticket, theme);
        },
      ),
    );
  }

  Widget _buildTicketCard(Ticket ticket, ThemeData theme) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => TicketDetailScreen(ticketId: ticket.id),
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
                  Expanded(
                    child: Text(
                      '#${ticket.id} - ${ticket.title}',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  _buildPriorityBadge(ticket.priority, theme),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                ticket.description,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildStatusChip(ticket.status, theme),
                  _buildInfoChip(Icons.person, ticket.requesterName, theme),
                  if (ticket.assignedTo != null)
                    _buildInfoChip(Icons.assignment_ind, ticket.assignedTo!, theme),
                  _buildInfoChip(Icons.access_time, _formatDate(ticket.createdAt), theme),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPriorityBadge(String priority, ThemeData theme) {
    Color color;
    switch (priority) {
      case 'very_high':
        color = Colors.red[700]!;
        break;
      case 'high':
        color = Colors.orange[700]!;
        break;
      case 'medium':
        color = Colors.blue[700]!;
        break;
      case 'low':
        color = Colors.green[700]!;
        break;
      case 'very_low':
        color = Colors.grey[700]!;
        break;
      default:
        color = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color),
      ),
      child: Text(
        _getPriorityLabel(priority),
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status, ThemeData theme) {
    Color color;
    IconData icon;
    
    switch (status) {
      case 'new':
        color = Colors.blue;
        icon = Icons.fiber_new;
        break;
      case 'assigned':
        color = Colors.purple;
        icon = Icons.assignment_ind;
        break;
      case 'in_progress':
        color = Colors.orange;
        icon = Icons.autorenew;
        break;
      case 'solved':
        color = Colors.green;
        icon = Icons.check_circle;
        break;
      case 'closed':
        color = Colors.grey;
        icon = Icons.cancel;
        break;
      default:
        color = Colors.grey;
        icon = Icons.info;
    }

    return Chip(
      avatar: Icon(icon, size: 16, color: color),
      label: Text(
        _getStatusLabel(status),
        style: TextStyle(fontSize: 11, color: color),
      ),
      backgroundColor: color.withOpacity(0.1),
      visualDensity: VisualDensity.compact,
    );
  }

  Widget _buildInfoChip(IconData icon, String label, ThemeData theme) {
    return Chip(
      avatar: Icon(icon, size: 14, color: theme.colorScheme.onSurfaceVariant),
      label: Text(
        label,
        style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurfaceVariant),
      ),
      visualDensity: VisualDensity.compact,
    );
  }

  void _showFilterDialog() {
    // Variables temporales para los filtros dentro del diálogo
    String? tempStatus = _selectedStatus;
    String? tempPriority = _selectedPriority;
    
    showDialog(
      context: context,
      barrierDismissible: false, // No permitir cerrar tocando fuera
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Filtros'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Estado', style: TextStyle(fontWeight: FontWeight.bold)),
                Wrap(
                  spacing: 8,
                  children: [
                    FilterChip(
                      label: const Text('Nuevo'),
                      selected: tempStatus == 'new',
                      onSelected: (selected) {
                        setDialogState(() {
                          tempStatus = selected ? 'new' : null;
                        });
                      },
                    ),
                    FilterChip(
                      label: const Text('En Progreso'),
                      selected: tempStatus == 'in_progress',
                      onSelected: (selected) {
                        setDialogState(() {
                          tempStatus = selected ? 'in_progress' : null;
                        });
                      },
                    ),
                    FilterChip(
                      label: const Text('Resuelto'),
                      selected: tempStatus == 'solved',
                      onSelected: (selected) {
                        setDialogState(() {
                          tempStatus = selected ? 'solved' : null;
                        });
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const Text('Prioridad', style: TextStyle(fontWeight: FontWeight.bold)),
                Wrap(
                  spacing: 8,
                  children: [
                    FilterChip(
                      label: const Text('Muy Alta'),
                      selected: tempPriority == 'very_high',
                      onSelected: (selected) {
                        setDialogState(() {
                          tempPriority = selected ? 'very_high' : null;
                        });
                      },
                    ),
                    FilterChip(
                      label: const Text('Alta'),
                      selected: tempPriority == 'high',
                      onSelected: (selected) {
                        setDialogState(() {
                          tempPriority = selected ? 'high' : null;
                        });
                      },
                    ),
                    FilterChip(
                      label: const Text('Media'),
                      selected: tempPriority == 'medium',
                      onSelected: (selected) {
                        setDialogState(() {
                          tempPriority = selected ? 'medium' : null;
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
                // Cerrar sin aplicar cambios
                Navigator.pop(context);
              },
              child: const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () {
                setState(() {
                  _selectedStatus = null;
                  _selectedPriority = null;
                  _applyFiltersAndSort();
                });
                Navigator.pop(context);
              },
              child: const Text('Limpiar'),
            ),
            FilledButton(
              onPressed: () {
                setState(() {
                  _selectedStatus = tempStatus;
                  _selectedPriority = tempPriority;
                  _applyFiltersAndSort();
                });
                Navigator.pop(context);
              },
              child: const Text('Aplicar'),
            ),
          ],
        ),
      ),
    );
  }

  String _getStatusLabel(String status) {
    switch (status) {
      case 'new':
        return 'Nuevo';
      case 'assigned':
        return 'Asignado';
      case 'in_progress':
        return 'En Progreso';
      case 'pending':
        return 'Pendiente';
      case 'solved':
        return 'Resuelto';
      case 'closed':
        return 'Cerrado';
      default:
        return status;
    }
  }

  String _getPriorityLabel(String priority) {
    switch (priority) {
      case 'very_high':
        return 'Muy Alta';
      case 'high':
        return 'Alta';
      case 'medium':
        return 'Media';
      case 'low':
        return 'Baja';
      case 'very_low':
        return 'Muy Baja';
      default:
        return priority;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'Hoy ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays == 1) {
      return 'Ayer';
    } else if (difference.inDays < 7) {
      return 'Hace ${difference.inDays} días';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}
