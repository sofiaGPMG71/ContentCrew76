"""Research only through a fixed, approved Wikipedia API endpoint."""
import requests

API = 'https://en.wikipedia.org/w/api.php'


def fetch_sources(topic: str, limit: int = 4) -> list[dict]:
    session = requests.Session()
    session.headers['User-Agent'] = 'ContentCrewStudy/1.0 (educational research app)'
    response = session.get(API, params={
        'action': 'query', 'format': 'json', 'generator': 'search',
        'gsrsearch': topic, 'gsrlimit': limit, 'prop': 'extracts|info',
        'explaintext': 1, 'exintro': 1, 'inprop': 'url', 'redirects': 1,
    }, timeout=25)
    response.raise_for_status()
    data = response.json()
    if 'error' in data:
        raise ValueError('The approved source returned an API error. Try another topic.')
    pages = sorted(data.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))
    sources = []
    for page in pages:
        extract = page.get('extract', '').strip()
        if extract and page.get('fullurl', '').startswith('https://en.wikipedia.org/wiki/'):
            sources.append({'id': f'S{len(sources)+1}', 'title': page['title'],
                            'url': page['fullurl'], 'excerpt': extract[:6000]})
    if not sources:
        raise ValueError('No usable source text found. Try a more specific topic.')
    return sources


def validate_request(topic: str, audience: str) -> None:
    if not 3 <= len(topic.strip()) <= 300:
        raise ValueError('Enter a topic between 3 and 300 characters.')
    if not 2 <= len(audience.strip()) <= 150:
        raise ValueError('Enter an audience between 2 and 150 characters.')
