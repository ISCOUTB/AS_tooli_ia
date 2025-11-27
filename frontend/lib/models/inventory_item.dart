class InventoryItem {
  final int id;
  final String name;
  final String type;
  final String? manufacturer;
  final String? model;
  final String? serialNumber;
  final String status;
  final String? location;
  final String? assignedTo;
  final DateTime? purchaseDate;
  final DateTime? warrantyExpiration;
  final Map<String, dynamic>? specifications;

  InventoryItem({
    required this.id,
    required this.name,
    required this.type,
    this.manufacturer,
    this.model,
    this.serialNumber,
    required this.status,
    this.location,
    this.assignedTo,
    this.purchaseDate,
    this.warrantyExpiration,
    this.specifications,
  });

  factory InventoryItem.fromJson(Map<String, dynamic> json) {
    return InventoryItem(
      id: json['id'],
      name: json['name'] ?? 'Sin nombre',
      type: json['type'] ?? 'other',
      manufacturer: json['manufacturer'],
      model: json['model'],
      serialNumber: json['serial_number'],
      status: json['status'] ?? 'available',
      location: json['location'],
      assignedTo: json['assigned_to'],
      purchaseDate: json['purchase_date'] != null ? DateTime.parse(json['purchase_date']) : null,
      warrantyExpiration: json['warranty_expiration'] != null ? DateTime.parse(json['warranty_expiration']) : null,
      specifications: json['specifications'],
    );
  }

  String get typeLabel {
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

  String get statusLabel {
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
