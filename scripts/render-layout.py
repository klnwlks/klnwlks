"""Regenerate the Growth Ledger's static layout from the portfolio and Simple Icons."""
from pathlib import Path
import re
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT.parent / 'portfolio-v3'
FONTS = PORTFOLIO / 'node_modules'
PAPER, DEEP, INK, RULE, MOSS = (
    '#F1EBDD', '#E6DDCB', '#25231F', '#CEC3AE', '#465043',
)
NAME = 'kalinaw lukas aom bebis'
ICONS = Path(sys.argv[1])


def face(package, filename, location=None):
    font = TTFont(FONTS / package / 'files' / filename)
    return font.getGlyphSet(location=location), font.getBestCmap(), font['head'].unitsPerEm


SERIF = face('@fontsource-variable/literata', 'literata-latin-opsz-normal.woff2', {'wght': 450, 'opsz': 60})
MONO = face('@fontsource/fragment-mono', 'fragment-mono-latin-400-normal.woff2')


def type_line(content, x, y, size, *, font=SERIF, color=INK, width=None, align='left'):
    glyphs, cmap, units = font
    scale = size / units
    tracking = -0.04 * units if font is SERIF else 0
    runs = []
    cursor = 0
    for character in content:
        glyph = glyphs[cmap[ord(character)]]
        pen = SVGPathPen(glyphs, ntos=lambda n: f'{n:.2f}'.rstrip('0').rstrip('.'))
        glyph.draw(pen)
        if commands := pen.getCommands():
            runs.append(f'<path transform="translate({cursor:g})" d="{commands}"/>')
        cursor += glyph.width + tracking
    advance = cursor - tracking
    if width is not None:
        scale = min(scale, width / advance)
    if align == 'right':
        x -= advance * scale
    return (f'<g fill="{color}" transform="translate({x:g} {y:g}) scale({scale:.6f} {-scale:.6f})">'
            + ''.join(runs) + '</g>')


def botanical_path():
    # Use the shipped hero's exact Braille ink, with the same 2×4 dot ordering.
    source = (PORTFOLIO / 'src/components/Hero.tsx').read_text()
    flower = re.search(r'const flower = `([\u2800-\u28ff\n]+)`;', source)[1]
    dots = []
    for row, line in enumerate(flower.splitlines()):
        for col, char in enumerate(line):
            for bit, (dx, dy) in enumerate(((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (0, 3), (1, 3))):
                if (ord(char) - 0x2800) & (1 << bit):
                    dots.append((col * 8 + dx * 4, row * 18 + dy * 4))
    x0 = min(x for x, _ in dots)
    y0 = min(y for _, y in dots)
    width = max(x for x, _ in dots) - x0 + 2.4
    path = ''.join(f'M{x - x0} {y - y0}h2.4v2.4h-2.4z' for x, y in dots)
    return width, path


BLOOM_WIDTH, BLOOM_PATH = botanical_path()


def bloom(x, y, width, color=MOSS):
    return (f'<path fill="{color}" transform="translate({x} {y}) scale({width / BLOOM_WIDTH:.6f})"'
            f' d="{BLOOM_PATH}"/>')


def rule(y, left=36, right=764):
    return f'<path d="M{left} {y}H{right}" fill="none" stroke="{RULE}"/>'


icons = ('typescript', 'python', 'c', 'react', 'astro', 'bun')
marks = []
for index, slug in enumerate(icons):
    path = re.search(r'<path d="([^"]+)"', (ICONS / f'{slug}.svg').read_text())[1]
    marks.append(f'<path transform="translate({36 + index * 64} 779) scale(1.5)" fill="{MOSS}" d="{path}"/>')

layers = [
    '<rect width="800" height="850" fill="#F1EBDD"/>',
    type_line(NAME, 36, 115, 69, width=580),
    bloom(622, 31, 142),
    rule(167),
    type_line('about me', 36, 230, 53),
    type_line("i'm lukas, a computer science student", 36, 284, 37),
    type_line('at UPLB and a full-stack developer.', 36, 329, 37),
    rule(368),
    type_line('contributions', 36, 435, 55),
    '<!-- calendar -->',
    rule(599),
    type_line('recent work', 36, 644, 28, font=MONO),
    type_line('MATA / RoomTBA / raymaku', 36, 687, 28, font=MONO),
    rule(718),
    type_line('tools', 36, 758, 28, font=MONO),
    *marks,
]
(ROOT / 'scripts/profile-template.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="850" viewBox="0 0 800 850">\n'
    '<title>Kalinaw Lukas Aom Bebis</title>\n'
    '<desc>Computer science student at UPLB and full-stack developer. GitHub contributions. '
    'Recent work: MATA, RoomTBA, raymaku. Tools: TypeScript, Python, C, React, Astro, Bun.</desc>\n'
    + '\n'.join(layers) + '\n</svg>\n', encoding='utf-8',
)
