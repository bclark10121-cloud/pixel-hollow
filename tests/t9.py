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
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
        r = await ev("""(()=>{const G=__game;G.openBridge(true);const a=G.reachFrom(14,27),c=G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y);G.openBridge(G.S.bridge);
          const bad=[];for(const it of G.ITEMS){const k=it.y*G.MW+it.x,cave=it.y>=62;let ok=cave?c[k]:a[k];if(it.rock)ok=a[k+1]||a[k-1]||a[k+G.MW];if(!ok)bad.push(it.id)}
          const tun=G.TUNNELS.flat().map(e=>!!a[(e[1]+1)*G.MW+e[0]]);
          return {total:G.ITEMS.length,unreachable:bad,tunnelsReachable:tun,hidden:G.ITEMS.filter(i=>i.set==='hidden').map(i=>[i.id,i.x,i.y,!!i.rock,!!i.hid,G.obj[i.y*G.MW+i.x],G.obj[(i.y+1)*G.MW+i.x]])}})()""")
        print(json.dumps(r))
        print("title slot:", await ev("tslotv.textContent"), "| pet granted:", await ev("__game.S.pet"), "| font:", await ev("getComputedStyle(document.body).fontFamily.slice(0,14)"), await ev("document.fonts.check('16px PixelifyWV')"))
        await pg.screenshot(path="v36_title.png")
        await pg.tap("#tcont"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="v36_play.png")
        # rock + hidden
        rk=await ev("__game.ITEMS.find(i=>i.rock)")
        nb=await ev(f"[[1,0],[-1,0],[0,1]].map(d=>[{rk['x']}+d[0],{rk['y']}+d[1]]).find(p=>!__game.solidTile(p[0],p[1]))")
        await ev(f"__game.S.x={nb[0]}*16+8;__game.S.y={nb[1]}*16+10"); await pg.wait_for_timeout(120)
        print("near rock ->", await ev("__game.nearest()&&__game.nearest().k")); await pg.keyboard.press("e"); await pg.wait_for_timeout(100)
        print("rock item found:", await ev(f"!!__game.S.found['{rk['id']}']"))
        # rare availability
        await ev("__game.S.clock=10"); d1=await ev("['firefly','rainlily'].map(id=>__game.avail(__game.ITEMS.find(i=>i.id===id)))")
        await ev("__game.S.clock=450"); d2=await ev("['firefly','rainlily'].map(id=>__game.avail(__game.ITEMS.find(i=>i.id===id)))")
        print("rare avail day:",d1,"night+rain(450):",d2)
        await ev("__game.S.x=40*16+8;__game.S.y=36*16+10"); await pg.wait_for_timeout(300); await pg.screenshot(path="v36_rain_night.png")
        await ev("__game.S.clock=10")
        # photo
        await ev("__game.S.x=40*16+8;__game.S.y=35*16+6"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(60)
        print("photo:", await ev("!!__game.S.found.pc1"), "flash>0:", await ev("__game.S.flash>0"))
        await pg.wait_for_timeout(700)
        # tunnel
        await ev("__game.S.x=5*16+8;__game.S.y=31*16+6"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("tunnel ->", await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]")); await pg.screenshot(path="v36_tunnel.png")
        # pet follows + radar
        await ev("__game.CFG.radar=1;__game.S.x=20*16+8;__game.S.y=31*16+10"); await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(1200); await pg.keyboard.up("ArrowRight"); await pg.wait_for_timeout(500)
        print("pet dist:", await ev("Math.round(Math.hypot(__game.PET.x-__game.S.x,__game.PET.y-__game.S.y))"))
        dg=await ev("__game.ITEMS.find(i=>i.id==='coin')"); await ev(f"__game.S.x={dg['x']+3}*16+8;__game.S.y={dg['y']}*16+10"); await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(150); await pg.keyboard.up("ArrowDown"); await pg.wait_for_timeout(600)
        print("radar near class:", await ev("document.getElementById('count').className"), "pet alert:", await ev("__game.PET.alert")); await pg.screenshot(path="v36_pet.png")
        # tap to walk
        await ev("__game.CFG.stick=2;__game.S.x=14*16+8;__game.S.y=28*16+10"); await pg.wait_for_timeout(200)
        await pg.touchscreen.tap(330,470); await pg.wait_for_timeout(200); n=await ev("__game.getPath()?__game.getPath().length:0"); x0=await ev("__game.S.x")
        await pg.wait_for_timeout(2500); print("tap path len:", n, "moved:", round(x0), "->", round(await ev("__game.S.x")), "arrived:", await ev("__game.getPath()===null"))
        await ev("__game.CFG.stick=0")
        # fast travel
        await pg.tap("#mapbtn"); await pg.wait_for_timeout(200); print("go buttons:", await ev("[...document.querySelectorAll('#mapgo .btn')].map(b=>b.textContent)")); await pg.screenshot(path="v36_map.png")
        await (await pg.query_selector_all("#mapgo .btn"))[3].tap(); await pg.wait_for_timeout(200); print("traveled to tile:", await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16),__game.stack.length]"))
        # journal pages
        await pg.tap("#jbtn"); await pg.wait_for_timeout(150); t1=await ev("jsum.textContent+' | '+jpn.textContent+' | '+document.querySelector('#jsets h2').textContent")
        await pg.tap("#jnext"); await pg.tap("#jnext"); await pg.tap("#jnext"); await pg.wait_for_timeout(400); print("journal:", t1, "=>", await ev("jpn.textContent+' | '+[...document.querySelectorAll('#jsets h2')].map(h=>h.textContent).join(' ; ')"))
        await pg.screenshot(path="v36_journal.png"); await pg.tap("#jclose")
        # settings
        await pg.tap("#mbtn"); await pg.tap("#pset"); await pg.wait_for_timeout(150); print("settings rows:", await ev("[...document.querySelectorAll('#srows .nm')].map(e=>e.textContent).join(', ')"))
        await ev("document.getElementById('settings').scrollTop=420"); await pg.wait_for_timeout(100); await pg.screenshot(path="v36_settings.png")
        await ev("__game.CFG.ts=2;__game.CFG.spk=1;__game.CFG.pet=2"); await pg.tap("#sback"); await pg.tap("#presume")
        # unlocks: finish 5 sets -> crown
        await ev("__game.ITEMS.filter(i=>['leaves','harvest'].includes(i.set)).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(900)
        print("crown unlocked:", await ev("__game.UNLOCK[0][4]()"), "| lantern:", await ev("__game.S.lantern"))
        await pg.tap("#dialog"); await pg.tap("#mbtn"); await pg.tap("#pchar"); await pg.wait_for_timeout(150); print("earn line:", await ev("bearn.textContent")); await pg.tap("#bdone"); await pg.tap("#presume")
        # slots
        await pg.tap("#mbtn"); await pg.tap("#ptitle"); await pg.wait_for_timeout(200)
        s1=await ev("tslotv.textContent"); await (await pg.query_selector_all("#tslot .pm"))[1].tap(); await pg.wait_for_timeout(150); s2=await ev("tslotv.textContent+' / '+tnew.textContent+' / cont:'+getComputedStyle(tcont).display")
        await (await pg.query_selector_all("#tslot .pm"))[0].tap(); await pg.wait_for_timeout(150); print("slots:", s1, "->", s2, "->", await ev("tslotv.textContent+' / found '+Object.keys(__game.S.found).length"))
        await pg.reload(); await pg.wait_for_timeout(600); print("reload:", await ev("tslotv.textContent"), await ev("[__game.S.pet,__game.S.signs,__game.CFG.ts]"))
        await pg.tap("#tcont"); await ev("__game.S.x=88*16+8;__game.S.y=20*16+10"); await pg.wait_for_timeout(400); await pg.screenshot(path="v36_autumn.png")
        print("errors", errs); await b.close()
asyncio.run(main())
