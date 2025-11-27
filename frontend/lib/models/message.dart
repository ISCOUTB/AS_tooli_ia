class Message {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? intention;
  final double? confidence;

  Message({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
    this.intention,
    this.confidence,
  }) : timestamp = timestamp ?? DateTime.now();
}
