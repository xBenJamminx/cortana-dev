import SwiftUI
import PencilKit

/// Main drawing canvas using PencilKit
struct CanvasView: View {
    @EnvironmentObject var appState: AppState
    @State private var canvasView = PKCanvasView()

    var body: some View {
        NavigationStack {
            ZStack {
                CanvasRepresentable(canvasView: $canvasView)
                    .ignoresSafeArea(edges: .bottom)

                VStack {
                    Spacer()
                    bottomToolbar
                }
            }
            .navigationTitle("SketchMagic")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        appState.currentScreen = .gallery
                    } label: {
                        Image(systemName: "photo.on.rectangle")
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Clear") {
                        canvasView.drawing = PKDrawing()
                    }
                }
            }
        }
    }

    private var bottomToolbar: some View {
        HStack(spacing: 20) {
            Button { canvasView.undoManager?.undo() } label: {
                Image(systemName: "arrow.uturn.backward").font(.title2)
            }
            Button { canvasView.undoManager?.redo() } label: {
                Image(systemName: "arrow.uturn.forward").font(.title2)
            }
            Spacer()
            Button {
                let image = canvasView.drawing.image(from: canvasView.bounds, scale: UIScreen.main.scale)
                appState.currentSketch = image
                appState.currentScreen = .stylePicker
            } label: {
                HStack {
                    Image(systemName: "wand.and.stars")
                    Text("Transform").fontWeight(.semibold)
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 12)
                .background(Color.purple)
                .foregroundColor(.white)
                .clipShape(Capsule())
            }
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 16)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .padding()
    }
}

struct CanvasRepresentable: UIViewRepresentable {
    @Binding var canvasView: PKCanvasView

    func makeUIView(context: Context) -> PKCanvasView {
        canvasView.drawingPolicy = .anyInput
        canvasView.tool = PKInkingTool(.pen, color: .black, width: 5)
        canvasView.backgroundColor = .white
        canvasView.isOpaque = true
        return canvasView
    }

    func updateUIView(_ uiView: PKCanvasView, context: Context) {}
}
