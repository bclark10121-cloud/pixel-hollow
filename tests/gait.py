import asyncio, base64
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        pg = await b.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
        d=await pg.evaluate("""(()=>{const c=document.createElement('canvas');c.width=1440;c.height=420;const g=c.getContext('2d');g.fillStyle='#3a5a3c';g.fillRect(0,0,1440,420);const og=ig;ig=g;
          for(let r=0;r<2;r++)for(let i=0;i<12;i++){g.setTransform(3,0,0,3,60+i*120,190+r*210);g.fillStyle='rgba(0,0,0,.25)';g.fillRect(-18,0,36,0.6);iperson(__game.S.ch,0,0,true,false,{ph:i/12*Math.PI*2,run:1,back:r===1,side:r?0.4:1})}
          ig=og;return c.toDataURL()})()""")
        open("gait.png","wb").write(base64.b64decode(d.split(",")[1])); print("errors",errs); await b.close()
asyncio.run(main())
