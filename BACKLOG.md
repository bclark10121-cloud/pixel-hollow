# Pixel Hollow: backlog

Updated 2026-11-15 with v0.15.0. BC decides the order.

## Done

- v0.1 to v0.14.8 as Helena Hollow, the 2D game with a pixel view and an angled view: six regions, 148 finds in 28 sets, museum, cabin, garden, fishing, bugs, neighbors, festivals, cooking, the merchant, photo mode, the Christmas theme.
- v0.15.0 (2026-11-15): split out as Pixel Hollow, its own public repo and game page. The pixel view only. Its own Android package and save. View opens the Menu like the Menu button.

## Now

1. Open items in `STANDARDS_OVERRIDES.md`: test hooks only with `?test` (G7.8), one Menu button with a row (G5.1), controls on the title card (G5.4, G5.5).

## Asked for by BC, not built yet

1. A new app icon of its own. Today it uses the Helena Hollow icon.

## Ideas to choose from (BC picks by number)

1. A short what's-new card the first time a player opens v0.15.0.
2. A Google Play listing of its own.

## Unfinished standards items (2026-11-15)

From the Open items in `STANDARDS_OVERRIDES.md`, plus what has not been tried on a real device. Each line comes off when it is done. BC picks when.

- The standards catch-up (Release 4, BC said go on 2026-11-15, 11:44 PM): the By Lantern's Glow v0.16.0 pattern on kit 1.9.1.
- G1.7: move the source into the private `game-studio` repo. This repo keeps the page, the builds, the release notes and the backlog.
- G5.1, G5.2: one Menu button at the top right that opens a row, in place of Journal, Map and Menu.
- G5.4, G5.5: the controls for the device in use on the title card.
- G5.9 to G5.17: kit Settings, five save slots, Tester tools, device hints, the pause on controller loss, the Menu order and the second press.
- G6.10: an icon of its own. The old Helena Hollow lantern is its only icon today.
- G7.8: `window.__game` and every test switch only with the whole-word `?test` flag.
- G1.4, G6.13: a privacy page linked from the game page.
- G2.10, G1.12: GitHub Releases with the APK and the newest two APKs on the page.
- G8.1: music and sounds are made in code, not tracks from Patch.gg.
- Real device check: a phone, the Retroid, an Xbox controller and sound.

## Later

1. Google Play: a listing and a 14 day closed test with 12 testers.

## Not planned (they break the pillars)

1. Swords, shields, enemies and bosses.
2. Hearts, damage, healing items and a hard mode.
3. Timed challenges that hold back a reward.
4. Leaderboards and opponents.
5. Copying characters, names, art, music or maps from any other game.

## Decisions from BC

- 2026-11-15: the pixel game becomes Pixel Hollow and the angled game becomes By Lantern's Glow, each in one public repo under the shared standards. Both start fresh with new Android packages. Old Helena Hollow installs stay as they are.
- 2026-11-15: both start at v0.15.0, after Helena Hollow v0.14.8.
- 2026-11-15: three test levels: a quick check every build, a release check every release, the full gate every 5th release and before production.
- 2026-11-15 (later): the every 5th release full gate is withdrawn. The full gate runs only before an Android production release or when BC asks (G7.9).
