import asyncio, json
from playwright.async_api import async_playwright
# v0.13: Deep Cave, Bram and the rope ladder, lake fishing, controller nav, front and back views, building draw order, text size, full screen, frame timing
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1000)
        # old save still loads, nothing from v0.13 is unlocked
        print("old save:", await ev("[Object.keys(__game.S.found).length,!!__game.S.vil.bram,__game.ITEMS.length,__game.SETS.length]"))
        assert await ev("Object.keys(__game.S.found).length")==15 and not await ev("!!__game.S.vil.bram")
        # reachability of everything placed in the Deep Cave and around the shaft
        r=await ev("""(()=>{const G=__game,D=G.deep(),W=G.MW,dr=G.reachFrom(D.DEEP_IN.x,D.DEEP_IN.y),cr=G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y),adj=(m,x,y)=>[[1,0],[-1,0],[0,1],[0,-1]].some(d=>m[(y+d[1])*W+x+d[0]]);
          const deep=G.ITEMS.filter(i=>i.deep),bad=deep.filter(i=>!dr[i.y*W+i.x]||G.regAt(i.x,i.y)!==G.REG.deep).map(i=>i.id);
          let shore=0;for(let y=62;y<100;y++)for(let x=84;x<120;x++){const k=y*W+x;if(dr[k]&&[[1,0],[-1,0],[0,1],[0,-1]].some(d=>G.ground[k+d[1]*W+d[0]]===4))shore++}
          return {deepItems:deep.length,unreachable:bad,pit:adj(cr,D.PIT.x,D.PIT.y),bram:adj(cr,D.BRAM.x,D.BRAM.y),pitOut:!!cr[D.PIT_OUT.y*W+D.PIT_OUT.x],ladder:adj(dr,D.DLAD.x,D.DLAD.y),landing:!!dr[D.DEEP_IN.y*W+D.DEEP_IN.x],shoreTiles:shore,lakeFish:G.ITEMS.filter(i=>i.fish==='deep').length}})()""")
        print("deep:", json.dumps(r))
        assert r["deepItems"]==10 and not r["unreachable"] and r["pit"] and r["bram"] and r["pitOut"] and r["ladder"] and r["landing"] and r["shoreTiles"]>10 and r["lakeFish"]==4
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        # Bram asks, the shaft is closed, then three crystals open it
        await ev("__game.S.lantern=true;const D=__game.deep();__game.hop(D.PIT_OUT.x,D.PIT_OUT.y,3)"); await pg.wait_for_timeout(200)
        await ev("__game.talk(__game.VIL.find(v=>v.id==='bram'))"); a1=await ev("dtext.textContent"); await ev("hush()")
        await ev("const D=__game.deep();__game.S.x=D.PIT_OUT.x*16+8;__game.S.y=D.PIT_OUT.y*16+10"); await pg.keyboard.press("e"); await pg.wait_for_timeout(200); a2=await ev("dtext.textContent"); await ev("hush()")
        print("bram ask:", a1[:60], "| shaft:", a2); assert "three different Cave Crystals" in a1 and "rope ladder" in a2 and await ev("__game.region().name")=="The Cave"
        await ev("['quartz','ruby','sapphire'].forEach(i=>__game.S.found[i]=1);__game.talk(__game.VIL.find(v=>v.id==='bram'))"); a3=await ev("dtext.textContent"); await ev("hush()")
        print("bram gives:", a3[:50], await ev("__game.S.vil.bram")); assert await ev("__game.S.vil.bram")==1
        await ev("const D=__game.deep();__game.S.x=D.PIT_OUT.x*16+8;__game.S.y=D.PIT_OUT.y*16+10"); await pg.keyboard.press("e"); await pg.wait_for_timeout(400)
        print("down the shaft:", await ev("__game.region().name")); assert await ev("__game.region().name")=="Deep Cave"
        assert await ev("__game.caveRg(__game.region())")
        c0=await ev("__game.S.clock"); await pg.wait_for_timeout(600); print("clock paused underground:", c0==await ev("__game.S.clock"))
        await pg.screenshot(path="t21_deep.png")
        # lake fishing gives Lake Fish only
        spot=await ev("(()=>{const G=__game,dr=G.reachFrom(G.deep().DEEP_IN.x,G.deep().DEEP_IN.y);for(let y=64;y<98;y++)for(let x=86;x<118;x++){const k=y*G.MW+x;if(dr[k]&&G.ground[k+1]===4&&G.ground[k+2]===4)return [x,y]}return null})()")
        await ev(f"__game.S.rod=true;__game.hop({spot[0]},{spot[1]},3);__game.S.dir=3"); zone=await ev("(__game.waterAhead()||{}).zone"); print("water zone:", zone); assert zone=="deep"
        got=set()
        for i in range(14):
            await pg.keyboard.press("e"); await pg.wait_for_timeout(60); await ev("__game.F.t=0"); await pg.wait_for_timeout(120); await pg.keyboard.press("e"); await pg.wait_for_timeout(80); await ev("hush()")
        got=await ev("__game.ITEMS.filter(i=>i.fish==='deep'&&__game.S.found[i.id]).map(i=>i.id)"); other=await ev("__game.ITEMS.filter(i=>i.fish&&i.fish!=='deep'&&__game.S.found[i.id]).length")
        print("lake catches:", got, "other fish:", other); assert len(got)>=2 and other==0
        # dig and pick up in the mine
        await ev("__game.S.shovel=true;__game.S.net=true;__game.ITEMS.filter(i=>i.deep).forEach(i=>{__game.hop(i.x,i.y+1,1);__game.S.y-=4;const n=__game.nearest();if(n&&n.it===i)action();else __game.collect(i)});hush()"); await pg.wait_for_timeout(300)
        print("deep sets done:", await ev("[__game.ITEMS.filter(i=>i.set==='deepglow'&&__game.S.found[i.id]).length,__game.ITEMS.filter(i=>i.set==='mine'&&__game.S.found[i.id]).length]"))
        assert await ev("__game.ITEMS.filter(i=>i.deep&&!__game.S.found[i.id]).length")==0
        await pg.wait_for_timeout(1500); await ev("hush()")
        await ev("openPanel('journal');for(let i=0;i<6;i++)jflip(1)"); await pg.wait_for_timeout(350); jt=await ev("[...document.querySelectorAll('#jsets h2')].map(h=>h.textContent).join(' ; ')"); print("journal:", jt); assert "The Deep Cave" in jt and "Old Mine (complete)" in jt; await ev("closeAll()")
        await ev("openPanel('map')"); await pg.wait_for_timeout(300); print("map:", await ev("mtitle.textContent")); assert await ev("mtitle.textContent")=="Map: Deep Cave"; await pg.screenshot(path="t21_map.png"); await ev("closeAll()")
        print("miner's lantern unlocked:", await ev("__game.FURN.find(f=>f.id==='f_minelamp').c()"))
        # climb back up
        await ev("const D=__game.deep();__game.hop(D.DEEP_IN.x,D.DEEP_IN.y,1);__game.S.y-=2"); await pg.keyboard.press("e"); await pg.wait_for_timeout(400); print("ladder up:", await ev("__game.region().name")); assert await ev("__game.region().name")=="The Cave"
        await ev("save()"); await pg.reload(); await pg.wait_for_timeout(900); print("reload keeps ladder:", await ev("__game.S.vil.bram")); assert await ev("__game.S.vil.bram")==1
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        # walking views: down shows the front, up the back, left and right the side
        views={}
        for k in ["ArrowDown","ArrowUp","ArrowLeft","ArrowRight"]:
            await ev("__game.hop(30,30,0);__game.S.bridge=true"); await pg.keyboard.down(k); await pg.wait_for_timeout(500); views[k]=await ev("WK.view"); await pg.keyboard.up(k); await pg.wait_for_timeout(200)
        sp=await ev("""(()=>{const G=__game,S=G.S,ob=blocked;window.blocked=()=>false;const o={};
          for(const k of ["arrowright","arrowdown","arrowleft","arrowup"]){G.hop(30,30,0);S.boots=false;S.vx=S.vy=0;closeAll();hush();const a=[(S.x-S.y)*38/16,(S.x+S.y)*19/16];keys[k]=1;for(let i=0;i<42;i++)update(1/60);keys[k]=0;const b=[(S.x-S.y)*38/16,(S.x+S.y)*19/16];o[k]=Math.round(Math.hypot(b[0]-a[0],b[1]-a[1]))}
          window.blocked=ob;fadeT=0;return o})()""")
        print("screen distance in 0.7 s:", sp); assert max(sp.values())<min(sp.values())*1.25
        print("views:", views); assert views=={"ArrowDown":"front","ArrowUp":"back","ArrowLeft":"side","ArrowRight":"side"}
        # standing in front of the museum walls keeps the player visible
        vis=await ev("""(()=>{const G=__game,S=G.S,oi=iperson;let hide=false;window.iperson=function(ch){if(hide&&ch===S.ch)return;return oi.apply(this,arguments)};const out=[];
          for(const t of [[44,43],[47,40],[20,30]]){S.x=t[0]*16+8;S.y=t[1]*16+10;S.vx=S.vy=0;const w=cv.width,h=cv.height,x0=Math.round(w/2-40*IK),y0=Math.round(h*0.56-70*IK),cw=Math.round(80*IK),ch=Math.round(80*IK);
            hide=false;renderIso();const A=cx.getImageData(x0,y0,cw,ch).data;hide=true;renderIso();const B=cx.getImageData(x0,y0,cw,ch).data;hide=false;let d=0;for(let i=0;i<A.length;i+=4)if(Math.abs(A[i]-B[i])+Math.abs(A[i+1]-B[i+1])+Math.abs(A[i+2]-B[i+2])>60)d++;out.push(d)}
          window.iperson=oi;return out})()""")
        print("player pixels at museum front, museum side, open meadow:", vis); assert vis[0]>vis[2]*0.6 and vis[1]>vis[2]*0.6
        # controller: the D-pad reaches every row and button of the character screen
        await ev("keyMode(true);openPanel('builder')"); seen=set(); 
        for i in range(40):
            seen.add(await ev("foc&&(foc.id||foc.textContent.slice(0,14))")); await ev("nav('down')")
        for i in range(40):
            seen.add(await ev("foc&&(foc.id||foc.textContent.slice(0,14))")); await ev("nav('up')")
        print("builder reached:", sorted(x for x in seen if x)); assert "ball" in seen and "bundo" in seen and "bdone" in seen
        await ev("setFoc($('ball'));nav('right')"); print("right of Random everything:", await ev("foc.id")); assert await ev("foc.id")=="brand"
        await ev("closeAll()")
        for pnl,want in [("pause",["presume","pjournal","pmap","pvil","pchar","pset","pfull","ptitle"]),("settings",["sback"])]:
            await ev(f"openPanel('{pnl}')"); got=set()
            for i in range(60): got.add(await ev("foc&&foc.id")); await ev("nav('down')")
            miss=[w for w in want if w not in got]; print(pnl,"missing:",miss); assert not miss; await ev("closeAll()")
        # text size and full screen
        print("text scale:", await ev("getComputedStyle(document.documentElement).getPropertyValue('--ts')"), "full screen button:", await ev("[$('tfull').style.display,$('pfull').style.display,$('tquit').style.display]"))
        assert (await ev("getComputedStyle(document.documentElement).getPropertyValue('--ts')")).strip()=="1.15" and await ev("$('pfull').style.display")=="" and await ev("$('tquit').style.display")=="none"
        for pnl in ["settings","journal","builder"]:
            await ev(f"openPanel('{pnl}')"); await pg.wait_for_timeout(250); r=await ev(f"(()=>{{const c=$('{pnl}').querySelector('.card').getBoundingClientRect();return [Math.round(c.left),Math.round(c.right),innerWidth]}})()"); print(pnl,"card",r); assert r[0]>=0 and r[1]<=r[2]; await ev("closeAll()")
        # frame timing: an early animation timestamp must not break the loop
        await ev("const t0=__game.S.t;frame(last-800);window.__t0=t0"); print("negative frame ok:", await ev("__game.S.t>=window.__t0"))
        ctx2 = await b.new_context(viewport={"width":640,"height":360}, device_scale_factor=3, has_touch=True); await ctx2.add_init_script("window.Android={quit(){},vibrate(){},copy(){},paste(){return ''},share(){}};"+SEED)
        pg2 = await ctx2.new_page(); pg2.on("pageerror", lambda e: errs.append(str(e)))
        await pg2.goto("file:///home/claude/game/index.html"); await pg2.wait_for_timeout(900)
        print("app build buttons:", await pg2.evaluate("[$('tfull').style.display,$('tquit').style.display]")); assert await pg2.evaluate("$('tfull').style.display")=="none" and await pg2.evaluate("$('tquit').style.display")==""
        await pg2.tap("#tcont"); await pg2.wait_for_timeout(200); await pg2.evaluate("__game.S.vil.bram=1;const D=__game.deep();__game.hop(D.DEEP_IN.x,D.DEEP_IN.y+2,0)"); await pg2.wait_for_timeout(400); await pg2.screenshot(path="t21_land_deep.png")
        await pg2.evaluate("const D=__game.deep();__game.hop(D.PIT_OUT.x,D.PIT_OUT.y,3)"); await pg2.wait_for_timeout(400); await pg2.screenshot(path="t21_land_pit.png")
        print("errors", errs); await b.close()
asyncio.run(main())
