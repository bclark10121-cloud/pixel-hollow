#!/usr/bin/env python3
# v0.15.0: the split out of Helena Hollow. One view only, the new name and version on the title card, its own save keys
# with a one-time copy of an old Helena Hollow browser save, no Graphics choice in Settings, and the title card, the
# pause menu and play with only a pretend Xbox controller (G5.8). Takes the page screenshots too.
#   t34_split.py <pixel|lantern> [game file] [shot folder]
import asyncio, json, os, sys
from playwright.async_api import async_playwright
G = {"pixel": ("Pixel Hollow", 0, "pixelhollow"), "lantern": ("By Lantern's Glow", 1, "lanternsglow")}[sys.argv[1]]
NAME, GFX, KEY = G
GAME = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/game/index.html"
SHOTS = sys.argv[3] if len(sys.argv) > 3 else "/home/claude/shots_split"
os.makedirs(SHOTS, exist_ok=True)
VER = "v0.15.0"
# an old Helena Hollow browser save with the other view chosen, written before the game loads
OLD = ("if(!localStorage.getItem('seeded')){localStorage.setItem('seeded','1');"
       "localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:%d}));"
       "localStorage.setItem('wandervalley_save_v1',JSON.stringify({v:1,x:232,y:442,boots:true,started:true,"
       "ch:{name:'Keeper',pro:0,body:0,skin:1,hs:0,hc:0,hat:0,shirt:0,bot:0,pc:0},found:['daisy','bluebell','poppy','sunflower','clover','scallop','conch','starfish']}))}") % (1 - GFX)
# the kit's pretend Xbox controller (tests/common/webkit.py in the Godot games), standard browser gamepad layout
PAD = """(() => {
  const pad = {id: "Xbox Wireless Controller (STANDARD GAMEPAD Vendor: 045e Product: 0b13)", index: 0, connected: true,
    mapping: "standard", timestamp: 0, axes: [0, 0, 0, 0], buttons: Array.from({length: 17}, () => ({value: 0, pressed: false, touched: false}))};
  Object.defineProperty(navigator, "getGamepads", {value: () => [pad, null, null, null], configurable: true});
  window.__pad_button = (b, v) => { pad.buttons[b].value = v; pad.buttons[b].pressed = v > 0.5; pad.timestamp = performance.now(); };
  window.__pad_axes = (x, y) => { pad.axes = [x, y, 0, 0]; pad.timestamp = performance.now(); };
})();"""
BTN = {"A": 0, "B": 1, "X": 2, "Y": 3, "VIEW": 8, "MENU": 9}
errs = []

def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what, flush=True)
    if not ok: errs.append(what)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        # ---- 1: an old save moves over, the title card, one view, Settings ----
        ctx = await b.new_context(viewport={"width": 1280, "height": 720}); await ctx.add_init_script(OLD)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append("page: " + str(e))); pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        ev = lambda s: pg.evaluate(s)
        await pg.goto("file://" + GAME); await pg.wait_for_timeout(1200)
        t = await ev("[document.title, document.querySelector('#title .logo').textContent, document.querySelector('#title .ver').textContent]")
        check(t[0] == NAME and t[1] == NAME and t[2] == VER, f"the page title and the title card read {NAME} {VER} ({t})")
        check(await ev("!document.body.innerText.includes('Helena')"), "no Helena on screen")
        keys = await ev(f"['{KEY}_save_v1','{KEY}_cfg_v1'].map(k=>localStorage.getItem(k)!==null)")
        check(keys == [True, True], f"the old Helena Hollow save and settings were copied to the {KEY} keys ({keys})")
        check(await ev("CFG.gfx") == GFX, f"the view is fixed to {'Angled' if GFX else 'Pixel'} even though the old settings chose the other ({await ev('CFG.gfx')})")
        check(await ev(f"document.body.classList.contains('iso')") == bool(GFX), "the page draws that view")
        await pg.screenshot(path=f"{SHOTS}/shot-title.jpg", type="jpeg", quality=85)
        await ev("closeAll()"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"{SHOTS}/shot-play.jpg", type="jpeg", quality=85)
        await pg.set_viewport_size({"width": 960, "height": 540}); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f"{SHOTS}/shelf.jpg", type="jpeg", quality=85)
        await pg.set_viewport_size({"width": 1280, "height": 720}); await pg.wait_for_timeout(600)
        await ev("openPanel('pause');openPanel('settings')"); await pg.wait_for_timeout(500)
        rows = await ev("document.getElementById('settings').innerText")
        check("Graphics" not in rows, "Settings has no Graphics choice")
        await ev("closeAll()"); await ev("openPanel('map')"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=f"{SHOTS}/shot-map.jpg", type="jpeg", quality=85)
        await ctx.close()
        # ---- 2: a fresh player with only a pretend Xbox controller ----
        ctx = await b.new_context(viewport={"width": 960, "height": 540}); await ctx.add_init_script(PAD)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append("page: " + str(e))); pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        ev = lambda s: pg.evaluate(s)
        async def pad(n, hold=250, wait=700):
            await ev(f"window.__pad_button({BTN[n]},1)"); await pg.wait_for_timeout(hold)
            await ev(f"window.__pad_button({BTN[n]},0)"); await pg.wait_for_timeout(wait)
        await pg.goto("file://" + GAME); await pg.wait_for_timeout(1200)
        await pad("A")   # the first press wakes the controller, as in a real browser
        on = await ev("document.body.classList.contains('ontitle')")
        for k in range(4):
            if not on: break
            await pad("A"); on = await ev("document.body.classList.contains('ontitle')")
        stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
        check(not on or stack, f"A on the title card starts play or opens the next screen (title {on}, open {stack})")
        await pg.screenshot(path=f"{SHOTS}/pad_after_A.jpg", type="jpeg", quality=80)
        for k in range(6):   # a new keeper may meet the character builder or a welcome first. A and B move past them
            stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
            if not stack: break
            await pad("B" if k % 2 else "A")
        stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
        check(not stack, f"A and B reach play with nothing open ({stack})")
        await pad("MENU"); stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
        check("pause" in stack, f"Menu opens the pause menu ({stack})")
        await pad("B"); stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
        check("pause" not in stack, f"B closes it ({stack})")
        await pad("VIEW"); stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
        check("pause" in stack, f"View opens the pause menu too ({stack})")
        await pad("VIEW"); stack = await ev("[...document.querySelectorAll('.ov')].filter(o=>getComputedStyle(o).display!=='none').map(o=>o.id)")
        check("pause" not in stack, f"View closes it again ({stack})")
        x0 = await ev("[S.x,S.y]"); await ev("window.__pad_axes(1,0)"); await pg.wait_for_timeout(1500); await ev("window.__pad_axes(0,0)"); await pg.wait_for_timeout(300)
        x1 = await ev("[S.x,S.y]"); check(abs(x1[0] - x0[0]) + abs(x1[1] - x0[1]) > 8, f"the left stick walks ({x0} to {x1})")
        await ctx.close(); await b.close()
    print("errors", errs)
asyncio.run(main())
