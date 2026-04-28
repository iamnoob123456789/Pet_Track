import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/foundation.dart' show Platform;

class Config {
  // Backend API configuration
  static String get apiBaseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000';
    } else if (Platform.isAndroid) {
      // Use your laptop's Wi-Fi IP here when testing on a real device
      return 'http://10.96.249.119:8000';
    } else if (Platform.isIOS) {
      return 'http://localhost:8000';
    } else {
      return 'http://localhost:8000';
    }
  }

  // Legacy support
  static String get backendUrl => apiBaseUrl;

  // Image upload configuration
  static const String cloudinaryUrl =
      'https://api.cloudinary.com/v1_1/dslut5epx/image/upload';
  static const String cloudinaryUploadPreset = 'pettrack_preset';

  // App configuration
  static const String appName = 'Pet-Track';
  static const String appVersion = '2.0.0';
  
  // API endpoints
  static const String authEndpoint = '/auth';
  static const String petsEndpoint = '/pets';
  static const String matchesEndpoint = '/matches';
  static const String contactsEndpoint = '/contacts';
  static const String notificationsEndpoint = '/notifications';
  
  // Pagination defaults
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // Image upload limits
  static const int maxImageSizeBytes = 5 * 1024 * 1024; // 5MB
  static const List<String> supportedImageFormats = ['jpg', 'jpeg', 'png', 'webp'];
  
  // Matching configuration
  static const double defaultMatchThreshold = 0.6;
  static const int defaultTopKMatches = 5;
  static const double defaultSearchRadiusKm = 10.0;
}
