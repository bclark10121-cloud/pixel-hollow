import asyncio, json
from playwright.async_api import async_playwright
JS=r"""
(()=>{const g=__game,T=16,res={};
 Object.assign(g.S,{shovel:true,rod:true,net:true,boots:true,lantern:true,bridge:true});g.openBridge&&g.openBridge(true);
 const starts={over:[14,28],autumn:[80,30],cave:[g.CAVE_IN.x,96],home:[g.HOME_IN.x,g.HOME_IN.y],snow:[g.SNOW_IN.x,g.SNOW_IN.y],desert:[g.DES_IN.x,g.DES_IN.y]};
 const names=["arrowleft","arrowright","arrowup","arrowdown"];
 for(const nm in starts){const st=starts[nm];g.S.x=st[0]*T+8;g.S.y=st[1]*T+10;g.S.vx=g.S.vy=0;const rg=g.region();let trapped=0,bad=0,moved=0,maxStill=0,still=0,first=null;const seenT=new Set();
  for(let i=0;i<120000;i++){if(i%40===0){for(const n of names)keys[n]=false;const k=Math.random()*9|0;if(k<4)keys[names[k]]=true;else if(k<8){keys[names[k%2]]=true;keys[names[2+(k>>1)%2]]=true}}
   const ox=g.S.x,oy=g.S.y;update(1/60);
   if(stack.length){while(stack.length)closePanel()}if(typeof dlg!=="undefined"&&dlg)hush();
   if(g.region()!==rg){g.S.x=ox;g.S.y=oy}
   if(!isFinite(g.S.x)||!isFinite(g.S.y)){bad++;break}
   seenT.add((g.S.x/T|0)+","+(g.S.y/T|0));
   const any=keys.arrowleft||keys.arrowright||keys.arrowup||keys.arrowdown;
   if(any&&Math.hypot(g.S.x-ox,g.S.y-oy)<0.001)still++;else{maxStill=Math.max(maxStill,still);still=0}
   if(i%20===0){let free=0;for(const d of [[2,0],[-2,0],[0,2],[0,-2]])if(!blocked(g.S.x+d[0],g.S.y+d[1]))free++;if(!free){trapped++;if(!first)first=[g.S.x,g.S.y]}}
   if(blocked(g.S.x,g.S.y)){bad++;if(!first)first=[g.S.x,g.S.y]}}
  for(const n of names)keys[n]=false;
  res[nm]={tilesVisited:seenT.size,trapped,insideWall:bad,first}}
 // teleport targets must be open and connected to a way out
 const tp=[["snow in",g.SNOW_IN.x,g.SNOW_IN.y],["desert in",g.DES_IN.x,g.DES_IN.y],["cave in",g.CAVE_IN.x,96],["home in",g.HOME_IN.x,g.HOME_IN.y],["boat back",g.BOAT.x,g.BOAT.y-1],["cabin door",g.CABIN?0:0,0]].filter(t=>t[1]);
 for(const tn of g.TUNNELS)for(const e of tn)tp.push(["tunnel",e[0],e[1]]);
 res.teleports=tp.map(t=>{let open=0;for(const d of [[1,0],[-1,0],[0,1],[0,-1]])if(!g.solidTile(t[1]+d[0],t[2]+d[1]))open++;return [t[0],t[1],t[2],open]}).filter(t=>t[3]===0);
 return res})()
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        ctx = await b.new_context(viewport={"width":412,"height":915}, device_scale_factor=1, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(800)
        await pg.tap("#tnew"); await pg.wait_for_timeout(300); await pg.tap("#bdone"); await pg.wait_for_timeout(700)
        for i in range(4): await pg.keyboard.press("e"); await pg.wait_for_timeout(200)
        r=await pg.evaluate(JS)
        for k,v in r.items(): print(k,v)
        print("errors",errs[:3]); await b.close()
asyncio.run(main())
