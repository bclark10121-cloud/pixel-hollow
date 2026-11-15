import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":412,"height":880}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page()
        errs=[]
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html")
        await pg.wait_for_timeout(800)
        r = await pg.evaluate("""()=>{const seen=__reach();const G=__game;return {items:G.ITEMS.map(i=>[i.id,!!seen[i.y*60+i.x],G.solidTile(i.x,i.y)]),
          signs:G.SIGNS.map(s=>[s.x,s.y,[[1,0],[-1,0],[0,1],[0,-1]].some(d=>seen[(s.y+d[1])*60+s.x+d[0]])]),cave:!!seen[5*60+30], bridge:!!seen[30*60+52]}}""")
        print(json.dumps(r))
        await pg.screenshot(path="s1_start.png")
        # walk right with keyboard
        x0 = await pg.evaluate("__game.S.x")
        await pg.keyboard.down("ArrowDown"); await pg.wait_for_timeout(500); await pg.keyboard.up("ArrowDown")
        await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(1000); await pg.keyboard.up("ArrowRight")
        x1 = await pg.evaluate("__game.S.x"); print("moved", x0, x1)
        # touch joystick
        await pg.touchscreen.tap(100,600)
        for name,(x,y) in {"s2_beach":(30,50),"s3_forest":(30,10),"s4_pond":(32,30),"s5_bridge":(52,30),"s6_cave":(30,5)}.items():
            await pg.evaluate(f"__game.S.x={x}*16+8;__game.S.y={y}*16+10")
            await pg.wait_for_timeout(300); await pg.screenshot(path=name+".png")
        await pg.evaluate("__game.ITEMS.slice(0,5).forEach(i=>__game.collect(i));__game.collect(__game.ITEMS[7])")
        await pg.wait_for_timeout(1200); await pg.screenshot(path="s7_reward.png")
        await pg.click("#dialog"); await pg.click("#jbtn"); await pg.wait_for_timeout(300); await pg.screenshot(path="s8_journal.png")
        await pg.reload(); await pg.wait_for_timeout(500)
        print("after reload", await pg.evaluate("[Object.keys(__game.S.found).length,__game.S.boots]"))
        print("errors", errs)
        await b.close()
asyncio.run(main())
