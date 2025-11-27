class Ticket {
  final int id;
  final String title;
  final String description;
  final String status;
  final String priority;
  final String category;
  final String requesterName;
  final String? assignedTo;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? dueDate;

  Ticket({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.priority,
    required this.category,
    required this.requesterName,
    this.assignedTo,
    required this.createdAt,
    this.updatedAt,
    this.dueDate,
  });

  factory Ticket.fromJson(Map<String, dynamic> json) {
    return Ticket(
      id: json['id'],
      title: json['title'] ?? 'Sin título',
      description: json['description'] ?? '',
      status: json['status'] ?? 'new',
      priority: json['priority'] ?? 'medium',
      category: json['category'] ?? 'general',
      requesterName: json['requester_name'] ?? 'Desconocido',
      assignedTo: json['assigned_to'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date']) : null,
    );
  }

  String get statusLabel {
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

  String get priorityLabel {
    switch (priority) {
      case 'very_low':
        return 'Muy Baja';
      case 'low':
        return 'Baja';
      case 'medium':
        return 'Media';
      case 'high':
        return 'Alta';
      case 'very_high':
        return 'Muy Alta';
      default:
        return priority;
    }
  }
}
