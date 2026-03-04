---
name: cs-artifacts
description: React artifact builder for creating complex web applications. This skill should be used when building elaborate frontend artifacts requiring React, TypeScript, Tailwind CSS, or shadcn/ui components. Provides initialization scripts for project setup and bundling to single HTML files for sharing as Claude artifacts.
---

# React Artifact Builder

Build production-quality React applications that bundle into single HTML files for sharing.

## Stack

- React 18 + TypeScript
- Vite (development)
- Tailwind CSS
- shadcn/ui components
- Parcel (bundling)

## Quick Start

### 1. Initialize Project

```bash
# Create new project
npm create vite@latest my-artifact -- --template react-ts
cd my-artifact

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Add shadcn/ui
npx shadcn-ui@latest init
```

### 2. Configure Tailwind

**tailwind.config.js:**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**src/index.css:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3. Develop

```bash
npm run dev
```

Build your React application with components, state management, and styling.

### 4. Bundle to Single HTML

```bash
# Install bundling tools
npm install -D parcel @parcel/config-default html-inline-external

# Build with Vite
npm run build

# Bundle to single file
npx parcel build dist/index.html --no-source-maps --dist-dir bundle
npx html-inline-external bundle/index.html > artifact.html
```

## Project Structure

```
my-artifact/
├── src/
│   ├── components/     # React components
│   ├── hooks/          # Custom hooks
│   ├── lib/            # Utilities
│   ├── App.tsx         # Main app
│   ├── main.tsx        # Entry point
│   └── index.css       # Styles
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Adding shadcn/ui Components

```bash
# Add specific components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
```

Usage:

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Dashboard</CardTitle>
      </CardHeader>
      <CardContent>
        <Button onClick={() => console.log('clicked')}>
          Click me
        </Button>
      </CardContent>
    </Card>
  )
}
```

## State Management

For complex artifacts, use React's built-in state:

```tsx
import { useState, useReducer, createContext, useContext } from 'react'

// Simple state
const [count, setCount] = useState(0)

// Complex state with reducer
const reducer = (state, action) => {
  switch (action.type) {
    case 'INCREMENT': return { ...state, count: state.count + 1 }
    case 'SET_DATA': return { ...state, data: action.payload }
    default: return state
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0, data: null })

// Global state with context
const AppContext = createContext(null)

function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}
```

## Routing (for multi-page artifacts)

```tsx
import { useState } from 'react'

type Page = 'home' | 'settings' | 'about'

function App() {
  const [page, setPage] = useState<Page>('home')

  const navigate = (to: Page) => setPage(to)

  return (
    <div>
      <nav>
        <button onClick={() => navigate('home')}>Home</button>
        <button onClick={() => navigate('settings')}>Settings</button>
      </nav>

      {page === 'home' && <HomePage />}
      {page === 'settings' && <SettingsPage />}
      {page === 'about' && <AboutPage />}
    </div>
  )
}
```

## Design Guidelines

**Avoid AI slop aesthetics:**
- Don't default to Inter font
- Avoid purple gradients on white
- Skip uniform centered layouts
- Use asymmetric, interesting compositions

**Good practices:**
- Distinctive font choices
- Bold color palettes
- Intentional whitespace
- Clear visual hierarchy
- Thoughtful animations

## Common Patterns

### Data fetching simulation

```tsx
const [data, setData] = useState(null)
const [loading, setLoading] = useState(true)

useEffect(() => {
  // Simulate API call
  setTimeout(() => {
    setData({ items: [...] })
    setLoading(false)
  }, 1000)
}, [])
```

### Form handling

```tsx
const [formData, setFormData] = useState({ name: '', email: '' })

const handleSubmit = (e) => {
  e.preventDefault()
  console.log('Submitted:', formData)
}

const handleChange = (e) => {
  setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
}
```

### Animation with Tailwind

```tsx
<div className="transition-all duration-300 hover:scale-105 hover:shadow-lg">
  Animated card
</div>
```

## Bundling Notes

The final `artifact.html` file:
- Contains all JavaScript inlined
- Contains all CSS inlined
- Works offline
- Can be shared directly in Claude conversations

## Dependencies Summary

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "parcel": "^2.12.0"
  }
}
```
