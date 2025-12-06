"""
Reorganize frontend structure according to best practices
"""
import shutil
from pathlib import Path

def reorganize_frontend():
    print("="*60)
    print("Reorganizing Frontend Structure")
    print("="*60)
    print()
    
    # Get the frontend directory
    frontend = Path(__file__).parent.resolve()
    src = frontend / "src"
    
    print(f"Working directory: {frontend}")
    print()
    
    # Create new directory structure
    directories = [
        "src/components",
        "src/components/common",
        "src/features",
        "src/hooks",
        "src/context",
        "src/services",
        "src/pages",
        "src/assets",
        "public",
    ]
    
    print("Creating directory structure...")
    for dir_path in directories:
        full_path = frontend / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}/")
    
    print()
    print("Moving files to new structure...")
    
    # Move api.ts to services/
    api_src = src / "api.ts"
    api_dest = src / "services" / "api.ts"
    if api_src.exists() and not api_dest.exists():
        shutil.move(str(api_src), str(api_dest))
        print(f"  ✓ api.ts -> services/api.ts")
    
    # Move types.ts to services/ (since it's API-related)
    types_src = src / "types.ts"
    types_dest = src / "services" / "types.ts"
    if types_src.exists() and not types_dest.exists():
        shutil.move(str(types_src), str(types_dest))
        print(f"  ✓ types.ts -> services/types.ts")
    
    # App.tsx stays in src/ (it's the main component)
    # main.tsx stays in src/ (it's the entry point)
    # index.css stays in src/ (global styles)
    
    print()
    print("Creating index files for better imports...")
    
    # Create services/index.ts for clean imports
    services_index = src / "services" / "index.ts"
    if not services_index.exists():
        services_index.write_text("""// Export all services for clean imports
export * from './api'
export * from './types'
""", encoding='utf-8')
        print("  ✓ services/index.ts")
    
    # Create components/index.ts
    components_index = src / "components" / "index.ts"
    if not components_index.exists():
        components_index.write_text("""// Export all components for clean imports
// Example: export { Button } from './common/Button'
""", encoding='utf-8')
        print("  ✓ components/index.ts")
    
    # Create hooks/index.ts
    hooks_index = src / "hooks" / "index.ts"
    if not hooks_index.exists():
        hooks_index.write_text("""// Export all custom hooks
// Example: export { useAuth } from './useAuth'
""", encoding='utf-8')
        print("  ✓ hooks/index.ts")
    
    # Create context/index.ts
    context_index = src / "context" / "index.ts"
    if not context_index.exists():
        context_index.write_text("""// Export all context providers
// Example: export { AuthProvider, useAuth } from './AuthContext'
""", encoding='utf-8')
        print("  ✓ context/index.ts")
    
    # Create pages/index.ts
    pages_index = src / "pages" / "index.ts"
    if not pages_index.exists():
        pages_index.write_text("""// Export all page components
// Example: export { Home } from './Home'
""", encoding='utf-8')
        print("  ✓ pages/index.ts")
    
    # Create README files for each directory
    print()
    print("Creating README files...")
    
    readmes = {
        "src/components/README.md": """# Components

Reusable UI components.

## Structure

- `common/` - Generic reusable components (Button, Input, Modal, etc.)
- Feature-specific components can be in their own folders

## Usage

```tsx
import { Button } from '@/components'
```
""",
        "src/features/README.md": """# Features

Feature-specific modules with their own components, hooks, and logic.

## Structure

Each feature should be self-contained:

```
features/
├── auth/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   └── index.ts
└── dashboard/
    ├── components/
    ├── hooks/
    └── index.ts
```

## Usage

```tsx
import { LoginForm } from '@/features/auth'
```
""",
        "src/hooks/README.md": """# Custom Hooks

Reusable React hooks.

## Examples

- `useAuth.ts` - Authentication hook
- `useApi.ts` - API call hook
- `useLocalStorage.ts` - Local storage hook

## Usage

```tsx
import { useAuth } from '@/hooks'
```
""",
        "src/context/README.md": """# Context

React Context providers for global state.

## Examples

- `AuthContext.tsx` - Authentication state
- `ThemeContext.tsx` - Theme state
- `ConfigContext.tsx` - App configuration

## Usage

```tsx
import { AuthProvider, useAuth } from '@/context'
```
""",
        "src/services/README.md": """# Services

API calls and external service integrations.

## Files

- `api.ts` - API client and endpoints
- `types.ts` - TypeScript types for API

## Usage

```tsx
import { playlistsApi, jobsApi } from '@/services'
```
""",
        "src/pages/README.md": """# Pages

Top-level route components.

## Structure

Each page represents a route in the application.

## Usage

```tsx
import { Home, Dashboard } from '@/pages'
```
""",
        "src/assets/README.md": """# Assets

Static assets like images, fonts, and icons.

## Structure

```
assets/
├── images/
├── fonts/
└── icons/
```
""",
        "public/README.md": """# Public

Static files served directly (favicon, robots.txt, etc.)

These files are copied as-is to the build output.
"""
    }
    
    for path, content in readmes.items():
        readme_path = frontend / path
        if not readme_path.exists():
            readme_path.write_text(content, encoding='utf-8')
            print(f"  ✓ {path}")
    
    # Create .env.example
    print()
    print("Creating configuration files...")
    env_example = frontend / ".env.example"
    if not env_example.exists():
        env_example.write_text("""# Frontend Environment Variables

# API Base URL
VITE_API_URL=http://localhost:8000

# Other configuration
# VITE_FEATURE_FLAG=true
""", encoding='utf-8')
        print("  ✓ .env.example")
    
    # Create vite path aliases config note
    vite_note = frontend / "VITE_PATHS.md"
    if not vite_note.exists():
        vite_note.write_text("""# Vite Path Aliases

To use clean imports like `@/components`, add this to `vite.config.ts`:

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
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

And update `tsconfig.json`:

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

Then you can import like:

```typescript
import { Button } from '@/components'
import { useAuth } from '@/hooks'
import { playlistsApi } from '@/services'
```
""", encoding='utf-8')
        print("  ✓ VITE_PATHS.md")
    
    print()
    print("="*60)
    print("Frontend Reorganization Complete!")
    print("="*60)
    print()
    print("New Structure:")
    print("  frontend/")
    print("    ├── public/              # Static assets")
    print("    ├── src/")
    print("    │   ├── assets/          # Images, fonts")
    print("    │   ├── components/      # Reusable UI components")
    print("    │   │   └── common/      # Generic components")
    print("    │   ├── features/        # Feature modules")
    print("    │   ├── hooks/           # Custom hooks")
    print("    │   ├── context/         # React Context")
    print("    │   ├── services/        # API calls")
    print("    │   │   ├── api.ts       # (moved)")
    print("    │   │   └── types.ts     # (moved)")
    print("    │   ├── pages/           # Route components")
    print("    │   ├── App.tsx          # Main component")
    print("    │   ├── main.tsx         # Entry point")
    print("    │   └── index.css        # Global styles")
    print("    ├── .env.example         # Environment template")
    print("    ├── package.json")
    print("    └── vite.config.ts")
    print()
    print("Next Steps:")
    print("  1. Update imports in App.tsx:")
    print("     - import { api } from './services/api'")
    print("     - import type { Playlist } from './services/types'")
    print()
    print("  2. (Optional) Set up path aliases in vite.config.ts")
    print("     See VITE_PATHS.md for instructions")
    print()
    print("  3. Extract components from App.tsx into components/")
    print("     - SettingsModal -> components/SettingsModal.tsx")
    print("     - ExclusionsModal -> components/ExclusionsModal.tsx")
    print("     - InitialSetupModal -> components/InitialSetupModal.tsx")
    print()

if __name__ == '__main__':
    reorganize_frontend()
