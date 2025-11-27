import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../widgets/message_bubble.dart';
import '../widgets/suggestions_panel.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    // Verificar conexión al iniciar (en modo silencioso para no ocultar el panel)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatProvider>().checkConnection(silent: true);
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    final text = _messageController.text;
    if (text.trim().isEmpty) return;

    // El provider manejará ocultar el panel de bienvenida
    context.read<ChatProvider>().sendMessage(text);
    _messageController.clear();

    // Scroll al final
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.support_agent, color: Colors.blue),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Tooli',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Agente Inteligente GLPI',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.normal),
                ),
              ],
            ),
          ],
        ),
        actions: [
          Consumer<ChatProvider>(
            builder: (context, provider, _) {
              return Icon(
                provider.isConnected
                    ? Icons.check_circle
                    : Icons.error_outline,
                color: provider.isConnected ? Colors.green : Colors.red,
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              // El provider manejará mostrar el panel de bienvenida
              await context.read<ChatProvider>().clearChat();
            },
          ),
        ],
        backgroundColor: Colors.blue[700],
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Lista de mensajes o panel de bienvenida
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, provider, _) {
                // Mostrar panel de sugerencias cuando debe mostrarse
                if (provider.showWelcomePanel && provider.messages.isEmpty) {
                  return SuggestionsPanel(
                    onSuggestionTap: (suggestion) {
                      _messageController.text = suggestion;
                      _sendMessage();
                    },
                  );
                }

                // Si no hay mensajes y no se debe mostrar el panel, mostrar mensaje de espera
                if (provider.messages.isEmpty) {
                  return const Center(
                    child: Text(
                      'Esperando respuesta...',
                      style: TextStyle(color: Colors.grey),
                    ),
                  );
                }

                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(8),
                  itemCount: provider.messages.length,
                  itemBuilder: (context, index) {
                    return MessageBubble(message: provider.messages[index]);
                  },
                );
              },
            ),
          ),

          // Indicador de carga
          Consumer<ChatProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading) {
                return Container(
                  padding: const EdgeInsets.all(8),
                  child: Row(
                    children: [
                      SpinKitThreeBounce(
                        color: Colors.blue[600]!,
                        size: 20.0,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'Tooli está pensando...',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                );
              }
              return const SizedBox.shrink();
            },
          ),

          // Input de mensaje
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.1),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    onSubmitted: (_) => _sendMessage(),
                    textInputAction: TextInputAction.send,
                    decoration: InputDecoration(
                      hintText: '¿Qué tickets disponibles hay?',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.grey[200],
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 10,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Consumer<ChatProvider>(
                  builder: (context, provider, _) {
                    return FloatingActionButton(
                      onPressed: provider.isLoading ? null : _sendMessage,
                      backgroundColor: Colors.blue[600],
                      child: const Icon(Icons.send, color: Colors.white),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
