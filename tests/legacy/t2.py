import asyncio, json
from playwright.async_api import async_playwright
SAMPLE="""()=>new Promise(r=>{const a=[];let n=0;function f(){a.push([__last.sx,__last.sy,__last.cam]);if(++n<70)requestAnimationFrame(f);else r(a)}requestAnimationFrame(f)})"""
async def run(file,label):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/"+file); await pg.wait_for_timeout(600)
        if label=="new":
            r = await pg.evaluate("""()=>{const seen=__reach();return __game.ITEMS.every(i=>seen[i.y*60+i.x])}"""); print("all reachable",r)
            await pg.evaluate("__game.S.x=30*16+8;__game.S.y=40*16")
            await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(300)
            a = await pg.evaluate(SAMPLE); await pg.keyboard.up("ArrowUp")
            sx=set(round(v[0],3) for v in a); sy=set(round(v[1],3) for v in a); cams=[v[2] for v in a]
            print("player screen x values",sx,"y values",sy)
            await pg.evaluate("__game.S.x=20*16+8;__game.S.y=28*16+10")
            await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(300)
            a = await pg.evaluate(SAMPLE); await pg.keyboard.up("ArrowRight")
            st=[round(a[i+1][2]-a[i][2],2) for i in range(len(a)-1)]
            print("screen x values",set(round(v[0],3) for v in a),"camera steps px/frame min,max",min(st),max(st),"integer cam",all(abs(v[2]-round(v[2]))<1e-6 for v in a))
            await pg.screenshot(path="n1_walk.png")
            # sprite sheet
            await pg.evaluate("""()=>{const c=document.createElement('canvas');c.width=16*5*8+40;c.height=23*4*8+40;c.style.cssText='position:absolute;left:0;top:0;z-index:99;background:#6fbf5a;width:'+c.width/2.625+'px';
              const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#6fbf5a';g.fillRect(0,0,c.width,c.height);
              __game.pspr[0].forEach((d,r)=>{[...d.f,d.blink].forEach((im,i)=>g.drawImage(im,10+i*16*8,10+r*23*8,16*8,23*8))});document.body.appendChild(c)}""")
            await pg.screenshot(path="n2_sheet.png", clip={"x":0,"y":0,"width":260,"height":296})
            # touch joystick drag moves player
            await pg.evaluate("document.querySelector('canvas[style*=\"z-index:99\"],canvas[style*=\"z-index: 99\"]').remove()")
            x0=await pg.evaluate("__game.S.x")
            cdp=await ctx.new_cdp_session(pg)
            await cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":120,"y":600}]})
            await cdp.send("Input.dispatchTouchEvent",{"type":"touchMove","touchPoints":[{"x":170,"y":600}]})
            await pg.wait_for_timeout(500)
            await cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
            print("touch moved", x0, await pg.evaluate("__game.S.x"))
            await pg.evaluate("__game.ITEMS.slice(0,5).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(900)
            await pg.reload(); await pg.wait_for_timeout(400)
            print("save ok", await pg.evaluate("[Object.keys(__game.S.found).length,__game.S.boots]"))
        print(label,"errors",errs); await b.close()
asyncio.run(run("index.html","new"))
