# Pixel Hollow: backlog

Updated 2026-11-18 with v0.19.0. BC decides the order.

## Done

- v0.19.0 (2026-11-18), Release 8 and the title track (kit 1.14.0): Back at the top left of every full-screen card through the kit `BC.header` (asked for by BC, G5.30). The fit check passes at 12 sizes upright and sideways (G6.18). The start screen plays "Airship Serenity" (asked for by BC, G5.21).

### Judgment calls in v0.19.0 (BC to confirm)

1. Your character keeps Done (not Back) at the top left: it confirms the look.
2. The Journal's "< Back" page button became "< Prev", so it is not mistaken for the panel's Back.
3. The title track is inlined in the page as base64, so the page and the APK stay one file. The page grew from about 0.45 MB to about 2.8 MB.
4. A browser that cannot decode Ogg Vorbis keeps the game's own tune on the start screen.
5. Photo mode's Done bar stays at the bottom: it is a bar over the picture, not a panel.

- v0.18.0 (Release 7, kit 1.13.0): Records with the 18 stamps and 7 stats, Change controls for keys and buttons, Run with Hold or Toggle, old-save checks, the error log in Copy bug report and sound through the kit mixer.
- v0.1 to v0.14.8 as Helena Hollow, the 2D game with a pixel view and an angled view: six regions, 148 finds in 28 sets, museum, cabin, garden, fishing, bugs, neighbors, festivals, cooking, the merchant, photo mode, the Christmas theme.
- v0.15.0 (2026-11-15): split out as Pixel Hollow, its own public repo and game page. The pixel view only. Its own Android package and save. View opens the Menu like the Menu button.
- v0.16.0 (2026-11-16): the standards catch-up, with no new content (Release 4, BC 2026-11-15, 11:44 PM: "move forward with the last games"). The By Lantern's Glow v0.16.0 pattern on kit 1.9.1. Its own app icon: an open pixel treasure chest on a grassy hill at night. Five save slots with Delete. One Menu button that opens a row at the top. The shared Settings menu: Music and Sound in five levels, Frame rate, Rumble, Text size, Reduce motion, Controls and Reset settings. Tester tools behind a code in test builds. Hints for the device in use. A pause when the controller drops. The second press before anything is lost. Test hooks only with `?test`. A privacy page. GitHub Releases. The source moved to the private `game-studio` repo. Version code 2.
- v0.17.0 (2026-11-17, Release 6): the shared start screen (G5.21), a pixel Lantern Hill with a chest under the lamp, and the talk box (G5.20) from By Lantern's Glow: parchment, ribbon names, writing-out text, pages, Press A for more or to close, voice blips with a Settings switch.

## Now

1. BC tries v0.16.0 on a real phone and an Xbox controller.
2. Open items in `STANDARDS_OVERRIDES.md`: Patch.gg music (G8.1).

## Asked for by BC, not built yet

1. Suno music, optional (BC, 2026-11-16, waits on G8.7). Music is made in code on purpose. A pixel-style Suno set is one way to close the G8.1 open item, only if BC wants a fuller sound.

## Ideas to choose from (BC picks by number)

1. A short what's-new card the first time a player opens a new version.

## Unfinished standards items (2026-11-16)

From the Open items in `STANDARDS_OVERRIDES.md`, plus what has not been tried on a real device. Each line comes off when it is done. BC picks when.

- G8.1: music and sounds are made in code, not tracks from Patch.gg.
- G5.11: Rumble on an Xbox controller in the Android app. The browser uses the browser's gamepad rumble. The Android app vibrates the phone only.
- Real device check: a phone, the Retroid, an Xbox controller and sound. Nothing has been tried on a real device since the split.

## Later

1. Nothing yet.

## Not planned (they break the pillars)

1. Swords, shields, enemies and bosses.
2. Hearts, damage, healing items and a hard mode.
3. Timed challenges that hold back a reward.
4. Leaderboards and opponents.
5. Copying characters, names, art, music or maps from any other game.
6. Google Play (BC, 2026-11-15, 10:07 PM: there is no Google Play store).

## Decisions from BC

- 2026-11-15: the pixel game becomes Pixel Hollow and the angled game becomes By Lantern's Glow, each in one public repo under the shared standards. Both start fresh with new Android packages. Old Helena Hollow installs stay as they are.
- 2026-11-15: both start at v0.15.0, after Helena Hollow v0.14.8.
- 2026-11-15: three test levels: a quick check every build, a release check every release, the full gate every 5th release and before production.
- 2026-11-15 (later): the every 5th release full gate is withdrawn. The full gate runs only before an Android production release or when BC asks (G7.9).
- 2026-11-15, 10:07 PM: no Google Play store and no end-to-end testing in this project. Every Proposed override row agreed, row 1 included.
- 2026-11-15, 11:44 PM: "move forward with the last games". Pixel Hollow gets its catch-up now. Unfinished items go in each game's backlog.

## Judgment calls made in v0.16.0 (BC to confirm or change)

1. The game file is By Lantern's Glow's v0.16.0 file with this game's names, save keys, tag line and pixel view. The two files were about 20 lines apart at v0.15.0.
2. The icon is new pixel art: an open treasure chest on a grassy hill under a night sky. No other game uses it.
3. On a phone held upright the Menu row uses tighter buttons. The wider pixel font made the row reach two thirds of the screen.
4. The loading screen reads "Waking the Hollow".
5. The version code goes from 1 to 2. v0.16.0 installs over v0.15.0 and keeps the saves.

## Judgment calls in v0.17.0 (BC to confirm)

1. The start screen and talk box for the two plain HTML games live in each game file, copied from By Lantern's Glow, not in the shared kit. Only these two HTML games have them.
2. The pixel start screen draws the night scene at a third of the screen size, so it reads as chunky pixels.

## Judgment calls in v0.18.0 (BC to confirm)

1. Records shows the game's own 18 stamps as its achievements, the same as Keeper of the Hollow. Ten Sets and Curator take longer than two hours. They were in the game before G4.10.
2. Change controls replaces the old controller rows in Settings, so keys and buttons live on one page. Old button choices carried over.
3. Menu, View and B cannot be picked, so the Menu and Back always work. Walking stays on the stick and D-pad.
4. Run has a keyboard key now (Shift), so Hold or Toggle works on keys too.
5. Sound is made in code, so there are no files for `loudness.py`. The sound runs through the kit mixer.
6. Backup codes stay the game's own `WV1:` codes (they already meet G5.19).

## Open items from v0.18.0

1. Release 8: Back at the top of every panel and both orientations (G5.30, G6.18). The web kit needs the header first.

