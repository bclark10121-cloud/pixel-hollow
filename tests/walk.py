import asyncio
from playwright.async_api import async_playwright
from PIL import Image
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1000); await pg.tap("#tcont"); await pg.wait_for_timeout(300)
        frames=[]
        for key in ["ArrowRight","ArrowUp","ArrowLeft","ArrowDown"]:
            await ev("__game.S.x=20*16+8;__game.S.y=30*16+10;__game.S.clock=100"); await pg.wait_for_timeout(200)
            await pg.keyboard.down(key); await pg.wait_for_timeout(260)
            a=await ev("[__game.S.x,__game.S.y]")
            for i in range(4):
                await pg.wait_for_timeout(70); await pg.screenshot(path="w.png"); frames.append(Image.open("w.png").convert("RGB").crop((390,1040,690,1400)))
            c=await ev("[__game.S.x,__game.S.y]"); await pg.keyboard.up(key)
            t0=await ev("[__game.S.vx,__game.S.vy]"); await pg.wait_for_timeout(120); t1=await ev("[__game.S.vx,__game.S.vy]")
            print(key,"speed after release 0ms",[round(v) for v in t0],"120ms",[round(v) for v in t1])
        await pg.wait_for_timeout(400); await pg.screenshot(path="w.png"); frames.append(Image.open("w.png").convert("RGB").crop((390,1040,690,1400)))
        W=Image.new("RGB",(300*9,720)); 
        for i,f in enumerate(frames): W.paste(f,((i%9)*300,(i//9)*360))
        W.resize((1350,360)).save("walksheet.png")
        await pg.tap("#mbtn"); await pg.wait_for_timeout(200); await pg.tap("#pchar"); await pg.wait_for_timeout(500); await pg.screenshot(path="walk_builder.png")
        print("errors",errs); await b.close()
asyncio.run(main())
