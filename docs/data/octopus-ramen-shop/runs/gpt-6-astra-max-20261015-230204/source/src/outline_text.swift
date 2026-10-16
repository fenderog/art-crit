import Foundation
import CoreText
import CoreGraphics

// Turn the illustration's lettering into portable vector outlines. No font files
// or linked assets are needed to view the finished SVG.
let input = FileHandle.standardInput.readDataToEndOfFile()
let requests = try JSONSerialization.jsonObject(with: input) as! [[String: Any]]
var output: [[String: Any]] = []
func number(_ x: CGFloat) -> String { String(format: "%.3f", Double(x)) }
for item in requests {
    let size = (item["size"] as! NSNumber).doubleValue
    let font = CTFontCreateWithName(item["font"] as! CFString, size, nil)
    let kern = (item["spacing"] as? NSNumber)?.doubleValue ?? 0
    let attributes: [NSAttributedString.Key: Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String): font,
        NSAttributedString.Key(kCTKernAttributeName as String): kern
    ]
    let string = NSAttributedString(string: item["text"] as! String, attributes: attributes)
    let line = CTLineCreateWithAttributedString(string)
    let width = CTLineGetTypographicBounds(line, nil, nil, nil)
    var commands: [String] = []
    let runs = CTLineGetGlyphRuns(line) as! [CTRun]
    for run in runs {
        let count = CTRunGetGlyphCount(run)
        var glyphs = [CGGlyph](repeating: 0, count: count)
        var positions = [CGPoint](repeating: .zero, count: count)
        CTRunGetGlyphs(run, CFRange(location: 0, length: 0), &glyphs)
        CTRunGetPositions(run, CFRange(location: 0, length: 0), &positions)
        let attrs = CTRunGetAttributes(run) as NSDictionary
        let runFont = attrs[kCTFontAttributeName] as! CTFont
        for i in 0..<count {
            var transform = CGAffineTransform(translationX: positions[i].x, y: positions[i].y)
            guard let path = CTFontCreatePathForGlyph(runFont, glyphs[i], &transform) else { continue }
            path.applyWithBlock { pointer in
                let e = pointer.pointee
                func p(_ i: Int) -> String { number(e.points[i].x) + "," + number(e.points[i].y) }
                switch e.type {
                    case .moveToPoint: commands.append("M" + p(0))
                    case .addLineToPoint: commands.append("L" + p(0))
                    case .addQuadCurveToPoint: commands.append("Q" + p(0) + " " + p(1))
                    case .addCurveToPoint: commands.append("C" + p(0) + " " + p(1) + " " + p(2))
                    case .closeSubpath: commands.append("Z")
                    @unknown default: break
                }
            }
        }
    }
    output.append(["width": width, "d": commands.joined(separator: " ")])
}
let json = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
FileHandle.standardOutput.write(json)
