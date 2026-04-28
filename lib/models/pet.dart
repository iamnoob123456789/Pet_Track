
class Pet {
  final String id;
  final String? name;
  final String breed;
  final String color;
  final String? size;
  final String? age;
  final String? gender;
  final String? description;
  final List<String> imageUrls;
  final List<double>? imageEmbeddings;
  final String? thumbnailUrl;
  final double latitude;
  final double longitude;
  final String? locationAddress;
  final String? locationCity;
  final String? locationState;
  final String? locationCountry;
  final String status; // "lost" or "found"
  final DateTime dateLostOrFound;
  final Map<String, dynamic> contactInfo;
  final String ownerId;
  final double? imageQualityScore;
  final bool isDuplicate;
  final String? duplicateOf;
  final int matchCount;
  final DateTime? lastMatched;
  final String? distinctiveFeatures;
  final String? medicalInfo;
  final String? behaviorTraits;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool isActive;

  Pet({
    required this.id,
    this.name,
    required this.breed,
    required this.color,
    this.size,
    this.age,
    this.gender,
    this.description,
    required this.imageUrls,
    this.imageEmbeddings,
    this.thumbnailUrl,
    required this.latitude,
    required this.longitude,
    this.locationAddress,
    this.locationCity,
    this.locationState,
    this.locationCountry,
    required this.status,
    required this.dateLostOrFound,
    required this.contactInfo,
    required this.ownerId,
    this.imageQualityScore,
    this.isDuplicate = false,
    this.duplicateOf,
    this.matchCount = 0,
    this.lastMatched,
    this.distinctiveFeatures,
    this.medicalInfo,
    this.behaviorTraits,
    required this.createdAt,
    required this.updatedAt,
    this.isActive = true,
  });

