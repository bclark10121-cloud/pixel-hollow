import asyncio
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        for name,vp,dsf in [("p",{"width":412,"height":915},2.625),("l",{"width":640,"height":360},2)]:
            ctx = await b.new_context(viewport=vp, device_scale_factor=dsf, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
            pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
            ev=lambda s: pg.evaluate(s)
            await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1000); await pg.screenshot(path=f"tour_{name}_title.png")
            await pg.tap("#tcont"); await pg.wait_for_timeout(300)
            await pg.tap("text=Journal"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"tour_{name}_journal.png"); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
            await pg.tap("text=Map"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"tour_{name}_map.png"); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
            v=await ev("(()=>{const v=__game.VIL[0];__game.S.x=v.x*16+8;__game.S.y=(v.y+1)*16+10;return v.id})()"); await pg.wait_for_timeout(300); await pg.keyboard.press("e"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"tour_{name}_talk.png")
            for i in range(5): await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
            await ev("__game.S.x=(__game.MUS.x+2)*16+8;__game.S.y=(__game.MUS.y+__game.MUS.h)*16+6"); await pg.wait_for_timeout(300); await pg.keyboard.press("e"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"tour_{name}_museum.png"); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
            await ev("__game.S.x=13*16+8;__game.S.y=21*16+10;__game.S.clock=100"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"tour_{name}_behind.png")
            await ev("__game.S.x=25*16+8;__game.S.y=94*16+10"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"tour_{name}_cave.png")
            await ev("__game.S.x=36*16+8;__game.S.y=6*16+10"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"tour_{name}_forest.png")
            for nm,x,y in [("edge1",3,3),("edge2",116,56),("edge3",4,105),("edge4",116,136)]:
                await ev(f"__game.S.x={x}*16+8;__game.S.y={y}*16+10;__game.S.clock=100"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"tour_{name}_{nm}.png")
            await ctx.close()
        print("errors",errs); await b.close()
asyncio.run(main())
