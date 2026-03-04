import SwiftUI
import Photos

/// Central app state managing navigation, sketch data, and generation lifecycle.
@MainActor
final class AppState: ObservableObject {

    enum Screen {
        case canvas
        case stylePicker
        case generating
        case result
        case gallery
    }

    // MARK: - Navigation

    @Published var currentScreen: Screen = .canvas

    // MARK: - Sketch & Generation

    @Published var currentSketch: UIImage?
    @Published var selectedStyle: ArtStyle = .watercolor
    @Published var generatedImage: UIImage?
    @Published var isGenerating = false
    @Published var errorMessage: String?

    // MARK: - Gallery

    @Published var gallery: [Creation] = []

    // MARK: - Actions

    /// Calls the Gemini API to transform the current sketch with the selected style.
    func generateArt() async {
        guard let sketch = currentSketch else {
            errorMessage = "No sketch to transform."
            return
        }

        isGenerating = true
        errorMessage = nil
        generatedImage = nil
        currentScreen = .generating

        do {
            let result = try await GeminiAPIClient.shared.transformSketch(
                sketch,
                stylePrompt: selectedStyle.promptTemplate
            )
            generatedImage = result
            isGenerating = false
            currentScreen = .result
        } catch {
            isGenerating = false
            errorMessage = error.localizedDescription
        }
    }

    /// Saves the generated image to the device's photo library.
    func saveToCameraRoll() {
        guard let image = generatedImage else { return }
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized else { return }
            UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil)
        }
    }

    /// Saves the current sketch + generated image pair to the in-memory gallery.
    func saveToGallery() {
        guard let sketch = currentSketch, let result = generatedImage else { return }
        let creation = Creation(
            sketch: sketch,
            result: result,
            style: selectedStyle
        )
        gallery.insert(creation, at: 0)
    }

    /// Resets state for a new drawing.
    func newDrawing() {
        currentSketch = nil
        generatedImage = nil
        errorMessage = nil
        selectedStyle = .watercolor
        currentScreen = .canvas
    }
}

// MARK: - Gallery Item

struct Creation: Identifiable {
    let id = UUID()
    let sketch: UIImage
    let result: UIImage
    let style: ArtStyle
    let date = Date()
}
