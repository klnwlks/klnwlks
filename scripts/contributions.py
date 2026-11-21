"""Refresh the public contribution calendar inside the profile's single SVG."""
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.request import Request, urlopen

URL = 'https://github.com/users/klnwlks/contributions'
TEMPLATE = Path(__file__).with_name('profile-template.svg')
OUTPUT = TEMPLATE.parents[1] / 'assets/profile-ledger.svg'
LEVELS = ('#DFD9C7', '#B5B99A', '#8D9B74', '#607650', '#344333')


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.total = None
        self.heading = None

    def handle_starttag(self, tag, attrs):
        if tag == 'h2' and dict(attrs).get('id') == 'js-contribution-activity-description':
            self.heading = []
        if tag != 'td':
            return
        attrs = dict(attrs)
        if 'ContributionCalendar-day' not in attrs.get('class', '').split():
            return
        day = date.fromisoformat(attrs['data-date'])
        level = int(attrs['data-level'])
        if day in self.days or not 0 <= level < len(LEVELS):
            raise ValueError(f'Unexpected contribution cell: {day}, level {level}')
        self.days[day] = level

    def handle_data(self, data):
        if self.heading is not None:
            self.heading.append(data)

    def handle_endtag(self, tag):
        if tag == 'h2' and self.heading is not None:
            match = re.fullmatch(r'\s*([\d,]+)\s+contributions?\s+in the last year\s*', ''.join(self.heading))
            if match:
                self.total = int(match[1].replace(',', ''))
            self.heading = None


def render(days, total):
    if total is None:
        raise ValueError('GitHub did not return a rolling-year contribution total')
    dates = sorted(days)
    if not 365 <= len(dates) <= 372 or (dates[-1] - dates[0]).days != len(dates) - 1:
        raise ValueError('GitHub did not return a contiguous rolling-year calendar')
    sunday = dates[0] - timedelta(days=(dates[0].weekday() + 1) % 7)
    weeks = (dates[-1] - sunday).days // 7 + 1
    pitch = 728 / weeks
    count = f'{total:,}'
    rows = [f'<g aria-label="{count} contributions in the last year">']
    x = 664
    for char in reversed(count):
        x -= 4 if char == ',' else 9
        rows.append(f'<use href="#total-{ord(char)}" x="{x}" y="230"/>')
    for day in dates:
        col, row = divmod((day - sunday).days, 7)
        rows.append(f'<rect x="{36 + col * pitch:.2f}" y="{249 + row * 12}" '
                    f'width="9" height="9" fill="{LEVELS[days[day]]}"/>')
    return '\n'.join([*rows, '</g>'])


if __name__ == '__main__':
    parser = Calendar()
    with urlopen(Request(URL, headers={'User-Agent': 'klnwlks-profile-calendar'}), timeout=20) as response:
        parser.feed(response.read().decode())
    template = TEMPLATE.read_text(encoding='utf-8')
    marker = '<!-- calendar -->'
    if template.count(marker) != 1:
        raise ValueError('Profile template must contain exactly one calendar marker')
    OUTPUT.write_text(template.replace(marker, render(parser.days, parser.total)), encoding='utf-8')
    print(f'Rendered {len(parser.days)} days through {max(parser.days)}; {parser.total:,} contributions')
