[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/dashlabib/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/dashlabib/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

# The Daily Globe — 26 November 2026

A newspaper front page that sums up Thursday 26 November 2026 in one image.
Built from real news reported by about 00:40 UTC that day, it is drawn
entirely in code: a hand-built 5x7 bitmap font, hand-drawn scenes, and a
hand-rolled PNG encoder, using only the Python standard library. No network,
no images, no external fonts — the output is byte-identical on every run.

## Stories on the front page

- **Lead — Trade war:** Washington proposes new tariffs on 14 trading
  partners — up to 25% on Indian goods (17% if a trade deal is reached), up
  to 15% on Taiwan in a Section 301 overcapacity probe.
- **Markets:** Nasdaq sinks about 4% on the AI rout and tariff fears; Taiwan
  shares fall 1,927 points; the NT dollar weakens past 33 per dollar; the
  Fed Beige Book shows modest growth, wage gains, and persistent price
  pressure.
- **South Africa:** a court rules the Ramaphosa impeachment report unlawful.
- **Cuba:** the WHO chief urges an end to the US fuel blockade on Cuba.
- **Philippines:** a Chinese long-range bomber flies within 45 nautical
  miles of the Philippine coast, about 170 from Manila.
- **North Korea:** North Korea orders Switzerland to close its newly opened
  diplomatic office in Pyongyang; its senior diplomat must leave within 48
  hours.
- **Canary Islands:** nearly 2,000 migrants reach Spain's Canary Islands in
  a record single-day arrival.
- **Space:** Pakistan's Muhammad Zeeshan Ali becomes the first foreign
  astronaut aboard China's Tiangong station (Shenzhou-24).
- **Sport:** Real Madrid thrash PSV 5-1 (Mbappe brace, Bellingham stunner);
  South Africa sweep Bangladesh 2-0 in the 2nd Test; 1,220 players register
  for the IPL 2027 auction; Gukesh faces Sindarov in the World Chess
  Championship.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, under 1 MiB).

Check determinism and size:

```sh
python3 main.py --self-test
```

The self-test renders the page twice into fresh temporary directories and
exits 0 only if the bytes are identical and within the 1 MiB limit.

## Referral

Referral code: `q5gfrt9g`

https://make.fun/bounty/news-image-20261126

## License

MIT — see `LICENSE`.
