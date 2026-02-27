import SwiftUI

/// Grid view for selecting an art style
struct StylePickerView: View {
    @EnvironmentObject var appState: AppState
    private let columns = [GridItem(.adaptive(minimum: 140, maximum: 180), spacing: 16)]

    var body: some View {
        NavigationStack {
            ScrollView {
                if let sketch = appState.currentSketch {
                    Image(uiImage: sketch)
                        .resizable()
                        .scaledToFit()
                        .frame(maxHeight: 200)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .shadow(radius: 4)
                        .padding(.horizontal)
                        .padding(.top, 8)
                }

                Text("Pick a Style")
                    .font(.title2).fontWeight(.bold)
                    .padding(.top, 8)

                LazyVGrid(columns: columns, spacing: 16) {
                    ForEach(ArtStyle.allCases) { style in
                        StyleCard(style: style, isSelected: appState.selectedStyle == style) {
                            appState.selectedStyle = style
                        }
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 100)
            }
            .navigationTitle("Choose Style")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Back") { appState.currentScreen = .canvas }
                }
            }
            .overlay(alignment: .bottom) {
                Button {
                    appState.currentScreen = .generating
                    Task { await appState.generateArt() }
                } label: {
                    HStack {
                        Image(systemName: "sparkles")
                        Text("Generate \(appState.selectedStyle.displayName)").fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(appState.selectedStyle.accentColor)
                    .foregroundColor(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
                .background(.ultraThinMaterial)
            }
        }
    }
}

struct StyleCard: View {
    let style: ArtStyle
    let isSelected: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 8) {
                Image(systemName: style.icon)
                    .font(.system(size: 32))
                    .foregroundColor(style.accentColor)
                Text(style.displayName)
                    .font(.headline).foregroundColor(.primary)
                Text(style.description)
                    .font(.caption).foregroundColor(.secondary)
                    .multilineTextAlignment(.center).lineLimit(2)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 20).padding(.horizontal, 8)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(isSelected ? style.accentColor.opacity(0.15) : Color(.systemGray6))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(isSelected ? style.accentColor : .clear, lineWidth: 3)
            )
        }
    }
}
