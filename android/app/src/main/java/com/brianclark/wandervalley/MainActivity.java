package com.brianclark.wandervalley;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.window.OnBackInvokedDispatcher;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.DisplayCutout;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowInsets;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import java.util.Locale;
import org.json.JSONObject;

public class MainActivity extends Activity {
    private WebView web;
    private int namedDevice = -1;
    /** Camera cutout insets in CSS pixels: top, right, bottom, left. */
    private volatile String safe = "0,0,0,0";

    /** Small bridge the game calls for things a web page cannot do on its own. */
    private class Bridge {
        @JavascriptInterface public void quit() { runOnUiThread(() -> finish()); }
        /** Save backup helpers: copy, paste and share a text code. */
        @JavascriptInterface public void copy(final String t) {
            runOnUiThread(() -> { try { ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                if (cm != null) cm.setPrimaryClip(ClipData.newPlainText("Pixel Hollow backup", t)); } catch (Exception ignored) { } });
        }
        @JavascriptInterface public String paste() {
            try { ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                ClipData c = cm == null ? null : cm.getPrimaryClip();
                if (c != null && c.getItemCount() > 0) { CharSequence cs = c.getItemAt(0).coerceToText(MainActivity.this); return cs == null ? "" : cs.toString(); }
            } catch (Exception ignored) { }
            return "";
        }
        @JavascriptInterface public void share(final String t) {
            runOnUiThread(() -> { try { Intent i = new Intent(Intent.ACTION_SEND); i.setType("text/plain");
                i.putExtra(Intent.EXTRA_SUBJECT, "Pixel Hollow backup"); i.putExtra(Intent.EXTRA_TEXT, t);
                startActivity(Intent.createChooser(i, "Save backup code")); } catch (Exception ignored) { } });
        }
        /** Photo mode: saves a JPEG to Pictures/Pixel Hollow. Returns "ok" or where it went. */
        @JavascriptInterface public String savePhoto(String b64, String name) {
            try {
                byte[] data = Base64.decode(b64, Base64.DEFAULT);
                String safe = name == null ? "PixelHollow.jpg" : name.replaceAll("[^A-Za-z0-9_.-]", "");
                if (!safe.endsWith(".jpg")) safe = safe + ".jpg";
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentResolver r = getContentResolver();
                    ContentValues v = new ContentValues();
                    v.put(MediaStore.Images.Media.DISPLAY_NAME, safe);
                    v.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
                    v.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/Pixel Hollow");
                    v.put(MediaStore.Images.Media.IS_PENDING, 1);
                    Uri u = r.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v);
                    if (u == null) return "error";
                    try (OutputStream o = r.openOutputStream(u)) { if (o == null) return "error"; o.write(data); }
                    v.clear(); v.put(MediaStore.Images.Media.IS_PENDING, 0);
                    r.update(u, v, null, null);
                    return "ok";
                }
                // Android 9 and older: no gallery access without a storage permission, so keep it in the app folder
                File dir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
                if (dir == null) return "error";
                if (!dir.exists()) dir.mkdirs();
                try (FileOutputStream o = new FileOutputStream(new File(dir, safe))) { o.write(data); }
                return "in Android/data/" + getPackageName() + "/files/Pictures";
            } catch (Exception e) { return "error"; }
        }
        @JavascriptInterface public String safeArea() { return safe; }
        @JavascriptInterface public void vibrate(int ms) {
            try {
                Vibrator v = (Vibrator) getSystemService(VIBRATOR_SERVICE);
                if (v == null || !v.hasVibrator()) return;
                ms = Math.max(1, Math.min(ms, 500));
                if (Build.VERSION.SDK_INT >= 26) v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE));
                else v.vibrate(ms);
            } catch (Exception ignored) { }
        }
    }

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);   // keeps the save file and settings on the device
        s.setMediaPlaybackRequiresUserGesture(false);
        web.addJavascriptInterface(new Bridge(), "Android");
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setBackgroundColor(0xFF1D2B24);
        web.setFocusable(true);
        web.setFocusableInTouchMode(true);
        setContentView(web);
        // Android 15 and newer draw the game edge to edge, under any camera cutout. Pass the cutout size to the game.
        web.setOnApplyWindowInsetsListener((v, in) -> {
            int t = 0, r = 0, bt = 0, l = 0;
            if (Build.VERSION.SDK_INT >= 28) {
                DisplayCutout c = in.getDisplayCutout();
                if (c != null) { t = c.getSafeInsetTop(); r = c.getSafeInsetRight(); bt = c.getSafeInsetBottom(); l = c.getSafeInsetLeft(); }
            }
            float d = getResources().getDisplayMetrics().density;
            String n = String.format(Locale.US, "%.1f,%.1f,%.1f,%.1f", t / d, r / d, bt / d, l / d);
            if (!n.equals(safe)) { safe = n; js("window.__safe&&__safe(" + n + ")"); }
            return v.onApplyWindowInsets(in);
        });
        web.loadUrl("file:///android_asset/index.html");
        web.requestFocus();
        // Android 13+: back gestures go to the game as well. On Android 16 this replaces the Back key event.
        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    OnBackInvokedDispatcher.PRIORITY_DEFAULT, () -> js("window.__back&&__back()"));
        }
    }

    private void js(String code) { web.evaluateJavascript(code, null); }

    private void nameDevice(InputDevice d) {
        if (d == null || d.getId() == namedDevice) return;
        namedDevice = d.getId();
        js("window.__padName&&__padName(" + JSONObject.quote(d.getName()) + ")");
    }

    /** Android button codes to the standard gamepad layout the game uses. */
    private static int mapKey(int k) {
        switch (k) {
            case KeyEvent.KEYCODE_BUTTON_A: return 0;
            case KeyEvent.KEYCODE_BUTTON_B: return 1;
            case KeyEvent.KEYCODE_BUTTON_X: return 2;
            case KeyEvent.KEYCODE_BUTTON_Y: return 3;
            case KeyEvent.KEYCODE_BUTTON_L1: return 4;
            case KeyEvent.KEYCODE_BUTTON_R1: return 5;
            case KeyEvent.KEYCODE_BUTTON_L2: return 6;
            case KeyEvent.KEYCODE_BUTTON_R2: return 7;
            case KeyEvent.KEYCODE_BUTTON_SELECT: return 8;
            case KeyEvent.KEYCODE_BUTTON_START: return 9;
            case KeyEvent.KEYCODE_BUTTON_THUMBL: return 10;
            case KeyEvent.KEYCODE_BUTTON_THUMBR: return 11;
            case KeyEvent.KEYCODE_DPAD_UP: return 12;
            case KeyEvent.KEYCODE_DPAD_DOWN: return 13;
            case KeyEvent.KEYCODE_DPAD_LEFT: return 14;
            case KeyEvent.KEYCODE_DPAD_RIGHT: return 15;
            default: return -1;
        }
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent e) {
        int code = e.getKeyCode(), src = e.getSource();
        boolean pad = (src & InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD
                || (src & InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK
                || KeyEvent.isGamepadButton(code);
        int idx = mapKey(code);
        if (pad && code == KeyEvent.KEYCODE_BACK) idx = 1;   // some pads send B as Back
        if (pad && idx >= 0) {
            nameDevice(e.getDevice());
            if (e.getAction() == KeyEvent.ACTION_DOWN && e.getRepeatCount() == 0) js("window.__padKey&&__padKey(" + idx + ",1)");
            else if (e.getAction() == KeyEvent.ACTION_UP) js("window.__padKey&&__padKey(" + idx + ",0)");
            return true;
        }
        if (code == KeyEvent.KEYCODE_BACK) {                  // system Back opens the pause menu, never quits
            if (e.getAction() == KeyEvent.ACTION_UP) js("window.__back&&__back()");
            return true;
        }
        return super.dispatchKeyEvent(e);
    }

    @Override
    public boolean dispatchGenericMotionEvent(MotionEvent e) {
        if ((e.getSource() & InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK && e.getAction() == MotionEvent.ACTION_MOVE) {
            nameDevice(e.getDevice());
            float lt = Math.max(e.getAxisValue(MotionEvent.AXIS_LTRIGGER), e.getAxisValue(MotionEvent.AXIS_BRAKE));
            float rt = Math.max(e.getAxisValue(MotionEvent.AXIS_RTRIGGER), e.getAxisValue(MotionEvent.AXIS_GAS));
            js(String.format(Locale.US, "window.__padAxes&&__padAxes(%.3f,%.3f,%.3f,%.3f,%.3f,%.3f)",
                    e.getAxisValue(MotionEvent.AXIS_X), e.getAxisValue(MotionEvent.AXIS_Y),
                    e.getAxisValue(MotionEvent.AXIS_HAT_X), e.getAxisValue(MotionEvent.AXIS_HAT_Y), lt, rt));
            return true;
        }
        return super.dispatchGenericMotionEvent(e);
    }

    @Override
    public void onWindowFocusChanged(boolean has) {
        super.onWindowFocusChanged(has);
        if (has) web.setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    @Override protected void onPause() { js("window.__pauseAudio&&__pauseAudio()"); super.onPause(); web.onPause(); }
    @Override protected void onResume() { super.onResume(); web.onResume(); js("window.__resumeAudio&&__resumeAudio()"); }
}
