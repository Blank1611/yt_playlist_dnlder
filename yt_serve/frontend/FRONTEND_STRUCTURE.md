# Frontend Structure

## Overview

The frontend has been reorganized following React best practices for better maintainability and scalability.

## Directory Structure

```
frontend/
├── public/                     # Static assets (favicon, robots.txt)
│   └── README.md
│
├── src/
│   ├── assets/                 # Images, fonts, icons
│   │   └── README.md
│   │
│   ├── components/             # Reusable UI components
│   │   ├── common/            # Generic components (Button, Input, Modal)
│   │   ├── index.ts           # Export barrel
│   │   └── README.md
│   │
│   ├── features/               # Feature-specific modules
│   │   └── README.md          # (Auth, Dashboard, etc.)
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── index.ts
│   │   └── README.md
│   │
│   ├── context/                # React Context/Global State
│   │   ├── index.ts
│   │   └── README.md
│   │
│   ├── services/               # API calls and external services
│   │   ├── api.ts             # API client and endpoints
│   │   ├── types.ts           # TypeScript types
│   │   ├── index.ts           # Export barrel
│   │   └── README.md
│   │
│   ├── pages/                  # Route components
│   │   ├── index.ts
│   │   └── README.md
│   │
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
│
├── .env.example                # Environment variables template
├── package.json                # Dependencies
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── VITE_PATHS.md              # Path aliases setup guide
└── FRONTEND_STRUCTURE.md       # This file
```

## Design Principles

### 1. Separation of Concerns

