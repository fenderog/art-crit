import { makeCloudTexture } from '../textures.js';
const t = makeCloudTexture(3);
const c = t.image;
c.style.background = '#ffb374';
c.style.width = '1024px';
c.style.height = '512px';
document.body.style.margin = '0';
document.body.appendChild(c);
