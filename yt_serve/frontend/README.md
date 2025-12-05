# YouTube Playlist Manager - Frontend

Modern React frontend for the YouTube Playlist Manager.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Frontend runs on: **http://localhost:5173**

**Note:** Make sure the backend is running on http://localhost:8000

## Features

✅ **Playlist Management**
- View all playlists with stats
- Add new playlists
- Delete playlists
- Refresh playlist stats

✅ **Download Operations**
- Download videos
- Extract audio
- Both (download + extract)
- Real-time progress tracking

✅ **Job Management**
- View running jobs
- Cancel jobs
- Progress bars
- Status indicators

✅ **Modern UI**
- Responsive design
- Tailwind CSS styling
- Real-time updates
- Loading states

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **TanStack Query** - Data fetching & caching
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Project Structure

```
src/
├── main.tsx          # Entry point
├── App.tsx           # Main app component
├── api.ts            # API client
├── types.ts          # TypeScript types
└── index.css         # Global styles
```

## API Integration

The frontend connects to the backend via proxy (configured in `vite.config.ts`):

- `/api/*` → `http://localhost:8000/api/*`
- `/ws/*` → `ws://localhost:8000/ws/*`

## Development

### Hot Reload

Changes to source files automatically reload the browser.

### Type Checking

```bash
npm run build
```

This runs TypeScript compiler and Vite build.

### Linting

```bash
npm run lint
```

## Building for Production

```bash
npm run build
```

Output in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Environment

No environment variables needed - API proxy is configured in Vite.

## Features Roadmap

Current implementation includes:
- ✅ Playlist CRUD
- ✅ Job management
- ✅ Real-time progress
- ✅ Responsive design

Future enhancements:
- [ ] Job logs viewer
- [ ] Exclusions editor
- [ ] Settings page
- [ ] Dark mode
- [ ] WebSocket live updates
- [ ] Search/filter playlists

## Troubleshooting

### Backend not connecting?

Make sure backend is running:
```bash
cd ../backend
python run.py
```

### Port 5173 in use?

Change port in `vite.config.ts`:
```ts
server: {
  port: 3000, // or any other port
}
```

### Dependencies not installing?

Try:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. ✅ Start backend: `cd ../backend && python run.py`
2. ✅ Install frontend: `npm install`
3. ✅ Start frontend: `npm run dev`
4. ✅ Open browser: http://localhost:5173

Enjoy your modern YouTube Playlist Manager! 🎵
