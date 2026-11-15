import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True)
        pg = await ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(600)
        await pg.tap("#tnew"); await pg.wait_for_timeout(300)
        base=await ev("JSON.stringify(__game.S.ch)")
        await pg.tap("#ball"); a1=await ev("JSON.stringify(__game.S.ch)"); print("random everything changed:", a1!=base, a1)
        await pg.tap("#bundo"); print("undo restores:", await ev("JSON.stringify(__game.S.ch)")==base)
        rows=await pg.query_selector_all("#brows .brow")
        print("rows:", len(rows))
        await (await rows[3].query_selector(".lk")).tap()   # lock Hair
        hs=await ev("__game.S.ch.hs"); ok=True
        for _ in range(12):
            await pg.tap("#brand"); ok = ok and (await ev("__game.S.ch.hs"))==hs
        print("locked hair survives 12 random looks:", ok)
        sk=await ev("__game.S.ch.skin"); await (await rows[2].query_selector(".dc")).tap(); print("dice changes skin:", (await ev("__game.S.ch.skin"))!=sk)
        for i,t in enumerate(["Farmer","Explorer","Beach day","Cozy","Night owl","Sporty"]):
            await (await pg.query_selector_all("#bthemes .btn"))[i].tap()
        print("themes ok; after Sporty:", await ev("[__game.S.ch.hat,__game.S.ch.bot]"))
        await pg.screenshot(path="v35_builder.png", full_page=False)
        await ev("document.getElementById('builder').scrollTop=9999"); await pg.wait_for_timeout(100); await pg.screenshot(path="v35_builder_b.png")
        await pg.tap("#bdone"); await pg.wait_for_timeout(200)
        await pg.reload(); await pg.wait_for_timeout(400); print("saved:", await ev("JSON.stringify(__game.S.ch)"))
        # controller: A rolls, Y locks
        await pg.tap("#tcont"); await pg.tap("#mbtn"); await pg.tap("#pchar"); await pg.wait_for_timeout(100)
        async def press(i):
            await ev(f"__padKey({i},1)"); await pg.wait_for_timeout(60); await ev(f"__padKey({i},0)"); await pg.wait_for_timeout(60)
        await press(13); await press(13); await press(13)
        v=await ev("__game.S.ch.skin"); await press(0); print("pad A rolls skin:", (await ev("__game.S.ch.skin"))!=v, "| focus:", await ev("document.querySelector('.foc .nm').textContent"))
        await press(3); print("pad Y locks:", await ev("document.querySelector('.foc').classList.contains('locked')"), "| hint:", await ev("bhint.textContent"))
        # sheet of looks
        await ev("""()=>{const cfgs=[{hs:4,hat:4,gl:1,face:0,pat:1,pack:0,body:1,skin:0,hc:3,eye:3,shirt:5,bot:2,pc:4,shoe:2},{hs:5,hat:4,gl:2,face:3,pat:0,pack:3,body:0,skin:2,hc:6,eye:0,shirt:9,bot:0,pc:4,shoe:1},{hs:6,hat:4,gl:0,face:0,pat:2,pack:0,body:1,skin:4,hc:1,eye:1,shirt:2,bot:0,pc:0,shoe:0},{hs:7,hat:4,gl:1,face:2,pat:0,pack:1,body:0,skin:3,hc:1,eye:1,shirt:3,bot:1,pc:1,shoe:0},{hs:0,hat:5,gl:0,face:1,pat:2,pack:0,body:0,skin:1,hc:0,eye:2,shirt:0,bot:0,pc:0,shoe:0},{hs:1,hat:6,gl:0,face:0,pat:1,pack:4,body:1,skin:5,hc:5,eye:4,shirt:1,bot:1,pc:2,shoe:6},{hs:2,hat:7,gl:0,face:0,pat:0,pack:2,body:1,skin:1,hc:2,eye:2,shirt:7,bot:1,pc:5,shoe:3},{hs:3,hat:8,gl:0,face:2,pat:0,pack:0,body:0,skin:2,hc:4,eye:0,shirt:6,bot:0,pc:3,shoe:1}];
          const c=document.createElement('canvas');c.width=4*16*8;c.height=cfgs.length*23*8;c.style.cssText='position:absolute;left:0;top:0;z-index:99;width:'+(c.width/2.625)+'px';
          const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#6fbf5a';g.fillRect(0,0,c.width,c.height);
          cfgs.forEach((cf,r)=>{[[0,0],[3,2],[1,1],[2,3]].forEach((dp,i)=>g.drawImage(__game.playerFrame(dp[0],dp[1],false,r%2==1,cf),i*128,r*184,128,184))});document.body.appendChild(c)}""")
        await pg.screenshot(path="v35_sheet.png", clip={"x":0,"y":0,"width":196,"height":561})
        print("errors", errs); await b.close()
asyncio.run(main())
