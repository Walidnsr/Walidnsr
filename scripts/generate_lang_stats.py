import requests
import os

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
USERNAME = 'Walidnsr'
HIDE = {'Jupyter Notebook', 'TeX', 'Makefile', 'Batchfile', 'Dockerfile'}

LANG_COLORS = {
    'Python': '#3572A5', 'JavaScript': '#f1e05a', 'HTML': '#e34c26',
    'CSS': '#563d7c', 'PHP': '#4F5D95', 'TypeScript': '#2b7489',
    'SQL': '#e38c00', 'Java': '#b07219', 'C': '#555555', 'C++': '#f34b7d',
    'Ruby': '#701516', 'Go': '#00ADD8', 'Rust': '#dea584', 'R': '#198CE7',
    'Vue': '#41b883', 'Shell': '#89e051', 'PowerShell': '#012456',
    'Dockerfile': '#384d54', 'Hack': '#878787',
}


def get_languages():
    query = """
    query($username: String!) {
      user(login: $username) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
          nodes {
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
      }
    }
    """
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}', 'Content-Type': 'application/json'}
    resp = requests.post('https://api.github.com/graphql',
        json={'query': query, 'variables': {'username': USERNAME}},
        headers=headers, timeout=30)
    resp.raise_for_status()
    lang_data = {}
    for repo in resp.json()['data']['user']['repositories']['nodes']:
        for edge in repo['languages']['edges']:
            name = edge['node']['name']
            if name in HIDE:
                continue
            color = LANG_COLORS.get(name, edge['node']['color'] or '#8b949e')
            lang_data.setdefault(name, {'size': 0, 'color': color})
            lang_data[name]['size'] += edge['size']
    top = sorted(lang_data.items(), key=lambda x: x[1]['size'], reverse=True)[:6]
    total = sum(v['size'] for _, v in top) or 1
    return [(name, info['color'], info['size'] / total * 100) for name, info in top]


def generate_svg(languages):
    # Thème bleu (identique à la palette de référence)
    bg, border = '#1a1b27', '#414868'
    title_c, text_c, bar_bg = '#58A6FF', '#a9b1d6', '#252d3d'
    w, pad, row_h, bar_h = 300, 20, 24, 7
    total_h = 42 + len(languages) * row_h + 10
    rows = []
    for i, (name, color, pct) in enumerate(languages):
        y = 40 + i * row_h
        bar_w = (w - 2 * pad) * pct / 100
        rows.append(
            f'<text x="{pad}" y="{y+11}" fill="{text_c}" font-family="Segoe UI,Helvetica,sans-serif" font-size="11">{name}</text>'
            f'<text x="{w-pad}" y="{y+11}" fill="{text_c}" font-family="Segoe UI,Helvetica,sans-serif" font-size="11" text-anchor="end">{pct:.1f}%</text>'
            f'<rect x="{pad}" y="{y+14}" width="{w-2*pad}" height="{bar_h}" rx="3" fill="{bar_bg}"/>'
            f'<rect x="{pad}" y="{y+14}" width="{bar_w:.1f}" height="{bar_h}" rx="3" fill="{color}"/>'
        )
    return (f'<svg width="{w}" height="{total_h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{total_h}" rx="10" fill="{bg}" stroke="{border}" stroke-width="1"/>'
            f'<text x="{pad}" y="25" fill="{title_c}" font-family="Segoe UI,Helvetica,sans-serif" font-size="13" font-weight="600">Most Used Languages</text>'
            + ''.join(rows) + '</svg>')


if __name__ == '__main__':
    langs = get_languages()
    svg = generate_svg(langs)
    with open('top_languages.svg', 'w') as f:
        f.write(svg)
    print("Generated:", ', '.join(f'{n} {p:.1f}%' for n, _, p in langs))