  factory Pet.fromJson(Map<String, dynamic> json) {
    return Pet(
      id: json['id'] as String,
      name: json['name'] as String?,
      breed: json['breed'] as String,
      color: json['color'] as String,
      size: json['size'] as String?,
      age: json['age'] as String?,
      gender: json['gender'] as String?,
      description: json['description'] as String?,
      imageUrls: List<String>.from(json['image_urls'] as List),
      imageEmbeddings: json['image_embeddings'] != null
          ? List<double>.from(json['image_embeddings'] as List)
          : null,
      thumbnailUrl: json['thumbnail_url'] as String?,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      locationAddress: json['location_address'] as String?,
      locationCity: json['location_city'] as String?,
      locationState: json['location_state'] as String?,
      locationCountry: json['location_country'] as String?,
      status: json['status'] as String,
      dateLostOrFound: DateTime.parse(json['date_lost_or_found'] as String),
      contactInfo: Map<String, dynamic>.from(json['contact_info'] as Map? ?? {}),
      ownerId: json['owner_id'] as String,
      imageQualityScore: json['image_quality_score'] as double?,
      isDuplicate: json['is_duplicate'] as bool? ?? false,
      duplicateOf: json['duplicate_of'] as String?,
      matchCount: json['match_count'] as int? ?? 0,
      lastMatched: json['last_matched'] != null
          ? DateTime.parse(json['last_matched'] as String)
          : null,
      distinctiveFeatures: json['distinctive_features'] as String?,
      medicalInfo: json['medical_info'] as String?,
      behaviorTraits: json['behavior_traits'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'breed': breed,
      'color': color,
      'size': size,
      'age': age,
      'gender': gender,
      'description': description,
      'image_urls': imageUrls,
      'image_embeddings': imageEmbeddings,
      'thumbnail_url': thumbnailUrl,
      'latitude': latitude,
      'longitude': longitude,
      'location_address': locationAddress,
      'location_city': locationCity,
      'location_state': locationState,
      'location_country': locationCountry,
      'status': status,
      'date_lost_or_found': dateLostOrFound.toIso8601String(),
      'contact_info': contactInfo,
      'owner_id': ownerId,
      'image_quality_score': imageQualityScore,
      'is_duplicate': isDuplicate,
      'duplicate_of': duplicateOf,
      'match_count': matchCount,
      'last_matched': lastMatched?.toIso8601String(),
      'distinctive_features': distinctiveFeatures,
      'medical_info': medicalInfo,
      'behavior_traits': behaviorTraits,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'is_active': isActive,
    };
  }

  Pet copyWith({
    String? id,
    String? name,
    String? breed,
    String? color,
    String? size,
    String? age,
    String? gender,
    String? description,
    List<String>? imageUrls,
    List<double>? imageEmbeddings,
    String? thumbnailUrl,
    double? latitude,
    double? longitude,
    String? locationAddress,
    String? locationCity,
    String? locationState,
    String? locationCountry,
    String? status,
    DateTime? dateLostOrFound,
    Map<String, dynamic>? contactInfo,
    String? ownerId,
    double? imageQualityScore,
    bool? isDuplicate,
    String? duplicateOf,
    int? matchCount,
    DateTime? lastMatched,
    String? distinctiveFeatures,
    String? medicalInfo,
    String? behaviorTraits,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isActive,
  }) {
    return Pet(
      id: id ?? this.id,
      name: name ?? this.name,
      breed: breed ?? this.breed,
      color: color ?? this.color,
      size: size ?? this.size,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      description: description ?? this.description,
      imageUrls: imageUrls ?? this.imageUrls,
      imageEmbeddings: imageEmbeddings ?? this.imageEmbeddings,
      thumbnailUrl: thumbnailUrl ?? this.thumbnailUrl,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      locationAddress: locationAddress ?? this.locationAddress,
      locationCity: locationCity ?? this.locationCity,
      locationState: locationState ?? this.locationState,
      locationCountry: locationCountry ?? this.locationCountry,
      status: status ?? this.status,
      dateLostOrFound: dateLostOrFound ?? this.dateLostOrFound,
      contactInfo: contactInfo ?? this.contactInfo,
      ownerId: ownerId ?? this.ownerId,
      imageQualityScore: imageQualityScore ?? this.imageQualityScore,
      isDuplicate: isDuplicate ?? this.isDuplicate,
      duplicateOf: duplicateOf ?? this.duplicateOf,
      matchCount: matchCount ?? this.matchCount,
      lastMatched: lastMatched ?? this.lastMatched,
      distinctiveFeatures: distinctiveFeatures ?? this.distinctiveFeatures,
      medicalInfo: medicalInfo ?? this.medicalInfo,
      behaviorTraits: behaviorTraits ?? this.behaviorTraits,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Pet &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'Pet{id: $id, name: $name, breed: $breed, status: $status}';
  }
}

class PetCreate {
  final String? name;
  final String breed;
  final String color;
  final String? size;
  final String? age;
  final String? gender;
  final String? description;
  final List<String> imageUrls;
  final double latitude;
  final double longitude;
  final String? locationAddress;
  final String? locationCity;
  final String? locationState;
  final String? locationCountry;
  final String status;
  final DateTime? dateLostOrFound;
  final Map<String, dynamic> contactInfo;
  final String? distinctiveFeatures;
  final String? medicalInfo;
  final String? behaviorTraits;

  PetCreate({
    this.name,
    required this.breed,
    required this.color,
    this.size,
    this.age,
    this.gender,
    this.description,
    required this.imageUrls,
    required this.latitude,
    required this.longitude,
    this.locationAddress,
    this.locationCity,
    this.locationState,
    this.locationCountry,
    required this.status,
    this.dateLostOrFound,
    this.contactInfo = const {},
    this.distinctiveFeatures,
    this.medicalInfo,
    this.behaviorTraits,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'breed': breed,
      'color': color,
      'size': size,
      'age': age,
      'gender': gender,
      'description': description,
      'image_urls': imageUrls,
      'latitude': latitude,
      'longitude': longitude,
      'location_address': locationAddress,
      'location_city': locationCity,
      'location_state': locationState,
      'location_country': locationCountry,
      'status': status,
      'date_lost_or_found': dateLostOrFound?.toIso8601String(),
      'contact_info': contactInfo,
      'distinctive_features': distinctiveFeatures,
      'medical_info': medicalInfo,
      'behavior_traits': behaviorTraits,
    };
  }
}

class PetUpdate {
  final String? name;
  final String? breed;
  final String? color;
  final String? size;
  final String? age;
  final String? gender;
  final String? description;
  final List<String>? imageUrls;
  final double? latitude;
  final double? longitude;
  final String? locationAddress;
  final String? locationCity;
  final String? locationState;
  final String? locationCountry;
  final String? status;
  final Map<String, dynamic>? contactInfo;
  final String? distinctiveFeatures;
  final String? medicalInfo;
  final String? behaviorTraits;
  final bool? isActive;

  PetUpdate({
    this.name,
    this.breed,
    this.color,
    this.size,
    this.age,
    this.gender,
    this.description,
    this.imageUrls,
    this.latitude,
    this.longitude,
    this.locationAddress,
    this.locationCity,
    this.locationState,
    this.locationCountry,
    this.status,
    this.contactInfo,
    this.distinctiveFeatures,
    this.medicalInfo,
    this.behaviorTraits,
    this.isActive,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    
    if (name != null) data['name'] = name;
    if (breed != null) data['breed'] = breed;
    if (color != null) data['color'] = color;
    if (size != null) data['size'] = size;
    if (age != null) data['age'] = age;
    if (gender != null) data['gender'] = gender;
    if (description != null) data['description'] = description;
    if (imageUrls != null) data['image_urls'] = imageUrls;
    if (latitude != null) data['latitude'] = latitude;
    if (longitude != null) data['longitude'] = longitude;
    if (locationAddress != null) data['location_address'] = locationAddress;
    if (locationCity != null) data['location_city'] = locationCity;
    if (locationState != null) data['location_state'] = locationState;
    if (locationCountry != null) data['location_country'] = locationCountry;
    if (status != null) data['status'] = status;
    if (contactInfo != null) data['contact_info'] = contactInfo;
    if (distinctiveFeatures != null) data['distinctive_features'] = distinctiveFeatures;
    if (medicalInfo != null) data['medical_info'] = medicalInfo;
    if (behaviorTraits != null) data['behavior_traits'] = behaviorTraits;
    if (isActive != null) data['is_active'] = isActive;
    
    return data;
  }
}
