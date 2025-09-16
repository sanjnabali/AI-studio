# AI Studio Login Fix TODO

## Completed Tasks
- [x] Update Frontend/src/api/client.ts to use /api/auth/* paths for auth endpoints (login, register, logout, refresh)
- [x] Enable authentication feature flag in Backend/app/core/config.py (set FEATURES["authentication"] = True)
- [x] Update client.ts to use relative paths (empty baseURL) to leverage Vite proxy for CORS-free requests

## Pending Tasks
- [ ] Test login functionality after fixes
- [ ] Verify no other endpoint mismatches exist
- [ ] Ensure error handling displays backend validation errors properly

## Notes
- Frontend was calling /auth/login but backend expects /api/auth/login due to /api prefix in main.py
- Authentication feature flag was disabled, preventing auth endpoints from functioning
- CORS settings appear correct for frontend on localhost:3000
- Updated client.ts to use relative paths, now leveraging Vite proxy for /api/* requests