Each directory has a specific purpose:
- **components/** - Presentational components
- **features/** - Business logic modules
- **services/** - External integrations
- **hooks/** - Reusable logic
- **context/** - Global state
- **pages/** - Route-level components

### 2. Colocation

Related files are kept together:
```
features/
└── auth/
    ├── components/
    ├── hooks/
    ├── services/
    └── index.ts
```

### 3. Clean Imports

Using barrel exports (index.ts files):
```typescript
// Instead of:
import { Button } from './components/common/Button'
import { Input } from './components/common/Input'

// Use:
import { Button, Input } from './components'
```

## File Organization

### Components

**Location:** `src/components/`

**Purpose:** Reusable UI components

**Structure:**
```
components/
├── common/              # Generic components
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Modal.tsx
├── SettingsModal.tsx    # Feature-specific components
├── ExclusionsModal.tsx
└── index.ts             # Export all
```

**Usage:**
```typescript
import { Button, Modal } from '@/components'
```

### Features

**Location:** `src/features/`

**Purpose:** Self-contained feature modules

**Structure:**
```
features/
├── auth/
│   ├── components/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── services/
│   │   └── authApi.ts
│   └── index.ts
└── dashboard/
    ├── components/
    ├── hooks/
    └── index.ts
```

**Usage:**
```typescript
import { LoginForm, useAuth } from '@/features/auth'
```

### Services

**Location:** `src/services/`

**Purpose:** API calls and external integrations

**Files:**
- `api.ts` - API client, endpoints (playlistsApi, jobsApi, configApi)
- `types.ts` - TypeScript interfaces for API responses
- `index.ts` - Export barrel

**Usage:**
```typescript
import { playlistsApi, type Playlist } from '@/services'
```

### Hooks

**Location:** `src/hooks/`

**Purpose:** Custom React hooks for reusable logic

**Examples:**
```typescript
// useLocalStorage.ts
export function useLocalStorage<T>(key: string, initialValue: T) {
  // ...
}

// useDebounce.ts
export function useDebounce<T>(value: T, delay: number) {
  // ...
}
```

**Usage:**
```typescript
import { useLocalStorage, useDebounce } from '@/hooks'
```

### Context

**Location:** `src/context/`

**Purpose:** React Context providers for global state

**Examples:**
```typescript
// ThemeContext.tsx
export const ThemeProvider = ({ children }) => {
  // ...
}

export const useTheme = () => useContext(ThemeContext)
```

**Usage:**
```typescript
import { ThemeProvider, useTheme } from '@/context'
```

### Pages

**Location:** `src/pages/`

**Purpose:** Top-level route components

**Structure:**
```
pages/
├── Home.tsx
├── Dashboard.tsx
├── Settings.tsx
└── index.ts
```

**Usage:**
```typescript
import { Home, Dashboard } from '@/pages'
```

## Path Aliases (Optional)

For cleaner imports, set up path aliases in `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

And in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Then import like:
```typescript
import { Button } from '@/components'
import { useAuth } from '@/hooks'
import { playlistsApi } from '@/services'
```

See `VITE_PATHS.md` for complete setup instructions.

## Migration Guide

### Current State

Files have been moved:
- ✅ `api.ts` → `services/api.ts`
- ✅ `types.ts` → `services/types.ts`
- ✅ Imports in `App.tsx` updated

### Next Steps

1. **Extract Components from App.tsx**

   Move modal components to separate files:
   ```
   App.tsx (800+ lines)
   ↓
   components/
   ├── InitialSetupModal.tsx
   ├── SettingsModal.tsx
   └── ExclusionsModal.tsx
   ```

2. **Create Custom Hooks**

   Extract reusable logic:
   ```typescript
   // hooks/useConfig.ts
   export function useConfig() {
     return useQuery({
       queryKey: ['config'],
       queryFn: async () => {
         const res = await configApi.get()
         return res.data
       },
     })
   }
   ```

3. **Add Context for Dark Mode**

   ```typescript
   // context/ThemeContext.tsx
   export const ThemeProvider = ({ children }) => {
     const [darkMode, setDarkMode] = useState(...)
     // ...
   }
   ```

4. **Create Page Components**

   If adding routing:
   ```
   pages/
   ├── Home.tsx          # Main playlist view
   ├── Settings.tsx      # Settings page
   └── Playlist.tsx      # Individual playlist view
   ```

## Benefits

### Maintainability
✅ **Clear structure** - Easy to find files  
✅ **Separation of concerns** - Each file has one purpose  
✅ **Scalable** - Easy to add new features  

### Developer Experience
✅ **Clean imports** - Using barrel exports  
✅ **Type safety** - TypeScript throughout  
✅ **Documentation** - README in each directory  

### Code Quality
✅ **Reusability** - Components and hooks are reusable  
✅ **Testability** - Isolated modules are easier to test  
✅ **Consistency** - Standard patterns throughout  

## Best Practices

### Component Organization

```typescript
// Good: Small, focused components
export function PlaylistCard({ playlist }: Props) {
  return (
    <div className="card">
      <PlaylistHeader title={playlist.title} />
      <PlaylistStats stats={playlist.stats} />
      <PlaylistActions playlist={playlist} />
    </div>
  )
}

// Avoid: Large, monolithic components
```

### Hook Usage

```typescript
// Good: Custom hooks for reusable logic
function usePlaylist(id: number) {
  const query = useQuery(['playlist', id], () => fetchPlaylist(id))
  const mutation = useMutation(updatePlaylist)
  
  return { playlist: query.data, update: mutation.mutate }
}

// Use in component:
function PlaylistView({ id }: Props) {
  const { playlist, update } = usePlaylist(id)
  // ...
}
```

### Service Layer

```typescript
// Good: Centralized API calls
export const playlistsApi = {
  list: () => api.get<Playlist[]>('/playlists'),
  get: (id: number) => api.get<Playlist>(`/playlists/${id}`),
  create: (url: string) => api.post<Playlist>('/playlists', { url }),
}

// Avoid: Scattered fetch calls throughout components
```

## Future Enhancements

Potential improvements:
- [ ] Extract modals into separate components
- [ ] Create custom hooks for API calls
- [ ] Add React Router for multi-page navigation
- [ ] Implement global state management (if needed)
- [ ] Add component library (shadcn/ui, etc.)
- [ ] Set up Storybook for component development
- [ ] Add unit tests for components and hooks

## Resources

- **[React Documentation](https://react.dev/)** - Official React docs
- **[Vite Documentation](https://vitejs.dev/)** - Vite build tool
- **[TypeScript Handbook](https://www.typescriptlang.org/docs/)** - TypeScript guide
- **[React Query](https://tanstack.com/query/latest)** - Data fetching library

## Questions?

See the README files in each directory for specific guidance:
- `src/components/README.md`
- `src/features/README.md`
- `src/hooks/README.md`
- `src/context/README.md`
- `src/services/README.md`
- `src/pages/README.md`

---

**Last Updated:** December 2024  
**Structure Version:** 2.0  
**Status:** ✅ Reorganized and ready for development
