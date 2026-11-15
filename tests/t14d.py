import asyncio, json
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625, has_touch=True, is_mobile=True)
        await ctx.add_init_script(SEED)
        pg = await ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        ev=lambda s: pg.evaluate(s)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(1200)
        await pg.tap("#tcont"); await pg.wait_for_timeout(200)
        await ev("__game.S.ch.name='Brian É';__game.collect(__game.ITEMS.find(i=>i.id==='maple'))"); await pg.wait_for_timeout(120); print("fx particles:", await ev("__game.FXP.length")); await pg.screenshot(path="v9_pop.png")
        await pg.tap("#mbtn"); print("pause:", await ev("pwho.textContent")); await pg.tap("#pset"); await pg.wait_for_timeout(150)
        await ev("document.getElementById('settings').scrollTop=99999"); await pg.wait_for_timeout(100)
        btn=await pg.query_selector("#srows .btn:last-of-type"); await btn.tap(); await pg.wait_for_timeout(200)
        code=await ev("bkout.value"); print("backup open:", await ev("[...__game.stack]"), "code len", len(code), code[:12]); await pg.screenshot(path="v9_backup.png")
        await pg.tap("#bkcopy"); await pg.wait_for_timeout(150); print("copy msg:", await ev("bkmsg.textContent"))
        await pg.tap("#bkrestore"); print("empty restore:", await ev("bkmsg.textContent"))
        print("bad code:", await ev("__game.restoreBackup('hello')"), "|", await ev("__game.restoreBackup('WV1:abc')"))
        # change state then restore
        await ev("__game.ITEMS.slice(15,25).forEach(i=>__game.collect(i))"); await pg.wait_for_timeout(100); n1=await ev("Object.keys(__game.S.found).length")
        await pg.fill("#bkin", code); await pg.tap("#bkrestore"); await pg.wait_for_timeout(150); await pg.tap("#cyes"); await pg.wait_for_timeout(400)
        print("restored:", n1, "->", await ev("Object.keys(__game.S.found).length"), await ev("[...__game.stack]"), await ev("tslotv.textContent"), await ev("__game.S.ch.name"))
        print("stored before reload:", await ev("(()=>{const d=JSON.parse(localStorage.getItem('wandervalley_save_v1'));return [d.found.length,d.ch.name,d.started,localStorage.getItem('seeded'),Object.keys(localStorage)]})()"), await ev("[Object.keys(__game.S.found).length,__game.S.ch.name,__game.CFG.slot]"))
        await pg.reload(); await pg.wait_for_timeout(900); print("after reload:", await ev("tslotv.textContent"), await ev("(()=>{const d=JSON.parse(localStorage.getItem('wandervalley_save_v1'));return [d.found.length,d.ch.name,d.started,localStorage.getItem('seeded'),Object.keys(localStorage)]})()"))
        # restore into another slot
        await (await pg.query_selector_all("#tslot .pm"))[1].tap(); await pg.wait_for_timeout(150); print("slot2:", await ev("tslotv.textContent"), "restore:", repr(await ev(f"__game.restoreBackup({json.dumps(code)})")), await ev("tslotv.textContent"))
        print("errors", errs); await b.close()
asyncio.run(main())
