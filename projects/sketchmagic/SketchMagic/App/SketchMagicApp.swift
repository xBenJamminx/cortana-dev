import SwiftUI

@main
struct SketchMagicApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// MARK: - Root Navigation

struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        Group {
            switch appState.currentScreen {
            case .canvas:
                CanvasView()
            case .stylePicker:
                StylePickerView()
            case .generating:
                GenerationView()
            case .result:
                ResultView()
            case .gallery:
                GalleryView()
            }
        }
        .animation(.easeInOut(duration: 0.25), value: appState.currentScreen)
    }
}

// Make Screen conform to Equatable for animation
extension AppState.Screen: Equatable {}
