import asyncio, json
from playwright.async_api import async_playwright
# v0.14: photo mode, journal hints and pins, pet fetch
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True, accept_downloads=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900); await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        print("old save pin:", await ev("__game.S.pin"), "| pet finds:", await ev("__game.ITEMS.filter(i=>i.pet).length"), "| total", await ev("__game.ITEMS.length"))
        # ---- photo mode ----
        await pg.tap("#mbtn"); await pg.wait_for_timeout(200); await pg.tap("#pphoto"); await pg.wait_for_timeout(300)
        print("photo open:", await ev("[__game.PH.on,[...__game.stack].join(),getComputedStyle($('hudr')).display,$('phtop').textContent]"))
        assert await ev("__game.PH.on") and await ev("getComputedStyle($('hudr')).display")=="none"
        await pg.screenshot(path="q_photo1.png")
        await pg.tap("#phf"); await pg.tap("#phf"); await pg.tap("#phz"); await pg.wait_for_timeout(200)
        print("filter/zoom:", await ev("[$('phf').textContent,$('phz').textContent,cv.style.filter.slice(0,20)]"))
        x0=await ev("__game.PH.ox"); await pg.touchscreen.tap(200,400)
        await ev("(()=>{const e=(t,x,y)=>cv.dispatchEvent(new PointerEvent(t,{pointerId:7,clientX:x,clientY:y,bubbles:true}));e('pointerdown',200,500);e('pointermove',120,460);e('pointerup',120,460)})()")
        print("drag pan ox,oy:", await ev("[Math.round(__game.PH.ox),Math.round(__game.PH.oy)]")); assert await ev("__game.PH.ox")>10
        await pg.tap("#phh"); await pg.wait_for_timeout(200); await pg.screenshot(path="q_photo2.png")
        async with pg.expect_download() as dl: await pg.tap("#phs")
        d=await dl.value; print("photo download:", d.suggested_filename); assert d.suggested_filename.startswith("HelenaHollow_") and d.suggested_filename.endswith(".jpg")
        await d.save_as("q_snap.jpg")
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
        print("photo closed:", await ev("[__game.PH.on,__game.stack.length,cv.style.filter]")); assert not await ev("__game.PH.on") and await ev("cv.style.filter")==""
        # keyboard and pad paths
        await ev("keyMode(true);openPhoto()"); await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(400); await pg.keyboard.up("ArrowRight"); print("key pan ox:", round(await ev("__game.PH.ox")))
        await pg.keyboard.press("q"); await pg.keyboard.press("h"); print("keys q,h:", await ev("[__game.PH.f,__game.PH.hide]"))
        await ev("__padKey(2,1)"); await pg.wait_for_timeout(120); await ev("__padKey(2,0)"); await pg.wait_for_timeout(120); print("pad X filter:", await ev("__game.PH.f"))
        await ev("__padKey(1,1)"); await pg.wait_for_timeout(120); await ev("__padKey(1,0)"); await pg.wait_for_timeout(200); print("pad B closes:", not await ev("__game.PH.on")); assert not await ev("__game.PH.on")
        # ---- hints and pins ----
        hints=await ev("['amber','koi','g_wheat','v_lure','token','moth','marble','kite','pc3','blueice','p_cap'].map(id=>id+': '+__game.hintFor(__game.ITEMS.find(i=>i.id===id)))")
        for h in hints: print("  hint", h[:150])
        await ev("openPanel('journal');jflip(1)"); await pg.wait_for_timeout(300)
        slots=await pg.query_selector_all("#jsets .slot.no"); await slots[0].tap(); await pg.wait_for_timeout(100); t1=await ev("jinfo.textContent"); await slots[0].tap(); await pg.wait_for_timeout(150)
        print("journal hint:", t1[:140]); print("pinned:", await ev("__game.S.pin"), await ev("$('jsets').querySelectorAll('.slot.pinned').length")); assert await ev("!!__game.S.pin")
        await ev("closeAll();openPanel('map')"); await pg.wait_for_timeout(300); print("map info:", (await ev("mapinfo.textContent"))[-90:]); await pg.screenshot(path="q_map_pin.png"); await ev("closeAll()")
        await ev("const it=__game.ITEMS.find(i=>i.id===__game.S.pin),sp=__game.pinSpot(it);__game.hop(sp[0]+9,sp[1],0)"); await pg.wait_for_timeout(300); await pg.screenshot(path="q_pin_world.png")
        await ev("save()"); await pg.reload(); await pg.wait_for_timeout(800); print("pin survives reload:", await ev("__game.S.pin")); assert await ev("!!__game.S.pin")
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        pid=await ev("__game.S.pin"); await ev(f"__game.collect(__game.ITEMS.find(i=>i.id==='{pid}'))"); print("pin cleared on find:", await ev("__game.S.pin")); assert await ev("__game.S.pin")==None
        # ---- pet fetch ----
        await ev("__game.S.pet=true;__game.CFG.pet=1;__game.PET.init=false;hush();__game.hop(24,34,3)"); await pg.wait_for_timeout(400)
        got=[]
        for i in range(20):
            await ev("hush();closeAll();__game.S.dir=3;const P=__game.PET;P.x=__game.S.x-12;P.y=__game.S.y;P.init=true"); thrown=await ev("__game.throwBall()")
            if not thrown: await ev("__game.S.dir=2"); thrown=await ev("__game.throwBall()")
            for k in range(40):
                await pg.wait_for_timeout(100)
                if not await ev("__game.FB.on"): break
            if i==0: print("first fetch phase done, toast:", await ev("document.getElementById('toast').textContent"))
            n=await ev("__game.ITEMS.filter(i=>i.pet&&__game.S.found[i.id]).length"); got.append(n)
            if n==5: break
        print("pet finds after each throw:", got); assert got[-1]==5 and len(got)<=15
        await ev("__game.S.dir=3;const P=__game.PET;P.x=__game.S.x-12;P.y=__game.S.y;__game.throwBall()"); await pg.wait_for_timeout(250); await pg.screenshot(path="q_fetch.png")
        await ev("__game.CFG.gfx=0;applyCfg('gfx')"); await pg.wait_for_timeout(300); await ev("openPhoto()"); await pg.wait_for_timeout(200); await pg.keyboard.press("e"); await pg.wait_for_timeout(200); await ev("closeAll()")
        print("errors", errs); await b.close()
asyncio.run(main())
