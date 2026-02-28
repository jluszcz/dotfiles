---
name: tv-id
description: This skill should be used when the user wants to identify TV show episodes from video files (MKV, MP4, etc.) and rename them for Plex. Triggers when the user mentions identifying episodes, renaming for Plex, matching episodes to season/episode numbers, or working with a directory of unnamed or generically-named TV video files. The user may optionally provide a target directory path; if not provided, use the current working directory.
version: 1.0.0
---

# TV Episode Identifier

Identify TV episodes from video files using visual credit analysis (written-by/directed-by cards and production codes), then rename files to Plex naming conventions using TMDB metadata.

## Prerequisites

- `ffmpeg` and `ffprobe` must be installed (`brew install ffmpeg`)
- A TMDB API key (free at https://www.themoviedb.org/settings/api) — store as `TMDB_API_KEY` env var

## Workflow

### Step 0: Determine the Target Directory

If the user provided a directory path (e.g. "identify episodes in ~/Videos/The Office Season 8"), use that path. Otherwise use the current working directory. All subsequent steps operate on this directory — referred to as `<target_dir>`.

### Step 1: Parse the Directory Name

Inspect the `<target_dir>` name to extract the show title and season number.

Common patterns:
- `The Office- Season 8 (Disc 2)` → show="The Office", season=8
- `Breaking Bad Season 3` → show="Breaking Bad", season=3
- `Parks and Recreation S05 Disc 1` → show="Parks and Recreation", season=5

Strip disc/part qualifiers and trailing punctuation from the show name.

### Step 2: List Video Files

List all `.mkv`, `.mp4`, `.avi`, `.m4v` files in `<target_dir>`. Note the count — this tells us how many episodes to expect on the disc.

### Step 3: Query TMDB for Episode Metadata

Run the query script to fetch episode titles, writers, directors, and production codes for the season:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/tv-episode-identifier/scripts/query_tmdb.py \
  "<show_name>" <season_number> --api-key "$TMDB_API_KEY"
```

The script prints matching shows to stderr for confirmation before selecting the first result. If the wrong show is selected, re-run with `--show-id <id>` using the correct ID from the list.

Save the JSON output to review episode writers and directors.

### Step 4: Extract Frames from Each Video File

For each video file, extract frames from two key regions:

Always pass the **absolute path** to the video file so no `cd` is needed:

**End credits** (production codes, copyright cards):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/tv-episode-identifier/scripts/extract_frames.py \
  "<target_dir>/<video_file>" --end-minutes 0.5
```

**Opening credits** (written-by and directed-by title cards):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/tv-episode-identifier/scripts/extract_frames.py \
  "<target_dir>/<video_file>" --opening-minutes 5
```

The script outputs a JSON object `{"duration_sec": ..., "frames": [...]}` with the video duration and file paths of extracted frames. Progress is printed to stderr.

### Step 5: Analyze Frames Visually

Read each extracted frame image using the Read tool. Look for:

**Production codes** (in end credits):
- Small text card near the very end, often white text on black
- Format varies by network: NBC uses formats like `1NAB2023`, `806`, `8G05`
- For The Office (US): production codes like `NAB-806` correspond to season 8, episode 6
- Match the numeric portion against episode numbers

**Written-by / Directed-by cards** (in opening section):
- Title cards that appear after the cold open, before the main title sequence
- Look for "Written by [Name]" or "Directed by [Name]" text
- Cross-reference the names against the TMDB episode crew data

**Episode-specific content**:
- Recognizable scenes, guest stars, or plot elements visible in frames
- Can be matched against episode overviews from TMDB

### Step 6: Match Episodes to TMDB Data

For each video file, combine all evidence:

**Duration match** (strong negative filter, secondary positive signal):
- TMDB `runtime` is in minutes; multiply by 60 to compare to `duration_sec` from frame extraction
- Tolerance: ±120 seconds (2 min) for normal episodes
- A large mismatch (>3 minutes) rules an episode out
- A 2× runtime mismatch suggests the file may contain two episodes (use `s08e01-e02` naming)

1. Duration match (cheap filter — check first to rule out candidates)
2. Production code (strongest signal if found)
3. Writer name match against TMDB writers list
4. Director name match against TMDB directors list
5. Content recognition from overview

Build a mapping: `filename → episode_number`. Verify that:
- No two files map to the same episode
- All identified episodes are plausible (they should be consecutive or from the correct disc range)

If a file cannot be identified, try extracting frames at additional positions (e.g., `--positions 0.15,0.20,0.25,0.50`).

### Step 7: Propose Renames

Present the proposed renames to the user in a clear table before executing:

```
Current filename                           →  New filename
The Office- Season 8_t00.mkv              →  The Office - s08e01.mkv
The Office- Season 8_t01.mkv              →  The Office - s08e02.mkv
...
```

Wait for user confirmation before proceeding.

### Step 8: Rename Files

After confirmation, rename each file using its full path within `<target_dir>`:

```bash
mv "<target_dir>/<current_name>" "<target_dir>/<new_name>"
```

Rename one file at a time and report each rename. If any rename fails, stop and report the error.

### Step 9: Clean Up Temporary Frames

After all renames are complete, delete the extracted frames:

```bash
rm -rf /tmp/episode_frames
```

## Naming Format Reference

See `references/plex-naming.md` for complete Plex naming rules. The standard format is:

```
{Show Name} - s{season:02d}e{episode:02d}.{ext}
```

Example: `The Office - S08E03 - Lotto.mkv`

## Tips for Shows

- Production codes at end of credits: look for a small card near the very end (last 30 seconds)
- Written/directed cards: usually appear in the first half of the episode as white text over images

## Handling Ambiguity

If identification is uncertain:
- Extract more frames at different positions
- Note which episodes are missing from the identified set — the unidentified files are probably those
- Check episode air dates against the disc release to narrow the range
- Ask the user for confirmation on uncertain matches before renaming
