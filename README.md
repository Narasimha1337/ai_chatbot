# LLM Web Chatbot Pentest Assessment Pack

## Files
- `LLM_Web_Chatbot_Pentest_Test_Cases.xlsx` — 361 test cases, execution log, payload library, automation matrix and findings sheet.
- `config.json` — target/request configuration.
- `prompt_injection_checks.py` — safe prompt-injection test batch.
- `http_security_checks.py` — basic HTTP security/header checks.
- `authorization_idor_checks.py` — bounded object authorization checks for supplied test IDs.
- `rag_smoke_checks.py` — safe RAG retrieval smoke tests using a non-sensitive fixture.
- `bounded_load_check.py` — very small, rate-limited load sanity check.
- `common.py` — shared HTTP/config helpers.

## Setup
```bash
python -m pip install requests
```

Edit `config.json` with the authorized test target, test token and request schema.

## Run
```bash
python prompt_injection_checks.py
python http_security_checks.py
python authorization_idor_checks.py
python rag_smoke_checks.py
python bounded_load_check.py
```

## Important
The scripts intentionally do not automate destructive command execution, credential attacks, cloud metadata exploitation, unrestricted SSRF, high-volume DoS, or arbitrary file operations. Those tests should be performed only in an approved test environment with explicit authorization and safe test fixtures.

The scripts produce evidence candidates; a human tester must validate exploitability, authorization context, business impact and severity.


## Single-file CLI

The recommended entry point is now `llm_pentest.py`.

Install:
```bash
python -m pip install requests
```

### 1. URL + Bearer token
```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --chat-path /api/chat \
  --token "TEST_TOKEN" \
  --all
```

### 2. URL + cookie authentication
```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --chat-path /api/chat \
  --cookie "session=TEST_SESSION; tenant=TEST_TENANT" \
  --all
```

### 3. Multiple custom headers
```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --header "Authorization=Bearer TEST_TOKEN" \
  --header "X-Tenant-ID=TEST_TENANT" \
  --header "X-Client=security-test" \
  --all
```

### 4. Login endpoint -> authenticated session
Cookie-based:
```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --login-url https://authorized-target.example/api/login \
  --username security-test \
  --password "TEST_PASSWORD" \
  --chat-path /api/chat \
  --all
```

Token-based login:
```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --login-url https://authorized-target.example/api/login \
  --username security-test \
  --password "TEST_PASSWORD" \
  --login-token-json "data.access_token" \
  --chat-path /api/chat \
  --all
```

Custom login body:
```bash
--login-payload '{"email":"security-test@example.com","password":"TEST_PASSWORD"}'
```

### 5. Authorization / BOLA with two test identities
```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --object-path /api/conversations/{id} \
  --object-id TEST_CONVERSATION_ID \
  --token-a "TOKEN_FOR_USER_A" \
  --token-b "TOKEN_FOR_USER_B" \
  --idor
```

The intended test is: User A owns the object; User B attempts to access the same object. Use only accounts and objects explicitly authorized for the engagement.

### 6. Individual checks
```bash
python llm_pentest.py --url https://authorized-target.example --token "TOKEN" --health
python llm_pentest.py --url https://authorized-target.example --token "TOKEN" --prompt-injection
python llm_pentest.py --url https://authorized-target.example --unauthenticated
python llm_pentest.py --url https://authorized-target.example --token "TOKEN" --rate-limit
python llm_pentest.py --url https://authorized-target.example --tls
```

### 7. Non-standard chatbot JSON
If the application expects:
```json
{"prompt":"...","conversationId":"TEST123","model":"approved-test-model"}
```
pass:
```bash
--request-template '{"prompt":"{prompt}","conversationId":"TEST123","model":"approved-test-model"}'
```

The tool writes one JSON evidence file by default:
```text
llm_pentest_results.json
```

The CLI is deliberately bounded. It does not automate brute force, unrestricted SSRF, command execution, cloud metadata exploitation, destructive file operations, or high-volume denial-of-service.


## Burp-aware workflow (recommended)

Export the chatbot request from Burp as a raw request, for example `chat.txt`.
If authentication requires a separate login request, export that as `login.txt`.

### Reuse the captured authenticated chatbot request

```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --burp-chat-request chat.txt \
  --all
```

The runner parses the method, URL/path, headers and body from the Burp request. It replaces `{prompt}` or `{{PROMPT}}` in the body when running prompt tests.

### Login flow + chatbot flow

```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --burp-login-request login.txt \
  --burp-chat-request chat.txt \
  --all
```

The login request is executed first in a persistent Python session. Cookies returned by the login are retained and reused for subsequent chatbot requests.

If login returns a JSON token:

```bash
--login-token-json data.access_token
```

### Send all generated traffic through Burp

Default:
```bash
--burp-proxy http://127.0.0.1:8080
```

Disable it:
```bash
--no-burp-proxy
```

This lets you watch the automated test traffic in Burp Proxy/HTTP history.

### Custom application headers

```bash
--header "X-Tenant-ID=TESTTENANT" \
--header "X-Client=security-test"
```

### Run selected suites

```bash
--suite auth,prompt,headers
```

Available suites:
- `auth`
- `prompt`
- `headers`
- `idor`
- `rate`
- `tls`

### BOLA/IDOR with two identities

Use two explicitly authorized test accounts:

```bash
python llm_pentest.py \
  --url https://authorized-target.example \
  --burp-chat-request chat.txt \
  --object-path /api/conversations/{id} \
  --object-id TEST-ID \
  --token-a TOKEN_A \
  --token-b TOKEN_B \
  --suite idor
```

### Important Burp limitation

A raw exported Burp request can contain an already-issued token/cookie. Replaying it is not equivalent to reproducing the entire browser authentication lifecycle. If the application uses rotating tokens, MFA, dynamic CSRF tokens, OAuth redirects, signed requests, or anti-replay controls, the captured login flow must be adapted to that application's exact protocol.

Do not export real production credentials into the assessment package. Use dedicated test accounts and redact secrets before storing request files where practical.
