import asyncio, sys
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
# screenshots of the main panels at portrait phone and landscape handheld sizes
async def main():
    tag=sys.argv[1] if len(sys.argv)>1 else "ui"
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        for name,vp,dpr in [("port",{"width":412,"height":915},2.625),("land",{"width":640,"height":360},3)]:
            ctx = await b.new_context(viewport=vp, device_scale_factor=dpr, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
            ev=lambda s: pg.evaluate(s)
            await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f"{tag}_{name}_title.png")
            await pg.tap("#tcont"); await pg.wait_for_timeout(300)
            await ev("say('Mira: I tend the meadow gardens. I would love to see a wild Sunflower. Have you found one?')"); await pg.wait_for_timeout(200); await pg.screenshot(path=f"{tag}_{name}_dialog.png"); await ev("hush()")
            for pnl in ["pause","journal","settings","builder"]:
                await ev(f"openPanel('{pnl}')"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"{tag}_{name}_{pnl}.png"); await ev("closeAll()")
            await ev("__game.openStove()"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"{tag}_{name}_stove.png"); await ev("closeAll()")
            ov=await ev("[...document.querySelectorAll('.card')].filter(c=>c.offsetParent).map(c=>c.getBoundingClientRect().right)"); print(name,"card right edges",ov)
            await ctx.close()
        print("errors",errs); await b.close()
asyncio.run(main())
