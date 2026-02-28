#!/usr/bin/env python3
"""Extract frames from a video file at key positions for episode credit analysis.

Usage:
    extract_frames.py <video_file> [--output-dir DIR] [--positions p1,p2,...] [--end-minutes N]

Options:
    --output-dir DIR       Directory to save frames (default: /tmp/episode_frames/<basename>)
    --positions p1,p2,...  Comma-separated list of positions as 0.0-1.0 fractions
    --end-minutes N        Extract one frame every second for last N minutes (default: 0.5)
    --opening-minutes N    Extract frames from first N minutes for opening credits (default: 5)

Output: JSON object with {duration_sec, frames: [{label, position_pct, timestamp_sec, path}, ...]}
"""

import sys
import os
import subprocess
import json


def get_duration(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', video_path],
        capture_output=True, text=True, check=True
    )
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def extract_frame(video_path, timestamp, output_path):
    subprocess.run(
        ['ffmpeg', '-ss', str(timestamp), '-i', video_path,
         '-vframes', '1', '-q:v', '2', output_path, '-y', '-loglevel', 'quiet'],
        check=True
    )
    return output_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Error: file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = f'/tmp/episode_frames/{base_name}'
    end_minutes = 0.5
    opening_minutes = 5
    custom_positions = None

    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        output_dir = sys.argv[idx + 1]

    if '--positions' in sys.argv:
        idx = sys.argv.index('--positions')
        custom_positions = [float(p) for p in sys.argv[idx + 1].split(',')]

    if '--end-minutes' in sys.argv:
        idx = sys.argv.index('--end-minutes')
        end_minutes = float(sys.argv[idx + 1])

    if '--opening-minutes' in sys.argv:
        idx = sys.argv.index('--opening-minutes')
        opening_minutes = float(sys.argv[idx + 1])

    os.makedirs(output_dir, exist_ok=True)

    duration = get_duration(video_path)
    print(f"Video duration: {duration:.1f}s ({duration/60:.1f}min)", file=sys.stderr)

    timestamps = []

    if custom_positions:
        for pos in custom_positions:
            timestamps.append(('custom', pos, duration * pos))
    else:
        # Opening credits: frames every 1s for the first `opening_minutes` minutes
        opening_end = min(opening_minutes * 60, duration * 0.3)
        t = 1.0
        while t <= opening_end:
            timestamps.append(('opening', t / duration, t))
            t += 1.0

        # End credits: frames every 1s for the last `end_minutes` minutes
        end_start = max(duration - end_minutes * 60, duration * 0.7)
        t = end_start
        while t <= duration - 2:
            timestamps.append(('end', t / duration, t))
            t += 1.0

    frame_paths = []
    for label, pos_frac, ts in timestamps:
        filename = f"{label}_{int(pos_frac * 1000):04d}_{int(ts):05d}s.jpg"
        output_path = os.path.join(output_dir, filename)
        try:
            extract_frame(video_path, ts, output_path)
            frame_paths.append({
                'label': label,
                'position_pct': round(pos_frac * 100, 1),
                'timestamp_sec': round(ts, 1),
                'path': output_path,
            })
            print(f"  {label} {pos_frac*100:.1f}% ({ts:.0f}s) → {output_path}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"  Failed at {ts:.0f}s: {e}", file=sys.stderr)

    print(json.dumps({'duration_sec': round(duration, 1), 'frames': frame_paths}, indent=2))


if __name__ == '__main__':
    main()
