# Summarise a .glb (stdlib only): materials, textures, alpha modes, vertex colours.
import json, struct, sys
path = sys.argv[1]
data = open(path, 'rb').read()
magic, ver, length = struct.unpack('<III', data[:12])
clen, ctype = struct.unpack('<II', data[12:20])
js = json.loads(data[20:20 + clen])
print("size MB", round(len(data) / 1e6, 2), "nodes", len(js.get('nodes', [])), "meshes", len(js.get('meshes', [])),
      "materials", len(js.get('materials', [])), "images", len(js.get('images', [])))
print("extensionsUsed", js.get('extensionsUsed'))
for m in js['materials']:
    pbr = m.get('pbrMetallicRoughness', {})
    flags = []
    if 'baseColorTexture' in pbr: flags.append('baseTex')
    if 'emissiveTexture' in m: flags.append('emTex')
    if m.get('alphaMode'): flags.append(m['alphaMode'])
    bc = [round(x, 2) for x in pbr.get('baseColorFactor', [1, 1, 1, 1])]
    print(f"  {m['name']:<22} base={bc} rough={pbr.get('roughnessFactor', 1)} metal={pbr.get('metallicFactor', 1)} "
          f"em={m.get('emissiveFactor')} {flags} ext={list(m.get('extensions', {}).keys())}")
vc = set()
for me in js['meshes']:
    for p in me['primitives']:
        if 'COLOR_0' in p['attributes']:
            vc.add(me['name'])
print("meshes with COLOR_0:", len(vc), sorted(vc)[:12])
tris = 0
for me in js['meshes']:
    for p in me['primitives']:
        acc = js['accessors'][p['indices']]
        tris += acc['count'] // 3
print("triangles", tris)
