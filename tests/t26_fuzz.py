# v0.14 review: random input fuzz and soak. Keys, taps and teleports for a few minutes.
# Checks: no errors, player never inside a wall, never off the map, panels and HUD stay in sync.
import asyncio, json, random, sys
from playwright.async_api import async_playwright
SECS = int(sys.argv[1]) if len(sys.argv)>1 else 150
KEYS = ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","e","Enter","Escape","j","m","p","q","h","l","z","f","Backspace","Tab"," "]
CHECK = r"""(()=>{const G=__game,S=G.S,T=G.T;const st=[...G.stack];const panel=document.body.classList.contains('panel');
 const tx=S.x/T|0,ty=S.y/T|0;const rg=G.regAt(tx,ty);
 const bad=[];if(!isFinite(S.x)||!isFinite(S.y))bad.push('nan');
 if(tx<0||ty<0||tx>=G.MW||ty>=G.MH)bad.push('offmap');
 if(G.solidTile(tx,ty)&&!G.PH.on)bad.push('inwall '+tx+','+ty);
 if(st.length===0&&panel)bad.push('panel class with empty stack');
 if(st.length>0&&!panel&&!st.includes('title'))bad.push('stack without panel class '+st.join());
 const vis=st.filter(id=>{const e=document.getElementById(id);return e&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden'});
 if(st.length&&vis.length!==1)bad.push('visible panels '+vis.join()+' of '+st.join());
 return {bad,rg:rg&&rg.name,st:st.join(),pos:[tx,ty]}})()"""
async def main():
    random.seed(1404)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]; issues={}
        for (w,h,mob) in [(412,915,True),(640,360,True),(1280,720,False)]:
            ctx = await b.new_context(viewport={"width":w,"height":h}, has_touch=mob, is_mobile=mob)
            pg = await ctx.new_page()
            pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(600)
            await pg.click("#tnew"); await pg.wait_for_timeout(300); await pg.click("#bdone"); await pg.wait_for_timeout(300)
            # unlock everything so the fuzz reaches every region
            await pg.evaluate("""(()=>{const G=__game,S=G.S;Object.assign(S,{shovel:true,rod:true,net:true,boots:true,lantern:true,bridge:true,pet:true});G.openBridge(true);['juniper','wren','bram','mira'].forEach(v=>S.vil[v]=1);G.CFG.pet=1})()""")
            spots = await pg.evaluate("""(()=>{const G=__game,D=G.deep();return [[14,27],[G.CAVE_IN.x,G.CAVE_IN.y],[G.SNOW_IN.x,G.SNOW_IN.y],[G.DES_IN.x,G.DES_IN.y],[D.DEEP_IN.x,D.DEEP_IN.y],[G.MUS_IN.x,G.MUS_IN.y],[G.HOME_IN.x,G.HOME_IN.y],[88,12],[60,20],[100,40]].map(([x,y])=>{for(let r=0;r<8;r++)for(let dx=-r;dx<=r;dx++)for(let dy=-r;dy<=r;dy++)if(!G.solidTile(x+dx,y+dy))return [x+dx,y+dy];return [14,27]})})()""")
            steps = int(SECS*1000/len([1,1,1])/120)
            for i in range(steps):
                r = random.random()
                try:
                    if r<0.55:
                        k=random.choice(KEYS[:4]); await pg.keyboard.down(k); await pg.wait_for_timeout(random.randint(60,500)); await pg.keyboard.up(k)
                    elif r<0.80:
                        k=random.choice(KEYS[4:]); await pg.keyboard.press(k); await pg.wait_for_timeout(80)
                    elif r<0.92:
                        btns = await pg.evaluate("[...document.querySelectorAll('button,.btn,.slot,.pm')].filter(e=>e.offsetParent&&e.getBoundingClientRect().width>0&&!['tquit','pquit','bkrestore','tnew','pnew'].includes(e.id)).map(e=>{const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,e.id||e.className]})")
                        if btns:
                            bx=random.choice(btns)
                            if mob: await pg.touchscreen.tap(bx[0],bx[1])
                            else: await pg.mouse.click(bx[0],bx[1])
                            await pg.wait_for_timeout(80)
                    elif r<0.97:
                        x=random.randint(5,w-5); y=random.randint(5,h-5)
                        if mob: await pg.touchscreen.tap(x,y)
                        else: await pg.mouse.click(x,y)
                        await pg.wait_for_timeout(100)
                    else:
                        sp=random.choice(spots); await pg.evaluate(f"__game.hop({sp[0]},{sp[1]},0)"); await pg.wait_for_timeout(150)
                except Exception as e:
                    issues.setdefault("driver "+str(e)[:60],0); issues["driver "+str(e)[:60]]+=1
                if i%5==0:
                    await pg.wait_for_timeout(30)
                    c = await pg.evaluate(CHECK)
                    for x in c["bad"]:
                        key=f"{w}x{h} {x} [{c['rg']}] st={c['st']}"
                        if key not in issues: print("ISSUE", key, c["pos"])
                        issues[key]=issues.get(key,0)+1
            fps = await pg.evaluate("new Promise(r=>{let n=0;const t0=performance.now();function f(){n++;if(performance.now()-t0<1000)requestAnimationFrame(f);else r(n)}requestAnimationFrame(f)})")
            print(f"{w}x{h} steps {steps} fps {fps} region {await pg.evaluate('__game.region().name')} found {await pg.evaluate('Object.keys(__game.S.found).length')}")
            await ctx.close()
        print("issues", json.dumps(issues, indent=0))
        print("errors", sorted(set(errs))[:20]); await b.close()
asyncio.run(main())
