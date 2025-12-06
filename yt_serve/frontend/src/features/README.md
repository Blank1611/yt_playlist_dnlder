# Features

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
