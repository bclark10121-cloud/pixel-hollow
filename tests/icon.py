import asyncio, base64
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        for name,vp,dsf in [("p",{"width":412,"height":915},2.625),("l",{"width":640,"height":360},2)]:
            ctx = await b.new_context(viewport=vp, device_scale_factor=dsf, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
            pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f"start_{name}.png")
            if name=="p":
                for out,size,layer,k in [("icon_full",1024,0,1.12),("icon_bg",432,1,1),("icon_fg",432,2,0.74)]:
                    d=await pg.evaluate(f"(()=>{{const c=document.createElement('canvas');c.width=c.height={size};__game.emblem(c.getContext('2d'),{size},{layer},{k});return c.toDataURL('image/png')}})()")
                    open(out+".png","wb").write(base64.b64decode(d.split(",")[1]))
                await pg.tap("#tcont"); await pg.wait_for_timeout(400); await pg.screenshot(path="start_p_after.png")
            await ctx.close()
        print("errors",errs); await b.close()
asyncio.run(main())
