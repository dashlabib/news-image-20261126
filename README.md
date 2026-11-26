# news-image-20261126

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)
![make.fun bounty](https://make.fun/badge/news-image-20261126.svg)

Round 1 entry for the make.fun bounty
[news-image-20261126](https://make.fun/bounty/news-image-20261126):
**"Sum up 26 November's world news in one image"** ($100).

A newspaper-style front page for **Thursday 26 November 2026**, drawn
entirely in pure-Python code (standard library only — no PIL, no network,
no fonts; the PNG is written with `zlib` + `struct` and text uses a
hand-built 5x7 bitmap font). Built from the real news reported by about
00:40 UTC, when the news day had barely begun in UTC but was well under
way in Asia; an improvement round will follow later in the day once more
of the day's news is in.

## The day it sums up

- **Lead — Trade war:** Washington proposes new tariffs on 14 trading
  partners — up to 25% on Indian goods (17% if a trade deal is reached),
  up to 15% on Taiwan in a Section 301 overcapacity probe.
- **Markets:** Nasdaq sinks about 4% on the AI rout and tariff fears;
  Taiwan shares fall 1,927 points; Fed Beige Book: modest growth,
  prices still high.
- **South Africa:** court rules the Ramaphosa impeachment report
  unlawful.
- **Cuba:** WHO chief urges an end to the US fuel blockade.
- **Philippines:** Chinese bomber flies within 45 nautical miles of the
  coast.
- **North Korea:** orders Switzerland to close its Pyongyang office in
  48 hours.
- **Canary Islands:** nearly 2,000 migrants arrive in a record single
  day.
- **Space:** Pakistan's Zeeshan Ali becomes the first foreign astronaut
  aboard China's Tiangong station.
- **Sport:** Real Madrid thrash PSV 5-1 (Mbappe brace); South Africa
  sweep Bangladesh 2-0; 1,220 players register for the IPL 2027 auction;
  Gukesh faces Sindarov in the World Chess Championship.
- **Wire:** six dead in a US plane crash; NATO boosts eastern-flank air
  surveillance; UN: five women killed every hour; Trump seeks faster
  federal executions; Miss Universe: Puerto Rico's Jennifer Barreto.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` — 1024x1024 PNG, well under 1 MiB, byte-identical
on every run. Check determinism with:

```sh
python3 main.py --self-test
```

## Referral

Referral code: **q5gfrt9g** — https://make.fun/bounty/news-image-20261126

## License

MIT — see [LICENSE](LICENSE).
