import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        ctx = await b.new_context(viewport={"width":640,"height":360}, device_scale_factor=3, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(600)
        async def press(i,hold=60):
            await ev(f"__padKey({i},1)"); await pg.wait_for_timeout(hold); await ev(f"__padKey({i},0)"); await pg.wait_for_timeout(70)
        await ev("__padName('Retroid Pocket Controller')"); await press(4)
        await press(13); print("focus after down:", await ev("document.querySelector('.foc').id"))
        await press(15); print("slot via right:", await ev("tslotv.textContent")); await press(14)
        await press(12); await press(0); print("start ->", await ev("[...__game.stack]"))
        await pg.screenshot(path="v36_land_builder.png")
        for _ in range(3): await press(13)
        await press(0); await press(3)
        await press(1); await pg.wait_for_timeout(300); print("playing:", await ev("__game.stack.length===0"), await ev("jbtn.textContent+' | '+mapbtn.textContent+' | '+mbtn.textContent"))
        x0=await ev("__game.S.x"); await ev("__padAxes(1,0,0,0,0,0)"); await pg.wait_for_timeout(500); x1=await ev("__game.S.x")
        await ev("__game.S.boots=true"); await ev("__padKey(5,1)"); await pg.wait_for_timeout(500); x2=await ev("__game.S.x"); await ev("__padKey(5,0)"); await ev("__padAxes(0,0,0,0,0,0)")
        print("walk px:", round(x1-x0), "run px (RB held, boots):", round(x2-x1))
        await pg.screenshot(path="v36_land_play.png")
        await press(3); await press(5); await pg.wait_for_timeout(350); print("journal RB flip:", await ev("jpn.textContent")); await press(4); await press(4); await pg.wait_for_timeout(350); print("LB x2:", await ev("jpn.textContent"))
        await pg.screenshot(path="v36_land_journal.png"); await press(1)
        await press(2); await pg.wait_for_timeout(150); print("X map:", await ev("[...__game.stack]")); await press(1)
        print("errors", errs); await b.close()
asyncio.run(main())
