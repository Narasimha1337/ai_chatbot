
import argparse, json, time
from pathlib import Path
import requests
from common import load_config, save_json

SECURITY_HEADERS = [
"Content-Security-Policy","X-Content-Type-Options","Referrer-Policy",
"Permissions-Policy","Strict-Transport-Security","Cache-Control"
]

def main():
    cfg=load_config()
    base=cfg["base_url"].rstrip("/")
    url=base+cfg.get("health_path","/")
    r=requests.get(url,headers=cfg.get("headers",{}),timeout=cfg.get("timeout_seconds",20),
                   verify=cfg.get("verify_tls",True))
    result={
      "url":url,"status":r.status_code,
      "security_headers":{h:r.headers.get(h) for h in SECURITY_HEADERS},
      "server":r.headers.get("Server"),
      "content_type":r.headers.get("Content-Type"),
      "content_length":len(r.content)
    }
    save_json("http_security_results.json",result)
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
