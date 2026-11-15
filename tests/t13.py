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
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1200)
        r = await ev("""(()=>{const G=__game,W=G.MW;G.openBridge(true);const a=G.reachFrom(14,27),c=G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y),sn=G.reachFrom(G.SNOW_IN.x,G.SNOW_IN.y),de=G.reachFrom(G.DES_IN.x,G.DES_IN.y),dp=G.reachFrom(G.deep().DEEP_IN.x,G.deep().DEEP_IN.y);G.openBridge(G.S.bridge);
          const pick=(x,y)=>{const rg=G.regAt(x,y);return rg===G.REG.over?a:rg===G.REG.cave?c:rg===G.REG.snow?sn:rg===G.REG.deep?dp:de};
          const bad=[];for(const it of G.ITEMS){if(it.off)continue;const k=it.y*W+it.x,m=pick(it.x,it.y);let ok=m[k];if(it.rock)ok=m[k+1]||m[k-1]||m[k+W];if(!ok)bad.push(it.id)}
          const adj=(x,y)=>{const m=pick(x,y),k=y*W+x;return !!(m[k+1]||m[k-1]||m[k+W]||m[k-W])};
          const cnt=m=>{let n=0;for(let i=0;i<m.length;i++)n+=m[i];return n};
          return {total:G.ITEMS.length,sets:G.SETS.length,unreachable:bad,villagers:G.VIL.map(v=>[v.id,adj(v.x,v.y)]),arch:adj(G.ARCH.x,G.ARCH.y),boat:adj(G.BOAT.x,G.BOAT.y),dboat:adj(G.DBOAT.x,G.DBOAT.y),signs:G.SIGNS.map(s=>adj(s.x,s.y)),snowTiles:cnt(sn),desertTiles:cnt(de),snowExit:!!sn[138*W+30]}})()""")
        print(json.dumps(r))
        print("old save:", await ev("[Object.keys(__game.S.found).length,__game.seen.length,tslotv.textContent]"))
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        # Mira
        await ev("__game.S.x=21*16+8;__game.S.y=27*16+8"); await pg.wait_for_timeout(200); await pg.screenshot(path="v6_mira.png"); await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("mira:", await ev("dtext.textContent"), "| gift:", await ev("!!__game.S.found.v_seed")); await pg.keyboard.press("e"); await pg.keyboard.press("e"); await pg.wait_for_timeout(100); print("mira after:", await ev("dtext.textContent")); await pg.keyboard.press("e")
        # Tom not ready
        await ev("__game.S.x=36*16+8;__game.S.y=50*16+8"); await pg.wait_for_timeout(150); await pg.keyboard.press("e"); await pg.wait_for_timeout(100); print("tom:", await ev("dtext.textContent")); await pg.keyboard.press("e")
        # gate closed
        await ev("__game.S.bridge=true;__game.openBridge(true);__game.S.x=88*16+8;__game.S.y=10*16+8"); await pg.wait_for_timeout(200); await pg.screenshot(path="v6_gate.png")
        await ev("__game.S.x=88*16+8;__game.S.y=9*16+6"); await pg.wait_for_timeout(100)
        print("nearest at gate:", await ev("__game.nearest()&&__game.nearest().k")); 
        await ev("__game.hop(88,9,1)"); await pg.wait_for_timeout(100)
        await ev("__game.talk(__game.VIL[3])"); print("juniper no lantern:", await ev("dtext.textContent")); await pg.keyboard.press("e")
        await ev("__game.S.lantern=true;__game.talk(__game.VIL[3])"); await pg.wait_for_timeout(100); print("juniper lantern:", await ev("dtext.textContent"), await ev("__game.S.vil.juniper")); await pg.keyboard.press("e")
        await ev("__game.S.x=88*16+8;__game.S.y=9*16+4"); await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(200); await pg.keyboard.up("ArrowUp")
        # use arch: stand below arch and act; pick nearest action directly
        res=await ev("(()=>{const G=__game;G.S.x=88*16+8;G.S.y=9*16+2;const n=G.nearest();return n&&n.k})()"); await pg.keyboard.press("e"); await pg.wait_for_timeout(300)
        print("after arch:", await ev("__game.region().name"), await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]"), await tt())
        if await ev("__game.region().name")!="Snowy Peaks": await ev("__game.hop(__game.SNOW_IN.x,__game.SNOW_IN.y,1)")
        await pg.wait_for_timeout(300); await pg.screenshot(path="v6_snow1.png")
        await ev("__game.S.x=38*16+8;__game.S.y=121*16+8"); await pg.wait_for_timeout(300); await pg.screenshot(path="v6_snow2.png")
        await pg.tap("#mapbtn"); await pg.wait_for_timeout(200); await pg.screenshot(path="v6_snowmap.png"); print("map:", await ev("mtitle.textContent")); await pg.tap("#mapclose")
        await ev("__game.hop(30,137,0)"); await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(900); await pg.keyboard.up("ArrowDown")
        print("walk out of snow:", await ev("__game.region().name"), await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]"))
        # boat
        await ev("__game.hop(88,54,0)"); await pg.wait_for_timeout(200); await pg.screenshot(path="v6_boat.png"); await pg.keyboard.press("e"); await pg.wait_for_timeout(150); print("boat before:", await ev("dtext.textContent")); await pg.keyboard.press("e")
        await ev("__game.S.found.sardine=1;__game.talk(__game.VIL[4])"); await pg.wait_for_timeout(100); await pg.keyboard.press("e")
        await ev("__game.hop(88,54,0)"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(300)
        print("boat after:", await ev("__game.region().name"), await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]")); await pg.screenshot(path="v6_desert1.png")
        await ev("__game.S.x=92*16+8;__game.S.y=125*16+8"); await pg.wait_for_timeout(300); await pg.screenshot(path="v6_desert2.png")
        await ev("__game.hop(63,120,2)"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(200); print("boat back:", await ev("__game.region().name"))
        # seasons
        for i,nm in enumerate(["spring","summer","autumn","winter"]):
            await ev(f"__game.CFG.season={i+1};__game.S.clock=20;__game.hop(24,30,0)"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"v6_{nm}.png")
        await ev("__game.CFG.season=0;__game.S.clock=880"); await pg.keyboard.down("ArrowLeft"); await pg.wait_for_timeout(1500); await pg.keyboard.up("ArrowLeft"); print("season toast:", await tt(), await ev("__game.season()"))
        await pg.tap("#jbtn"); await pg.tap("#jprev"); await pg.wait_for_timeout(350); print("journal:", await ev("jpn.textContent+' '+[...document.querySelectorAll('#jsets h2')].map(h=>h.textContent).join(' ; ')")); await pg.tap("#jclose")
        await pg.reload(); await pg.wait_for_timeout(900); print("reload vil:", await ev("Object.keys(__game.S.vil)"), await ev("tslotv.textContent"))
        print("errors", errs); await b.close()
asyncio.run(main())
