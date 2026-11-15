# Pixel Hollow: project rules

Pixel Hollow is a quiet exploration and collecting game in pixel art, with no combat. It was split out of Helena Hollow, the 2D game, on 2026-11-15: the pixel view became this game. One HTML file in an Android WebView, plus the same file in the browser. This repo is public.

## Standards (G0.10, G10)

- Read `GAME_STANDARDS.md` (rule ids start with G) and `ENGINEERING_STANDARDS.md` (rule ids start with E) first. Both live only in the private repo `bclark10121-cloud/game-standards`. Clone it outside this repo. This repo holds no copies.
- Overrides, open items and the standards version this game was checked against live in `STANDARDS_OVERRIDES.md`. Order of authority: Brian in the chat, then `STANDARDS_OVERRIDES.md`, then the standards.
- The shared kit is pulled into `addons/bc_common/`, `tools/common/` and `tests/common/` with `bash <game-standards>/common/sync_common.sh <game-standards> .`. This game uses its tools and test helpers. The Godot helpers in `addons/bc_common/` are not used. Never edit those files here. Propose changes to Brian for `game-standards/common`.
- Signing: the key and its settings live in the private repo `bclark10121-cloud/game-signing` (G1.7). Clone it next to this repo. The Gradle build reads it through `GAME_SIGNING`. Never commit a key or password, and never write a password in a build file or a reply (G1.9).
- Only Brian approves an override. Add it as Proposed and list it as a judgment call. A Proposed row is not in force.

## Pillars (never break these)

1. No combat.
2. No limits. Unlimited bag, no energy bar, no pressure timers.
3. No way to lose.
4. Finding things is the reward.
5. Upgrades open doors.

## Rules

- The game is Pixel Hollow in everything a player reads. The place is the Hollow. Never use the name Helena in player text.
- One view: pixel. `CFG.gfx` is fixed to 0 and Settings has no Graphics choice.
- Package `com.brianclark.pixelhollow` from v0.15.0. It installs next to the old Helena Hollow app and does not replace it. Raise `versionCode` by one on every build.
- Saves: `pixelhollow_save_v1` (slot 1), `_s2`, `_s3`, settings `pixelhollow_cfg_v1`, album `pixelhollow_album_v1`. The first run copies an old `wandervalley_` browser save once. Save format `v:1`. Only add fields, each with a safe default.
- Never rename or remove a treasure id or set id. Backup codes start with `WV1:` and work in both split games.
- The meadow area (x under 60, y under 60) comes from a seeded loop. Do not change that loop. Add new content after it.
- Original names and art only (G8.4). Every outside asset goes in `CREDITS.md` with its licence.

## Layout

- `android/` the Gradle project. `android/app/src/main/assets/index.html` is the whole game: sprites and art drawn in code.
- `docs/` the game page (GitHub Pages from `main` `/docs`). `docs/play/index.html` is a copy of the game for the browser. `docs/downloads/` APKs. `docs/release-notes/v<version>.md`. `docs/.nojekyll` keeps the notes as plain files.
- `tests/` Playwright suites in headless Chrome. They load the working copy `/home/claude/game/index.html`: copy the game there first and run each suite from `tests/`.
- `tools/rel.sh` builds, signs, verifies and copies a release into `docs/`.

## Test gate

Three levels (G7.9, Brian 2026-11-15). Test what changed. The full run is only for an Android production release or when Brian asks. No release count triggers it.

1. Quick check, every build: `bash tools/common/sync_common.sh --check .` prints `COMMON check ok`. `bash tools/common/check_secrets.sh` prints `SECRETS check ok`. `python3 tests/t34_split.py pixel` prints `errors []`: the title card, one view, the save keys, Settings, and play with only the kit's pretend Xbox controller (G5.8).
2. Release check, every release: the quick check, a new suite or check for what changed, and the older suites for the areas it touched. `t22_fit` for any menu change. `t27_reach` for anything placed in the world. View a screenshot of each new screen.
3. Full gate: `bash tests/gate.sh` (copy `tests/` to `/home/claude/test/` first) plus `bot2.py`. Only before a Google Play or other Android production release, or when Brian asks (G7.9). A change to saves or world building runs the suites for those parts, not the full gate.

A failed check reruns alone once before it counts. Two fails stop the release and Brian hears about it before any game code changes.

## Deliver every time

1. Game page link: https://bclark10121-cloud.github.io/pixel-hollow/
2. GitHub repo link: https://github.com/bclark10121-cloud/pixel-hollow
3. The APK, named `PixelHollow-v<version>.apk`, in `docs/downloads/` and sent to Brian as a file.
4. `BACKLOG.md`, updated, linked and sent as a file.
5. The handoff zip from game-standards, sent as a file.
6. `docs/index.html` with the version line under the buttons (G1.8). `docs/release-notes/v<version>.md` with what is new, a test checklist and the kit version (G10.4). The workflow turns it into a GitHub Release with the APK.
7. The Game Shelf card in `bclark10121-cloud.github.io`: a fresh 960 x 540 picture in `images/pixel-hollow.jpg`, the version and any changed text (G1.10, G2.7). Give Brian the dashboard link https://bclark10121-cloud.github.io/

## Reporting to Brian

Lead with the links and files. Segment the answer. Short active sentences. No em dashes, no semicolons, no Oxford comma. State plainly what was tested and where, and what was not tested. List every judgment call.
