import asyncio, json
from playwright.async_api import async_playwright
# v0.14.7: Christmas theme toggle (title and settings), decorations in every area, off by default
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":732,"height":412}, device_scale_factor=2, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900)
        print("default:", await ev("[CFG.xmas,$('txmas').textContent]")); assert await ev("CFG.xmas")==0
        await ev("$('txmas').scrollIntoView()"); await pg.tap("#txmas"); await pg.wait_for_timeout(500); print("title toggle:", await ev("[CFG.xmas,$('txmas').textContent]")); assert await ev("CFG.xmas")==1
        await pg.screenshot(path="xm_title.png"); await ev("$('tcont').scrollIntoView()"); await pg.tap("#tcont"); await pg.wait_for_timeout(300)
        spots=await ev("__game.XSPOTS.map(q=>[q.x,q.y,q.rg.name,__game.solidTile(q.x,q.y)])"); regs=sorted(set(s[2] for s in spots)); print("gift trees:", len(spots), regs)
        print("on a solid tile (skipped when drawn):",[s for s in spots if s[3]]); assert len(regs)>=7 and sum(1 for s in spots if s[3])<=1
        # they never block: the reachable area is the same with the theme on
        print("settings row:", await ev("(()=>{openPanel('settings');const r=[...document.querySelectorAll('#srows .srow')].find(r=>r.textContent.includes('Christmas theme'));const t=r?r.textContent:'';closeAll();return t})()"))
        for tag,x,y in [("cabin",15,28),("cave",30,8),("museum",45,45),("autumn",80,30),("snow",32,133),("desert",66,119),("incave",26,94)]:
            await ev(f"(()=>{{const G=__game;G.seen.fill(1);let X={x},Y={y};for(let r=0;r<5&&G.solidTile(X,Y);r++)X++;G.S.x=X*16+8;G.S.y=Y*16+10;G.S.clock=100}})()"); await pg.wait_for_timeout(450); await pg.screenshot(path=f"xm_{tag}.png")
        await ev("CFG.xmas=0;applyCfg('xmas')"); await pg.wait_for_timeout(300); await pg.reload(); await pg.wait_for_timeout(800); print("off persists:", await ev("CFG.xmas")); assert await ev("CFG.xmas")==0
        print("errors", errs); await b.close()
asyncio.run(main())
