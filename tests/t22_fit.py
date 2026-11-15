import asyncio, json, sys
from playwright.async_api import async_playwright
# every menu fits every screen: phones, handhelds, tablets and desktops, upright and sideways, at Normal and Large text
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
SIZES=[("phone-xs",320,568,2),("phone-s",360,640,3),("phone",390,844,3),("phone-l",412,915,2.625),("tablet",768,1024,2),
       ("phone-side",640,360,3),("retroid",732,412,2.625),("phone-side-l",844,390,3),("phone-side-xl",915,412,2.625),("tablet-side",1024,768,2),("laptop",1366,768,1),("desktop",1920,1080,1)]
CHECK=r"""(async(pnl)=>{const out=[],W=innerWidth,H=innerHeight,ov=$(pnl),card=ov.querySelector('.card');ov.scrollTop=0;await new Promise(r=>setTimeout(r,30));
  const c=card.getBoundingClientRect();if(c.left<-1||c.right>W+1)out.push('card width '+Math.round(c.left)+'..'+Math.round(c.right)+' of '+W);if(c.top<-1)out.push('card top cut '+Math.round(c.top));
  for(const e of navEls()){setFoc(e);await new Promise(r=>setTimeout(r,0));const q=e.getBoundingClientRect();if(q.top<-1||q.bottom>H+1||q.left<-1||q.right>W+1)out.push((e.id||e.textContent.slice(0,12))+' off screen '+[q.left,q.top,q.right,q.bottom].map(Math.round).join(','))}
  const sc=[...card.querySelectorAll('*')].filter(x=>x.scrollWidth>x.clientWidth+2&&getComputedStyle(x).overflowX!=='visible'&&x.tagName!=='TEXTAREA').map(x=>x.id||x.className);if(sc.length)out.push('sideways scroll in '+sc.join());
  const under=stack.slice(0,-1).filter(id=>$(id).style.visibility!=='hidden');if(under.length)out.push('menu showing underneath: '+under.join());
  return out})"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]; fails=0
        for name,w,h,dpr in SIZES:
            for ts in ([1,2] if name in ("phone-s","phone-side","retroid","desktop") else [1]):
                ctx = await b.new_context(viewport={"width":w,"height":h}, device_scale_factor=dpr, has_touch=dpr>1, is_mobile=dpr>1); await ctx.add_init_script(SEED+f"if(!localStorage.getItem('ts{ts}')){{localStorage.setItem('ts{ts}','1');localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({{ts:{ts}}}))}}")
                pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
                ev=lambda s: pg.evaluate(s)
                await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
                res={}
                res["title"]=await ev(CHECK+"('title')")
                await ev("closeAll()")
                for pnl,op in [("pause","openPanel('pause')"),("journal","openPanel('journal')"),("map","openPanel('map')"),("settings","openPanel('pause');openPanel('settings')"),("builder","openPanel('builder')"),("museum","openPanel('museum')"),("backup","openPanel('settings');$('srows').querySelector('.btn').click()"),("picker","__game.openStove()"),("confirm","ask('Start a new game? This erases your current save.','Start over',null)")]:
                    await ev(op); await pg.wait_for_timeout(250); res[pnl]=await ev(CHECK+f"('{pnl}')")
                    if name in ("retroid","phone-side","phone-s","desktop","tablet") and ts==1 and pnl in ("pause","map","settings","journal"): await pg.screenshot(path=f"fit_{name}_{pnl}.png")
                    await ev("closeAll()")
                hud=await ev("(()=>{const a=$('count').getBoundingClientRect(),b=$('hudr').getBoundingClientRect(),o=[];if(a.right>b.left&&a.bottom>b.top&&a.left<b.right&&a.top<b.bottom)o.push('count overlaps buttons');if(b.right>innerWidth+1||b.left<0)o.push('buttons off screen');say('Captain Wren: My boat sails to Sunny Canyon. Show me any Sea Fish first, so I know you respect the water.');const d=$('dialog').getBoundingClientRect();if(d.left<0||d.right>innerWidth+1||d.top<0)o.push('dialog off screen');hush();return o})()")
                res["hud"]=hud
                bad={k:v for k,v in res.items() if v}
                print(f"{name} {w}x{h} text {ts}:", "ok" if not bad else json.dumps(bad)[:900]); fails+=len(bad)
                await ctx.close()
        print("problems", fails); print("errors", errs[:5]); await b.close()
asyncio.run(main())
