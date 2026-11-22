# The World Today — Sunday, 22 November 2026

A one-page, map-led newspaper front page summing up the world news of
Sunday 22 November 2026, built for the make.fun competition
`news-image-20261122`.

## What's on the page

- **Lead:** Iran widens the Gulf war — a US air base in Kuwait is hit,
  Bahrain is struck, and tankers burn in the Strait of Hormuz. A drawn
  world map carries numbered markers for the lead and every story card.
- **12 illustrated cards:** COP31 nears a deal in Antalya; Verstappen on
  pole for the Las Vegas night race; a 'triple-tap' strike kills a boy
  and a paramedic in Kryvyi Rih; drones set the Russian cargo ship
  Sparta II ablaze in the Gulf of Finland; a magnitude 6.9 quake shakes
  Peru's Andes; an AI rout wipes out the Nasdaq's 2026 gains; Mexico
  captures cartel boss 'El Chapo Isidro'; Estonia closes its border
  with Russia; 11 die drinking illicit alcohol in Manipur; the RSF is
  accused of killing civilians in West Kordofan; the US loses measles
  elimination status; an Air Niugini jet lands safely after an engine
  fire warning.
- **12 more stories** in a regional text list, plus a 6-item ticker:
  31 stories across 7 regions in all.

## How it works

- `stories.json` holds the day's stories (region, headline, summary,
  scene motif, map coordinates).
- `generate.py` draws the 1024x1024 front page with Pillow: masthead,
  a world map with numbered story markers, the lead panel, a 4x3 grid
  of illustrated story cards (every scene drawn from shapes in code),
  a two-column text list, a ticker strip and a footer. Nothing is
  downloaded.
- `main.py` copies the committed `entry.png` to `MAKEFUN_OUTPUT_DIR`
  (or `/output`).

The output is deterministic: the same `stories.json` always produces a
byte-identical `entry.png`.

## Run it

```
python3 generate.py          # writes ./entry.png (needs Pillow)
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/DavidQlla06/news-image-20261122-v4/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/DavidQlla06/news-image-20261122-v4/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
