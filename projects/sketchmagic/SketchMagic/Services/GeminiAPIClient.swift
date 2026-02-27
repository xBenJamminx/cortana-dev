import Foundation
import UIKit

/// Client for the Gemini API (Nano Banana 2) that transforms sketches into art.
/// MVP: API key embedded in app. Production: use a backend proxy.
final class GeminiAPIClient {

    static let shared = GeminiAPIClient()

    private let model = "gemini-3.1-flash-image-preview"
    private let baseURL = "https://generativelanguage.googleapis.com/v1beta/models"
    private let session: URLSession
    private let timeoutSeconds: TimeInterval = 60

    /// Set your API key here for MVP. In production, route through a backend proxy.
    var apiKey: String = "" // Set via Config.plist or Keychain in production

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = timeoutSeconds
        config.timeoutIntervalForResource = timeoutSeconds
        session = URLSession(configuration: config)
    }

    // MARK: - Public API

    /// Transforms a sketch into AI-generated art using the given style prompt.
    /// - Parameters:
    ///   - sketch: The user's drawing as a UIImage (will be sent as PNG).
    ///   - stylePrompt: The full prompt describing the desired art style transformation.
    /// - Returns: The generated UIImage from NB2.
    func transformSketch(_ sketch: UIImage, stylePrompt: String) async throws -> UIImage {
        guard !apiKey.isEmpty else {
            throw GeminiError.missingAPIKey
        }

        guard let pngData = sketch.pngData() else {
            throw GeminiError.imageEncodingFailed
        }

        let base64Image = pngData.base64EncodedString()
        let request = try buildRequest(base64Image: base64Image, prompt: stylePrompt)
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw GeminiError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let body = String(data: data, encoding: .utf8) ?? "No body"
            throw GeminiError.apiError(statusCode: httpResponse.statusCode, message: body)
        }

        return try parseImageFromResponse(data)
    }

    // MARK: - Request Building

    private func buildRequest(base64Image: String, prompt: String) throws -> URLRequest {
        let endpoint = "\(baseURL)/\(model):generateContent?key=\(apiKey)"

        guard let url = URL(string: endpoint) else {
            throw GeminiError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "contents": [
                [
                    "parts": [
                        [
                            "inline_data": [
                                "mime_type": "image/png",
                                "data": base64Image
                            ]
                        ],
                        [
                            "text": prompt
                        ]
                    ]
                ]
            ],
            "generationConfig": [
                "responseModalities": ["IMAGE", "TEXT"],
                "candidateCount": 1
            ]
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        return request
    }

    // MARK: - Response Parsing

    /// Parses the generated image from the Gemini API response.
    /// Response structure: candidates[0].content.parts[] -> find part with inline_data.mime_type starting with "image/"
    private func parseImageFromResponse(_ data: Data) throws -> UIImage {
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let candidates = json["candidates"] as? [[String: Any]],
              let firstCandidate = candidates.first,
              let content = firstCandidate["content"] as? [String: Any],
              let parts = content["parts"] as? [[String: Any]] else {
            throw GeminiError.parseError("Could not parse response structure")
        }

        // Find the image part in the response
        for part in parts {
            if let inlineData = part["inline_data"] as? [String: Any],
               let mimeType = inlineData["mime_type"] as? String,
               mimeType.hasPrefix("image/"),
               let base64String = inlineData["data"] as? String,
               let imageData = Data(base64Encoded: base64String),
               let image = UIImage(data: imageData) {
                return image
            }
        }

        // No image found - check for text error message
        let textParts = parts.compactMap { $0["text"] as? String }
        let errorMessage = textParts.joined(separator: " ")
        throw GeminiError.noImageInResponse(textResponse: errorMessage)
    }
}

// MARK: - Error Types

enum GeminiError: LocalizedError {
    case missingAPIKey
    case imageEncodingFailed
    case invalidURL
    case invalidResponse
    case apiError(statusCode: Int, message: String)
    case parseError(String)
    case noImageInResponse(textResponse: String)

    var errorDescription: String? {
        switch self {
        case .missingAPIKey:
            return "API key is not set. Please add your Gemini API key."
        case .imageEncodingFailed:
            return "Could not encode your drawing. Please try again."
        case .invalidURL:
            return "Invalid API endpoint URL."
        case .invalidResponse:
            return "Received an invalid response from the server."
        case .apiError(let code, let message):
            return "API error (\(code)): \(message)"
        case .parseError(let detail):
            return "Could not parse the response: \(detail)"
        case .noImageInResponse(let text):
            return "No image was generated. Server said: \(text.prefix(200))"
        }
    }
}
