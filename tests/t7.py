import asyncio, json
from playwright.async_api import async_playwright
SEED="if(!localStorage.getItem('seeded')){localStorage.setItem('seeded','1');localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));localStorage.setItem('wandervalley_save_v1',JSON.stringify({v:1,x:232,y:442,boots:true,started:true,ch:{name:'Brian',pro:0,body:0,skin:1,hs:0,hc:0,hat:0,shirt:0,bot:0,pc:0},found:['daisy','bluebell','poppy','sunflower','clover','scallop','conch','starfish','seaglass','driftwood','acorn','pinecone','mushroom','feather','amber']}))}"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        # valley layout must match v0.2.6 exactly
        import os
        if os.path.exists("/home/claude/game/index.v0.2.6.html"):
            pg0 = await b.new_page(); await pg0.goto("file:///home/claude/game/index.v0.2.6.html"); await pg0.wait_for_timeout(400)
            old = await pg0.evaluate("(()=>{let s='';for(let y=0;y<60;y++)for(let x=0;x<56;x++)s+=__game.solidTile(x,y)?1:0;return s})()")
        else: old = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"valley_v026.txt")).read().strip()  # saved from v0.12, which matched v0.2.6
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True)
        await ctx.add_init_script(SEED)
        pg = await ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(700)
        new = await ev("(()=>{let s='';for(let y=0;y<60;y++)for(let x=0;x<56;x++)s+=__game.solidTile(x,y)?1:0;return s})()")
        # v0.14.1 clears a few trees that boxed treasures in. Those tiles are expected to open up. Everything else must match.
        cl = await ev("JSON.stringify((__game.CLEARED||[]).filter(c=>c[0]<56&&c[1]<60).map(c=>c[1]*56+c[0]))"); cl=set(json.loads(cl))
        exp = "".join("0" if i in cl else ch for i,ch in enumerate(old))
        print("valley identical to v0.2.6 apart from", len(cl), "cleared trees:", exp==new, "diff tiles:", sum(a!=c for a,c in zip(exp,new)))
        if exp!=new: errs.append("valley layout changed")
        r = await ev("""(()=>{const G=__game;G.openBridge(true);const a=G.reachFrom(14,27),c=G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y);G.openBridge(G.S.bridge);
          const bad=[];for(const it of G.ITEMS){const k=it.y*G.MW+it.x;const cave=it.y>=62;if(!(cave?c[k]:a[k]))bad.push(it.id)}
          const sh=a[G.SHOVEL.y*G.MW+G.SHOVEL.x];let fl=0,cr=0;for(let y=62;y<100;y++)for(let x=0;x<50;x++){if(G.ground[y*G.MW+x]===7){fl++;if(c[y*G.MW+x])cr++}}
          return {total:G.ITEMS.length,unreachable:bad,shovel:!!sh,caveFloor:fl,caveReach:cr,caveItems:G.ITEMS.filter(i=>i.y>=62).map(i=>[i.id,i.x,i.y]),exit:!!c[98*G.MW+25]}})()""")
        print(json.dumps(r))
        print("loaded save:", await ev("[Object.keys(__game.S.found).length,__game.S.boots,__game.S.bridge,document.getElementById('count').textContent]"))
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        # walk to the bridge: auto repair
        await ev("__game.S.x=52*16+8;__game.S.y=30*16+10"); await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(700)
        print("bridge:", await ev("__game.S.bridge"), "|", await ev("dtext.textContent")); await pg.screenshot(path="v3_bridge.png")
        await pg.wait_for_timeout(2500); await pg.keyboard.up("ArrowRight")
        print("crossed to x tile", await ev("Math.floor(__game.S.x/16)"))
        await pg.screenshot(path="v3_autumn1.png")
        for name,(x,y) in {"v3_autumn2":(88,30),"v3_patch":(73,37),"v3_pond":(95,24),"v3_shovel":(110,30)}.items():
            await ev(f"__game.S.x={x}*16+8;__game.S.y={y}*16+10"); await pg.wait_for_timeout(250); await pg.screenshot(path=name+".png")
        await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(150); await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(150); await pg.keyboard.press("e"); await pg.wait_for_timeout(100)
        print("shovel:", await ev("__game.S.shovel"), "|", await ev("dtext.textContent")); await pg.tap("#dialog")
        # dig spot
        await ev("__game.S.x=93*16+8;__game.S.y=41*16+4"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(100)
        print("dig:", await ev("!!__game.S.found.key"))
        # finish an autumn set -> lantern
        await ev("__game.ITEMS.filter(i=>i.set==='leaves').forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(900)
        print("lantern:", await ev("__game.S.lantern"), "|", await ev("dtext.textContent")); await pg.tap("#dialog")
        # cave
        await ev("__game.S.x=30*16+8;__game.S.y=5*16+8"); await pg.wait_for_timeout(100); await pg.keyboard.press("e"); await pg.wait_for_timeout(300)
        print("in cave tile:", await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]")); await pg.screenshot(path="v3_cave1.png")
        ci = await ev("__game.ITEMS.find(i=>i.set==='crystal')")
        await ev(f"__game.S.x={ci['x']}*16+8;__game.S.y={ci['y']+1}*16+10"); await pg.wait_for_timeout(250); await pg.screenshot(path="v3_cave2.png")
        await pg.tap("#mapbtn"); await pg.wait_for_timeout(200); await pg.screenshot(path="v3_map_cave.png"); await pg.tap("#mapclose")
        await ev("__game.S.x=25*16+8;__game.S.y=97*16+4"); await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(600); await pg.keyboard.up("ArrowDown")
        print("exit to tile:", await ev("[Math.floor(__game.S.x/16),Math.floor(__game.S.y/16)]"), "blocked there:", await ev("__game.solidTile(30,5)"))
        await pg.tap("#mapbtn"); await pg.wait_for_timeout(200); print("map:", await ev("mtitle.textContent+' :: '+mapinfo.textContent")); await pg.screenshot(path="v3_map.png"); await pg.tap("#mapclose")
        await pg.tap("#jbtn"); await pg.wait_for_timeout(150); print("journal:", await ev("jsum.textContent+' | '+jup.textContent")); await pg.screenshot(path="v3_journal.png"); await pg.tap("#jclose")
        # night
        await ev("__game.S.clock=450;__game.S.x=20*16+8;__game.S.y=31*16"); await pg.wait_for_timeout(250); await pg.screenshot(path="v3_night.png")
        await ev("__game.S.clock=355"); await pg.wait_for_timeout(250); await pg.screenshot(path="v3_dusk.png")
        await pg.reload(); await pg.wait_for_timeout(500)
        print("reload:", await ev("[__game.S.bridge,__game.S.shovel,__game.S.lantern,Object.keys(__game.S.found).length,__game.seen.reduce((a,b)=>a+b,0)]"))
        # new game resets and bridge needs 8
        await pg.tap("#tnew"); await pg.tap("#cyes"); await pg.tap("#bdone"); await pg.wait_for_timeout(200)
        await ev("__game.S.x=53*16+8;__game.S.y=30*16+4"); await pg.wait_for_timeout(100); await pg.keyboard.press("e")
        print("new game bridge sign:", await ev("dtext.textContent"), "| solid bridge:", await ev("__game.solidTile(__game.BRX,30)"))
        print("errors", errs); await b.close()
asyncio.run(main())
