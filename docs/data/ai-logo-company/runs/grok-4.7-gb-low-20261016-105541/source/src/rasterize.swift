import AppKit
import Foundation

func hex(_ s: String) -> NSColor {
    var hex = s.trimmingCharacters(in: .whitespaces)
    if hex.hasPrefix("#") { hex.removeFirst() }
    let v = Int(hex, radix: 16) ?? 0
    let r = CGFloat((v >> 16) & 0xFF) / 255
    let g = CGFloat((v >> 8) & 0xFF) / 255
    let b = CGFloat(v & 0xFF) / 255
    return NSColor(srgbRed: r, green: g, blue: b, alpha: 1)
}

func parsePath(_ d: String) -> CGPath {
    let path = CGMutablePath()
    let tokens = d.replacingOccurrences(of: ",", with: " ").split(whereSeparator: { $0.isWhitespace }).map(String.init)
    var i = 0
    func num() -> CGFloat {
        let n = CGFloat(Double(tokens[i])!)
        i += 1
        return n
    }
    while i < tokens.count {
        let cmd = tokens[i]
        i += 1
        switch cmd {
        case "M":
            path.move(to: CGPoint(x: num(), y: num()))
        case "L":
            path.addLine(to: CGPoint(x: num(), y: num()))
        case "C":
            let c1 = CGPoint(x: num(), y: num())
            let c2 = CGPoint(x: num(), y: num())
            let p = CGPoint(x: num(), y: num())
            path.addCurve(to: p, control1: c1, control2: c2)
        case "Q":
            let c = CGPoint(x: num(), y: num())
            let p = CGPoint(x: num(), y: num())
            path.addQuadCurve(to: p, control: c)
        case "Z":
            path.closeSubpath()
        default:
            fputs("bad path cmd \(cmd)\n", stderr)
            exit(1)
        }
    }
    return path
}

struct Shape {
    let fill: NSColor
    let evenOdd: Bool
    let d: String
    let transform: CGAffineTransform
}

func attr(_ tag: String, _ name: String) -> String? {
    guard let r = tag.range(of: "\(name)=\"") else { return nil }
    let rest = tag[r.upperBound...]
    guard let end = rest.firstIndex(of: "\"") else { return nil }
    return String(rest[..<end])
}

func parseTransform(_ s: String?) -> CGAffineTransform {
    guard let s else { return .identity }
    var t = CGAffineTransform.identity
    let re = try! NSRegularExpression(pattern: "(translate|scale)\\(([^)]*)\\)")
    let ns = s as NSString
    for match in re.matches(in: s, range: NSRange(location: 0, length: ns.length)) {
        let kind = ns.substring(with: match.range(at: 1))
        let body = ns.substring(with: match.range(at: 2))
        let nums = body.split(whereSeparator: { $0.isWhitespace || $0 == "," }).map { CGFloat(Double($0)!) }
        if kind == "translate" {
            let y = nums.count > 1 ? nums[1] : 0
            t = t.concatenating(CGAffineTransform(translationX: nums[0], y: y))
        } else {
            let sy = nums.count > 1 ? nums[1] : nums[0]
            t = t.concatenating(CGAffineTransform(scaleX: nums[0], y: sy))
        }
    }
    return t
}

let args = CommandLine.arguments
if args.count < 4 {
    fputs("usage: rasterize in.svg out.png longEdge\n", stderr)
    exit(1)
}
let svg = try String(contentsOfFile: args[1], encoding: .utf8)
guard let vbRange = svg.range(of: "viewBox=\"") else { exit(1) }
let vbRest = svg[vbRange.upperBound...]
let vbStr = String(vbRest[..<vbRest.firstIndex(of: "\"")!])
let vb = vbStr.split(whereSeparator: { $0.isWhitespace }).map { Double($0)! }
let vbW = CGFloat(vb[2])
let vbH = CGFloat(vb[3])
let longEdge = CGFloat(Double(args[3])!)
let scale = longEdge / max(vbW, vbH)
let w = max(1, Int((vbW * scale).rounded()))
let h = max(1, Int((vbH * scale).rounded()))

var shapes: [Shape] = []
var groupStack: [CGAffineTransform] = [.identity]
let pattern = "</g>|<g\\b[^>]*>|<(rect|path)\\b[^>]*>"
let regex = try NSRegularExpression(pattern: pattern)
let ns = svg as NSString
for match in regex.matches(in: svg, range: NSRange(location: 0, length: ns.length)) {
    let tag = ns.substring(with: match.range)
    if tag == "</g>" {
        _ = groupStack.popLast()
    } else if tag.hasPrefix("<g") {
        let local = parseTransform(attr(tag, "transform"))
        groupStack.append(groupStack.last!.concatenating(local))
    } else if tag.hasPrefix("<rect"), let fill = attr(tag, "fill") {
        shapes.append(Shape(fill: hex(fill), evenOdd: false, d: "M 0 0 L \(vbW) 0 L \(vbW) \(vbH) L 0 \(vbH) Z", transform: groupStack.last!))
    } else if tag.hasPrefix("<path"), let fill = attr(tag, "fill"), let d = attr(tag, "d") {
        let even = tag.contains("evenodd")
        let local = parseTransform(attr(tag, "transform"))
        shapes.append(Shape(fill: hex(fill), evenOdd: even, d: d, transform: groupStack.last!.concatenating(local)))
    }
}

let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: w,
    pixelsHigh: h,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .deviceRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
)!
let ctx = NSGraphicsContext(bitmapImageRep: rep)!
NSGraphicsContext.current = ctx
let cg = ctx.cgContext
cg.setAllowsAntialiasing(true)
cg.setShouldAntialias(true)
cg.interpolationQuality = .high
cg.scaleBy(x: scale, y: scale)
cg.setFillColor(NSColor.clear.cgColor)
cg.fill(CGRect(x: 0, y: 0, width: vbW, height: vbH))
// Flip because SVG y grows downward and this bitmap context is y-up.
cg.translateBy(x: 0, y: vbH)
cg.scaleBy(x: 1, y: -1)
for shape in shapes {
    cg.saveGState()
    cg.concatenate(shape.transform)
    if shape.evenOdd { cg.setFillColor(shape.fill.cgColor); cg.addPath(parsePath(shape.d)); cg.drawPath(using: .eoFill) }
    else { cg.setFillColor(shape.fill.cgColor); cg.addPath(parsePath(shape.d)); cg.fillPath() }
    cg.restoreGState()
}
NSGraphicsContext.current = nil
let png = rep.representation(using: .png, properties: [:])!
try png.write(to: URL(fileURLWithPath: args[2]))
print("\(w)x\(h) \(args[2])")
