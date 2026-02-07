# Local Development

## Without Docker
1. `npm install`
2. `cp .env.example .env.local`
3. Set `VITE_GEMINI_API_KEY` in `.env.local`
4. `npm run dev`

## With Docker
1. `cp .env.example .env`
2. Set `VITE_GEMINI_API_KEY`
3. `npm run container:up`
4. Open `http://localhost:8080`
5. Optional: `npm run container:logs` to inspect startup logs
