class User {
  final String id;
  final String email;
  final String username;
  final String? fullName;
  final String? phone;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? lastLogin;
  final NotificationPreferences notificationPreferences;

  User({
    required this.id,
    required this.email,
    required this.username,
    this.fullName,
    this.phone,
    required this.isActive,
    required this.createdAt,
    this.lastLogin,
    required this.notificationPreferences,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      phone: json['phone'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      lastLogin: json['last_login'] != null 
          ? DateTime.parse(json['last_login'] as String) 
          : null,
      notificationPreferences: NotificationPreferences.fromJson(
        json['notification_preferences'] as Map<String, dynamic>? ?? {}
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'full_name': fullName,
      'phone': phone,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
      'notification_preferences': notificationPreferences.toJson(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? username,
    String? fullName,
    String? phone,
    bool? isActive,
    DateTime? createdAt,
    DateTime? lastLogin,
    NotificationPreferences? notificationPreferences,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      username: username ?? this.username,
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      lastLogin: lastLogin ?? this.lastLogin,
      notificationPreferences: notificationPreferences ?? this.notificationPreferences,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is User &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'User{id: $id, email: $email, username: $username, fullName: $fullName}';
  }
}

class NotificationPreferences {
  final bool emailNotifications;
  final bool inAppNotifications;
  final bool matchAlerts;

  NotificationPreferences({
    required this.emailNotifications,
    required this.inAppNotifications,
    required this.matchAlerts,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      emailNotifications: json['email_notifications'] as bool? ?? true,
      inAppNotifications: json['in_app_notifications'] as bool? ?? true,
      matchAlerts: json['match_alerts'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'email_notifications': emailNotifications,
      'in_app_notifications': inAppNotifications,
      'match_alerts': matchAlerts,
    };
  }

  NotificationPreferences copyWith({
    bool? emailNotifications,
    bool? inAppNotifications,
    bool? matchAlerts,
  }) {
    return NotificationPreferences(
      emailNotifications: emailNotifications ?? this.emailNotifications,
      inAppNotifications: inAppNotifications ?? this.inAppNotifications,
      matchAlerts: matchAlerts ?? this.matchAlerts,
    );
  }
}

class UserCreate {
  final String email;
  final String username;
  final String password;
  final String? fullName;
  final String? phone;

  UserCreate({
    required this.email,
    required this.username,
    required this.password,
    this.fullName,
    this.phone,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'username': username,
      'password': password,
      'full_name': fullName,
      'phone': phone,
    };
  }
}

class UserLogin {
  final String email;
  final String password;

  UserLogin({
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
    };
  }
}

class AuthResponse {
  final String accessToken;
  final String tokenType;
  final User user;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String,
      user: User.fromJson(json['user'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'user': user.toJson(),
    };
  }
}
