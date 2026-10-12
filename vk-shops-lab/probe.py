#!/usr/bin/env python3
import json, re, urllib.request, urllib.error, datetime

URLS = "vk-shops-lab/posts.txt"
UA = "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
def run_one(link):
    m = re.search(r"wall(-?\d+)_(\d+)",link)
    if not m: return {"source":link,"status":"INVALID_LINK"}
    post = f"{m[1]}_{m[2]}"
    result={"source":link,"id":post,"verified_views":None,"status":"UNVERIFIED","attempts":[]}
    for domain in ("m.vk.ru","m.vk.com","vk.ru"):
        url = f"https://{domain}/wall{post}"
        try:
            req=urllib.request.Request(url, headers={"User-Agent":UA,"Accept-Language":"ru-RU,ru;q=0.9"})
            with urllib.request.urlopen(req,timeout=12) as resp:
                text=resp.read(300_000).decode("utf-8","replace")
                final=resp.geturl()
                kind="BROWSER_UNSUPPORTED" if "Update your browser" in text else "LOGIN_REDIRECT" if "login" in final else "PAGE_RETURNED_UNVERIFIED"
                result["attempts"].append({"site":domain,"http":resp.status,"status":kind,"bytes":len(text)})
        except Exception as exc:
            result["attempts"].append({"site":domain,"status":"REQUEST_FAILED","reason":type(exc).__name__})
    return result
def main():
    links=[x.strip() for x in open(URLS,encoding="utf-8") if x.strip() and not x.startswith("#")][:5]
    out={"at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"results":[run_one(x) for x in links]}
    print("VK_PROBE_REPORT_START")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    print("VK_PROBE_REPORT_END")
if __name__=="__main__":main()
