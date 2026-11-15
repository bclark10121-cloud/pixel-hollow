import asyncio, json
from playwright.async_api import async_playwright
# v0.14.2 quick wins: requests page, villager markers, door fast travel, companion name and reactions, safe area
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
CHECK=open('t22_fit.py').read().split('CHECK=r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900); await pg.tap("#tcont"); await pg.wait_for_timeout(250)
        print("old save: pn", repr(await ev("__game.S.pn")), "| label", await ev("document.querySelector('#title .ver').textContent"))
        assert await ev("(__game.S.pn||'')===''")
        # ---- requests page ----
        await ev("openPanel('journal');jflip(-1)"); await pg.wait_for_timeout(350)
        rows=await ev("[...document.querySelectorAll('#jsets .req')].map(d=>d.dataset.req+':'+d.className.split(' ').pop()+':'+d.textContent)")
        print("requests page:", await ev("jpn.textContent+' | '+document.querySelector('#jsets h2').textContent")); [print("  ",r[:110]) for r in rows]
        assert len(rows)==13, len(rows)
        await (await pg.query_selector_all("#jsets .req"))[0].tap(); await pg.wait_for_timeout(100); print("detail:", (await ev("jinfo.textContent"))[:200])
        await pg.screenshot(path="qw_requests.png")
        # states move as you play: meet Mira, then find a Sunflower
        await ev("(()=>{const G=__game,L=G.vl();delete G.S.vil.mira;delete G.S.found.sunflower;delete L.fd.mira})()")
        st=lambda: ev("__game.reqList().find(r=>r.id==='mira').st")
        s1=await st(); await ev("__game.vl().fd.mira=1"); s2=await st(); await ev("__game.S.found.sunflower=1"); s3=await st(); await ev("__game.S.vil.mira=1"); s4=await st()
        print("Mira:", s1, "->", s2, "->", s3, "->", s4); assert [s1,s2,s3,s4]==["new","open","ready","done"]
        print("Mira done detail:", (await ev("(()=>{const r=__game.reqList().find(r=>r.id==='mira');buildJournal();return document.querySelector('#jsets [data-req=mira]').textContent})()")))
        # controller: D-pad moves through the rows
        await ev("keyMode(true);setFoc(navEls()[0])")
        f0=await ev("foc.textContent"); await ev("nav('down')"); await ev("nav('down')"); f1=await ev("foc.textContent+' || '+jinfo.textContent.slice(0,60)")
        print("pad focus:", f0[:30], "=>", f1[:110]); await ev("keyMode(false);closeAll()")
        # ---- map markers ----
        await ev("__game.seen.fill(1);openPanel('map')"); await pg.wait_for_timeout(350)
        mi=await ev("mapinfo.textContent"); print("map info end:", mi[-120:]); assert "Blue crosses are neighbors" in mi
        go=await ev("[...document.querySelectorAll('#mapgo .btn')].map(b=>b.textContent)"); print("fast travel:", go); assert go[0]=="Cabin door" and go[1]=="Museum door"
        await pg.screenshot(path="qw_map.png")
        await (await pg.query_selector_all("#mapgo .btn"))[1].tap(); await pg.wait_for_timeout(250)
        pos=await ev("(()=>{const G=__game,x=G.S.x/16|0,y=(G.S.y-2)/16|0;return [x,y,G.MUS.x+2,G.MUS.y+G.MUS.h,G.solidTile(x,y),G.region().name,G.stack.length]})()"); print("museum door:", pos)
        assert pos[0]==pos[2] and pos[1]==pos[3] and not pos[4] and pos[6]==0
        await ev("openPanel('map')"); await pg.wait_for_timeout(200); await (await pg.query_selector_all("#mapgo .btn"))[0].tap(); await pg.wait_for_timeout(250)
        pos=await ev("(()=>{const G=__game,x=G.S.x/16|0,y=(G.S.y-2)/16|0;return [x,y,G.solidTile(x,y),G.region().name]})()"); print("cabin door:", pos); assert not pos[2]
        # from inside the cabin, the doors still work
        await ev("__game.enterHome();openPanel('map')"); await pg.wait_for_timeout(200); await (await pg.query_selector_all("#mapgo .btn"))[1].tap(); await pg.wait_for_timeout(200)
        print("from cabin to museum door:", await ev("__game.region().name")); assert await ev("__game.region().name")=="Home Meadows"
        # ---- companion name ----
        await ev("__game.S.pet=false;openPanel('builder')"); await pg.wait_for_timeout(200); hid=await ev("getComputedStyle($('bpetrow')).display"); await ev("closeAll()")
        await ev("__game.S.pet=true;__game.CFG.pet=1;openPanel('builder')"); await pg.wait_for_timeout(200); shown=await ev("getComputedStyle($('bpetrow')).display")
        print("pet row hidden before companion:", hid, "| shown after:", shown); assert hid=="none" and shown!="none"
        await pg.screenshot(path="qw_builder.png")
        await pg.fill("#bpet","Biscuit<"); await ev("closeAll()"); print("named:", await ev("__game.S.pn")); assert await ev("__game.S.pn")=="Biscuit"
        await ev("openPanel('builder');$('bpetrow').querySelector('.rnd').click()"); rn=await ev("__game.S.pn"); print("random name:", rn); assert await ev(f"__game.PETN.includes({json.dumps(rn)})")
        await ev("$('bpet').value='Biscuit';$('bpet').dispatchEvent(new Event('input'));closeAll();save()")
        await pg.reload(); await pg.wait_for_timeout(900); await pg.tap("#tcont"); await pg.wait_for_timeout(250)
        print("after reload:", await ev("[__game.S.pn,__game.S.pet]")); assert await ev("__game.S.pn")=="Biscuit"
        await ev("openPanel('journal')"); up=await ev("jup.textContent"); print("journal:", up[:120]); assert "Biscuit the dog (plays fetch)" in up; await ev("closeAll()")
        # fetch reactions: force a miss and check the toast and the happy hop
        await ev("(()=>{const G=__game;G.FB.miss=0;const r=Math.random;Math.random=()=>0.9;try{for(let i=0;i<3;i++){G.FB.miss=0;G.FB.on=true;fetchDone()}}finally{Math.random=r}})()")
        t=await ev("$('toast').textContent"); j=await ev("__game.PET.joy"); print("reaction:", t, "| joy", j); assert "Biscuit" in t and j>0
        for k in range(40):
            await pg.wait_for_timeout(250)
            if await ev("__game.PET.joy")==0: break
        print("joy fades:", await ev("__game.PET.joy")); assert await ev("__game.PET.joy")==0
        # ---- safe area ----
        before=await ev("[$('count').getBoundingClientRect().top,$('hudr').getBoundingClientRect().right,STK.cx]")
        await ev("__safe(40,30,20,10)"); await pg.wait_for_timeout(100)
        after=await ev("[$('count').getBoundingClientRect().top,$('hudr').getBoundingClientRect().right,STK.cx,__game.SA.t]")
        print("safe area top/right/stick:", before, "->", after); assert round(after[0]-before[0])==40 and round(before[1]-after[1])==30 and round(after[2]-before[2])==10
        await ev("openPanel('pause')"); pad=await ev("getComputedStyle($('pause')).paddingTop"); print("menu padding top:", pad); await pg.screenshot(path="qw_safe.png"); await ev("closeAll()")
        await ev("__safe(0,0,0,0)"); print("reset:", await ev("[$('count').getBoundingClientRect().top,__game.SA.t]"))
        await ctx.close()
        # ---- the requests page fits every screen shape ----
        for name,w,h,dpr in [("phone-xs",320,568,2),("phone-l",412,915,2.625),("phone-side",640,360,3),("retroid",732,412,2.625),("tablet",768,1024,2),("desktop",1920,1080,1)]:
            c2 = await b.new_context(viewport={"width":w,"height":h}, device_scale_factor=dpr, has_touch=dpr>1, is_mobile=dpr>1); await c2.add_init_script(SEED)
            p2 = await c2.new_page(); p2.on("pageerror", lambda e: errs.append(str(e)))
            await p2.goto("file:///home/claude/game/index.html"); await p2.wait_for_timeout(700); await p2.evaluate("closeAll();openPanel('journal');jflip(-1)"); await p2.wait_for_timeout(300)
            r=await p2.evaluate(CHECK+"('journal')"); print("fit", name, "ok" if not r else r)
            if r: errs.append("requests page fit "+name+": "+json.dumps(r)[:200])
            if name in ("retroid","phone-xs"): await p2.screenshot(path=f"qw_requests_{name}.png")
            await c2.close()
        print("errors", errs); await b.close()
asyncio.run(main())
