import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True)
        pg = await ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        # old v0.2 style save without character must still load
        await pg.goto("file:///home/claude/game/index.html")
        await ev("localStorage.setItem('wandervalley_save_v1',JSON.stringify({v:1,x:232,y:442,boots:true,started:true,found:['daisy','poppy']}))")
        await pg.reload(); await pg.wait_for_timeout(400)
        print("old save:", await ev("[Object.keys(__game.S.found).length,__game.S.boots,__game.S.ch.name,getComputedStyle(tcont).display]"))
        await ev("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(400)
        await pg.tap("#tnew"); await pg.wait_for_timeout(300)
        print("new game ->", await ev("[...__game.stack]"))
        await pg.screenshot(path="v25_builder.png")
        await pg.fill("#bname","Brian"); 
        rows = await pg.query_selector_all("#brows .srow")
        async def plus(i,n=1):
            for _ in range(n): await (await rows[i].query_selector_all(".pm"))[1].tap()
        await plus(1,2); await plus(2,1); await plus(4,1); await plus(8,2)
        await pg.wait_for_timeout(200); await pg.screenshot(path="v25_builder2.png")
        await pg.tap("#bdone"); await pg.wait_for_timeout(300)
        print("after done:", await ev("[...__game.stack]"), await ev("JSON.stringify(__game.S.ch)"))
        await ev("__game.S.x=14*16+8;__game.S.y=26*16+2"); await pg.wait_for_timeout(100); await pg.tap("#abtn"); await pg.wait_for_timeout(100)
        print("cabin:", await ev("dtext.textContent"))
        await ev("__game.S.x=16*16+8;__game.S.y=27*16+8"); await pg.wait_for_timeout(100); await pg.tap("#dialog"); await pg.tap("#abtn")
        print("sign:", await ev("dtext.textContent")); await pg.tap("#dialog")
        await ev("__game.ITEMS.slice(0,5).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(900); await pg.tap("#dialog")
        await pg.tap("#jbtn"); print("journal:", await ev("jtitle.textContent+' | '+jup.textContent")); await pg.tap("#jclose")
        await pg.tap("#mbtn"); print("pause:", await ev("pwho.textContent")); await pg.tap("#presume")
        await pg.wait_for_timeout(200); await pg.screenshot(path="v25_play.png")
        await pg.reload(); await pg.wait_for_timeout(400)
        print("reload keeps:", await ev("JSON.stringify(__game.S.ch)"))
        # controller in builder
        await pg.tap("#tcont"); await ev("__padKey(9,1)"); await pg.wait_for_timeout(80); await ev("__padKey(9,0)"); await pg.wait_for_timeout(80)
        async def press(i):
            await ev(f"__padKey({i},1)"); await pg.wait_for_timeout(60); await ev(f"__padKey({i},0)"); await pg.wait_for_timeout(60)
        await press(13); await press(13); await press(0); print("pad opens:", await ev("[...__game.stack]"))
        await press(13); await press(15); print("pad pronoun ->", await ev("__game.S.ch.pro"))
        await press(1); await press(1); print("B closes:", await ev("[...__game.stack]"))
        # variety sheet
        await ev("""()=>{const cfgs=[{body:0,skin:1,hs:0,hc:0,hat:0,shirt:0,bot:0,pc:0},{body:1,skin:0,hs:1,hc:2,hat:3,shirt:7,bot:2,pc:5},{body:1,skin:4,hs:3,hc:1,hat:4,shirt:4,bot:1,pc:1},{body:0,skin:5,hs:0,hc:1,hat:1,shirt:2,bot:1,pc:3},{body:1,skin:2,hs:2,hc:3,hat:2,shirt:5,bot:0,pc:4},{body:0,skin:3,hs:1,hc:4,hat:4,shirt:8,bot:0,pc:2}];
          const c=document.createElement('canvas');c.id='sheet';c.width=4*16*10;c.height=cfgs.length*23*10;c.style.cssText='position:absolute;left:0;top:0;z-index:99;width:'+(c.width/2.625)+'px';
          const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#6fbf5a';g.fillRect(0,0,c.width,c.height);
          cfgs.forEach((cf,r)=>{[[0,0],[3,2],[1,1],[2,3]].forEach((dp,i)=>g.drawImage(__game.playerFrame(dp[0],dp[1],false,false,cf),i*160,r*230,160,230))});document.body.appendChild(c)}""")
        await pg.screenshot(path="v25_sheet.png", clip={"x":0,"y":0,"width":244,"height":526})
        print("errors", errs); await b.close()
asyncio.run(main())
