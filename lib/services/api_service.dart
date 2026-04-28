import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../config.dart';
import '../models/user.dart';
import '../models/pet.dart';
import '../models/match.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  static const String _baseUrl = Config.apiBaseUrl;
  
  // Auth headers
  Map<String, String> _getHeaders({bool includeAuth = true}) {
    final Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (includeAuth) {
      headers['Authorization'] = 'Bearer ${_storage.read(key: 'access_token')}';
    }

    return headers;
  }

  // Generic HTTP methods
  Future<http.Response> _get(String endpoint, {bool includeAuth = true}) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    return await http.get(uri, headers: _getHeaders(includeAuth: includeAuth));
  }

  Future<http.Response> _post(String endpoint, {dynamic body, bool includeAuth = true}) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    return await http.post(
      uri,
      headers: _getHeaders(includeAuth: includeAuth),
      body: body != null ? jsonEncode(body) : null,
    );
  }

  Future<http.Response> _put(String endpoint, {dynamic body, bool includeAuth = true}) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    return await http.put(
      uri,
      headers: _getHeaders(includeAuth: includeAuth),
      body: body != null ? jsonEncode(body) : null,
    );
  }

  Future<http.Response> _delete(String endpoint, {bool includeAuth = true}) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    return await http.delete(uri, headers: _getHeaders(includeAuth: includeAuth));
  }

  // Error handling
  Exception _handleError(http.Response response) {
    String message = 'An error occurred';
    
    try {
      final body = jsonDecode(response.body);
      message = body['detail'] ?? message;
    } catch (e) {
      message = 'Server error: ${response.statusCode}';
    }

    return Exception(message);
  }

  // Authentication
  Future<AuthResponse> login(String email, String password) async {
    try {
      final response = await _post(
        '/auth/login',
        body: {'email': email, 'password': password},
        includeAuth: false,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final authResponse = AuthResponse.fromJson(data);
        
        // Store token
        await _storage.write(key: 'access_token', value: authResponse.accessToken);
        
        return authResponse;
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }

  Future<User> register(String email, String username, String password, {String? fullName, String? phone}) async {
    try {
      final response = await _post(
        '/auth/register',
        body: {
          'email': email,
          'username': username,
          'password': password,
          'full_name': fullName,
          'phone': phone,
        },
        includeAuth: false,
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return User.fromJson(data);
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Registration failed: $e');
    }
  }

  Future<User> getCurrentUser() async {
    try {
      final response = await _get('/auth/me');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return User.fromJson(data);
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to get current user: $e');
    }
  }

  Future<void> logout() async {
    try {
      await _post('/auth/logout');
      await _storage.delete(key: 'access_token');
    } catch (e) {
      // Even if the API call fails, remove the local token
      await _storage.delete(key: 'access_token');
    }
  }

  Future<bool> isTokenValid() async {
    try {
      final token = await _storage.read(key: 'access_token');
      if (token == null) return false;
      
      // Check if token is expired
      return !JwtDecoder.isExpired(token);
    } catch (e) {
      return false;
    }
  }

  // Pets
  Future<Pet> createPet(PetCreate petCreate) async {
    try {
      final response = await _post('/pets/', body: petCreate.toJson());
      
      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return Pet.fromJson(data);
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to create pet: $e');
    }
  }

  Future<List<Pet>> getPets({
    String? status,
    String? breed,
    String? color,
    String? location,
    double? radiusKm,
    double? latitude,
    double? longitude,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final queryParams = <String, String>{
        'skip': skip.toString(),
        'limit': limit.toString(),
      };

      if (status != null) queryParams['status'] = status;
      if (breed != null) queryParams['breed'] = breed;
      if (color != null) queryParams['color'] = color;
      if (location != null) queryParams['location'] = location;
      if (radiusKm != null) queryParams['radius_km'] = radiusKm.toString();
      if (latitude != null) queryParams['latitude'] = latitude.toString();
      if (longitude != null) queryParams['longitude'] = longitude.toString();

      final uri = Uri.parse('$_baseUrl/pets/').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: _getHeaders());
      
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Pet.fromJson(json)).toList();
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to get pets: $e');
    }
  }

  Future<Pet> getPet(String petId) async {
    try {
      final response = await _get('/pets/$petId');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return Pet.fromJson(data);
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to get pet: $e');
    }
  }

  Future<Pet> updatePet(String petId, PetUpdate petUpdate) async {
    try {
      final response = await _put('/pets/$petId', body: petUpdate.toJson());
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return Pet.fromJson(data);
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to update pet: $e');
    }
  }

  Future<void> deletePet(String petId) async {
    try {
      final response = await _delete('/pets/$petId');
      
      if (response.statusCode != 200) {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to delete pet: $e');
    }
  }

  Future<List<MatchResult>> findMatches(String petId, {int topK = 5}) async {
    try {
      final response = await _post('/pets/$petId/matches', body: {'top_k': topK});
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> matches = data['matches'];
        return matches.map((json) => MatchResult.fromJson(json)).toList();
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to find matches: $e');
    }
  }

  // Matches
  Future<List<Match>> getMatches({
    String? status,
    double? minScore,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final queryParams = <String, String>{
        'skip': skip.toString(),
        'limit': limit.toString(),
      };

      if (status != null) queryParams['status'] = status;
      if (minScore != null) queryParams['min_score'] = minScore.toString();

      final uri = Uri.parse('$_baseUrl/matches/').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: _getHeaders());
      
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Match.fromJson(json)).toList();
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to get matches: $e');
    }
  }

  Future<Match> getMatch(String matchId) async {
    try {
      final response = await _get('/matches/$matchId');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return Match.fromJson(data);
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to get match: $e');
    }
  }

  Future<void> reviewMatch(String matchId, String action) async {
    try {
      final response = await _post('/matches/$matchId/review', body: null);
      
      if (response.statusCode != 200) {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to review match: $e');
    }
  }

  // File upload
  Future<String> uploadImage(File imageFile) async {
    try {
      final uri = Uri.parse('$_baseUrl/upload/image');
      final request = http.MultipartRequest('POST', uri);
      
      // Add auth header
      final token = await _storage.read(key: 'access_token');
      if (token != null) {
        request.headers['Authorization'] = 'Bearer $token';
      }
      
      // Add image file
      final imageBytes = await imageFile.readAsBytes();
      final multipartFile = http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: imageFile.path.split('/').last,
      );
      request.files.add(multipartFile);
      
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['image_url'] as String;
      } else {
        throw _handleError(response);
      }
    } catch (e) {
      throw Exception('Failed to upload image: $e');
    }
  }

  // Utility methods
  Future<void> clearStoredData() async {
    await _storage.deleteAll();
  }

  Future<String?> getStoredToken() async {
    return await _storage.read(key: 'access_token');
  }
}
