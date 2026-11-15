import asyncio, base64, sys
from playwright.async_api import async_playwright
# contact sheet: rows = side, front, back walking frames, plus a row of standing front views in many looks
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        pg = await b.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
        d=await pg.evaluate("""(()=>{const c=document.createElement('canvas');c.width=1440;c.height=1000;const g=c.getContext('2d');g.fillStyle='#3a5a3c';g.fillRect(0,0,1440,1000);const og=ig;ig=g;
          const ch=Object.assign({},__game.S.ch,{hs:1,hc:2,hat:4,gl:1,pack:2,shirt:5,pat:1});
          ['side','front','back'].forEach((v,r)=>{for(let i=0;i<8;i++){g.setTransform(3,0,0,3,80+i*170,200+r*210);iperson(ch,0,0,true,false,{ph:i/8*Math.PI*2,run:1,view:v,side:1})}});
          const looks=[{hs:0,hat:0},{hs:1,hat:4,face:0,gl:1},{hs:2,hat:1},{hs:3,hat:4,body:1},{hs:4,hat:2,gl:2},{hs:5,hat:4,face:2},{hs:6,hat:4,face:1},{hs:7,hat:5,face:3},{hs:0,hat:9,pat:2,bot:1},{hs:1,hat:7,bot:2,body:1},{hs:4,hat:3,pat:3},{hs:0,hat:8,pack:5}];
          looks.forEach((l,i)=>{g.setTransform(2.2,0,0,2.2,60+i*115,920);iperson(Object.assign({},__game.S.ch,l),0,0,false,i===0,{view:i%2&&i>7?'back':'front'})});
          ig=og;return c.toDataURL()})()""")
        open(sys.argv[1] if len(sys.argv)>1 else "sheet.png","wb").write(base64.b64decode(d.split(",")[1])); print("errors",errs); await b.close()
asyncio.run(main())
