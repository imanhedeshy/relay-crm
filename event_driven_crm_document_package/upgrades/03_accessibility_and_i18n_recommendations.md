# Accessibility and Internationalization Recommendations

## Accessibility Baseline Already Present
- semantic labels on the demo-user selector and lead form
- visible focus states on buttons, inputs, and selects
- keyboard-accessible navigation and submission flow
- explicit loading, error, and empty states
- text labels on status chips so state is not communicated by color alone
- read-only permission messaging instead of silently disabling the product

## Async UI Accessibility Status
Because the product demonstrates eventual consistency, the current UI already includes:
- clear text states such as `PENDING`, `COMPLETED`, and `FAILED`
- `role="status"` and `role="alert"` usage for loading and error areas
- workflow explanations that tell the reviewer what will update automatically

## Best Next Accessibility Upgrades
- add dedicated `aria-live` messaging for lead status transitions after polling refreshes
- run a screen-reader pass against the full dashboard
- test zoom, reduced-motion, and higher-contrast modes

## Internationalization Status
- timestamps are formatted consistently through shared helpers
- workflow data is stored in UTC-compatible timestamps from the backend

## Best Next Internationalization Upgrades
- move user-facing strings into a translatable dictionary
- avoid hard-coded `en-US` formatting once locale switching matters
- add timezone-aware rendering for users outside the demo defaults
