#!/bin/bash
# usage: tools/rel.sh <versionName> <versionCode>   run from the repo root after the test gate passes
# Builds and signs the APK from game-signing (G1.9), checks it, then copies the game and the APK into docs/.
set -e
V=$1; C=$2; [ -n "$V" ] && [ -n "$C" ] || { echo "usage: tools/rel.sh <versionName> <versionCode>"; exit 1; }
BT=${BT:-/home/claude/android-sdk/build-tools/36.0.0}
export ANDROID_HOME=${ANDROID_HOME:-/home/claude/android-sdk}
export GAME_SIGNING=${GAME_SIGNING:-$(cd .. && pwd)/game-signing}   # next to this repo, never inside it
sed -i "s/versionCode [0-9]*; versionName '[^']*'/versionCode $C; versionName '$V'/" android/app/build.gradle
(cd android && gradle --no-daemon -q assembleRelease 2>&1 | grep -v -i "warning\|deprecat\|JAVA_TOOL\|^Note" | tail -5)
APK=android/app/build/outputs/apk/release/app-release.apk
$BT/apksigner verify --print-certs $APK 2>/dev/null | grep -m1 "SHA-256" | grep -q " 5db69ffb" || { echo "SIGN FAIL"; exit 1; }
$BT/aapt2 dump badging $APK 2>/dev/null | grep -E "^package|application-label:" | cut -c1-100
cp android/app/src/main/assets/index.html docs/play/index.html
cp $APK docs/downloads/PixelHollow-v$V.apk
unzip -p docs/downloads/PixelHollow-v$V.apk assets/index.html | cmp - docs/play/index.html && echo "apk and docs/play match"
bash tools/common/check_secrets.sh
