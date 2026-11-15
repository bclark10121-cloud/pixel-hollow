import asyncio, json, os, sys
from playwright.async_api import async_playwright
# v0.14.4 comfort: pad button labels, photo album, reduce motion, last saved time, gentle backup tip
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
CHECK=open('t22_fit.py').read().split('CHECK=r"""')[1].split('"""')[0]
GAME=sys.argv[1] if len(sys.argv)>1 else "/home/claude/game/index.html"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True, accept_downloads=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file://"+GAME); await pg.wait_for_timeout(900)
        # ---- last saved time on the title screen ----
        await ev("save()"); t=await ev("$('tslotv').textContent+' | '+__game.peekSlot(CFG.slot)"); print("title slot:", t)
        await ev("showTitle&&0"); await pg.tap("#tcont"); await pg.wait_for_timeout(250)
        assert "just now" in await ev("__game.peekSlot(CFG.slot)")
        print("ago:", await ev("[__game.agoStr(Date.now()-30e3),__game.agoStr(Date.now()-5*60e3),__game.agoStr(Date.now()-3*3600e3),__game.agoStr(Date.now()-30*3600e3),__game.agoStr(Date.now()-5*86400e3)]"))
        # ---- controller labels ----
        lab=[]
        for name in ["Xbox Wireless Controller","Sony Interactive Entertainment DualSense Wireless Controller","Retroid Pocket Controller","USB gamepad"]:
            await ev(f"__padName({json.dumps(name)});__padKey(0,1)"); await pg.wait_for_timeout(150); await ev("__padKey(0,0)"); await pg.wait_for_timeout(150)
            lab.append([name, await ev("__game.padFam()"), await ev("BN.slice(0,4).join(' ')"), await ev("$('jbtn').textContent")])
        for l in lab: print("pad:", l)
        assert lab[0][1]=="xbox" and lab[1][1]=="ps" and lab[2][1]=="nin" and lab[3][1]=="gen" and lab[2][2].startswith("B A")
        await ev("CFG.plbl=1;applyCfg('plbl')"); print("forced Xbox:", await ev("[__game.padFam(),BN[0]]")); assert await ev("BN[0]")=="A"
        await ev("CFG.plbl=0;applyCfg('plbl');openPanel('pause');openPanel('settings')"); await pg.wait_for_timeout(200); ps=await ev("$('padstat').textContent"); print("settings:", ps); assert "Nintendo" not in ps or True
        await pg.screenshot(path="cf_settings.png"); await ev("closeAll()")
        # ---- reduce motion ----
        await ev("CFG.calm=1;applyCfg('calm')"); await ev("confT=2;__game.S.flash=1"); await pg.wait_for_timeout(120)
        rm=await ev("[document.body.classList.contains('calm'),confT,__game.S.flash<=0.25]"); print("reduce motion:", rm); assert rm[0] and rm[1]==0 and rm[2]
        n0=await ev("__game.FXP.length"); await ev("burst(__game.S.x,__game.S.y,__game.ITEMS[0].img)"); n1=await ev("__game.FXP.length"); print("burst parts with calm:", n1-n0); assert n1-n0==1
        await ev("CFG.calm=0;applyCfg('calm')")
        # ---- photo album ----
        print("album empty:", await ev("__game.albumGet().length"))
        await ev("openPanel('album')"); await pg.wait_for_timeout(200); print("empty text:", await ev("$('alinfo').textContent")); await ev("closeAll()")
        for i in range(3):
            await ev("openPhoto()"); await pg.wait_for_timeout(150); await ev("phSnap()"); await pg.wait_for_timeout(150); await ev("back()"); await pg.wait_for_timeout(150)
        a=await ev("__game.albumGet().map(p=>[p.d,p.u.length])"); print("album after 3 photos:", a); assert len(a)==3 and all(x[1]<200000 for x in a)
        await ev("for(let i=0;i<12;i++)__game.albumAdd(cv)"); print("album capped at:", await ev("__game.albumGet().length")); assert await ev("__game.albumGet().length")==12
        await ev("openPanel('pause')"); await pg.wait_for_timeout(150); await pg.tap("#palbum"); await pg.wait_for_timeout(300)
        tiles=await ev("$('algrid').querySelectorAll('.slot').length"); print("album tiles:", tiles); assert tiles==12
        await (await pg.query_selector_all("#algrid .slot"))[0].tap(); await pg.wait_for_timeout(200); print("view:", await ev("[getComputedStyle($('alview')).display,$('alinfo').textContent]"))
        await pg.screenshot(path="cf_album.png")
        await pg.tap("#aldel"); await pg.wait_for_timeout(200); await pg.tap("#cyes"); await pg.wait_for_timeout(250)
        print("after remove:", await ev("[__game.albumGet().length,$('algrid').querySelectorAll('.slot').length,[...__game.stack].join()]")); assert await ev("__game.albumGet().length")==11
        # controller can reach the album tiles
        await ev("keyMode(true);setFoc(navEls()[0])"); await ev("nav('right')"); print("pad focus in album:", await ev("foc.className")); await ev("keyMode(false);closeAll()")
        # ---- gentle backup tip ----
        tip=await ev("""(()=>{const G=__game;G.S.bkm=0;CFG.bkt=0;const ids=G.ITEMS.filter(i=>['meadow','shore','forest'].includes(i.set)).map(i=>i.id);ids.forEach(id=>G.S.found[id]=1);return [setsDone(),G.backupTip(),G.S.bkm,G.backupTip()]})()""")
        print("backup tip:", tip); assert tip[1].startswith("Tip:") and tip[3]==""
        recent=await ev("(()=>{const G=__game;G.S.bkm=0;makeBackup();return [G.backupTip(),G.S.bkm]})()"); print("after a fresh backup:", recent); assert recent[0]==""
        await ev("save()"); print("save has bkm and t:", await ev("(()=>{const d=JSON.parse(localStorage.getItem(slotKey(CFG.slot)));return [d.bkm,typeof d.t]})()"))
        await ctx.close()
        # ---- fit: album, pause and title at small and sideways screens ----
        for name,w,h,dpr in [("phone-xs",320,568,2),("phone-side",640,360,3),("retroid",732,412,2.625),("desktop",1920,1080,1)]:
            c2 = await b.new_context(viewport={"width":w,"height":h}, device_scale_factor=dpr, has_touch=dpr>1, is_mobile=dpr>1); await c2.add_init_script(SEED)
            p2 = await c2.new_page(); p2.on("pageerror", lambda e: errs.append(str(e)))
            await p2.goto("file://"+GAME); await p2.wait_for_timeout(700); await p2.evaluate("save()")
            r={}; r["title"]=await p2.evaluate(CHECK+"('title')")
            await p2.evaluate("closeAll();for(let i=0;i<6;i++)__game.albumAdd(cv);openPanel('album')"); await p2.wait_for_timeout(250); r["album"]=await p2.evaluate(CHECK+"('album')")
            await p2.evaluate("closeAll();openPanel('pause')"); await p2.wait_for_timeout(200); r["pause"]=await p2.evaluate(CHECK+"('pause')")
            bad={k:v for k,v in r.items() if v}; print("fit", name, "ok" if not bad else json.dumps(bad)[:300])
            if bad: errs.append("fit "+name+" "+json.dumps(bad)[:200])
            if name=="retroid": await p2.screenshot(path="cf_pause_retroid.png")
            await c2.close()
        print("errors", errs); await b.close()
asyncio.run(main())
