import asyncio, json
from playwright.async_api import async_playwright
# v0.14.1: can a player really walk to every outdoor treasure? No teleporting.
# 1) Walk test: one search from each region entrance that moves the way the game does (8-way D-pad in the angled view,
#    the same speed, hitbox and wall checks as update()). Every treasure must come within pickup range.
# 2) Pocket test: no treasure may sit at the end of a hidden one-tile lane between trees. Cliff nooks are allowed and listed.
WALK=r"""(async(cfg)=>{const G=__game,T=16,W=G.MW,H=G.MH;G.openBridge(true);
 const sol=new Uint8Array(W*H);for(let y=0;y<H;y++)for(let x=0;x<W;x++)sol[y*W+x]=G.solidTile(x,y)?1:0;
 const blocked=(px,py)=>{const x0=Math.floor((px-4)/T),x1=Math.floor((px+4)/T),y0=Math.floor((py-5)/T),y1=Math.floor(py/T);if(x0<0||y0<0||x1>=W||y1>=H)return true;for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++)if(sol[y*W+x])return true;return false};
 const acts=[];for(const ax of [-1,0,1])for(const ay of [-1,0,1]){if(!ax&&!ay)continue;let dx=ax/(cfg.iw/2)+ay/(cfg.ih/2),dy=ay/(cfg.ih/2)-ax/(cfg.iw/2);const m=Math.hypot(dx,dy);acts.push([dx/m,dy/m])}
 const sp=62*0.9*0.72,rg=G.REG[cfg.reg],ent=cfg.reg==="over"?{x:14,y:27}:cfg.reg==="snow"?G.SNOW_IN:cfg.reg==="cave"?G.CAVE_IN:cfg.reg==="deep"?G.deep().DEEP_IN:G.DES_IN;
 const items=G.ITEMS.filter(i=>!i.off&&!i.fish&&!i.gard&&!i.gift&&!i.pet&&G.regAt(i.x,i.y)===rg);
 const KW=W*8,seen=new Uint8Array(KW*(H*8+2)),cap=3000000,qx=new Float32Array(cap),qy=new Float32Array(cap);let n=0,h=0;
 const near=new Map();for(const it of items){for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++){const k=(it.y+dy)*W+it.x+dx;if(!near.has(k))near.set(k,[]);near.get(k).push(it)}}
 const push=(x,y)=>{const k=Math.round(y/2)*KW+Math.round(x/2);if(seen[k]||n>=cap)return;seen[k]=1;qx[n]=x;qy[n]=y;n++};push(ent.x*T+8,ent.y*T+10);const got=new Set();
 while(h<n){const x=qx[h],y=qy[h];h++;const l=near.get(((y-4)/T|0)*W+(x/T|0));if(l)for(const it of l)if(!got.has(it.id)&&Math.hypot(it.x*T+8-x,it.y*T+8-(y-4))<22)got.add(it.id);
   for(const a of acts){let X=x,Y=y;for(let s=0;s<6;s++){const vx=a[0]*sp/60,vy=a[1]*sp/60;if(!blocked(X+vx,Y))X+=vx;if(!blocked(X,Y+vy))Y+=vy}if(G.regAt(X/T|0,Y/T|0)!==rg)continue;push(X,Y)}
   if(h%60000===0)await new Promise(r=>setTimeout(r,0))}
 G.openBridge(G.S.bridge);return {items:items.length,reached:got.size,missed:items.filter(i=>!got.has(i.id)).map(i=>i.id),states:n}})"""
POCKET=r"""(()=>{const G=__game,D4=[[1,0],[-1,0],[0,1],[0,-1]],plant=new Set([1,2,3,4,5,6,7,12,13,15,16,17]);G.openBridge(true);const bad=[],nooks=[];
 for(const it of G.ITEMS){if(it.off||it.hid||it.fish||it.gard||it.gift||it.pet)continue;const rg=G.regAt(it.x,it.y);if(![G.REG.over,G.REG.snow,G.REG.desert].includes(rg))continue;
   const st=G.solidTile(it.x,it.y)?D4.map(d=>[it.x+d[0],it.y+d[1]]).filter(p=>!G.solidTile(p[0],p[1])):[[it.x,it.y]];const seen=new Set(st.map(p=>p[0]+','+p[1]));let fr=st;
   for(let s=0;s<3;s++){const nf=[];for(const[x,y]of fr)for(const d of D4){const X=x+d[0],Y=y+d[1],k=X+','+Y;if(seen.has(k)||G.solidTile(X,Y))continue;seen.add(k);nf.push([X,Y])}fr=nf}
   if(seen.size>=8)continue;let trees=0;for(const k of seen){const[x,y]=k.split(',').map(Number);for(const d of D4){const o=G.obj[(y+d[1])*G.MW+x+d[0]];if(plant.has(o))trees++}}
   (trees>=2?bad:nooks).push([it.id,it.x,it.y,seen.size,trees])}
 G.openBridge(G.S.bridge);return {bad,nooks,cleared:G.CLEARED.length}})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); errs=[]
        pg = await b.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(900)
        iw,ih=await pg.evaluate("[ITW,ITH]")
        pk=await pg.evaluate(POCKET); print("pocket check:", json.dumps(pk))
        if pk["bad"]: errs.append("treasure in a hidden tree lane: "+json.dumps(pk["bad"]))
        print("cleared tiles:", await pg.evaluate("JSON.stringify(__game.CLEARED)"))
        for reg in ["over","snow","desert","cave","deep"]:
            v=await pg.evaluate(WALK+"("+json.dumps({"iw":iw,"ih":ih,"reg":reg})+")"); print("walk test",reg,"(angled view, 8-way pad, from the entrance):", json.dumps(v))
            if v["missed"]: errs.append(reg+" walk missed "+",".join(v["missed"]))
        # the cave mountain still lets the player in: the mouth tile is open and reachable
        print("cave mouth:", await pg.evaluate("(()=>{const G=__game,r=G.reachFrom(14,27);const x=30,y=5;return [!G.solidTile(x,y),!!r[y*G.MW+x]]})()"))
        print("errors", errs); await b.close()
asyncio.run(main())
