import asyncio, json
from playwright.async_api import async_playwright
# v0.14.3: every treasure has a clean drawn icon in the angled view. The pixel view keeps the pixel art.
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":732,"height":412}, device_scale_factor=2.625, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900); await pg.tap("#tcont"); await pg.wait_for_timeout(250)
        r=await ev("""(()=>{const G=__game,miss=G.ITEMS.filter(i=>!G.VIC[i.id]).map(i=>i.id),imgs=new Set(G.ITEMS.map(i=>i.img)),bad=[];
          for(const it of G.ITEMS){const c=G.vicon(it.id),d=c.getContext('2d').getImageData(0,0,96,96).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>40)n++;const f=n/(96*96);if(f<0.12||f>0.9)bad.push([it.id,+f.toFixed(2)])}
          return {items:G.ITEMS.length,withIcon:G.ITEMS.length-miss.length,missing:miss,distinctImages:imgs.size,coverageOutOfRange:bad,size:sicon(G.ITEMS[0].img).width}})()""")
        print("icons:", json.dumps(r))
        if r["missing"]: errs.append("missing icons "+",".join(r["missing"]))
        if r["coverageOutOfRange"]: errs.append("icon looks empty or overfilled "+json.dumps(r["coverageOutOfRange"]))
        if r["distinctImages"]!=r["items"]: errs.append("treasures share an image")
        if r["size"]!=96: errs.append("angled icon size "+str(r["size"]))
        # journal and museum show the new icons
        await ev("openPanel('journal')"); await pg.wait_for_timeout(300); print("journal icon canvas:", await ev("(()=>{const c=document.querySelector('#jsets .slot canvas');return [c.width,c.height,getComputedStyle(c).width]})()"))
        await pg.screenshot(path="ic_journal.png"); await ev("jflip(1);jflip(1);jflip(1);jflip(1)"); await pg.wait_for_timeout(300); await pg.screenshot(path="ic_journal_fish.png"); await ev("closeAll()")
        # in the world: stand by a few treasures
        await ev("(()=>{const G=__game;['amber','pinecone','mushroom','nest','kite','pc3'].forEach(id=>delete G.S.found[id]);G.S.x=33*16+8;G.S.y=9*16+10;G.S.clock=100})()"); await pg.wait_for_timeout(600); await pg.screenshot(path="ic_world.png")
        # the pixel view keeps the pixel art
        await ev("__game.CFG.gfx=0;applyCfg('gfx');openPanel('journal')"); await pg.wait_for_timeout(300)
        px=await ev("(()=>{const c=document.querySelector('#jsets .slot canvas');return [c.width,c.height]})()"); print("pixel view journal canvas:", px); assert px==[10,10]
        await ev("closeAll();__game.CFG.gfx=1;applyCfg('gfx')")
        print("errors", errs); await b.close()
asyncio.run(main())
