import asyncio, json
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0]
SHOTS=[("valley",14,28,100),("behind",14,21,100),("builder",14,28,100),("museum",44,45,100),("cavedoor",30,7,100),("autumn",80,30,100),("pond",30,30,100),("cave",25,94,100),("home",70,75,100),("snow",30,122,100),("desert",90,122,100),("night",14,28,450),("rain",44,45,460)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        for name,vp,dsf in [("p",{"width":412,"height":915},2.625),("l",{"width":640,"height":360},2)]:
            ctx = await b.new_context(viewport=vp, device_scale_factor=dsf, has_touch=True, is_mobile=True)
            await ctx.add_init_script(SEED); await ctx.add_init_script("if(!localStorage.getItem('isoset')){localStorage.setItem('isoset','1');localStorage.removeItem('wandervalley_cfg_v1')}")
            pg = await ctx.new_page()
            pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
            ev=lambda s: pg.evaluate(s)
            await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1200)
            print(name,"gfx",await ev("CFG.gfx"),"body iso",await ev("document.body.classList.contains('iso')"))
            await pg.screenshot(path=f"iso_{name}_title.png")
            await pg.tap("#tcont"); await pg.wait_for_timeout(300)
            for s,x,y,c in (SHOTS if name=="p" else SHOTS[:2]+SHOTS[5:7]):
                await ev(f"__game.S.x={x}*16+8;__game.S.y={y}*16+10;__game.S.clock={c}"); await pg.wait_for_timeout(350)
                await pg.screenshot(path=f"iso_{name}_{s}.png")
            if name=="p":
                # movement mapping: screen right should move right on screen (x up, y down in world)
                await ev("__game.S.x=14*16+8;__game.S.y=28*16+10;__game.S.clock=100"); await pg.wait_for_timeout(100)
                for key,exp in [("ArrowRight","sx+"),("ArrowLeft","sx-"),("ArrowUp","sy-"),("ArrowDown","sy+")]:
                    a=await ev("[__game.S.x,__game.S.y]"); await pg.keyboard.down(key); await pg.wait_for_timeout(300); await pg.keyboard.up(key); c=await ev("[__game.S.x,__game.S.y]")
                    dx,dy=c[0]-a[0],c[1]-a[1]; print(key,"world d",round(dx,1),round(dy,1),"screen d",round(dx-dy,1),round(dx+dy,1),exp)
                # tap walk: tap a spot right of the player, expect path target near there
                await ev("CFG.stick=2"); st=await ev("__game.isoState()"); 
                await pg.touchscreen.tap(300,560); await pg.wait_for_timeout(900); c2=await ev("[__game.S.x,__game.S.y]"); print("tapwalk moved to",[round(v,1) for v in c2])
                await pg.tap("#mbtn"); await pg.wait_for_timeout(200); await pg.screenshot(path="iso_p_pause.png"); await pg.tap("#pset"); await pg.wait_for_timeout(200); await pg.screenshot(path="iso_p_settings.png")
            await ctx.close()
        print("errors", errs); await b.close()
asyncio.run(main())
