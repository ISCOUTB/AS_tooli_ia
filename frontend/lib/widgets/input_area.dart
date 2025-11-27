import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class InputArea extends StatefulWidget {
  final Function(String) onSendMessage;
  final bool isLoading;

  const InputArea({
    Key? key,
    required this.onSendMessage,
    this.isLoading = false,
  }) : super(key: key);

  @override
  State<InputArea> createState() => _InputAreaState();
}

class _InputAreaState extends State<InputArea> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    setState(() {
      _hasText = _controller.text.trim().isNotEmpty;
    });
  }

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isEmpty || widget.isLoading) return;

    widget.onSendMessage(text);
    _controller.clear();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        border: Border(
          top: BorderSide(
            color: theme.dividerColor,
            width: 1,
          ),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Input field
          Expanded(
            child: Container(
              constraints: const BoxConstraints(
                minHeight: 48,
                maxHeight: 200,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                border: Border.all(
                  color: theme.dividerColor,
                  width: 1,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: TextField(
                controller: _controller,
                focusNode: _focusNode,
                enabled: !widget.isLoading,
                maxLines: null,
                textInputAction: TextInputAction.newline,
                decoration: InputDecoration(
                  hintText: widget.isLoading
                      ? 'Processing...'
                      : 'Ask about tickets, statistics, inventory...',
                  hintStyle: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.textTheme.bodyMedium?.color?.withOpacity(0.5),
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 14,
                  ),
                ),
                style: theme.textTheme.bodyMedium,
                onSubmitted: (_) => _sendMessage(),
                keyboardType: TextInputType.multiline,
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Send button
          _buildSendButton(theme),
        ],
      ),
    );
  }

  Widget _buildSendButton(ThemeData theme) {
    return Container(
      height: 48,
      width: 48,
      decoration: BoxDecoration(
        color: (_hasText && !widget.isLoading)
            ? theme.colorScheme.primary
            : theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: theme.dividerColor,
          width: 1,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: (_hasText && !widget.isLoading) ? _sendMessage : null,
          borderRadius: BorderRadius.circular(8),
          child: widget.isLoading
              ? Padding(
                  padding: const EdgeInsets.all(12),
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      theme.colorScheme.primary,
                    ),
                  ),
                )
              : Icon(
                  Icons.send,
                  color: (_hasText && !widget.isLoading)
                      ? Colors.white
                      : theme.iconTheme.color?.withOpacity(0.3),
                  size: 24,
                ),
        ),
      ),
    );
  }
}
