import asyncio, json
from playwright.async_api import async_playwright
# v0.14: walk-in museum, curator, exhibits, background sounds, cabin stove and bench
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900); await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        r=await ev("""(()=>{const G=__game,W=G.MW,m=G.reachFrom(G.MUS_IN.x,G.MUS_IN.y),adj=(x,y)=>[[1,0],[-1,0],[0,1],[0,-1]].some(d=>m[(y+d[1])*W+x+d[0]]);
          return {cases:G.CASES.length,sets:G.SETS.length,unreachableCases:G.CASES.filter(c=>!adj(c.x,c.y)).map(c=>c.set),curator:adj(G.CURATOR.x,G.CURATOR.y),door:!!m[98*W+68],region:G.regAt(G.MUS_IN.x,G.MUS_IN.y).name,wallSolid:G.solidTile(55,90)&&G.solidTile(70,85)}})()""")
        print("museum layout:", json.dumps(r)); assert r["cases"]==r["sets"]==28 and not r["unreachableCases"] and r["curator"] and r["door"] and r["region"]=="Hollow Museum" and r["wallSolid"]
        # walk in through the door
        await ev("const M=__game.MUS;__game.S.x=(M.x+2)*16+8;__game.S.y=(M.y+M.h)*16+6;__game.S.dir=1"); n=await ev("(()=>{const n=__game.nearest();return n&&n.k})()"); await pg.keyboard.press("e"); await pg.wait_for_timeout(400)
        print("door:", n, "->", await ev("__game.region().name")); assert await ev("__game.region().name")=="Hollow Museum"
        await pg.screenshot(path="m_hall.png")
        # an exhibit already donatable (Meadow Blooms are complete in the seed save)
        await ev("const c=__game.CASES.find(c=>c.set==='meadow');__game.S.x=c.x*16+8;__game.S.y=(c.y+1)*16+10"); await pg.keyboard.press("e"); await pg.wait_for_timeout(250)
        print("exhibit ask:", (await ev("ctext.textContent"))[:110]); assert "Donate" in await ev("ctext.textContent")
        await pg.tap("#cyes"); await pg.wait_for_timeout(300); print("donated:", await ev("!!__game.S.don.meadow"), "|", (await ev("dtext.textContent"))[:60]); await ev("hush()")
        await pg.keyboard.press("e"); await pg.wait_for_timeout(200); print("exhibit again:", (await ev("dtext.textContent"))[:120]); assert "on display" in await ev("dtext.textContent"); await ev("hush()")
        await ev("const c=__game.CASES.find(c=>c.set==='crystal');__game.S.x=c.x*16+8;__game.S.y=(c.y+1)*16+10"); await pg.keyboard.press("e"); await pg.wait_for_timeout(200); print("unfinished:", (await ev("dtext.textContent"))[:120]); await ev("hush()")
        # curator opens the donation desk
        await ev("__game.S.x=__game.CURATOR.x*16+8;__game.S.y=(__game.CURATOR.y+1)*16+10"); await pg.keyboard.press("e"); await pg.wait_for_timeout(250)
        print("curator:", await ev("[...__game.stack].join()"), (await ev("musum.textContent"))[:70]); assert await ev("__game.stack.includes('museum')"); await ev("closeAll()")
        await ev("['shore','forest'].forEach(id=>__game.donate(id))"); await pg.wait_for_timeout(200); await ev("hush();__game.hop(__game.MUS_IN.x,90,1)"); await pg.wait_for_timeout(400); await pg.screenshot(path="m_cases.png")
        await ev("__game.CFG.gfx=0;applyCfg('gfx')"); await pg.wait_for_timeout(300); await pg.screenshot(path="m_hall_px.png"); await ev("__game.CFG.gfx=1;applyCfg('gfx')")
        # walk out the door
        await ev("__game.S.x=68*16+8;__game.S.y=97*16+8"); await pg.keyboard.down("ArrowDown"); await pg.keyboard.down("ArrowLeft"); await pg.wait_for_timeout(600); await pg.keyboard.up("ArrowDown"); await pg.keyboard.up("ArrowLeft"); await pg.wait_for_timeout(300)
        print("walked out:", await ev("__game.region().name"), await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]")); assert await ev("__game.region().name")=="Home Meadows"
        await ev("save()"); await pg.reload(); await pg.wait_for_timeout(800); print("reload keeps donations:", await ev("Object.keys(__game.S.don).join()"))
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        # background sounds come up after a tap and change with the area
        await pg.touchscreen.tap(200,500); await pg.wait_for_timeout(600)
        st=[]
        for where in ["__game.hop(24,34,0)","__game.S.lantern=true;__game.hop(__game.CAVE_IN.x,94,1)","__game.S.vil.bram=1;__game.hop(__game.deep().DEEP_IN.x,__game.deep().DEEP_IN.y,0)","__game.hop(__game.SNOW_IN.x,__game.SNOW_IN.y,1)"]:
            await ev(where); await pg.wait_for_timeout(700); st.append(await ev("(()=>{const A=__game.AS;return A.on?[__game.region().name,+A.ch.wind.g.gain.value.toFixed(3),+A.ch.hum.g.gain.value.toFixed(3)]:'off'})()"))
        print("ambience:", st); assert all(x!="off" for x in st)
        await ev("__game.CFG.amb=0"); await pg.wait_for_timeout(700); print("ambience off bus:", await ev("+__game.AS.bus.gain.value.toFixed(3)"))
        # the cabin stove and workbench are solid, the door path is open
        await ev("__game.enterHome()"); await pg.wait_for_timeout(200); print("stove/bench solid:", await ev("[__game.solidTile(67,76),__game.solidTile(73,76),__game.solidTile(70,77)]")); assert await ev("__game.solidTile(67,76)&&__game.solidTile(73,76)&&!__game.solidTile(70,77)")
        print("errors", errs); await b.close()
asyncio.run(main())
