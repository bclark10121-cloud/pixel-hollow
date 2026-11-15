import asyncio, json
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        clr="while(stack.length)closePanel();hush()"
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1000); await pg.tap("#tcont"); await pg.wait_for_timeout(300)
        g="__game"
        print("old save: mail", await ev("__game.vl().mail.length"), "recipes", await ev("Object.keys(__game.vl().rec).join()"))
        props=await ev("__game.PROPS.map(p=>[p.k,p.x,p.y,p.ok,[[1,0],[-1,0],[0,1],[0,-1]].some(d=>!__game.solidTile(p.x+d[0],p.y+d[1]))])"); print("props", props)
        assert all(p[3] and p[4] for p in props), "prop placement"
        print("home tiles", await ev("[__game.ground[__game.STOVE.y*__game.MW+__game.STOVE.x],__game.ground[__game.BENCH.y*__game.MW+__game.BENCH.x]]"))
        # each prop reachable by walking: path to a neighbour from the start
        r=await ev("(()=>{const g=__game,ra=g.reachFrom(14,27);return g.PROPS.map(p=>[[1,0],[-1,0],[0,1],[0,-1]].some(d=>ra[(p.y+d[1])*g.MW+p.x+d[0]]))})()"); print("props reachable (hen..mail side of river only before bridge):", r)
        # mail
        await ev("__game.readMail()"); print("mail:", (await ev("dtext.textContent"))[:70]); await ev(clr)
        await ev("__game.readMail()"); print("mail empty:", (await ev("dtext.textContent"))[:40]); await ev(clr)
        # stove: locked recipes, then cook
        await ev("__game.openStove()"); await pg.wait_for_timeout(150); print("stove:", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(e=>e.textContent+(e.classList.contains('no')?'*':'')).join(' | ')")); await pg.screenshot(path="vil_stove.png"); await ev(clr)
        await ev("['g_wheat','g_sunflower','carp','catfish','g_pumpkin','crab','mushroom','trout','acorn','sardine','flounder'].forEach(id=>__game.collect(__game.ITEMS.find(i=>i.id===id)))"); await pg.wait_for_timeout(200); await ev(clr)
        await ev("__game.openStove()"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[0].tap(); await pg.wait_for_timeout(150)
        await ev("__game.openStove()"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[1].tap(); await pg.wait_for_timeout(150)
        await ev("__game.openStove()"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[0].tap(); await pg.wait_for_timeout(150)
        print("dishes:", await ev("JSON.stringify(__game.vl().dish)"), "cooked", await ev("Object.keys(__game.vl().cooked).length"))
        # friendship: daily chat, then gift a dish, hearts and mail
        await ev("__game.S.vil.mira=1;__game.talk(__game.VIL[0])"); await pg.wait_for_timeout(150); print("gift picker:", await ev("pktitle.textContent"), "|", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(e=>e.textContent).join(' | ')"))
        await (await pg.query_selector_all("#pkgrid .slot"))[1].tap(); await pg.wait_for_timeout(200); print("after gift:", await ev("dtext.textContent"), "pts", await ev("__game.vl().fr.mira")); await ev(clr)
        await ev("__game.talk(__game.VIL[0])"); await pg.wait_for_timeout(100); print("same day again:", await ev("stack.join()"), (await ev("dtext.textContent"))[:60]); await ev(clr)
        for dd in range(3):
            await ev("__game.S.clock+=600;__game.talk(__game.VIL[0])"); await pg.wait_for_timeout(150)
            if await ev("stack.length>0"): await (await pg.query_selector_all("#pkgrid .slot"))[1].tap(); await pg.wait_for_timeout(150)
            await ev(clr)
        print("mira hearts:", await ev("__game.hearts('mira')"), "mail:", await ev("JSON.stringify(__game.vl().mail.map(m=>m.r||m.d||'note'))"))
        await ev("__game.readMail()"); print("recipe letter:", (await ev("dtext.textContent"))[:90], "| soup known", await ev("__game.vl().rec.soup")); await ev(clr)
        # animals
        for dd in range(3):
            await ev("__game.S.clock+=600;__game.petAnimal('hen');"); await ev(clr); await ev("__game.petAnimal('goat')"); await ev(clr); await ev("__game.petAnimal('duck')"); msg=await ev("dtext.textContent"); await ev(clr)
        print("animals:", await ev("JSON.stringify(__game.vl().ani)"), "| duck:", msg[:90])
        await ev("__game.petAnimal('hen')"); print("pet twice:", await ev("dtext.textContent")); await ev(clr)
        await ev("__game.openStove()"); await pg.wait_for_timeout(150); print("stove now:", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(e=>e.textContent+(e.classList.contains('no')?'*':'')).join(' | ')")); await ev(clr)
        # workbench
        await ev("__game.openBench()"); await pg.wait_for_timeout(150); print("bench:", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(e=>e.textContent+(e.classList.contains('no')?'*':'')).join(' | ')")); await (await pg.query_selector_all("#pkgrid .slot"))[0].tap(); await pg.wait_for_timeout(150); print("crafted:", await ev("JSON.stringify(__game.vl().craft)"))
        # merchant: closed day, open day
        await ev("while(__game.day()%2===0)__game.S.clock+=600;__game.openCart()"); print("cart closed:", (await ev("dtext.textContent"))[:60]); await ev(clr)
        await ev("__game.S.clock+=600;for(let i=0;i<4;i++){__game.vl().dish.bread=(__game.vl().dish.bread||0)+1};__game.openCart()"); await pg.wait_for_timeout(150); print("cart:", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(e=>e.textContent+(e.classList.contains('no')?'*':'')).join(' | ')")); await pg.screenshot(path="vil_cart.png")
        n0=await ev("__game.dishCount()"); await (await pg.query_selector_all("#pkgrid .slot"))[0].tap(); await pg.wait_for_timeout(150); print("bought clock:", await ev("__game.vl().shop.m_clock"), "dishes", n0, "->", await ev("__game.dishCount()"))
        await ev("__game.openCart()"); await pg.wait_for_timeout(150); await (await pg.query_selector_all("#pkgrid .slot"))[2].tap(); await pg.wait_for_timeout(150); print("tip:", await ev("dtext.textContent")); await ev(clr)
        # festival and bundles
        await ev("__game.S.clock=Math.floor(__game.S.clock/900)*900+900+350"); await pg.wait_for_timeout(1300); print("fest on:", await ev("__game.festNow()"), "mail", await ev("__game.vl().mail.length"))
        await ev("__game.openBoard()"); await pg.wait_for_timeout(150); print("board:", await ev("pkinfo.textContent")[:0] if False else (await ev("pkinfo.textContent"))[:120]); print("  ", await ev("[...document.querySelectorAll('#pkgrid .slot')].map(e=>e.textContent+(e.classList.contains('no')?'*':'')).join(' | ')")); await pg.screenshot(path="vil_board.png")
        await (await pg.query_selector_all("#pkgrid .slot"))[0].tap(); await pg.wait_for_timeout(200); print("festival:", (await ev("dtext.textContent"))[:80], "fest", await ev("JSON.stringify(__game.vl().fest)")); await ev(clr)
        await ev("__game.ITEMS.filter(i=>i.gard||i.fish).forEach(i=>__game.collect(i));['soup','cakes','omelet','trout'].forEach(k=>__game.vl().cooked[k]=1);__game.VIL.forEach(v=>__game.vl().fr[v.id]=9)"); await pg.wait_for_timeout(200); await ev(clr)
        for i in range(1,5):
            await ev("__game.openBoard()"); await pg.wait_for_timeout(120); await (await pg.query_selector_all("#pkgrid .slot"))[i].tap(); await pg.wait_for_timeout(150); await ev(clr)
        print("bundles:", await ev("JSON.stringify(__game.vl().bun)"), "well", await ev("__game.vl().well"))
        # furniture unlocks show in the picker
        await ev("__game.enterHome()"); await pg.wait_for_timeout(600); await ev("pickFurn(3)"); await pg.wait_for_timeout(150); print("furniture:", await ev("[...document.querySelectorAll('#pkgrid .slot')].slice(16).map(e=>e.textContent+(e.classList.contains('no')?'*':'')).join(' | ')")); await ev(clr)
        await ev("__game.S.home.fu[3]='m_clock';__game.S.home.fu[2]='c_shelf';__game.S.x=(__game.STOVE.x+1)*16+8;__game.S.y=(__game.STOVE.y+1)*16+10"); await pg.wait_for_timeout(400); await pg.screenshot(path="vil_home.png")
        print("near stove:", await ev("(()=>{const n=__game.nearest();return n&&n.k})()"))
        # almanac from pause
        await pg.tap("#mbtn"); await pg.wait_for_timeout(200); await pg.tap("#pvil"); await pg.wait_for_timeout(200); print("almanac:", (await ev("pkinfo.textContent"))[:140]); await pg.screenshot(path="vil_almanac.png"); await ev(clr)
        # save and reload keeps village data
        await ev("save()"); before=await ev("JSON.stringify(__game.vl())"); await pg.reload(); await pg.wait_for_timeout(900); await pg.tap("#tcont"); await pg.wait_for_timeout(300); after=await ev("JSON.stringify(__game.vl())"); print("save roundtrip equal:", before==after, len(before))
        # world shots
        for nm,k in [("mail","mail"),("board","board"),("cart","cart"),("hen","hen"),("goat","goat"),("duck","duck"),("well","well")]:
            await ev(f"(()=>{{const p=__game.PROPS.find(q=>q.k==='{k}');__game.exitHome&&0;__game.S.x=(p.x+1)*16+8;__game.S.y=(p.y+1)*16+10;if(__game.solidTile(p.x+1,p.y+1)){{__game.S.x=p.x*16+8;__game.S.y=(p.y+1)*16+10}}}})()"); await pg.wait_for_timeout(350); await pg.screenshot(path=f"vil_{nm}.png")
        print("errors", errs); await b.close()
asyncio.run(main())
