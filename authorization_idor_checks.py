
import json, argparse
from pathlib import Path
import requests
from common import load_config, save_json

def main():
    cfg=load_config()
    ids=cfg.get("object_ids",[])
    if not ids:
        print("Add only authorized test object IDs to config.json; two test identities are recommended.")
        return
    base=cfg["base_url"].rstrip("/")
    results=[]
    for oid in ids:
        # Configure the endpoint pattern for the application under test.
        path=cfg.get("object_path_template","/api/conversations/{id}").replace("{id}",str(oid))
        url=base+path
        try:
            r=requests.get(url,headers=cfg.get("headers",{}),timeout=cfg.get("timeout_seconds",20),
                           verify=cfg.get("verify_tls",True))
            results.append({"object_id":oid,"url":url,"status":r.status_code,
                            "body_preview":r.text[:4000]})
        except Exception as e:
            results.append({"object_id":oid,"error":str(e)})
    save_json("idor_results.json",results)
    print("Wrote idor_results.json. Compare results across authorized identities; HTTP 200 alone is not proof of BOLA.")

if __name__=="__main__": main()
