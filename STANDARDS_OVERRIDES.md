# Pixel Hollow: standards overrides

Standards: `GAME_STANDARDS.md` (rule ids start with G) and `ENGINEERING_STANDARDS.md` (rule ids start with E) in the private repo `bclark10121-cloud/game-standards`. This repo holds no copies.
This file lists where this game does something else, and why. A rule not listed here applies in full.
Order of authority: Brian in the chat, then this file, then the standards.

Last reviewed: v0.15.0 (2026-11-15).
Checked against: game-standards version 2026-11-15 (commit b2c2865).

## Overrides

| # | Rule | Standard says | This game does | Why | Ends when | Agreed |
|---|---|---|---|---|---|---|
| 1 | G6.1 | Landscape, 1280 x 720 base | Plays upright and sideways. Menus fit 12 screen sizes from 320 x 568 to 1920 x 1080 (`t22_fit`) | The game was built for a phone held upright since v0.1. Locking it sideways would change how every player holds it | Brian asks for landscape only | Proposed |

A Proposed row is not in force. The standard applies until Brian agrees.

## Open items (rule applies, work not finished)

- G5.1, G5.2: the top right shows three buttons (Journal, Map, Menu), not one Menu button that opens a row.
- G5.4, G5.5: the title card has the name, the tag line, the version and Start. It does not show the controls or the keys. They sit in Settings.
- G7.8: the game is one plain script, so its functions are page globals, and `window.__game` holds test helpers in every build. The tests set `window.__month` and similar before the game loads and open the file with no `?test` flag. Plan: gate `window.__game` and every test switch behind the whole-word `?test` flag and open every suite with it.
- G8.1: music and sounds are made in code, not tracks from Patch.gg.
- G1.4: the page has no privacy policy link yet. The old Helena Hollow policy covered the Google Play listing, which this game does not have.

## Rules met

Checked on 2026-11-15:

- G0.1 to G0.12.
- G1.1 to G1.11: one public repo, page in `docs/` on `main`, browser build in `docs/play/`, APK in `docs/downloads/`, notes in `docs/release-notes/`, the version line under the buttons, no key or password in the repo, a card on The Game Shelf and a footer link back, no personal names on the page.
- G2.1 to G2.7.
- G3.1 to G3.5.
- G4.1 to G4.6. G4.5: the Christmas theme starts off.
- G5.3: touch controls hide when a key or a controller is used (`keymode`).
- G5.6: settings and progress save on the device. G5.8: A chooses, B goes back, View and Menu open the Menu, button names follow the controller (View and Menu on an Xbox controller). `tests/t34_split.py` plays with only the kit's pretend Xbox controller.
- G6.2: package `com.brianclark.pixelhollow`, version code raised every build. G6.3: signed with the shared key, signature starts with `5db69ffb`.
- G6.4: the world is built in code.
- G7.2: `tests/t27_reach.py` proves every outdoor find is reachable on foot. G7.3, G7.4, G7.5.
- G8.3, G8.4.
- G10.1 to G10.4, G10.8: kit 1.5.0 is pulled with `common.lock`. `check_secrets.sh` and `page_check.py` run in the gate.

Not checked: G5.7 (units in player text). Sound. A real device. Not run this release: the full gate (`gate.sh`, `bot2.py`).

## Not in use in this game

- `ENGINEERING_STANDARDS.md` (all E rules): written for Godot. This game is one HTML file with no engine.
- G6.5, G6.6: no roads or decals. Paths are drawn into the ground.
- G7.1: no route to drive.
- G7.6: no rules-based matches.
- G10.7 and `addons/bc_common/`: Godot code, not used here.
- G8.2: no outside pictures or sounds.
- Proposed rules, not in force: G4.8, G4.9, G6.7, G7.6, G7.7.

## How to add an override

1. Flag the conflict to Brian with the options. Do not override by yourself.
2. Add the row as Proposed and list it as a judgment call in the report to Brian.
3. Once he agrees, put the date in the Agreed column.
4. When an override ends, move its row to Ended overrides with the date.
5. When an override fits every game, ask Brian to make it a standard. Then end the override.

## Ended overrides

None yet.
