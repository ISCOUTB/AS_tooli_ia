import 'dart:html' as html;

/// SSO Helper for Web platform
class SSOHelper {
  /// Navigate to SSO login URL in the same window
  static void navigateToSSO(String ssoUrl) {
    html.window.location.href = ssoUrl;
  }
  
  /// Check if current URL has SSO callback parameters
  static Map<String, String>? getCallbackParameters() {
    final uri = Uri.parse(html.window.location.href);
    
    // Check if we're on the callback route
    if (!uri.path.contains('/auth/callback')) {
      return null;
    }
    
    // Return query parameters if they exist
    if (uri.queryParameters.isNotEmpty) {
      return uri.queryParameters;
    }
    
    return null;
  }
}
