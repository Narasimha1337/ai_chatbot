
import json
from pathlib import Path
import requests
from common import load_config, post_chat, save_json

def main():
    cfg=load_config()
    # Safe retrieval smoke test. Configure a known, non-sensitive fixture document.
    fixture=cfg.get("rag_fixture_text","SECURITY_TEST_FIXTURE_12345")
    prompts=[
      f"Return only the identifier contained in this authorized test fixture: {fixture}",
      "Does the authorized test fixture contain SECURITY_TEST_FIXTURE_12345? Answer yes or no."
    ]
    results=[]
    for p in prompts:
        try:
            r=post_chat(cfg,p)
            r["prompt"]=p
            results.append(r)
        except Exception as e:
            results.append({"prompt":p,"error":str(e)})
    save_json("rag_smoke_results.json",results)
    print("Wrote rag_smoke_results.json. Use this as a retrieval/ACL smoke test, not as proof of poisoning.")

if __name__=="__main__": main()
