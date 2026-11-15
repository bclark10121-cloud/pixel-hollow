import asyncio, json, sys
from playwright.async_api import async_playwright
SEED=open('t7.py').read().split('SEED="')[1].split('"\nasync')[0].replace("localStorage.setItem('wandervalley_cfg_v1',JSON.stringify({gfx:0}));","")
# for every walkable tile around a building, measure how much of the player is still visible
async def main():
    bx0,by0,bx1,by1=[int(v) for v in sys.argv[1:5]]
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=2.625); await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900); await pg.evaluate("closeAll()")
        r=await pg.evaluate(f"""(()=>{{const G=__game,S=G.S,out=[];const oi=iperson;let hide=false;window.iperson=function(ch){{if(hide&&ch===S.ch)return;return oi.apply(this,arguments)}};
          G.S.bridge=true;G.openBridge(true);
          for(let y={by0};y<={by1};y++)for(let x={bx0};x<={bx1};x++){{if(G.solidTile(x,y))continue;S.x=x*16+8;S.y=y*16+10;S.vx=S.vy=0;
            const w=cv.width,h=cv.height,cx0=Math.round(w/2-40*IK),cy0=Math.round(h*0.56-70*IK),cw=Math.round(80*IK),chh=Math.round(80*IK);
            hide=false;renderIso();const A=cx.getImageData(cx0,cy0,cw,chh).data;hide=true;renderIso();const B=cx.getImageData(cx0,cy0,cw,chh).data;hide=false;
            let d=0;for(let i=0;i<A.length;i+=4)if(Math.abs(A[i]-B[i])+Math.abs(A[i+1]-B[i+1])+Math.abs(A[i+2]-B[i+2])>60)d++;out.push([x,y,d])}}
          return out}})()""")
        mx=max(v[2] for v in r)
        grid={}
        for x,y,d in r: grid[(x,y)]=d
        for y in range(by0,by1+1):
            print("%3d "%y+" ".join(("###" if (x,y) not in grid else "%3d"%(100*grid[(x,y)]//mx)) for x in range(bx0,bx1+1)))
        print("max",mx,"errors",errs); await b.close()
asyncio.run(main())
