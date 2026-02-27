import SwiftUI

/// All available art styles for transforming sketches.
enum ArtStyle: String, CaseIterable, Identifiable {
    case photorealistic
    case watercolor
    case anime
    case pixelArt
    case fantasy
    case cartoon
    case oilPainting
    case pencilSketch
    case popArt
    case storybook

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .photorealistic: return "Photorealistic"
        case .watercolor: return "Watercolor"
        case .anime: return "Anime"
        case .pixelArt: return "Pixel Art"
        case .fantasy: return "Fantasy"
        case .cartoon: return "Cartoon"
        case .oilPainting: return "Oil Painting"
        case .pencilSketch: return "Pencil Sketch"
        case .popArt: return "Pop Art"
        case .storybook: return "Storybook"
        }
    }

    var icon: String {
        switch self {
        case .photorealistic: return "\u{1F4F7}" // camera
        case .watercolor: return "\u{1F3A8}" // palette
        case .anime: return "\u{2728}" // sparkles
        case .pixelArt: return "\u{1F579}" // joystick
        case .fantasy: return "\u{1F52E}" // crystal ball
        case .cartoon: return "\u{1F4AC}" // speech balloon
        case .oilPainting: return "\u{1F5BC}" // framed picture
        case .pencilSketch: return "\u{270F}" // pencil
        case .popArt: return "\u{2B50}" // star
        case .storybook: return "\u{1F4D6}" // open book
        }
    }

    var description: String {
        switch self {
        case .photorealistic: return "Make it look real"
        case .watercolor: return "Soft, flowing colors"
        case .anime: return "Japanese animation style"
        case .pixelArt: return "Retro video game pixels"
        case .fantasy: return "Enchanted and mystical"
        case .cartoon: return "Bold and fun comic style"
        case .oilPainting: return "Classical museum quality"
        case .pencilSketch: return "Professional artist sketch"
        case .popArt: return "Bold like Warhol"
        case .storybook: return "Like your favorite picture book"
        }
    }

    var previewColor: Color {
        switch self {
        case .photorealistic: return Color(hex: "2C3E50")
        case .watercolor: return Color(hex: "3498DB")
        case .anime: return Color(hex: "E91E63")
        case .pixelArt: return Color(hex: "27AE60")
        case .fantasy: return Color(hex: "9B59B6")
        case .cartoon: return Color(hex: "F39C12")
        case .oilPainting: return Color(hex: "8B4513")
        case .pencilSketch: return Color(hex: "7F8C8D")
        case .popArt: return Color(hex: "E74C3C")
        case .storybook: return Color(hex: "1ABC9C")
        }
    }

    /// The full prompt sent to NB2 along with the sketch image.
    var promptTemplate: String {
        switch self {
        case .photorealistic:
            return """
            Transform this sketch into a photorealistic image. Create a highly detailed, \
            lifelike rendering with natural lighting, realistic textures, and accurate \
            proportions. Maintain the exact composition and subject of the original drawing. \
            The result should look like a professional photograph.
            """

        case .watercolor:
            return """
            Transform this sketch into a beautiful watercolor painting. Use soft, flowing \
            washes of color with visible brushstrokes and gentle color bleeding at the edges. \
            Include subtle paper texture. Maintain the composition and subject of the original \
            drawing. The style should feel like a hand-painted watercolor artwork with \
            translucent layers.
            """

        case .anime:
            return """
            Transform this sketch into anime/manga style artwork. Use clean bold outlines, \
            vibrant flat colors, large expressive eyes if characters are present, and dynamic \
            shading typical of Japanese animation. Add subtle cel-shading and anime-style \
            highlights. Maintain the composition and subject of the original drawing.
            """

        case .pixelArt:
            return """
            Transform this sketch into detailed pixel art. Use a visible pixel grid with \
            carefully chosen colors in a limited palette. The style should evoke classic \
            16-bit era video games with clean, deliberate pixel placement. Maintain the \
            composition and subject of the original drawing. Include subtle dithering \
            for shading.
            """

        case .fantasy:
            return """
            Transform this sketch into a magical fantasy illustration. Add glowing magical \
            effects, ethereal lighting, sparkling particles, and an enchanted atmosphere. \
            Use rich, vibrant colors with magical auras and fantasy-style rendering. Maintain \
            the composition and subject of the original drawing. The result should feel like \
            concept art from a fantasy world.
            """

        case .cartoon:
            return """
            Transform this sketch into a bold cartoon/comic book style illustration. Use \
            thick black outlines, vibrant flat colors, exaggerated proportions, and dynamic \
            comic-style shading with halftone dots. Maintain the composition and subject of \
            the original drawing. The style should feel like a modern cartoon or comic book panel.
            """

        case .oilPainting:
            return """
            Transform this sketch into a classical oil painting. Use rich, thick brushstrokes \
            with visible texture and impasto technique. Include realistic lighting with dramatic \
            chiaroscuro, warm tones, and the depth typical of old master paintings. Maintain \
            the composition and subject of the original drawing. The result should look like \
            it belongs in a museum.
            """

        case .pencilSketch:
            return """
            Transform this rough sketch into a professional artist's pencil drawing. Use \
            precise graphite pencil techniques with varied line weight, detailed cross-hatching \
            for shading, and subtle blending. Add depth through careful tonal values from \
            light to dark. Maintain the composition and subject of the original drawing. The \
            result should look like a skilled artist's finished pencil illustration.
            """

        case .popArt:
            return """
            Transform this sketch into a vibrant pop art illustration in the style of Andy \
            Warhol and Roy Lichtenstein. Use bold primary colors, thick black outlines, \
            Ben-Day dots pattern, and high contrast. Include comic-style elements and dramatic \
            color blocking. Maintain the composition and subject of the original drawing. The \
            result should feel like iconic 1960s pop art.
            """

        case .storybook:
            return """
            Transform this sketch into a charming children's storybook illustration. Use warm, \
            inviting colors with soft textures and gentle shading. The style should feel like \
            a beloved picture book with whimsical details, approachable characters, and a cozy \
            atmosphere. Maintain the composition and subject of the original drawing. Add subtle \
            background details that enhance the storybook feel.
            """
        }
    }
}

// MARK: - Color Hex Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: .alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r = Double((int >> 16) & 0xFF) / 255.0
        let g = Double((int >> 8) & 0xFF) / 255.0
        let b = Double(int & 0xFF) / 255.0
        self.init(red: r, green: g, blue: b)
    }
}
