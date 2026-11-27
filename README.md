# World News — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/akbare12/news-26-b94-numbers/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/akbare12/news-26-b94-numbers/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image summing up the world's news on Thursday 26 November 2026:
**50 stories** — 3 heroes, 10 cards, 37 also.

## Heroes

1. **Macy's 100th Thanksgiving Parade postponed** — delayed by the East Coast
   storm, the first weather postponement in the parade's history; gusts hit
   60 mph. Rescheduled for Saturday 28 November, 08:30 ET.
2. **Hormuz: IRGC claims 2 tankers hit by mines** — a supertanker carrying
   2M barrels is among the vessels Iran says were mined near Khasab. The
   claim is unverified.
3. **Tariffs: markets rebound** — stocks rally as the new US tariffs on
   14 partners will not stack on the July duties; China faces 20%.

## How to read it

- `[C]` CONFIRMED · `[R]` REPORTED · `[CL]` CLAIM / 25 NOV EVENT.
- Every `[CL]` item happened on 25 November and is marked as such in the
  image; all other stories happened on 26 November.
- The date check at the top of the image says so plainly:
  "[CL] items happened 25 Nov — all others 26 Nov".
- The map pins every place to a story told in the image: New York, Khasab,
  Jazan, Cologne, Kyiv, Gaza, Bogor and Beijing. Jazan is pinned only
  because the image carries the matching story: "Jazan port: minor damage
  25 Nov" ([CL]).

## Build

`gen.py` (Pillow, build time only) renders `entry.png` (1024×1024).
`main.py` is standard-library only and copies `entry.png` into
`$MAKEFUN_OUTPUT_DIR`.

```sh
python3 gen.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verification

- `entry.png` SHA-256:
  `5099f9705594285d5a187e9aede3ae50aec831ac9055a6e485f2fe6bc2111804`
- `entry.png` size: 200644 bytes (1024×1024 px, under the 1 MiB cap)
- Rendered twice with `python3 gen.py`; both runs produced the identical
  SHA-256 above.
- Stdlib-only simulation (venv without Pillow, different working directory,
  empty output directory, read-only repo copy): exit 0, output SHA-256
  matches the committed `entry.png`.
- Content: 3 heroes + 10 cards + 37 ALSO = 50 stories, each tagged
  `[C]`, `[R]` or `[CL]`; every string measured with Pillow font metrics
  and asserted to fit — no silent truncation.
