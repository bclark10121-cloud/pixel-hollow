import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for (w,h,dpr) in [(412,915,2.625),(360,800,3),(393,873,2.75),(640,360,3),(384,854,2.8125)]:
            ctx = await b.new_context(viewport={"width":w,"height":h}, device_scale_factor=dpr, has_touch=True, is_mobile=True)
            pg = await ctx.new_page(); await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(500)
            r = await pg.evaluate("(()=>{const c=document.getElementById('c'),d=devicePixelRatio;return [c.width,c.height,parseFloat(c.style.width)*d,parseFloat(c.style.height)*d]})()")
            print((w,h,dpr),"backing",r[0],r[1],"css size in device px",round(r[2],2),round(r[3],2),"=> stretch", "NONE" if abs(r[0]-r[2])<0.01 and abs(r[1]-r[3])<0.01 else "YES (blur)")
            await ctx.close()
        await b.close()
asyncio.run(main())
