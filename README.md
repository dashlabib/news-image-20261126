[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/dashlabib/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/dashlabib/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# The Daily Globe — Thursday 26 November 2026

A newspaper front page for Thursday 26 November 2026, drawn entirely by a small Python program using only the standard library. No images, fonts or network calls are used: the page is painted pixel by pixel, the letters come from a hand-made 5x7 bitmap font defined in `main.py`, and the PNG file is encoded by hand with `zlib` and `struct`.

## Stories on the page

- **Lead — Trade war:** Washington proposes new Section 301 tariffs on 14 trading partners. China faces 20%, rising to 40% if the trade truce lapses on 10 January; India 17% with a deal, 25% without; Vietnam 20% with a deal, 35% without; the EU, Japan, South Korea and Taiwan broadly capped at 15%. Major economies push back; a hearing and public comment come first, with the earliest effect in January.
- **Markets:** Shares slide on tariff fears and the AI rout — Nasdaq down about 4%; Taiwan shares fall 1,927 points; the NT dollar weakens past 33 per US dollar. The Fed's Beige Book reports modest growth with persistent price pressure. A memory-chip shortage triples some RAM prices.
- **Gaza:** Israeli strikes and gunfire kill at least nine Palestinians overnight, including Hamas-appointed deputy education minister Khaled Abu Nada and his wife in Deir al-Balah — a third straight night of strikes despite a year-old ceasefire. The UN rights chief warns of a widening risk of atrocity crimes.
- **Ukraine:** Russian ballistic missiles hit Kyiv overnight, wounding seven and hitting a shopping centre; Moscow says it struck drone sites. Ukraine says its drones set fire to a key oil pipeline hub in Bashkortostan.
- **North Korea:** Kim Jong Un inspects nuclear facilities and vows to expand the arsenal and widen tactical nuclear weapons deployment, calling nuclear status irreversible. Separately, Ukraine's intelligence says Kim personally suspended North Korean military support to Russia.
- **Europe:** EU leaders meet in Brussels over the next EU budget and more Ukraine funding, split over who pays. France says talks cannot run past December; Slovakia, Hungary, Bulgaria and the Czech Republic resist an extra Ukraine loan (a 45-billion-euro loan for 2027 is proposed).
- **Britain:** UK net migration falls to 77,000 in the year to June, down from 204,000 — the lowest since 1997 outside the pandemic, and about 90% below the 2023 peak of nearly a million.
- **Space / Tech:** Elon Musk pledges two SpaceX shares for every child in the US (about 72 million children; worth about $18 billion). Hours earlier SpaceX won US approval to deploy 1 million satellites for space-based data centres.
- **Thanksgiving (US):** The 100th Macy's Thanksgiving Day Parade marches in New York — a record 100 inflatables, 3.5 hours, NBC. Thanksgiving football: a five-game NFL slate.
- **In brief:** Pakistan's Muhammad Zeeshan Ali becomes the first foreign astronaut aboard China's Tiangong station, flying on Shenzhou-24. Nearly 2,000 migrants reach Spain's Canary Islands in a single day — a record daily arrival. A court rules the impeachment report against President Ramaphosa unlawful. The WHO chief urges an end to the US fuel blockade on Cuba. Duran Duran guitarist Andy Taylor dies at 65. The Congo Ebola outbreak passes 12,000 cases. A 5.4-magnitude earthquake jolts Nepal.
- **Sport:** Real Madrid beat PSV 5-1 (Mbappe scores twice); South Africa sweep Bangladesh 2-0 in the Test series; holders Italy beat South Korea to reach the Davis Cup semi-finals; 1,220 players register for the IPL 2027 auction.

Proposals and pledges are worded as proposals and pledges, not as facts already in effect.

## Run

```bash
python3 main.py
```

This writes `./out/entry.png` (1024x1024, under 1 MB). To choose a different output folder, set the environment variable first:

```bash
MAKEFUN_OUTPUT_DIR=/path/to/folder python3 main.py
```

The program needs Python 3.13 and nothing else — standard library only, no pip packages, no network access, no files read at run time.

## Self-test

```bash
python3 main.py --self-test
```

The self-test renders the page twice into two fresh temporary directories and exits 0 only if the two files are byte-identical, the file is at most 1,048,576 bytes, and the image is exactly 1024x1024. It prints the size and SHA-256 hash of the render.

## Referral

Referral code: `q5gfrt9g`

https://make.fun/bounty/news-image-20261126

## Licence

MIT — see the licence note: this project is released under the MIT Licence.
