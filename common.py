
import json, time, csv, argparse, re
from pathlib import Path
import requests

def load_config(path="config.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def render_request(template, prompt):
    if isinstance(template, dict):
        return {k: render_request(v, prompt) for k,v in template.items()}
    if isinstance(template, list):
        return [render_request(v, prompt) for v in template]
    if isinstance(template, str):
        return template.replace("{prompt}", prompt)
    return template

def post_chat(cfg, prompt):
    url = cfg["base_url"].rstrip("/") + cfg["chat_path"]
    headers = dict(cfg.get("headers", {}))
    payload = render_request(cfg.get("request_template", {"message":"{prompt}"}), prompt)
    t0=time.time()
    r=requests.request(cfg.get("method","POST").upper(), url, headers=headers,
                        json=payload, timeout=cfg.get("timeout_seconds",20),
                        verify=cfg.get("verify_tls",True))
    return {
        "url": url, "status": r.status_code, "elapsed_ms": round((time.time()-t0)*1000,2),
        "headers": dict(r.headers), "body": r.text[:20000]
    }

def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
