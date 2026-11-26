# iOS Build Bootstrap

The repository's SwiftUI source is not yet packaged as an Xcode project. This document records the next build-enablement work.

## Current files
- `ios/GozIhale/GozIhaleApp.swift`
- `ios/GozIhale/ContentView.swift`

## Build path
- Create a native Xcode project (`.xcodeproj`) referencing these source files.
- Set deployment target conservatively and test on a simulator.
- Add a macOS GitHub Actions runner workflow using Xcode build and simulator tests.
- Before device distribution: configure signing and TestFlight with the developer account owner.

## Important
No signed IPA or installation build is available yet. Do not treat the prototype/demo login as real authentication. The demo gate is solely a UI placeholder.
