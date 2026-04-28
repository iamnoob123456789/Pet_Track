import 'pet.dart';

class Match {
  final String id;
  final String lostPetId;
  final String foundPetId;
  final double matchScore;
  final double imageSimilarityScore;
  final double metadataSimilarityScore;
  final double locationSimilarityScore;
  final double hybridScore;
  final bool breedMatch;
  final bool colorMatch;
  final bool sizeMatch;
  final double distanceKm;
  final String status; // pending, reviewed, confirmed, rejected
  final String? reviewedBy;
  final DateTime? reviewedAt;
  final String? confirmedBy;
  final DateTime? confirmedAt;
  final bool contactInitiated;
  final String? contactInitiatedBy;
  final DateTime? contactInitiatedAt;
  final DateTime createdAt;
  final DateTime updatedAt;

  Match({
    required this.id,
    required this.lostPetId,
    required this.foundPetId,
    required this.matchScore,
    required this.imageSimilarityScore,
    required this.metadataSimilarityScore,
    required this.locationSimilarityScore,
    required this.hybridScore,
    required this.breedMatch,
    required this.colorMatch,
    required this.sizeMatch,
    required this.distanceKm,
    required this.status,
    this.reviewedBy,
    this.reviewedAt,
    this.confirmedBy,
    this.confirmedAt,
    this.contactInitiated = false,
    this.contactInitiatedBy,
    this.contactInitiatedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Match.fromJson(Map<String, dynamic> json) {
    return Match(
      id: json['id'] as String,
      lostPetId: json['lost_pet_id'] as String,
      foundPetId: json['found_pet_id'] as String,
      matchScore: (json['match_score'] as num).toDouble(),
      imageSimilarityScore: (json['image_similarity_score'] as num).toDouble(),
      metadataSimilarityScore: (json['metadata_similarity_score'] as num).toDouble(),
      locationSimilarityScore: (json['location_similarity_score'] as num).toDouble(),
      hybridScore: (json['hybrid_score'] as num).toDouble(),
      breedMatch: json['breed_match'] as bool,
      colorMatch: json['color_match'] as bool,
      sizeMatch: json['size_match'] as bool,
      distanceKm: (json['distance_km'] as num).toDouble(),
      status: json['status'] as String,
      reviewedBy: json['reviewed_by'] as String?,
      reviewedAt: json['reviewed_at'] != null
          ? DateTime.parse(json['reviewed_at'] as String)
          : null,
      confirmedBy: json['confirmed_by'] as String?,
      confirmedAt: json['confirmed_at'] != null
          ? DateTime.parse(json['confirmed_at'] as String)
          : null,
      contactInitiated: json['contact_initiated'] as bool? ?? false,
      contactInitiatedBy: json['contact_initiated_by'] as String?,
      contactInitiatedAt: json['contact_initiated_at'] != null
          ? DateTime.parse(json['contact_initiated_at'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'lost_pet_id': lostPetId,
      'found_pet_id': foundPetId,
      'match_score': matchScore,
      'image_similarity_score': imageSimilarityScore,
      'metadata_similarity_score': metadataSimilarityScore,
      'location_similarity_score': locationSimilarityScore,
      'hybrid_score': hybridScore,
      'breed_match': breedMatch,
      'color_match': colorMatch,
      'size_match': sizeMatch,
      'distance_km': distanceKm,
      'status': status,
      'reviewed_by': reviewedBy,
      'reviewed_at': reviewedAt?.toIso8601String(),
      'confirmed_by': confirmedBy,
      'confirmed_at': confirmedAt?.toIso8601String(),
      'contact_initiated': contactInitiated,
      'contact_initiated_by': contactInitiatedBy,
      'contact_initiated_at': contactInitiatedAt?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Match copyWith({
    String? id,
    String? lostPetId,
    String? foundPetId,
    double? matchScore,
    double? imageSimilarityScore,
    double? metadataSimilarityScore,
    double? locationSimilarityScore,
    double? hybridScore,
    bool? breedMatch,
    bool? colorMatch,
    bool? sizeMatch,
    double? distanceKm,
    String? status,
    String? reviewedBy,
    DateTime? reviewedAt,
    String? confirmedBy,
    DateTime? confirmedAt,
    bool? contactInitiated,
    String? contactInitiatedBy,
    DateTime? contactInitiatedAt,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Match(
      id: id ?? this.id,
      lostPetId: lostPetId ?? this.lostPetId,
      foundPetId: foundPetId ?? this.foundPetId,
      matchScore: matchScore ?? this.matchScore,
      imageSimilarityScore: imageSimilarityScore ?? this.imageSimilarityScore,
      metadataSimilarityScore: metadataSimilarityScore ?? this.metadataSimilarityScore,
      locationSimilarityScore: locationSimilarityScore ?? this.locationSimilarityScore,
      hybridScore: hybridScore ?? this.hybridScore,
      breedMatch: breedMatch ?? this.breedMatch,
      colorMatch: colorMatch ?? this.colorMatch,
      sizeMatch: sizeMatch ?? this.sizeMatch,
      distanceKm: distanceKm ?? this.distanceKm,
      status: status ?? this.status,
      reviewedBy: reviewedBy ?? this.reviewedBy,
      reviewedAt: reviewedAt ?? this.reviewedAt,
      confirmedBy: confirmedBy ?? this.confirmedBy,
      confirmedAt: confirmedAt ?? this.confirmedAt,
      contactInitiated: contactInitiated ?? this.contactInitiated,
      contactInitiatedBy: contactInitiatedBy ?? this.contactInitiatedBy,
      contactInitiatedAt: contactInitiatedAt ?? this.contactInitiatedAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Match &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'Match{id: $id, lostPetId: $lostPetId, foundPetId: $foundPetId, hybridScore: $hybridScore}';
  }
}

class MatchResult {
  final String petId;
  final Pet pet;
  final SimilarityResult similarity;

  MatchResult({
    required this.petId,
    required this.pet,
    required this.similarity,
  });

  factory MatchResult.fromJson(Map<String, dynamic> json) {
    return MatchResult(
      petId: json['pet_id'] as String,
      pet: Pet.fromJson(json['pet'] as Map<String, dynamic>),
      similarity: SimilarityResult.fromJson(json['similarity'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'pet_id': petId,
      'pet': pet.toJson(),
      'similarity': similarity.toJson(),
    };
  }
}

class SimilarityResult {
  final double imageSimilarity;
  final double metadataSimilarity;
  final double locationSimilarity;
  final double hybridScore;
  final Map<String, dynamic> details;

  SimilarityResult({
    required this.imageSimilarity,
    required this.metadataSimilarity,
    required this.locationSimilarity,
    required this.hybridScore,
    required this.details,
  });

  factory SimilarityResult.fromJson(Map<String, dynamic> json) {
    return SimilarityResult(
      imageSimilarity: (json['image_similarity'] as num).toDouble(),
      metadataSimilarity: (json['metadata_similarity'] as num).toDouble(),
      locationSimilarity: (json['location_similarity'] as num).toDouble(),
      hybridScore: (json['hybrid_score'] as num).toDouble(),
      details: Map<String, dynamic>.from(json['details'] as Map? ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'image_similarity': imageSimilarity,
      'metadata_similarity': metadataSimilarity,
      'location_similarity': locationSimilarity,
      'hybrid_score': hybridScore,
      'details': details,
    };
  }

  double get matchPercentage => hybridScore * 100;

  String get matchPercentageText => '${(matchPercentage).toStringAsFixed(1)}%';
}
