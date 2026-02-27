import SwiftUI

/// Loading view while NB2 generates, then shows result
struct GenerationView: View {
    @EnvironmentObject var appState: AppState
    @State private var animationPhase: Double = 0

    var body: some View {
        VStack(spacing: 32) {
            if appState.isGenerating {
                loadingContent
            } else if let error = appState.errorMessage {
                errorContent(error)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
    }

    private var loadingContent: some View {
        VStack(spacing: 24) {
            if let sketch = appState.currentSketch {
                Image(uiImage: sketch)
                    .resizable().scaledToFit()
                    .frame(maxHeight: 300)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16).fill(
                            LinearGradient(colors: [.clear, appState.selectedStyle.accentColor.opacity(0.3), .clear],
                                           startPoint: .leading, endPoint: .trailing)
                        ).offset(x: animationPhase)
                    )
                    .clipped()
                    .onAppear {
                        withAnimation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true)) {
                            animationPhase = 200
                        }
                    }
            }
            VStack(spacing: 8) {
                ProgressView().scaleEffect(1.5)
                Text("Creating \(appState.selectedStyle.displayName)...").font(.title3).fontWeight(.medium)
                Text("This usually takes 10-20 seconds").font(.caption).foregroundColor(.secondary)
            }
        }.padding()
    }

    private func errorContent(_ message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle").font(.system(size: 48)).foregroundColor(.orange)
            Text("Oops!").font(.title2).fontWeight(.bold)
            Text(message).font(.body).foregroundColor(.secondary).multilineTextAlignment(.center).padding(.horizontal)
            HStack(spacing: 16) {
                Button("Try Again") { Task { await appState.generateArt() } }.buttonStyle(.borderedProminent)
                Button("Back to Drawing") {
                    appState.errorMessage = nil
                    appState.currentScreen = .canvas
                }.buttonStyle(.bordered)
            }
        }
    }
}

/// Shows the generated result with save/share options
struct ResultView: View {
    @EnvironmentObject var appState: AppState
    @State private var showOriginal = false
    @State private var savedToPhotos = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    if let result = appState.generatedImage {
                        Image(uiImage: result)
                            .resizable().scaledToFit()
                            .clipShape(RoundedRectangle(cornerRadius: 16))
                            .shadow(radius: 8)
                            .padding(.horizontal)
                    }

                    if showOriginal, let sketch = appState.currentSketch {
                        VStack(spacing: 8) {
                            Text("Your Drawing").font(.caption).foregroundColor(.secondary)
                            Image(uiImage: sketch)
                                .resizable().scaledToFit()
                                .frame(maxHeight: 200)
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                        }.padding(.horizontal)
                    }

                    Button {
                        withAnimation { showOriginal.toggle() }
                    } label: {
                        Label(showOriginal ? "Hide Original" : "Show Original",
                              systemImage: showOriginal ? "eye.slash" : "eye")
                    }.buttonStyle(.bordered)

                    HStack {
                        Image(systemName: appState.selectedStyle.icon)
                        Text(appState.selectedStyle.displayName)
                    }
                    .font(.subheadline)
                    .padding(.horizontal, 12).padding(.vertical, 6)
                    .background(appState.selectedStyle.accentColor.opacity(0.15))
                    .clipShape(Capsule())

                    // Actions
                    VStack(spacing: 12) {
                        Button {
                            appState.saveToCameraRoll()
                            savedToPhotos = true
                        } label: {
                            HStack {
                                Image(systemName: savedToPhotos ? "checkmark" : "square.and.arrow.down")
                                Text(savedToPhotos ? "Saved!" : "Save to Photos").fontWeight(.semibold)
                            }
                            .frame(maxWidth: .infinity).padding(.vertical, 14)
                            .background(savedToPhotos ? Color.green : Color.purple)
                            .foregroundColor(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                        }

                        HStack(spacing: 12) {
                            Button {
                                appState.currentScreen = .stylePicker
                            } label: {
                                HStack { Image(systemName: "paintpalette"); Text("Try Style") }
                                    .frame(maxWidth: .infinity).padding(.vertical, 14)
                                    .background(Color(.systemGray5)).foregroundColor(.primary)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                            Button {
                                appState.saveToGallery()
                                appState.newDrawing()
                            } label: {
                                HStack { Image(systemName: "pencil.tip"); Text("New Drawing") }
                                    .frame(maxWidth: .infinity).padding(.vertical, 14)
                                    .background(Color(.systemGray5)).foregroundColor(.primary)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                        }
                    }.padding(.horizontal)
                }.padding(.vertical)
            }
            .navigationTitle("Your Art!")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

/// Simple gallery of saved creations
struct GalleryView: View {
    @EnvironmentObject var appState: AppState
    private let columns = [GridItem(.adaptive(minimum: 150, maximum: 200), spacing: 12)]

    var body: some View {
        NavigationStack {
            Group {
                if appState.gallery.isEmpty {
                    ContentUnavailableView("No Creations Yet", systemImage: "paintpalette",
                                           description: Text("Your masterpieces will appear here"))
                } else {
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: 12) {
                            ForEach(appState.gallery) { creation in
                                Image(uiImage: creation.result)
                                    .resizable().scaledToFill()
                                    .frame(minHeight: 150)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                        }.padding()
                    }
                }
            }
            .navigationTitle("Gallery")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Back") { appState.currentScreen = .canvas }
                }
            }
        }
    }
}
