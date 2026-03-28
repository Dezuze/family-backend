# Family App Frontend

Nuxt 3 (Vue 3) Frontend for the Family Application.

## Prerequisites
- Node.js 20+
- NPM

## Setup

1.  **Install Dependencies**
    **Important**: Use `--legacy-peer-deps` due to Pinia plugin compatibility.
    ```bash
    npm install --legacy-peer-deps
    ```

2.  **Run Development Server**
    ```bash
    npm run dev
    ```
    The app will be available at http://localhost:3000.

## 📦 Build for Production

1.  **Build**
    ```bash
    npm run build
    ```
    Output will be in `.output/`.

2.  **Preview**
    ```bash
    npm run preview
    ```

## Key Libraries
- **Nuxt 3**: meta-framework.
- **Pinia**: State management (persisted state plugin used).
- **Tailwind CSS**: Styling.
- **D3.js**: Family tree visualization.

## Core UX Features

### Family Tree Editor
- Route: `/familytree`
- Dual mode add-relative flow:
    - **Create New**: create and link a new member profile.
    - **Link Existing**: search existing members and link them.
- Editor enforces backend constraints in UI warnings:
    - spouse uniqueness,
    - father/mother uniqueness,
    - max two parents.

### i18n Architecture
- Uses native Nuxt i18n (`@nuxtjs/i18n`) with lazy locale files.
- Locale files:
    - `i18n/locales/en.json`
    - `i18n/locales/ml.json`
- Strategy is configured to `no_prefix` and language choice is persisted via app composable.

### Motion And Interaction Style
- Interfaces use transition-rich interactions for:
    - panel open/close,
    - dropdowns,
    - mode switches,
    - status messages,
    - button and card hover states.
- Maintain consistent spacing/radius/focus states across editor and page controls.

## ⚠️ Known Issues
- **Peer Dependencies**: Always use `npm install --legacy-peer-deps` when adding new packages or updating.
