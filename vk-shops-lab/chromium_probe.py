import asyncio, json, datetime, re
from playwright.async_api import async_playwright
POSTS=["-224838397_52150","-226819393_26471"]
async def main():
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        context=await browser.new_context(viewport={"width":390,"height":844},device_scale_factor=1,is_mobile=True,has_touch=True,user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",locale="ru-RU")
        for post in POSTS:
            page=await context.new_page()
            try:
                url="https://m.vk.com/wall"+post
                await page.goto(url,wait_until="domcontentloaded",timeout=20000)
                await page.wait_for_timeout(2500)
                body=await page.locator("body").inner_text(timeout=10000)
                markers=[m for m in [post,"просмотров","views","Обновите ваш браузер","ВКонтакте"] if m.lower() in body.lower()]
                results.append({"post":post,"requested_url":url,"final_url":page.url,"title":await page.title(),"body_chars":len(body),"markers":markers,"body_preview":body[:380],"post_views":None,"status":"UNVERIFIED_CHROMIUM_REQUIRES_PAGE_SPECIFIC_COUNTER"})
            except Exception as e:
                results.append({"post":post,"status":"FAILED","error_type":type(e).__name__})
            finally:await page.close()
        await browser.close()
    print("MOBILE_CHROMIUM_REPORT_START")
    print(json.dumps({"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"results":results},ensure_ascii=False,indent=2))
    print("MOBILE_CHROMIUM_REPORT_END")
asyncio.run(main())
