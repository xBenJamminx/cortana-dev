import SwiftUI
import SwiftData

@main
struct SketchMagicApp: App {

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: Artwork.self)
    }
}

// MARK: - Root Navigation

struct ContentView: View {
    enum Screen {
        case canvas
        case gallery
    }

    @State private var currentScreen: Screen = .canvas
    @State private var sketchImage: UIImage?
    @State private var selectedStyle: ArtStyle?
    @State private var showStylePicker = false
    @State private var showGeneration = false

    var body: some View {
        NavigationStack {
            Group {
                switch currentScreen {
                case .canvas:
                    CanvasView(
                        onTransform: { image in
                            sketchImage = image
                            showStylePicker = true
                        },
                        onGallery: {
                            currentScreen = .gallery
                        }
                    )
                case .gallery:
                    GalleryView(
                        onBack: {
                            currentScreen = .canvas
                        }
                    )
                }
            }
            .sheet(isPresented: $showStylePicker) {
                StylePickerView(
                    sketchImage: sketchImage,
                    onSelect: { style in
                        selectedStyle = style
                        showStylePicker = false
                        showGeneration = true
                    }
                )
                .presentationDetents([.medium, .large])
            }
            .fullScreenCover(isPresented: $showGeneration) {
                if let sketch = sketchImage, let style = selectedStyle {
                    GenerationView(
                        sketchImage: sketch,
                        style: style,
                        onDone: {
                            showGeneration = false
                        },
                        onTryAnother: {
                            showGeneration = false
                            showStylePicker = true
                        }
                    )
                }
            }
        }
    }
}

// MARK: - SwiftData Model

@Model
final class Artwork {
    var id: UUID
    @Attribute(.externalStorage) var sketchData: Data
    @Attribute(.externalStorage) var generatedData: Data
    var styleName: String
    var createdAt: Date
    var isFavorite: Bool

    init(sketchData: Data, generatedData: Data, styleName: String) {
        self.id = UUID()
        self.sketchData = sketchData
        self.generatedData = generatedData
        self.styleName = styleName
        self.createdAt = Date()
        self.isFavorite = false
    }
}

// MARK: - Gallery (Placeholder)

struct GalleryView: View {
    let onBack: () -> Void

    @Query(sort: \Artwork.createdAt, order: .reverse) private var artworks: [Artwork]

    var body: some View {
        Group {
            if artworks.isEmpty {
                VStack(spacing: 16) {
                    Text("\u{1F3A8}")
                        .font(.system(size: 80))
                    Text("No art yet!")
                        .font(.title2.bold())
                    Text("Start drawing to create your first masterpiece.")
                        .foregroundStyle(.secondary)
                }
            } else {
                ScrollView {
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 8) {
                        ForEach(artworks) { artwork in
                            if let image = UIImage(data: artwork.generatedData) {
                                Image(uiImage: image)
                                    .resizable()
                                    .aspectRatio(1, contentMode: .fill)
                                    .clipped()
                                    .cornerRadius(8)
                            }
                        }
                    }
                    .padding()
                }
            }
        }
        .navigationTitle("My Gallery")
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Back") { onBack() }
            }
        }
    }
}
