# bodhixmusic.com

The home for BODHI X's musical life. Static site on GitHub Pages: plain HTML and CSS, no build step. Every colour, font, mark and component comes from the BODHI X brand system (private repo aicontentnow/bodhixmusic-brand, and the BODHI X Design System artifact).

## What is where

| Path | What |
|---|---|
| `index.html` | Home: the SEASØNS cover, the short bio, the four seasons, the era rooms, the socials |
| `seasons/index.html` | The SEASØNS room: the code-drawn branch ring, wind, winding the year, Today and Whole year. Share-safe: no audio, no lyrics, no dates |
| `404.html` | Page not found |
| `assets/tokens/tokens.css` | Brand tokens, copied from the brand repo (`tokens/tokens.css`) |
| `assets/css/bodhix.css` | Brand components, class prefix `bx-`, copied from the brand repo (`components/bodhix.css`) |
| `assets/css/site.css` | This site's page layout only |
| `assets/fonts/` | Inter variable (optical size and weight), from the brand repo, with its licence |
| `assets/marks/` | Favicon, year rings, wordmarks, from the brand repo |
| `assets/img/` | Web-size covers (600 and 1200 px) from SEASØNS / 00_Album / Cover, and the share images |
| `CNAME` | The custom domain. Do not delete it |

## Rules for every change

- No unreleased music in public. No audio until a song's release day.
- No dates on screen (decision 17). "Coming soon" and "Out now" instead.
- Never Bodhi's face, no photos of him.
- The spine only: paper, ink, the four season colours, Inter Display Light caps, the ring. The site never warms through the year.
- BODHI X in caps. SEASØNS with the Ø where it is read, plain letters in URLs and file names. No em dashes.
- Season-coloured text under 24 px uses the `-text` shades (`bx-spring`, `bx-summer`, `bx-autumn`, `bx-winter`).

## How to update a page

1. Edit the file in `~/Sites/bodhixmusic.com` on the Mac.
2. Look at it locally: `python3 -m http.server 8000` in the folder, then open http://localhost:8000.
3. Commit and push to `main`. GitHub Pages publishes in a minute or two.

```
cd ~/Sites/bodhixmusic.com
git add -A
git commit -m "What changed"
git push
```

If the brand system changes, copy the new `tokens.css`, `bodhix.css`, fonts or marks from the brand repo into `assets/`. Do not retype values.

## How a new song gets added

On the home page and in the room's Notes, each song is a `bx-song` row (`SPRING 02`, the title, then "Soon" or "Out now").

1. Before release: the row reads Soon, with no date.
2. On release day: change "Soon" to "Out now", give its dot the season class (`bx-dot spring`), and link the title to the song's listening links.
3. Audio on the site only from release day, and only if Bodhi asks. The prototype's player and timed lyrics live in the private prototype (claude.ai/artifact/A8D9aTuwSb6Yx89FyMjQYz) and can be switched on here per song: set `PUBLIC` to false only for released songs.
4. In `seasons/index.html`, the release marks on the ring light automatically from the release calendar in the code (`RAW`); song titles sit in `TITLES`.

New era rooms (Heavy Sun, The Next T-Shirt, the originals, the marriage years, after, now) follow the Design System's eras.md: one mark, one accent colour, its own page at `/<room>/`. Do not open a room until Bodhi does.

## How DNS is set

The domain is registered at Spaceship (registered to 2027-10-29). Records in Spaceship, Advanced DNS, bodhixmusic.com:

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | aicontentnow.github.io |
| TXT | _github-pages-challenge-aicontentnow | the verification value GitHub gave (keeps the domain claimed for this account) |

- The domain is verified on the aicontentnow account (github.com, Settings, Pages), so nobody else can point a Pages site at it.
- Repo Settings, Pages: deploy from `main`, root, custom domain `bodhixmusic.com`, Enforce HTTPS on. www redirects to the apex.
- No MX records yet: there is no mailbox at the domain. Never add a wildcard (`*`) record.
- Check: https://dns.google/resolve?name=bodhixmusic.com&type=A should list the four GitHub IPs.

## Defaults taken at launch (Bodhi can change any)

- Albums are sections (bodhixmusic.com/seasons), not subdomains.
- No audio before release day.
- No dates on screen.
- The ring is drawn in code.
- No mailing list yet; a spot is left on the home page.
- The repo is public (free GitHub Pages).
- No email at the domain yet.

## Room pages

Each older era can have its own room page at `/<room>/` that looks like that era's album, not like the calm home page. The home page stays in the SEASØNS spine look; the room is where the album's own style lives. Every room page keeps the BODHI X strip at the top (ring and BODHI X, linking home) and a "Back to BODHI X" link at the bottom.

- `/black-hat-villain/`: dark brick, bone white, blood red, Oswald and Special Elite (fonts self-hosted in `assets/rooms/black-hat-villain/` with their licences). My Generation cover, story, Bandcamp player, line-up, links to Bandcamp and youtube.com/@TheBlackHatNation.

- `/heavy-sun/`, `/the-next-t-shirt/`, `/the-originals/`, `/the-marriage-years/`: built by `tools/build-rooms.py` (text and track lists live in it; run it with the fonts and covers folders to rebuild). Each wears its album: Heavy Sun sunburst and marker type; the next t-shirt handwriting with the red "the"; the 2008 SEASONS circles in Baskerville with the four 2019 remaster covers; Unreleased Gems sky blue, orange and Josefin Sans. Fonts self-hosted in `assets/rooms/fonts/` with their licences.
- Album covers that show Bodhi are fine (Bodhi, 2026-11-03): The Fifth Floor and Unreleased Gems use their real covers.
- The home page shows only a blurb and an Enter the room button per room. All outside links live inside the rooms.

## The player (assets/js/dock.js)

One player for the whole site. Every album in a room has a Play button; it loads that album's Bandcamp player into a bar at the bottom of the screen (cover, album and room, a hide button and a close button). While the bar is loaded, links inside the site swap the page content instead of reloading, so the music keeps playing on every page, including Back and Forward.

- Every page loads `/assets/js/dock.js` in its head. A new page needs that one line and nothing else.
- A Play button is any element with `class="play-album"` and `data-album` (the Bandcamp album id), `data-title`, `data-room`, `data-room-href`, `data-cover`.
- Pages with their own scripts must carry `<meta name="bx-isolate" content="1">` (the SEASØNS room does). While the player is loaded they open inside a frame above the bar, so their code never mixes with the player. Their site links still go through the player.
- With the player closed, the site behaves like plain pages.
- When SEASØNS songs go public, the SEASØNS room's own audio should pause the bar (or play through it). Decide then.

## Pre-save and Listen button (Watch You Grow)

Two copies, both hidden now: under Enter SEASØNS on the home page (`index.html`) and in the SEASØNS notes (`seasons/index.html`), each a `<p class="presave-wrap" data-presave hidden>`.
- **When the HyperFollow link exists (after the DistroKid upload, by Dec 17):** put the link in both `href=""` and delete `hidden` from both.
- **Release day (Fri Mar 19, 2027):** change both labels from "Pre-save Watch You Grow" to "Listen to Watch You Grow". The HyperFollow link stays the same; it turns into store buttons by itself.
- Later: Spotify and Apple artist pages go in the Follow list once they exist (icons are ready in the sprite).
