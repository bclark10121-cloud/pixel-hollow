import asyncio, json
from playwright.async_api import async_playwright
# v0.14.8: messages sit about one third down the screen, just above the character, upright and sideways
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        for w,h,tag in [(412,915,"portrait"),(640,360,"landscape"),(732,412,"wide")]:
            ctx = await b.new_context(viewport={"width":w,"height":h}, device_scale_factor=2, has_touch=True, is_mobile=True); await ctx.add_init_script(SEED)
            pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
            ev=lambda s: pg.evaluate(s)
            await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900); await ev("$('tcont').scrollIntoView()"); await pg.tap("#tcont"); await pg.wait_for_timeout(400)
            await ev("toast('Found: Daisy!')"); await pg.wait_for_timeout(200)
            r=await ev("(()=>{const t=$('toast').getBoundingClientRect(),b=Math.max($('hudr').getBoundingClientRect().bottom,$('count').getBoundingClientRect().bottom);return [Math.round(t.top),Math.round(t.bottom),Math.round(b),innerHeight]})()")
            print(tag,"one line: top",r[0],"bottom",r[1],"buttons end",r[2],"screen",r[3],"-> bottom at",round(r[1]/r[3]*100),"percent"); await pg.screenshot(path=f"third_{tag}_toast.png")
            assert r[0]>=r[2] and abs(r[1]-r[3]*0.4)<=3, "one-line message should end 40 percent down"
            await ev("say('Mira: I tend the meadow gardens. I would love to see a wild Sunflower. Have you found one?')"); await pg.wait_for_timeout(200); await ev("toast('Found: Poppy!')"); await pg.wait_for_timeout(200)
            q=await ev("(()=>{const d=$('dialog').getBoundingClientRect(),t=$('toast').getBoundingClientRect();return [Math.round(d.top),Math.round(d.bottom),Math.round(t.top),Math.round(t.bottom)]})()")
            print(tag,"speech: top",q[0],"bottom",q[1],"| find message with it: top",q[2],"bottom",q[3]); await pg.screenshot(path=f"third_{tag}_speech.png")
            assert q[0]>=r[2] and (q[1]<=r[3]*0.4+3 or q[0]<=r[2]+9), "speech should end by 40 percent down unless it is pinned under the buttons"
            assert q[3]<=q[0] or q[2]>=q[1], "the find message must not overlap the speech box"
            await ev("hush()"); await ev("openPanel('settings')"); await pg.wait_for_timeout(200); await ev("closeAll()"); await ctx.close()
        print("errors", errs); await b.close()
asyncio.run(main())
