## Standalone Packaging Rule
When the user asks to push changes to git, you MUST always rebuild the React frontend (`cd frontend && npm run build`) and copy the resulting `frontend/dist` folder to `standalone/dist` BEFORE committing and pushing.
