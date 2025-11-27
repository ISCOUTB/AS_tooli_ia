import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/message.dart';

class MessageList extends StatefulWidget {
  final List<Message> messages;

  const MessageList({
    Key? key,
    required this.messages,
  }) : super(key: key);

  @override
  State<MessageList> createState() => _MessageListState();
}

class _MessageListState extends State<MessageList> {
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(MessageList oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.messages.length != oldWidget.messages.length) {
      // Auto-scroll to bottom when new message arrives
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: widget.messages.length,
      itemBuilder: (context, index) {
        return _MessageBubble(message: widget.messages[index]);
      },
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final Message message;

  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUser = message.isUser;

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            _buildAvatar(context, isUser),
            const SizedBox(width: 12),
          ],
          Flexible(
            child: Container(
              constraints: const BoxConstraints(maxWidth: 600),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isUser
                    ? theme.colorScheme.primary.withOpacity(0.1)
                    : theme.colorScheme.surface,
                border: Border.all(
                  color: theme.dividerColor,
                  width: 1,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Message content
                  if (isUser)
                    Text(
                      message.text,
                      style: theme.textTheme.bodyMedium,
                    )
                  else
                    MarkdownBody(
                      data: message.text,
                      styleSheet: MarkdownStyleSheet(
                        p: theme.textTheme.bodyMedium,
                        h1: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        h2: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        h3: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        strong: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        code: theme.textTheme.bodySmall?.copyWith(
                          fontFamily: 'monospace',
                          backgroundColor:
                              theme.colorScheme.surface.withOpacity(0.5),
                        ),
                        listBullet: theme.textTheme.bodyMedium,
                      ),
                    ),
                  const SizedBox(height: 8),
                  // Timestamp and metadata
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _formatTimestamp(message.timestamp),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.textTheme.bodySmall?.color
                              ?.withOpacity(0.6),
                        ),
                      ),
                      if (!isUser && message.confidence != null)
                        Row(
                          children: [
                            Icon(
                              Icons.check_circle_outline,
                              size: 14,
                              color: _getConfidenceColor(
                                  message.confidence!, context),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '${(message.confidence! * 100).toStringAsFixed(0)}%',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: _getConfidenceColor(
                                    message.confidence!, context),
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 12),
            _buildAvatar(context, isUser),
          ],
        ],
      ),
    );
  }

  Widget _buildAvatar(BuildContext context, bool isUser) {
    final theme = Theme.of(context);
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: isUser
            ? theme.colorScheme.primary.withOpacity(0.2)
            : theme.colorScheme.secondary.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Icon(
        isUser ? Icons.person : Icons.smart_toy,
        size: 24,
        color: isUser
            ? theme.colorScheme.primary
            : theme.colorScheme.secondary,
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month}/${timestamp.year} ${timestamp.hour}:${timestamp.minute.toString().padLeft(2, '0')}';
    }
  }

  Color _getConfidenceColor(double confidence, BuildContext context) {
    final theme = Theme.of(context);
    if (confidence >= 0.85) {
      return Colors.green;
    } else if (confidence >= 0.65) {
      return Colors.orange;
    } else {
      return theme.colorScheme.error;
    }
  }
}
