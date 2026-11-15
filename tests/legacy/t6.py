import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":412,"height":915},has_touch=True,is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(300)
        await pg.tap("#tnew"); await pg.fill("#bname","Brian")
        row=(await pg.query_selector_all("#brows .srow"))[1]
        for want in ["They","She","Name only","He","Name only"]:
            await (await row.query_selector_all(".pm"))[1 if want!="Name only" or True else 0].tap()
            if want=="Name only" and await ev("__game.S.ch.pro")!=3: await (await row.query_selector_all(".pm"))[0].tap(); await (await row.query_selector_all(".pm"))[0].tap()
        print("row shows:", await row.inner_text(), "pro", await ev("__game.S.ch.pro"))
        await pg.tap("#bdone"); await pg.wait_for_timeout(200)
        await ev("__game.S.x=14*16+8;__game.S.y=26*16+2"); await pg.wait_for_timeout(100); await pg.tap("#abtn")
        print("cabin:", await ev("dtext.textContent")); await pg.tap("#dialog")
        await ev("__game.ITEMS.slice(0,5).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(900); await pg.tap("#dialog")
        await pg.tap("#jbtn"); print("journal:", await ev("jup.textContent")); await pg.tap("#jclose")
        await pg.tap("#mbtn"); print("pause:", await ev("pwho.textContent"))
        await pg.reload(); await pg.wait_for_timeout(300); print("saved pro:", await ev("__game.S.ch.pro"), "errors", errs)
        await b.close()
asyncio.run(main())
