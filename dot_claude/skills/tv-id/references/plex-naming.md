# Plex Naming Conventions for TV Shows

Source: https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/

## Directory Structure

```
TV Shows/
└── Show Name/
    ├── Season 01/
    │   ├── Show Name - s01301.mkv
    │   ├── Show Name - s01302.mkv
    │   └── ...
    └── Season 02/
        └── ...
```

## File Naming Format

### Standard Episodes

```
{Show Name} - s{season:02d}e{episode:02d}.{ext}
```

Examples:
- `The Office - s08e01.mkv`
- `The Office - s08e12.mkv`

### Multi-Episode Files

If one file contains multiple episodes:

```
The Office - s08e01-e03.mkv
```

## Key Rules

1. **Show name must exactly match** the name in your Plex library (which comes from TMDB)
2. **Season and episode numbers** must be zero-padded to 2 digits: `s08e01` not `e8e1`
3. **Separator**: Use ` - ` (space-dash-space) between components
4. **Extension**: Keep original (`.mkv`, `.mp4`, etc.)

## TMDB Ordering vs. DVD Ordering

Plex defaults to TMDB episode ordering (by original air date). When disc sets use a different ordering:
- TMDB ordering is authoritative for Plex matching
- Check `https://www.themoviedb.org/tv/{show_id}/season/{season}` for correct order
- The file ordering may differ from TMDB air-date order

## Show Name Matching Tips

- If the show name has special characters, match TMDB exactly
- Use the `query_tmdb.py` script to confirm the exact show name TMDB uses
