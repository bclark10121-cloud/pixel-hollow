import asyncio, json
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True)
        await ctx.add_init_script(SEED)
        pg = await ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        tt=lambda: ev("document.getElementById('toast').textContent")
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        print("items:", await ev("__game.ITEMS.length"), "sets:", await ev("__game.SETS.length"))
        # garden
        await ev("__game.S.x=19*16+8;__game.S.y=23*16+12"); await pg.wait_for_timeout(150); await pg.screenshot(path="v5_garden0.png")
        await pg.keyboard.press("e"); await pg.wait_for_timeout(200); print("seed picker:", await ev("[...__game.stack]"), await ev("[...document.querySelectorAll('#pkgrid .slot')].map(d=>d.textContent+(d.classList.contains('no')?'(locked)':''))"))
        await (await pg.query_selector_all("#pkgrid .slot"))[3].tap(); await pg.wait_for_timeout(200); print("planted:", await ev("JSON.stringify(__game.S.garden[1])"), await tt())
        await pg.keyboard.press("e"); await pg.wait_for_timeout(100); print("water:", await tt(), await ev("__game.S.garden[1].g.toFixed(2)"))
        await pg.keyboard.press("e"); await pg.wait_for_timeout(100); print("water again:", await tt())
        await ev("__game.S.garden[1].g=2.2;__game.S.garden[0]={k:'daisy',g:1.2,w:-1};__game.S.garden[2]={k:'poppy',g:0.2,w:-1}"); await pg.wait_for_timeout(200); await pg.screenshot(path="v5_garden1.png")
        await ev("__game.S.garden[1].g=3"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("harvest:", await tt(), await ev("!!__game.S.found.g_sunflower")); await pg.screenshot(path="v5_garden2.png")
        # home
        await ev("__game.S.x=14*16+8;__game.S.y=26*16+2"); await pg.wait_for_timeout(150); await pg.keyboard.press("e"); await pg.wait_for_timeout(300)
        print("home region:", await ev("__game.region().name"), await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]")); await pg.screenshot(path="v5_home0.png")
        # frame at (64,67): stand at (64,68)
        await ev("__game.S.x=64*16+8;__game.S.y=68*16+10"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("display picker:", await ev("pktitle.textContent"), await ev("document.querySelectorAll('#pkgrid .slot').length"))
        await (await pg.query_selector_all("#pkgrid .slot"))[4].tap(); await pg.wait_for_timeout(150)
        for (x,y,idx) in [(67,68,9),(73,68,12),(76,68,2)]:
            await ev(f"__game.S.x={x}*16+8;__game.S.y={y}*16+10"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[idx].tap(); await pg.wait_for_timeout(120)
        for (x,y,idx) in [(63,70,6),(63,72,7),(63,74,15),(76,70,14),(76,72,3),(76,74,11)]:
            await ev(f"__game.S.x={x}*16+8;__game.S.y={y}*16+10"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[idx].tap(); await pg.wait_for_timeout(120)
        print("displays:", await ev("JSON.stringify(__game.S.home.sh)"))
        # furniture slot 4 at (66,73): stand at (66,74)
        await ev("__game.S.x=66*16+8;__game.S.y=74*16+10"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("furn picker:", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(d=>d.textContent+(d.classList.contains('no')?'*':'')).join(', ')"))
        await (await pg.query_selector_all("#pkgrid .slot"))[9].tap(); await pg.wait_for_timeout(120); print("locked pick:", await ev("pkinfo.textContent"), await ev("[...__game.stack]"))
        await (await pg.query_selector_all("#pkgrid .slot"))[4].tap(); await pg.wait_for_timeout(150); print("placed:", await ev("JSON.stringify(__game.S.home.fu)"), "solid:", await ev("__game.solidTile(66,73)"))
        await ev("__game.S.x=74*16+8;__game.S.y=74*16+10"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[3].tap(); await pg.wait_for_timeout(150)
        await ev("__game.S.x=63*16+8;__game.S.y=76*16+10"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(100); print("wall:", await ev("__game.S.home.wall"), await tt())
        await ev("__game.S.x=76*16+8;__game.S.y=76*16+10"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(100); print("floor:", await ev("__game.S.home.floor"))
        await ev("__game.S.x=70*16+8;__game.S.y=73*16+10"); await pg.wait_for_timeout(2700); await pg.screenshot(path="v5_home1.png")
        await pg.tap("#mapbtn"); await pg.wait_for_timeout(200); print("map:", await ev("mtitle.textContent")); await pg.tap("#mapclose")
        # walk out the door
        await ev("__game.S.x=70*16+8;__game.S.y=76*16+10"); await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(900); await pg.keyboard.up("ArrowDown")
        print("after exit:", await ev("__game.region().name"), await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]"))
        await pg.reload(); await pg.wait_for_timeout(600)
        print("reload:", await ev("JSON.stringify(__game.S.home)"), await ev("JSON.stringify(__game.S.garden.map(p=>p&&p.k))"), await ev("tslotv.textContent"))
        await pg.tap("#tcont"); await pg.tap("#jbtn"); await pg.tap("#jprev"); await pg.wait_for_timeout(350); print("journal last page:", await ev("[...document.querySelectorAll('#jsets h2')].map(h=>h.textContent).join(' ; ')")); await pg.tap("#jclose")
        print("errors", errs); await b.close()
asyncio.run(main())
