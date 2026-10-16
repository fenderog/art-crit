import AppKit
import CoreText

struct GlyphRun {
    let d: String
    let width: CGFloat
    let ascent: CGFloat
    let descent: CGFloat
}

func svgPath(_ path: CGPath, dx: CGFloat, baseline: CGFloat) -> String {
    var parts: [String] = []
    path.applyWithBlock { element in
        let e = element.pointee
        func fmt(_ p: CGPoint) -> String {
            let x = p.x + dx
            let y = baseline - p.y
            return String(format: "%.2f %.2f", x, y)
        }
        switch e.type {
        case .moveToPoint:
            parts.append("M \(fmt(e.points[0]))")
        case .addLineToPoint:
            parts.append("L \(fmt(e.points[0]))")
        case .addQuadCurveToPoint:
            parts.append("Q \(fmt(e.points[0])) \(fmt(e.points[1]))")
        case .addCurveToPoint:
            parts.append("C \(fmt(e.points[0])) \(fmt(e.points[1])) \(fmt(e.points[2]))")
        case .closeSubpath:
            parts.append("Z")
        @unknown default:
            break
        }
    }
    return parts.joined(separator: " ")
}

func outline(text: String, fontName: String, size: CGFloat, kern: CGFloat) -> GlyphRun {
    guard let font = NSFont(name: fontName, size: size) else {
        fputs("missing font \(fontName)\n", stderr)
        exit(1)
    }
    let ctFont = font as CTFont
    var pen: CGFloat = 0
    var chunks: [String] = []
    for ch in text {
        let s = String(ch)
        var chars = Array(s.utf16)
        var glyphs = [CGGlyph](repeating: 0, count: chars.count)
        let ok = CTFontGetGlyphsForCharacters(ctFont, &chars, &glyphs, chars.count)
        if !ok {
            fputs("missing glyph for \(s)\n", stderr)
            exit(1)
        }
        var advance = CGSize.zero
        CTFontGetAdvancesForGlyphs(ctFont, .horizontal, glyphs, &advance, 1)
        if let path = CTFontCreatePathForGlyph(ctFont, glyphs[0], nil) {
            chunks.append(svgPath(path, dx: pen, baseline: 0))
        }
        pen += advance.width + kern
    }
    let ascent = CTFontGetAscent(ctFont)
    let descent = CTFontGetDescent(ctFont)
    return GlyphRun(d: chunks.joined(separator: " "), width: pen - kern, ascent: ascent, descent: descent)
}

let args = CommandLine.arguments
if args.count < 5 {
    fputs("usage: outline font size kern text\n", stderr)
    exit(1)
}
let fontName = args[1]
let size = CGFloat(Double(args[2])!)
let kern = CGFloat(Double(args[3])!)
let text = args[4...].joined(separator: " ")
let run = outline(text: text, fontName: fontName, size: size, kern: kern)
print(String(format: "%.3f", run.width))
print(String(format: "%.3f", run.ascent))
print(String(format: "%.3f", run.descent))
print(run.d)
