import asyncio, json, sys
from playwright.async_api import async_playwright
# v0.14.5: wildlife to photograph, stamp card, calendar touches
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
GAME=sys.argv[1] if len(sys.argv)>1 else "/home/claude/game/index.html"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":732,"height":412}, device_scale_factor=2.625, has_touch=True, is_mobile=True, accept_downloads=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file://"+GAME); await pg.wait_for_timeout(900)
        # ---- calendar on the title screen ----
        for m,tag in [(11,"dec"),(9,"oct"),(5,"jun")]:
            await ev(f"window.__month={m}"); await pg.wait_for_timeout(500); await pg.screenshot(path=f"wl_title_{tag}.png")
        await ev("delete window.__month"); await pg.tap("#tcont"); await pg.wait_for_timeout(300)
        # ---- wildlife homes ----
        r=await ev("""(()=>{const G=__game;return G.CRIT.map(c=>[c.id,c.hx,c.hy,G.regAt(c.hx,c.hy).name,G.solidTile(c.hx,c.hy)])})()""")
        for x in r: print("  home", x)
        assert len(r)==14 and not any(x[4] for x in r)
        print("totals:", await ev("[__game.ITEMS.length,__game.SETS.length,__game.ITEMS.filter(i=>i.wild).length,__game.ITEMS.filter(i=>i.wild&&!i.off).length]"))
        # walk up to the rabbit, open photo mode, take a picture
        spotted=[]
        for cid in ["w_rabbit","w_deer","w_heron"]:
            await ev(f"(()=>{{const G=__game,c=G.CRIT.find(q=>q.id==='{cid}');G.S.x=c.x+70;G.S.y=c.y+70;c.x=c.hx*16+8;c.y=c.hy*16+10;G.S.clock=100;closeAll()}})()"); await pg.wait_for_timeout(500)
            await ev("openPhoto()"); await pg.wait_for_timeout(400)
            on=await ev(f"__game.CRIT.find(q=>q.id==='{cid}').on"); await pg.screenshot(path=f"wl_{cid}.png")
            await ev("phSnap()"); await pg.wait_for_timeout(1500); got=await ev(f"!!__game.S.found['{cid}']"); spotted.append([cid,on,got]); await ev("back()"); await pg.wait_for_timeout(200)
        print("photo spotting:", spotted); assert all(s[2] for s in spotted)
        print("toast:", await ev("$('toast').textContent"))
        # the owl only comes out at night
        print("owl by day / night:", await ev("(()=>{const G=__game,c=G.CRIT.find(q=>q.id==='w_owl');G.S.clock=100;const a=critAwake(c);G.S.clock=450;const b=critAwake(c);G.S.clock=100;return [a,b]})()"))
        # animals step away when you walk up, then settle near home
        fl=await ev("(()=>{const G=__game,c=G.CRIT.find(q=>q.id==='w_fox');c.x=c.hx*16+8;c.y=c.hy*16+10;G.S.x=c.x-20;G.S.y=c.y;const d0=Math.hypot(G.S.x-c.x,G.S.y-c.y);for(let i=0;i<30;i++)G.updateCrit(0.05);return [Math.round(d0),Math.round(Math.hypot(G.S.x-c.x,G.S.y-c.y)),Math.round(Math.hypot(c.x-c.hx*16,c.y-c.hy*16))]})()")
        print("fox shy:", fl); assert fl[1]>fl[0]
        # journal wildlife page and hints
        await ev("openPanel('journal');jflip(-1);jflip(-1);jflip(-1)"); await pg.wait_for_timeout(300); print("journal page:", await ev("jpn.textContent+' | '+[...document.querySelectorAll('#jsets h2')].map(h=>h.textContent).join(' ; ')"))
        await pg.screenshot(path="wl_journal.png")
        print("hint:", await ev("__game.hintFor(__game.ITEMS.find(i=>i.id==='w_owl'))"))
        # ---- stamps ----
        await ev("jflip(1)"); await pg.wait_for_timeout(300); st=await ev("jpn.textContent+' | '+document.querySelector('#jsets h2').textContent"); print("stamps page:", st); assert "Stamps" in st
        await pg.screenshot(path="wl_stamps.png")
        n0=await ev("__game.S.stp.length"); await ev("for(let i=0;i<10;i++)stampCount('ph')"); await ev("closeAll()"); await pg.wait_for_timeout(2600)
        print("stamps before/after 10 photos:", n0, await ev("__game.S.stp.length"), "| toast:", await ev("$('toast').textContent")); assert await ev("__game.S.stp.includes('photo')")
        await ev("save()"); print("saved:", await ev("(()=>{const d=JSON.parse(localStorage.getItem(slotKey(CFG.slot)));return [d.sc,d.stp.length]})()"))
        # ---- museum gets a Wildlife case ----
        print("museum cases:", await ev("[__game.CASES.length,__game.CASES.some(c=>c.set==='wildlife')]"))
        # ---- pixel view draws the animals too ----
        await ev("__game.CFG.gfx=0;applyCfg('gfx');(()=>{const G=__game,c=G.CRIT.find(q=>q.id==='w_rabbit');G.S.x=c.x+30;G.S.y=c.y+20})()"); await pg.wait_for_timeout(500); await pg.screenshot(path="wl_pixel.png")
        print("pixel on screen:", await ev("__game.CRIT.find(q=>q.id==='w_rabbit').on")); await ev("__game.CFG.gfx=1;applyCfg('gfx')")
        print("errors", errs); await b.close()
asyncio.run(main())
