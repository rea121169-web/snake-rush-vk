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
    elif result["views"] <= 50000:
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


# VK SHOPS V5: fresh public source posts above 50,000 views; price checked separately on Ozon.
import time

USED_SKUS = {
    "2438903294", "3210776803", "3843402249", "1956626965",
    "1613218722", "851843173", "3093383856", "1196752643",
    "2834734941", "3858982397",
    "1875254493", "1404253192", "2864668123", "3521161250",
    "2195916581", "1926742046", "2317789406", "5827491783",
}

def public_ozon_links(item):
    found = {}
    def visit(value):
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str):
            decoded = urllib.parse.unquote(value)
            for raw in re.findall(r'https?://(?:www\.)?ozon\.ru/product/[^\s<>"\\]+', decoded):
                path = urllib.parse.urlsplit(raw).path.rstrip("/")
                match = re.search(r"(?:/|-)(\d{6,14})$", path)
                if match:
                    sku = match.group(1)
                    found[sku] = "https://ozon.ru/product/" + sku
    visit(item)
    return found

def describe_public_post(item, group_name, checked):
    owner = item.get("owner_id", item.get("from_id"))
    post_id = item.get("id")
    timestamp = item.get("date")
    if not all(isinstance(x, int) for x in (owner, post_id, timestamp)):
        return None
    published = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc)
    elapsed = checked - published
    views = get_count(item, "views")
    if not isinstance(views, int) or views <= 50000 or not dt.timedelta(0) <= elapsed <= dt.timedelta(days=21):
        return None
    if item.get("marked_as_ads") != 1:
        return None
    links = public_ozon_links(item)
    if not links or all(sku in USED_SKUS for sku in links):
        return None
    return {
        "post_id": f"{owner}_{post_id}",
        "owner_id": owner, "source_group": group_name,
        "public_url": f"https://vk.ru/wall{owner}_{post_id}",
        "published_utc": published.isoformat(),
        "views": views,
        "reactions": get_count(item, "likes"),
        "reposts": get_count(item, "reposts"),
        "comments": get_count(item, "comments"),
        "marked_as_ads": 1,
        "ozon_products": [
            {"ozon_sku": sku, "ozon_url": url}
            for sku, url in links.items() if sku not in USED_SKUS
        ],
        "source_text": item.get("text", ""),
        "checked_utc": checked.isoformat(),
    }

def discover_public_posts(token):
    checked = dt.datetime.now(dt.timezone.utc)
    with open("vk-shops-lab/candidates.csv", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    owners = []
    for row in rows:
        match = re.search(r"wall(-?\d+)_(\d+)", row.get("post_url", ""))
        if match and int(match.group(1)) not in owners:
            owners.append(int(match.group(1)))
    discovered = []
    checks = []
    # These are only the already-observed public communities in our candidate register.
    for owner in owners[:18]:
        data = request("wall.get", {"owner_id": owner, "count": 100, "filter": "owner", "extended": 1}, token)
        time.sleep(0.4)
        if "local_error" in data:
            checks.append({"owner_id": owner, "status": "NETWORK_ERROR", "detail": data["local_error"]})
            continue
        if "error" in data:
            code = data["error"].get("error_code")
            checks.append({"owner_id": owner, "status": "API_ERROR", "error_code": code, "detail": error_description(code)})
            continue
        response = data.get("response", {})
        names = {group.get("id"): group.get("name") for group in response.get("groups", [])}
        group_name = names.get(abs(owner))
        items = resolve_posts(data)
        accepted = []
        for item in items:
            candidate = describe_public_post(item, group_name, checked)
            if candidate is not None:
                accepted.append(candidate)
        discovered.extend(accepted)
        checks.append({"owner_id": owner, "source_group": group_name, "status": "CHECKED",
                       "posts_returned": len(items), "accepted_new_product_posts": len(accepted)})
    # Explicit post references from the register are also checked, including previously blank SKU rows.
    for row in rows:
        match = re.search(r"wall(-?\d+)_(\d+)", row.get("post_url", ""))
        if not match:
            continue
        pid = f"{match.group(1)}_{match.group(2)}"
        data = request("wall.getById", {"posts": pid, "extended": 1}, token)
        time.sleep(0.4)
        if "error" in data or "local_error" in data:
            continue
        response = data.get("response", {})
        names = {group.get("id"): group.get("name") for group in response.get("groups", [])} if isinstance(response, dict) else {}
        for item in resolve_posts(data):
            if str(item.get("id")) != match.group(2) or str(item.get("owner_id")) != match.group(1):
                continue
            candidate = describe_public_post(item, names.get(abs(int(match.group(1)))), checked)
            if candidate is not None:
                discovered.append(candidate)
    unique = {item["post_id"]: item for item in discovered}
    return {"checked_utc": checked.isoformat(), "communities": checks, "posts": list(unique.values())}


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
        report["discovery"] = discover_public_posts(token)
    with open("vk-shops-api-report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    print("VK_SHOPS_API_REPORT_START")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("VK_SHOPS_API_REPORT_END")
    return 0 if token else 2

if __name__ == "__main__":
    sys.exit(main())
