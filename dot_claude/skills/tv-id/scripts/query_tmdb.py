#!/usr/bin/env python3
"""Query TMDB for TV show episode data including per-episode crew information.

Usage:
    query_tmdb.py <show_name> <season_number> [--api-key KEY] [--show-id ID]

Output: JSON with episodes list including writers, directors, and production codes.
"""

import sys
import json
import os
import urllib.request
import urllib.parse
import urllib.error


BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(path, api_key, params=None):
    p = {'api_key': api_key}
    if params:
        p.update(params)
    query = urllib.parse.urlencode(p)
    url = f"{BASE_URL}{path}?{query}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"TMDB API error {e.code} for {path}: {e.read().decode()}", file=sys.stderr)
        raise


def search_show(api_key, show_name):
    data = tmdb_get("/search/tv", api_key, {'query': show_name})
    return data.get('results', [])


def get_season(api_key, show_id, season_number):
    return tmdb_get(f"/tv/{show_id}/season/{season_number}", api_key)


def get_episode_credits(api_key, show_id, season_number, episode_number):
    return tmdb_get(
        f"/tv/{show_id}/season/{season_number}/episode/{episode_number}/credits",
        api_key
    )


def main():
    if len(sys.argv) < 3:
        print("Usage: query_tmdb.py <show_name> <season_number> [--api-key KEY] [--show-id ID]")
        sys.exit(1)

    show_name = sys.argv[1]
    season_number = int(sys.argv[2])

    api_key = os.environ.get('TMDB_API_KEY')
    if '--api-key' in sys.argv:
        idx = sys.argv.index('--api-key')
        api_key = sys.argv[idx + 1]

    if not api_key:
        print("Error: TMDB API key required. Set TMDB_API_KEY env var or use --api-key KEY", file=sys.stderr)
        sys.exit(1)

    # Allow bypassing show search if ID is known
    show_id = None
    if '--show-id' in sys.argv:
        idx = sys.argv.index('--show-id')
        show_id = int(sys.argv[idx + 1])
        show_info = {'id': show_id, 'name': show_name, 'first_air_date': None}
    else:
        results = search_show(api_key, show_name)
        if not results:
            print(f"No shows found matching '{show_name}'", file=sys.stderr)
            sys.exit(1)
        # Print all results so user can confirm / pick one
        print("# Show search results:", file=sys.stderr)
        for i, r in enumerate(results[:5]):
            print(f"  [{i}] {r['name']} ({r.get('first_air_date', 'unknown')[:4]}) id={r['id']}", file=sys.stderr)
        show_info = results[0]
        show_id = show_info['id']
        print(f"# Using: {show_info['name']} (id={show_id})", file=sys.stderr)

    season = get_season(api_key, show_id, season_number)
    episodes = season.get('episodes', [])

    output = {
        'show': {
            'id': show_id,
            'name': show_info['name'],
            'first_air_date': show_info.get('first_air_date'),
        },
        'season_number': season_number,
        'episodes': [],
    }

    for ep in episodes:
        ep_num = ep['episode_number']
        writers = []
        directors = []
        try:
            credits = get_episode_credits(api_key, show_id, season_number, ep_num)
            for member in credits.get('crew', []):
                job = member.get('job', '')
                name = member.get('name', '')
                if job in ('Writer', 'Teleplay', 'Story', 'Written by'):
                    writers.append(name)
                elif job == 'Director':
                    directors.append(name)
        except Exception as e:
            print(f"  Warning: could not fetch credits for episode {ep_num}: {e}", file=sys.stderr)

        output['episodes'].append({
            'episode_number': ep_num,
            'title': ep.get('name', ''),
            'air_date': ep.get('air_date', ''),
            'overview': ep.get('overview', ''),
            'production_code': ep.get('production_code', ''),
            'runtime': ep.get('runtime'),
            'writers': writers,
            'directors': directors,
        })

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
