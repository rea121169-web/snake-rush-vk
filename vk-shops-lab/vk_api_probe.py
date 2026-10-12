#!/usr/bin/env python3
"""Read-only VK wall.getById batch verification. Guard secret in all output."""
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_POSTS = [
    {"owner": -224838397, "post": 52150, "sku": "2438903294",
     "prior_views": "52.9K observed by user 2026-10-12"},
    {"owner": -226819393, "post": 26471, "sku": "3210776803",
     "prior_views": "11.1K previously confirmed 2026-10-11"},
]

def request(method, params, token):
    arguments = dict(params)
    arguments["access_token"] = token
    arguments["v"] = "5.199"
    encoded = urllib.parse.urlencode(arguments)
    url = "https://api.vk.com/method/" + method + "?" + encoded
    req = urllib.request.Request(url, headers={
        "User-Agent": "VK-Shops-ReadOnlyVerifier/0.1",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=22) as reply:
            return json.load(reply)
    except urllib.error.HTTPError as e:
        return {"local_error": "HTTP_" + str(e.code)}
    except Exception as e:
        # Never stringify the exception: it might contain a URL with the secret.
        return {"local_error": type(e).__name__}

def error_description(code):
    return {
        5: "invalid or expired access token",
        6: "too many requests",
        10: "internal VK API error",
        15: "access denied to the post or method",
        27: "application authorization missing or method unsupported",
        29: "method rate limits exceeded",
        100: "invalid VK API parameters",
        113: "invalid user id",
    }.get(code, "VK API rejected the request")

def resolve_posts(data):
    resp = data.get("response")
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        if isinstance(resp.get("items"), list):
            return resp["items"]
        if isinstance(resp.get("posts"), list):
            return resp["posts"]
        if "id" in resp and "owner_id" in resp:
            return [resp]
    return []

def get_count(post, key):
    obj = post.get(key)
    if isinstance(obj, dict):
        value = obj.get("count")
        return value if isinstance(value, int) and not isinstance(value, bool) else None
    return None

def inspect_one(expected, token):
    post_id = f"{expected['owner']}_{expected['post']}"
    result = {
        "post_id": post_id,
        "public_url": "https://vk.ru/wall" + post_id,
        "ozon_sku": expected["sku"],
        "prior_human_observation": expected["prior_views"],
        "status": "UNVERIFIED",
        "views": None,
    }
    data = request("wall.getById", {"posts": post_id, "extended": 0}, token)
    if "local_error" in data:
        result.update(status="NETWORK_ERROR", detail=data["local_error"])
        return result
    if "error" in data:
        code = data["error"].get("error_code")
        result.update(status="API_ERROR", error_code=code, detail=error_description(code))
        return result
    items = resolve_posts(data)
    item = next((p for p in items if str(p.get("id")) == str(expected["post"])
                 and str(p.get("owner_id")) == str(expected["owner"])), None)
    if item is None:
        result.update(status="POST_NOT_RETURNED", items_count=len(items))
        return result
    timestamp = item.get("date")
    date = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc) if isinstance(timestamp, int) else None
    age_days = (dt.datetime.now(dt.timezone.utc) - date).days if date else None
    result.update(
        published_utc=date.isoformat() if date else None,
        age_days=age_days,
        views=get_count(item, "views"),
        reactions=get_count(item, "likes"),
        reposts=get_count(item, "reposts"),
        comments=get_count(item, "comments"),
        marked_as_ads=item.get("marked_as_ads", None),
        sku_present_in_api_payload=expected["sku"] in json.dumps(item, ensure_ascii=False),
    )
    if result["views"] is None:
        result["status"] = "POST_FOUND_NO_VIEWS"
    elif result["views"] <= 10000:
        result["status"] = "REJECT_UNDER_VIEWS_THRESHOLD"
    elif age_days is None or age_days < 0 or age_days > 21:
        result["status"] = "REJECT_DATE"
    else:
        result["status"] = "VIEWS_VERIFIED"
    return result

def load_candidates():
    with open("vk-shops-lab/candidates.csv", encoding="utf-8", newline="") as source:
        rows=list(csv.DictReader(source))
    selected=[]
    for row in rows[:50]:
        match=re.search(r"wall(-?\d+)_(\d+)",row.get("post_url",""))
        sku=row.get("ozon_sku","").strip()
        if match and sku:
            selected.append({"owner":int(match[1]),"post":int(match[2]),"sku":sku,"prior_views":"not checked"})
    return selected

def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    token = os.getenv("VK_SERVICE_TOKEN", "").strip()
    posts=load_candidates()
    report = {"checked_utc": now, "secret_provided": bool(token), "results": []}
    if not token:
        report["status"] = "SECRET_MISSING_IN_ACTIONS"
        report["results"] = [{"post_id": f"{p['owner']}_{p['post']}", "status": "UNVERIFIED"} for p in posts]
    else:
        report["results"] = [inspect_one(p, token) for p in posts]
        report["status"] = "TEST_COMPLETE"
    with open("vk-shops-api-report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    print("VK_SHOPS_API_REPORT_START")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("VK_SHOPS_API_REPORT_END")
    return 0 if token else 2

if __name__ == "__main__":
    sys.exit(main())
