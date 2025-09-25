# Frontend & Backend Fixes: Resolve Auth Errors, Repeated Calls, and Warnings

## Current Work
Addressing post-registration/login issues: 400 Bad Request (duplicate register attempts), repeated /api/auth/me calls (7+ times causing noise/performance issues and potential error popups), passlib/bcrypt version warning, and generic "API Error" popup. Root causes: Frontend auth store eager fetching + no dedup logic; backend bcrypt incompatibility.

## Key Technical Concepts
- Pinia store (auth.ts): Reactive state for user/token; prevent redundant API calls with loaded flag.
- Backend deps (requirements.txt): Version pinning for bcrypt to fix passlib handler warning.
- FastAPI auth endpoints: Validate duplicates (400 correct); no changes needed.
- Axios client: Handles token refresh; calls are fine, but over-triggered by store.

## Relevant Files and Code
- Backend/requirements.txt:
  - Current: passlib[bcrypt]==1.7.4 (traps bcrypt version error).
  - Change: Add bcrypt==4.0.1 (compatible, has __about__).
- Frontend/src/store/auth.ts:
  - Current: getCurrentUser() called eagerly at end (runs on import); fetchUser() called multiple times (initializeAuth, router guard, etc.).
  - Changes: Add userLoaded ref; skip fetch if loaded; set loaded=true post login/register; remove eager call.
  - Important: In login/register: After apiClient call success, set userLoaded=true to prevent re-fetch.

## Problem Solving
- Repeated me calls: Store init + app.vue init + router guard → dedup with flag.
- 400 register: User retry (same email); frontend loading disables submit, but not issue.
- Bcrypt warning: Version mismatch; pin to 4.0.1.
- API popup: From authStore.error on failed fetches; reduced calls fix.

## Pending Tasks and Next Steps
1. **Update Backend/requirements.txt**:
   - Add `bcrypt==4.0.1` line.
   - "From the most recent conversation: Pin bcrypt to resolve passlib warning."

2. **Install updated requirements**:
   - Run `cd Backend && pip install -r requirements.txt` to update bcrypt.
   - Restart backend: Kill current uvicorn, rerun `cd Backend; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

3. **Update Frontend/src/store/auth.ts**:
   - Add `const userLoaded = ref(false)`
   - Remove `getCurrentUser()` call at end.
   - In fetchUser: `if (userLoaded.value) return;`
   - In login/register: After `user.value = response.user`, add `userLoaded.value = true`
   - In initializeAuth: `if (!userLoaded.value) await fetchUser()`
   - Expose userLoaded in return (for router guard if needed).
   - "From the most recent conversation: Prevent redundant user fetches with userLoaded flag."

4. **Test fixes**:
   - Clear localStorage, reload /auth.
   - Register new user (different email) → expect single register (201) + single me (200) → redirect to / (Studio dashboard, no errors/warnings/repeats).
   - Login → single me call.
   - Check console/backend logs: No passlib warning, clean auth flow, no popup.
   - Use browser_action: Launch http://localhost:5173 → verify /auth renders, register works smoothly.

5. **Verify backend restart**:
   - Confirm no more bcrypt warnings in terminal.
   - Health check: /api/health 200.
