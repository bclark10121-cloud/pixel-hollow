import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=1, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
        await pg.tap("#tnew"); await pg.wait_for_timeout(300); await pg.tap("#bdone"); await pg.wait_for_timeout(700)
        for i in range(4): await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        print("gfx",await ev("CFG.gfx"))
        await ev("Object.assign(__game.S,{shovel:true,rod:true,net:true,boots:true,lantern:true});__game.ITEMS.filter(i=>!i.off).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(300)
        for k in range(12):
            if await ev("stack.length>0||!!dlg"): await ev("while(stack.length)closePanel();hush()"); await pg.wait_for_timeout(100)
        # gifts: talk to every villager a few times
        for r in range(4):
            n=await ev("__game.VIL.length")
            for i in range(n):
                await ev(f"__game.talk(__game.VIL[{i}])"); await pg.wait_for_timeout(120); await ev("while(stack.length)closePanel();hush()")
        print("gifts:",await ev("__game.ITEMS.filter(i=>i.gift).map(i=>i.id+':'+(__game.S.found[i.id]?1:0)).join(' ')"))
        print("villagers done:",await ev("JSON.stringify(__game.S.vil)"))
        # garden: grow each seed kind to full and harvest
        kinds=await ev("__game.ITEMS.filter(i=>i.gard).map(i=>i.gard)")
        for j,k in enumerate(kinds):
            await ev(f"__game.S.garden[{j%6}]={{k:'{k}',g:3.2,w:-1}};__game.tendPlot({j%6})"); await pg.wait_for_timeout(120); await ev("while(stack.length)closePanel();hush()")
        print("garden:",await ev("__game.ITEMS.filter(i=>i.gard).map(i=>i.id+':'+(__game.S.found[i.id]?1:0)).join(' ')"))
        await ev("__game.ITEMS.filter(i=>i.fish).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(200); await ev("while(stack.length)closePanel();hush()")
        for r in range(3):
            for i in range(await ev("__game.VIL.length")):
                await ev(f"__game.talk(__game.VIL[{i}])"); await pg.wait_for_timeout(120); await ev("while(stack.length)closePanel();hush()")
        print("total found:",await ev("Object.keys(__game.S.found).length"),"of",await ev("__game.ITEMS.length"),"missing:",await ev("__game.ITEMS.filter(i=>!__game.S.found[i.id]).map(i=>i.id).join(',')"))
        print("errors",errs[:3]); await b.close()
asyncio.run(main())
