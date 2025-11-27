import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';

/// Simple chat screen for debugging
class ChatScreenDebug extends StatefulWidget {
  const ChatScreenDebug({super.key});

  @override
  State<ChatScreenDebug> createState() => _ChatScreenDebugState();
}

class _ChatScreenDebugState extends State<ChatScreenDebug> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatProvider>().checkConnection();
    });
  }

  @override
  Widget build(BuildContext context) {
    final chatProvider = context.watch<ChatProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('GLPI Assistant - Debug'),
        backgroundColor: Colors.blue,
      ),
      body: Column(
        children: [
          // Connection status
          Container(
            padding: const EdgeInsets.all(16),
            color: chatProvider.isConnected ? Colors.green : Colors.red,
            child: Row(
              children: [
                Icon(
                  chatProvider.isConnected ? Icons.check_circle : Icons.error,
                  color: Colors.white,
                ),
                const SizedBox(width: 8),
                Text(
                  chatProvider.isConnected ? 'Connected' : 'Disconnected',
                  style: const TextStyle(color: Colors.white),
                ),
              ],
            ),
          ),

          // Messages
          Expanded(
            child: chatProvider.messages.isEmpty
                ? const Center(
                    child: Text('No messages yet. Try sending one!'),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: chatProvider.messages.length,
                    itemBuilder: (context, index) {
                      final message = chatProvider.messages[index];
                      return Card(
                        color: message.isUser
                            ? Colors.blue[100]
                            : Colors.grey[200],
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Text(message.text),
                        ),
                      );
                    },
                  ),
          ),

          // Input
          if (chatProvider.isLoading)
            const LinearProgressIndicator()
          else
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(
                        hintText: 'Type a message...',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (text) {
                        if (text.isNotEmpty) {
                          chatProvider.sendMessage(text);
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
