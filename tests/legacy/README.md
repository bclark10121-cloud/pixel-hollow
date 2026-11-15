# Retired tests

These early tests (v0.2 to v0.4) check behavior the game has since replaced on purpose:

- `t.py` and `t2.py` call `__reach`, which became `reachFrom` in v0.6.
- `t4.py` and `t6.py` expect the cabin door to show a line of text. Since v0.5 the door walks you into the cabin.

They stay here for history. The release gate does not run them.
