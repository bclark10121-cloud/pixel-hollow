# v0.14 review: fresh-game progression audit and exit audit.
# Simulates a player from a new game. Uses real gate rules and real collect().
import asyncio, json
from playwright.async_api import async_playwright
JS = r"""(()=>{const G=__game,S=G.S,W=G.MW,T=G.T,R=G.REG,log=[];
 const tile=(px)=>Math.floor(px/T);
 const k=(x,y)=>y*W+x;
 const adjOk=(m,x,y)=>!!(m[k(x,y)]||m[k(x+1,y)]||m[k(x-1,y)]||m[k(x,y+1)]||m[k(x,y-1)]);
 const D=G.deep();
 function over(){G.openBridge(!!S.bridge);let m=G.reachFrom(14,27);
   // hollow log shortcuts work both ways and are not gated
   for(let pass=0;pass<3;pass++)for(const tn of G.TUNNELS)for(let e=0;e<2;e++){const a=tn[e],b=tn[1-e];if(adjOk(m,a[0],a[1])){const b2=G.reachFrom(b[0],b[1]+1);for(let i=0;i<m.length;i++)if(b2[i])m[i]=1}}
   return m}
 function maps(){const o=over();return {o,
   c:S.lantern?G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y):null,
   s:S.vil.juniper&&adjOk(o,G.ARCH.x,G.ARCH.y)?G.reachFrom(G.SNOW_IN.x,G.SNOW_IN.y):null,
   d:S.vil.wren&&adjOk(o,G.BOAT.x,G.BOAT.y)?G.reachFrom(G.DES_IN.x,G.DES_IN.y):null,
   p:null}}
 const quiet=()=>{try{while(G.stack.length)G.stack.pop()}catch(e){}};
 let M=maps();
 function mapFor(x,y){const rg=G.regAt(x,y);return rg===R.over?M.o:rg===R.cave?M.c:rg===R.snow?M.s:rg===R.desert?M.d:rg===R.deep?M.p:null}
 const got=id=>!!S.found[id];
 const take=(it,why)=>{if(got(it.id))return false;G.collect(it);quiet();log.push(why+":"+it.id);return true};
 let round=0;
 for(;round<60;round++){let ch=false;M=maps();
   if(M.c&&S.vil.bram&&adjOk(M.c,D.BRAM.x,D.BRAM.y))M.p=G.reachFrom(D.DEEP_IN.x,D.DEEP_IN.y);
   // tools
   if(!S.shovel&&adjOk(M.o,G.SHOVEL.x,G.SHOVEL.y)){S.shovel=true;log.push("tool:shovel");ch=true}
   if(!S.rod&&adjOk(M.o,G.ROD.x,G.ROD.y)){S.rod=true;log.push("tool:rod");ch=true}
   if(!S.net&&adjOk(M.o,G.NET.x,G.NET.y)){S.net=true;log.push("tool:net");ch=true}
   // bridge
   if(!S.bridge&&Object.keys(S.found).length>=8&&adjOk(M.o,G.BRX-2,G.BRIDGE_Y)){S.bridge=true;log.push("bridge");ch=true}
   // placed treasures
   for(const it of G.ITEMS){if(it.off||got(it.id))continue;const m=mapFor(it.x,it.y);if(!m)continue;
     let ok=it.rock?(m[k(it.x+1,it.y)]||m[k(it.x-1,it.y)]||m[k(it.x,it.y+1)]):(m[k(it.x,it.y)]||adjOk(m,it.x,it.y));
     if(it.dig&&!S.shovel)ok=false;if(it.bug&&!S.net)ok=false;
     if(ok&&take(it,"walk"))ch=true}
   // fishing: pond and sea in the valley, mirror in the Autumn Woods, deep lake below
   if(S.rod)for(const it of G.ITEMS){if(!it.fish||got(it.id))continue;
     const z=it.fish;const ok=z==="pond"||z==="sea"||(z==="mirror"&&S.bridge)||(z==="deep"&&M.p);if(ok&&take(it,"fish"))ch=true}
   // villagers
   for(const v of G.VIL){if(S.vil[v.id])continue;const m=mapFor(v.x,v.y);if(!m||!adjOk(m,v.x,v.y))continue;if(v.ok()){S.vil[v.id]=1;log.push("vil:"+v.id);if(v.gift){const it=G.ITEMS.find(i=>i.id===v.gift);take(it,"gift")}ch=true}}
   // garden: a wild flower gives its seeds
   for(const it of G.ITEMS){if(!it.gard||got(it.id))continue;const sd=G.SEEDS?G.SEEDS.find(x=>x[0]===it.gard):null;if(!sd||got(sd[2]))if(take(it,"garden"))ch=true}
   // pet fetch
   for(const it of G.ITEMS){if(it.pet&&!got(it.id)&&take(it,"fetch"))ch=true}
   // wildlife: photograph an animal once its home is reachable
   for(const c of G.CRIT){const it=G.ITEMS.find(i=>i.id===c.id);if(got(it.id))continue;const m=mapFor(c.hx,c.hy);if(m&&m[k(c.hx,c.hy)]&&take(it,"photo"))ch=true}
   if(!ch)break}
 const missing=G.ITEMS.filter(i=>!got(i.id)).map(i=>i.id);
 // exits and arrival spots
 M=maps();const all=G.reachFrom(14,27);
 const solidAt=(x,y)=>G.solidTile(x,y);
 const arrive={MUS_IN:[G.MUS_IN.x,G.MUS_IN.y],HOME_IN:[G.HOME_IN.x,G.HOME_IN.y],CAVE_IN:[G.CAVE_IN.x,G.CAVE_IN.y],SNOW_IN:[G.SNOW_IN.x,G.SNOW_IN.y],DES_IN:[G.DES_IN.x,G.DES_IN.y],DEEP_IN:[D.DEEP_IN.x,D.DEEP_IN.y],PIT_OUT:[D.PIT_OUT.x,D.PIT_OUT.y]};
 const arriveBad=Object.entries(arrive).filter(([n,p])=>solidAt(p[0],p[1])).map(e=>e[0]);
 const exitOK={};
 {const m=G.reachFrom(G.MUS_IN.x,G.MUS_IN.y);exitOK.museum=[67,68,69].some(x=>m[k(x,97)])}
 {const m=G.reachFrom(G.HOME_IN.x,G.HOME_IN.y);let f=false;for(let x=59;x<82;x++)if(m[k(x,78)])f=true;exitOK.home=f}
 {const m=G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y);let f=false;for(let x=0;x<W;x++)if(m[k(x,97)]&&G.regAt(x,97)===R.cave)f=true;exitOK.cave=f}
 {const m=G.reachFrom(G.SNOW_IN.x,G.SNOW_IN.y);exitOK.snow=!!m[k(30,138)]}
 {const m=G.reachFrom(G.DES_IN.x,G.DES_IN.y);exitOK.desert=adjOk(m,G.DBOAT.x,G.DBOAT.y)}
 {const m=G.reachFrom(D.DEEP_IN.x,D.DEEP_IN.y);exitOK.deep=adjOk(m,D.DLAD.x,D.DLAD.y)}
 // where each exit drops you in the valley must join the start area
 G.openBridge(true);const ov=G.reachFrom(14,27);G.openBridge(!!S.bridge);
 const outs={museum:[G.MUS?0:0],};
 const drop={museumOut:[(43+1),43],homeOut:[14,26],archOut:[G.ARCH.x,G.ARCH.y+2],boatOut:[G.BOAT.x,G.BOAT.y-1]};
 const cv=G.reachFrom(G.CAVE_IN.x,G.CAVE_IN.y);const deepBack=adjOk(cv,D.PIT_OUT.x,D.PIT_OUT.y);
 const dropBad=Object.entries(drop).filter(([n,p])=>!adjOk(ov,p[0],p[1])).map(e=>e[0]);
 return {rounds:round,total:G.ITEMS.length,found:Object.keys(S.found).length,missing,order:log.filter(s=>!s.startsWith("walk")),arriveBad,exitOK,dropBad,deepBack,lantern:S.lantern,boots:S.boots}})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        pg = await (await b.new_context(viewport={"width":412,"height":915})).new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(600)
        await pg.click("#tnew"); await pg.wait_for_timeout(300); await pg.click("#bdone"); await pg.wait_for_timeout(300)
        r = await pg.evaluate(JS)
        print(json.dumps(r, indent=0))
        if r["missing"]: errs.append("missing "+",".join(r["missing"]))
        if r["arriveBad"]: errs.append("solid arrival "+",".join(r["arriveBad"]))
        bad=[k for k,v in r["exitOK"].items() if not v]
        if bad: errs.append("no exit "+",".join(bad))
        if not r["deepBack"]: errs.append("deep exit lands cut off")
        if r["dropBad"]: errs.append("bad drop "+",".join(r["dropBad"]))
        # a save written between the last autumn find and the reward must still open the cave
        await pg.evaluate("""(()=>{const G=__game;const a=G.SETS.find(s=>s.area==='autumn');const ids=G.ITEMS.filter(i=>i.set===a.id).map(i=>i.id);
          localStorage.setItem('wandervalley_save_v1',JSON.stringify({v:1,x:14*16+8,y:27*16+10,found:ids,lantern:false,boots:false,started:true}))})()""")
        await pg.reload(); await pg.wait_for_timeout(500)
        rep = await pg.evaluate("[__game.S.lantern,__game.S.boots]")
        print("repair on load lantern,boots", rep)
        if rep!=[True,True]: errs.append("reward repair failed")
        # rewards are granted the moment the set completes, before the celebration
        pg = await (await b.new_context(viewport={"width":412,"height":915})).new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(500)
        await pg.click("#tnew"); await pg.wait_for_timeout(200); await pg.click("#bdone"); await pg.wait_for_timeout(200)
        now = await pg.evaluate("(()=>{const G=__game;const a=G.SETS.find(s=>s.area==='autumn');G.ITEMS.filter(i=>i.set===a.id).forEach(i=>G.collect(i));const r=[G.S.lantern,G.S.boots,JSON.parse(localStorage.getItem('wandervalley_save_v1')).lantern];return r})()")
        print("instant reward lantern,boots,saved", now)
        if now!=[True,True,True]: errs.append("reward not instant")
        print("errors", errs); await b.close()
asyncio.run(main())
