// Optional source utility: outline the small descriptor using macOS CoreText.
// The generated JSON is included so build.py itself needs only Python's standard library.
// Run from the project root:
//   swift -module-cache-path .build-cache src/outline_descriptor.swift > src/descriptor.json
import Foundation
import CoreText
import CoreGraphics

let label = "GENERATIVE INTELLIGENCE"
let font = CTFontCreateWithName("AvenirNext-Medium" as CFString, 16, nil)
let attributes: [NSAttributedString.Key: Any] = [
    NSAttributedString.Key(kCTFontAttributeName as String): font,
    NSAttributedString.Key(kCTKernAttributeName as String): 4.4
]
let line = CTLineCreateWithAttributedString(NSAttributedString(string: label, attributes: attributes))

func number(_ n: CGFloat) -> String {
    let value = abs(n) < 0.0005 ? 0 : n
    return String(format: "%.3f", Double(value))
        .replacingOccurrences(of: #"\.?0+$"#, with: "", options: .regularExpression)
}

var outlines: [String] = []
for run in CTLineGetGlyphRuns(line) as! [CTRun] {
    let count = CTRunGetGlyphCount(run)
    var glyphs = [CGGlyph](repeating: 0, count: count)
    var positions = [CGPoint](repeating: .zero, count: count)
    CTRunGetGlyphs(run, CFRange(location: 0, length: 0), &glyphs)
    CTRunGetPositions(run, CFRange(location: 0, length: 0), &positions)
    for index in 0..<count {
        guard let path = CTFontCreatePathForGlyph(font, glyphs[index], nil) else { continue }
        let origin = positions[index]
        func point(_ p: CGPoint) -> String {
            return "\(number(p.x + origin.x)) \(number(-p.y - origin.y))"
        }
        var commands: [String] = []
        path.applyWithBlock { element in
            let e = element.pointee
            switch e.type {
            case .moveToPoint: commands.append("M" + point(e.points[0]))
            case .addLineToPoint: commands.append("L" + point(e.points[0]))
            case .addQuadCurveToPoint: commands.append("Q" + point(e.points[0]) + " " + point(e.points[1]))
            case .addCurveToPoint: commands.append("C" + point(e.points[0]) + " " + point(e.points[1]) + " " + point(e.points[2]))
            case .closeSubpath: commands.append("Z")
            @unknown default: fatalError("Unexpected path element")
            }
        }
        outlines.append(commands.joined(separator: " "))
    }
}
let result: [String: Any] = [
    "text": label,
    "font": "AvenirNext-Medium",
    "size": 16,
    "tracking": 4.4,
    "advance": CTLineGetTypographicBounds(line, nil, nil, nil),
    "paths": outlines
]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
print(String(data: data, encoding: .utf8)!)
