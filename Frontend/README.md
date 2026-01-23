# Family App Frontend

Nuxt 3 (Vue 3) Frontend for the Family Application.

## 📋 Prerequisites
- Node.js 20+
- NPM

## 🚀 Setup

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

## 🧩 Key Libraries
- **Nuxt 3**: meta-framework.
- **Pinia**: State management (persisted state plugin used).
- **Tailwind CSS**: Styling.
- **D3.js**: Family tree visualization.

## ⚠️ Known Issues
- **Peer Dependencies**: Always use `npm install --legacy-peer-deps` when adding new packages or updating.
