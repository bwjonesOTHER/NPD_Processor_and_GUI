## Frontend Packaging Rule
When the user asks to push changes to git, you MUST always rebuild the React frontend (`cd frontend && npm run build`) BEFORE committing and pushing, so that the static bundle is up-to-date for the backend to serve.
