# iOS Build and Distribution Status

## Current files
- `ios/GozIhale.xcodeproj`: native Xcode project is present.
- `ios/GozIhale/GozIhaleApp.swift`
- `ios/GozIhale/ContentView.swift`
- `.github/workflows/ios-build.yml`: simulator build workflow.

## Build path
- Build the simulator target with the repository's iOS CI workflow.
- The prototype uses HTTPS-only API configuration in Settings; an empty server address is intentionally not defaulted to localhost.
- Set the deployed API base URL (for example, `https://api.example.com`) after the server is deployed.

## Distribution
- The simulator build is not a signed device IPA.
- Device distribution requires Apple Developer signing credentials and TestFlight provisioning.
- Demo login remains a UI placeholder and is not real authentication.
