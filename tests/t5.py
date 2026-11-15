import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":412,"height":915})
        await ctx.add_init_script("if(!localStorage.getItem('seeded')){localStorage.setItem('seeded','1');localStorage.setItem('wandervalley_save_v1',JSON.stringify({v:1,x:232,y:442,boots:true,started:true,found:['daisy','poppy']}))}")
        pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(400)
        print("v0.2 save loads:", await pg.evaluate("[Object.keys(__game.S.found).length,__game.S.boots,__game.S.ch.name,getComputedStyle(tcont).display]"), errs)
        await b.close()
asyncio.run(main())
