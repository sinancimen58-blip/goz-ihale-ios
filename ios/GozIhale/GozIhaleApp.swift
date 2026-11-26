import SwiftUI

@main
struct GozIhaleApp: App {
    @AppStorage("gozihale_demo_session") private var demoSession = false

    var body: some Scene {
        WindowGroup {
            if demoSession {
                ContentView()
            } else {
                PrototypeLoginView {
                    demoSession = true
                }
            }
        }
    }
}

struct PrototypeLoginView: View {
    var onDemoLogin: () -> Void
    @State private var username = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "eye.circle.fill")
                .font(.system(size: 76))
                .foregroundStyle(.tint)
            VStack(spacing: 8) {
                Text("Gözİhale").font(.largeTitle.bold())
                Text("Oftalmoloji satın alma ve ihale takip")
                    .foregroundStyle(.secondary).multilineTextAlignment(.center)
            }
            VStack(spacing: 14) {
                TextField("Kullanıcı adı / e-posta", text: $username)
                    .textInputAutocapitalization(.never).autocorrectionDisabled()
                    .padding().background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 12))
                SecureField("Şifre", text: $password)
                    .padding().background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 12))
                Button(action: onDemoLogin) {
                    Text("Prototipi görüntüle")
                        .font(.headline).frame(maxWidth: .infinity).padding()
                }.buttonStyle(.borderedProminent)
            }
            Text("Bu ekran prototip amaçlıdır. Gerçek kullanıcı doğrulaması henüz bağlı değildir. Demo girişi sunucu hesabı oluşturmaz.")
                .font(.footnote).foregroundStyle(.secondary).multilineTextAlignment(.center)
            Spacer()
        }.padding(24)
    }
}
