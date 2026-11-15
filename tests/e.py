import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page()
        pg.on("pageerror", lambda e: print("ERR", e, getattr(e,'stack','')))
        await pg.goto("file:///home/claude/game/index.html"); await pg.wait_for_timeout(500); await b.close()
asyncio.run(main())
