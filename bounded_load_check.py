
import time, json
from common import load_config, post_chat, save_json

def main():
    cfg=load_config()
    n=min(int(cfg.get("safe_load_requests",5)),10)
    delay=max(60.0/max(int(cfg.get("max_requests_per_minute",20)),1),0.5)
    prompt="Return the word SECURITY-TEST and nothing else."
    results=[]
    for i in range(n):
        try:
            r=post_chat(cfg,prompt)
            results.append({"sequence":i+1,**r})
        except Exception as e:
            results.append({"sequence":i+1,"error":str(e)})
        if i<n-1: time.sleep(delay)
    save_json("bounded_load_results.json",results)
    print("Completed bounded load check. Increase limits only under explicit written authorization and a controlled test window.")

if __name__=="__main__": main()
