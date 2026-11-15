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
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1000)
        await pg.tap("#tnew"); await pg.wait_for_timeout(400); await pg.tap("#ball"); await pg.wait_for_timeout(200); await pg.tap("#bdone"); await pg.wait_for_timeout(900)
        print("after start: stack",await ev("[...__game.stack]"),"dlg",await ev("document.getElementById('dialog').offsetParent?document.getElementById('dialog').textContent:''"))
        await pg.screenshot(path="bot_first.png")
        for i in range(6):
            await pg.keyboard.press("e"); await pg.wait_for_timeout(250)
        await ev("CFG.stick=2;Object.assign(__game.S,{shovel:true,rod:true,net:true,boots:true,lantern:true})")
        ok=[];bad=[];skip=[]
        items=await ev("__game.ITEMS.map(i=>({id:i.id,x:i.x,y:i.y,off:!!i.off,rock:!!i.rock,dig:!!i.dig,hid:!!i.hid,photo:!!i.photo,bug:!!i.bug,when:i.when||''}))")
        for it in items:
            if it["off"]: skip.append(it["id"]); continue
            clock=450 if it["when"]=="night" else 460 if it["when"]=="rain" else 100
            cx=cy=0
            for attempt in range(2):
                spot=await ev(f"""(()=>{{const g=__game,x={it['x']},y={it['y']};let best=null;for(let r=2;r<=4;r++)for(let dx=-r;dx<=r;dx++)for(let dy=-r;dy<=r;dy++){{if(Math.max(Math.abs(dx),Math.abs(dy))!==r)continue;const X=x+dx,Y=y+dy;if(g.regAt(X,Y)!==g.regAt(x,y)||g.solidTile(X,Y))continue;g.S.x=X*16+8;g.S.y=Y*16+10;const p=g.findPath(x*16+8,y*16+8);if(p&&p.length){{const e=p[p.length-1];if(Math.abs((e[0]/16|0)-x)+Math.abs((e[1]/16|0)-y)<=(g.solidTile(x,y)?1:0)){{if(!best||p.length<best[2])best=[X,Y,p.length]}}}}}}if(best){{g.S.x=best[0]*16+8;g.S.y=best[1]*16+10}}g.S.clock={clock};return best}})()""")
                if not spot: got=False; continue
                await pg.wait_for_timeout(120)
                st=await ev("__game.isoState()"); pt=await ev(f"__game.ip({it['x']}+0.5,{it['y']}+0.5)")
                cx=pt[0]*st["IK"]/2.625; cy=pt[1]*st["IK"]/2.625
                await pg.touchscreen.tap(cx,cy); 
                for k in range(80):
                    await pg.wait_for_timeout(150)
                    if not await ev("!!(__game.getPath()&&__game.getPath().length)"): break
                got=await ev(f"!!__game.S.found['{it['id']}']")
                if not got:
                    await pg.keyboard.press("e"); await pg.wait_for_timeout(250)
                    for k in range(8):
                        got=await ev(f"!!__game.S.found['{it['id']}']")
                        if got or it["id"] in ok: break
                        await pg.keyboard.press("e"); await pg.wait_for_timeout(250)
                # clear any dialog or panel
                for k in range(4):
                    if await ev("!!document.getElementById('dialog').offsetParent"): await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
                    elif await ev("__game.stack.length>0"): await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
                if not got:
                    await pg.wait_for_timeout(400); got=await ev(f"!!__game.S.found['{it['id']}']")
                if got: break
            if got: ok.append(it["id"])
            else:
                d=await ev(f"Math.hypot(__game.S.x-({it['x']}*16+8),__game.S.y-({it['y']}*16+8))"); bad.append((it["id"],{k:v for k,v in it.items() if v and k not in('id','x','y')},round(d),[round(cx),round(cy)],await ev("[...__game.stack].join()+'|'+(document.getElementById('dialog').offsetParent?document.getElementById('dialog').textContent.slice(0,60):'')+'|'+(document.getElementById('toast').textContent||'').slice(0,60)"))); await pg.screenshot(path=f"bot_bad_{it['id']}.png")
        print("picked",len(ok),"skipped offworld",len(skip),"failed",len(bad)); print(bad)
        print("errors", errs); await b.close()
asyncio.run(main())
