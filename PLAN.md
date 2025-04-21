# Firefly III Custom Reporting Frontend - Plan

This document outlines the plan for creating a custom web frontend for Firefly III reporting using Vue.js and Vuetify.

**Core Requirements:**

*   Specify Firefly III base URL and Personal Access Token (PAT).
*   Fetch masterdata (like Accounts, Categories, Tags, Budgets) on load.
*   Filter transactions based on masterdata and transaction properties (like date, description, amount).
*   Display filtered transactions as a list and aggregated charts.
*   Allow configuration of the aggregation property (default: Category).
*   Persist filter/aggregation settings in URL query parameters.

**Technology Stack:**

*   **Framework:** Vue.js 3
*   **UI Library:** Vuetify
*   **Charting:** Chart.js (via `vue-chartjs`)
*   **State Management:** Pinia
*   **API Client:** Axios
*   **Build Tool:** Vite (default with `create-vue`)

**Phase 1: Project Setup & Configuration**

1.  **Initialize Vue.js Project:**
    *   Use `npm create vue@latest`.
    *   Select options: TypeScript, Pinia, Vue Router.
2.  **Install Dependencies:**
    *   Vuetify: `npm install vuetify` + plugin setup.
    *   Chart.js: `npm install chart.js vue-chartjs`.
    *   Axios: `npm install axios`.
3.  **Basic Layout:**
    *   Set up `v-app`, `v-app-bar`, `v-main`. Consider `v-navigation-drawer` for filters.
4.  **Configuration Component:**
    *   Create a view/component for URL and PAT input (`v-text-field`).
    *   Store values in Pinia store (`configStore`). Basic validation.

**Phase 2: API Interaction & State Management**

1.  **API Service Module (`src/services/fireflyApi.ts`):**
    *   Axios instance configured with base URL and Authorization header from `configStore`.
    *   Functions to fetch: Accounts, Categories, Tags, Budgets, Transactions (with filter params).
    *   Error handling.
2.  **State Management (Pinia):**
    *   `configStore`: Manages URL, PAT.
    *   `masterDataStore`: Stores fetched Accounts, Categories, Tags, Budgets. Actions to fetch data.
    *   `transactionStore`: Manages filters, raw transactions, aggregation settings, aggregated results. Actions for fetching, filtering, and aggregating.

**Phase 3: Core Reporting Features**

1.  **Masterdata Loading:**
    *   Fetch masterdata via `masterDataStore` actions on app load/config confirmation.
    *   Loading indicators.
2.  **Filter UI Component (`FilterPanel.vue`):**
    *   Use `v-select` (multiple, chips) for Accounts, Categories, Tags, Budgets.
    *   `v-date-picker` (range) for dates.
    *   `v-text-field` for description.
    *   `v-range-slider` or number fields for amount.
    *   Bind inputs to `transactionStore` filter state.
3.  **Transaction Fetching & Filtering:**
    *   Trigger `transactionStore` action on filter change.
    *   Call API service with filters as query params.
    *   Store raw results in `transactionStore`.
4.  **Aggregation Logic:**
    *   Implement in `transactionStore` (getter or action).
    *   Group transactions by selected property (default: Category), sum amounts.
    *   Store aggregated results.
5.  **Display Components:**
    *   `TransactionList.vue`: `v-data-table` for raw filtered transactions.
    *   `ChartsDisplay.vue`: Use `vue-chartjs` (`Bar`, `Pie`) for aggregated data.
    *   Aggregation Selector: `v-select` bound to `transactionStore` aggregation setting.

**Phase 4: URL Integration & Refinements**

1.  **URL Query Parameter Handling (Vue Router):**
    *   On state change (filters, aggregation), update `route.query`.
    *   On load, read `route.query` to initialize `transactionStore`.
2.  **Error Handling & User Feedback:**
    *   API error handling (`v-snackbar`, `v-alert`).
    *   Loading states (`v-progress-linear`, `v-progress-circular`).
3.  **Styling & Responsiveness:**
    *   Use Vuetify grid system and utilities.

**Visualization: Component Structure / Data Flow**

```mermaid
graph LR
    subgraph Browser
        URL[URL Query Params]
    end

    subgraph Vue App
        Router --> App[App.vue / Layout]
        App --> ConfigView(Configuration View)
        App --> ReportView(Main Report View)

        subgraph ReportView
            FilterPanel(Filter Panel) --> StoreFilters(Transaction Store: Filters)
            AggregationSelector(Aggregation Selector) --> StoreAgg(Transaction Store: Aggregation Setting)
            Display --> TransactionList(Transaction List)
            Display --> ChartsDisplay(Charts Display)
        end

        subgraph State (Pinia Stores)
            ConfigStore(Config Store) -- URL/Token --> ApiService
            MasterDataStore(MasterData Store) -- Fetched Data --> FilterPanel
            TransactionStore(Transaction Store) -- Filters/Data --> Display
            StoreFilters -- Triggers Fetch --> ApiService
            StoreAgg -- Triggers Re-aggregation --> TransactionStore
        end

        subgraph Services
            ApiService(API Service: Axios) -- Requests --> FireflyAPI[Firefly III API]
        end

        URL -- Read --> Router
        StoreFilters -- Write --> Router -- Write --> URL
        ConfigView -- Writes --> ConfigStore
        FilterPanel -- Reads --> MasterDataStore
        Display -- Reads --> TransactionStore
        MasterDataStore -- Uses --> ApiService
        TransactionStore -- Uses --> ApiService
    end

    FireflyAPI -- Responses --> ApiService