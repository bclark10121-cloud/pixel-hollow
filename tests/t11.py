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
          const bad=[];for(const it of G.ITEMS){if(it.fish)continue;const k=it.y*G.MW+it.x,cave=it.y>=62;let ok=cave?c[k]:a[k];if(it.rock)ok=a[k+1]||a[k-1]||a[k+G.MW];if(!ok)bad.push(it.id)}
          const at=p=>!!a[p.y*G.MW+p.x];
          return {total:G.ITEMS.length,unreachable:bad,rod:at(G.ROD),net:at(G.NET),museumDoor:at({x:G.MUS.x+2,y:G.MUS.y+G.MUS.h}),tunnels:G.TUNNELS.flat().map(e=>!!a[(e[1]+1)*G.MW+e[0]]),shovel:at(G.SHOVEL)}})()""")
        print(json.dumps(r))
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        print("save ok:", await ev("[Object.keys(__game.S.found).length,__game.S.rod,__game.S.net,document.getElementById('count').textContent]"))
        # net
        await ev("__game.S.x=20*16+8;__game.S.y=34*16+14"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(80)
        print("bug without net:", await ev("dtext.textContent")); await pg.keyboard.press("e")
        await ev("__game.S.x=22*16+8;__game.S.y=25*16+10"); await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(350); await pg.keyboard.up("ArrowUp")
        print("net:", await ev("__game.S.net"), "|", await ev("dtext.textContent")); await pg.keyboard.press("e")
        await pg.screenshot(path="v4_net.png")
        await ev("__game.S.x=20*16+8;__game.S.y=34*16+14"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(100)
        print("ladybug caught:", await ev("!!__game.S.found.ladybug"), await ev("document.getElementById('toast').textContent"))
        # rod + fishing
        await ev("__game.S.x=48*16+8;__game.S.y=32*16+10"); await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(350); await pg.keyboard.up("ArrowUp")
        print("rod:", await ev("__game.S.rod")); await pg.keyboard.press("e")
        await ev("__game.S.x=40*16+8;__game.S.y=34*16+6"); await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(250); await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(150)
        print("at pond edge tile y:", await ev("Math.floor(__game.S.y/16)"), "water ahead:", await ev("JSON.stringify(__game.waterAhead())"), "nearest:", await ev("__game.nearest()&&__game.nearest().k"))
        await ev("__game.S.found.pc1=1"); await pg.wait_for_timeout(50); print("nearest now:", await ev("__game.nearest()&&__game.nearest().k"))
        await pg.keyboard.press("e"); await pg.wait_for_timeout(200); print("casting:", await ev("__game.F.on"))
        await pg.keyboard.press("e"); print("early press toast:", await ev("document.getElementById('toast').textContent"), "still on:", await ev("__game.F.on"))
        for _ in range(60):
            await pg.wait_for_timeout(100)
            if await ev("__game.F.bite>0"): break
        await pg.screenshot(path="v4_fish.png"); await pg.keyboard.press("e"); await pg.wait_for_timeout(150)
        print("after reel:", await ev("document.getElementById('toast').textContent"), "| fish found:", await ev("__game.ITEMS.filter(i=>i.fish&&__game.S.found[i.id]).map(i=>i.id)"))
        # catch many to check all pond species reachable by chance
        got=await ev("""(()=>{const G=__game;let n=0;for(let k=0;k<400;k++){G.F.on=true;G.F.bite=1;G.F.zone=['pond','sea','mirror'][k%3];document.dispatchEvent(new Event('x'));n++;}return 0})()""")
        await ev("""(()=>{for(let k=0;k<300;k++){__game.F.on=true;__game.F.bite=1;__game.F.zone=['pond','sea','mirror'][k%3];window.dispatchEvent(new KeyboardEvent('keydown',{key:'e'}));window.dispatchEvent(new KeyboardEvent('keyup',{key:'e'}));if(dialog.style.display==='block')dialog.dispatchEvent(new Event('pointerdown'))}})()""")
        await pg.wait_for_timeout(1500)
        print("fish after many casts:", await ev("__game.ITEMS.filter(i=>i.fish&&__game.S.found[i.id]).length"), "of 12")
        # museum
        await ev("if(dialog.style.display==='block')dialog.dispatchEvent(new Event('pointerdown'))")
        await ev("__game.S.x=44*16+8;__game.S.y=43*16+6"); await pg.wait_for_timeout(150); await pg.screenshot(path="v4_museum_out.png"); await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("museum door enters hall:", await ev("__game.region().name"))
        # v0.14: the door walks into the hall. Ada the curator opens the donation list.
        await ev("__game.S.x=__game.CURATOR.x*16+8;__game.S.y=(__game.CURATOR.y+1)*16+6;__game.S.dir=1"); await pg.wait_for_timeout(200); await pg.keyboard.press("e"); await pg.wait_for_timeout(250)
        print("museum open:", await ev("[...__game.stack]"), "|", await ev("musum.textContent"))
        rows=await pg.query_selector_all("#murows .srow"); await rows[0].tap(); await pg.wait_for_timeout(150); print("donate 1:", await ev("document.getElementById('toast').textContent"))
        for i in (1,3,2):
            rows=await pg.query_selector_all("#murows .srow"); await rows[i].tap(); await pg.wait_for_timeout(120)
        print("after donations:", await ev("musum.textContent.slice(0,30)"), "| toast:", await ev("document.getElementById('toast').textContent"), "| top hat unlocked:", await ev("__game.UNLOCK[3][4]()"))
        await pg.screenshot(path="v4_museum.png"); await pg.tap("#muclose")
        await pg.tap("#mapbtn"); await pg.wait_for_timeout(200); print("map:", await ev("mapinfo.textContent")); await pg.screenshot(path="v4_map.png"); await pg.tap("#mapclose")
        await pg.tap("#jbtn"); await pg.tap("#jprev"); await pg.wait_for_timeout(400); print("journal:", await ev("jpn.textContent+' | '+jup.textContent")); await pg.screenshot(path="v4_journal.png"); await pg.tap("#jclose")
        await pg.reload(); await pg.wait_for_timeout(600); print("reload:", await ev("[__game.S.rod,__game.S.net,Object.keys(__game.S.don).length,tslotv.textContent]"))
        print("errors", errs); await b.close()
asyncio.run(main())
