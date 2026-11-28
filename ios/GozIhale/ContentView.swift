import SwiftUI

struct APIHealth: Codable {
    let status: String
    let live_collection_configured: Bool
    let sources_with_runs: Int
    let latest_scan: LatestScan?
}

struct LatestScan: Codable {
    let source_key: String?
    let status: String?
    let finished_at: String?
}

struct Tender: Identifiable, Codable {
    let id: String
    let title: String
    let institution: String
    let city: String?
    let category: String
    let deadline: String?
    let source_name: String
    let source_url: String?
    let summary: String?
    let status: String
    let days_remaining: Int?
    let urgency: String?
    let procurement_method: String?
    let payment_terms: String?
}

@MainActor
final class TenderViewModel: ObservableObject {
    @Published var tenders: [Tender] = []
    @Published var loading = false
    @Published var errorMessage: String?
    @Published var connectionStatus: String?
    @Published var connectionTesting = false
    @Published var serverURL: String = UserDefaults.standard.string(forKey: "gozihale_server") ?? ""
    @Published var favorites: Set<String> = Set(UserDefaults.standard.stringArray(forKey: "gozihale_favorites") ?? [])

    func load(query: String? = nil, category: String? = nil) async {
        let trimmedServerURL = serverURL.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedServerURL.isEmpty else {
            errorMessage = "Önce Ayarlar bölümünden HTTPS API adresini girin."
            return
        }
        guard let base = URL(string: trimmedServerURL),
              base.scheme?.lowercased() == "https",
              base.host != nil,
              base.user == nil,
              base.password == nil,
              base.query == nil,
              base.fragment == nil else {
            errorMessage = "Geçerli, kullanıcı bilgisi içermeyen HTTPS sunucu adresi girin."
            return
        }
        loading = true; errorMessage = nil
        defer { loading = false }
        do {
            var components = URLComponents(url: base.appending(path: "api/priority-notices"), resolvingAgainstBaseURL: false)
            var items: [URLQueryItem] = []
            if let query, !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                items.append(URLQueryItem(name: "q", value: query))
            }
            if let category, !category.isEmpty {
                items.append(URLQueryItem(name: "category", value: category))
            }
            components?.queryItems = items.isEmpty ? nil : items
            guard let url = components?.url else { throw URLError(.badURL) }
            let (data, response) = try await URLSession.shared.data(from: url)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw URLError(.badServerResponse) }
            tenders = try JSONDecoder().decode([Tender].self, from: data)
        } catch {
            errorMessage = "HTTPS API erişilemedi veya yanıt biçimi uyumsuz. Sunucu adresini ve API durumunu kontrol edin."
        }
    }
    func testConnection() async {
        let trimmedServerURL = serverURL.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedServerURL.isEmpty else {
            connectionStatus = "Önce HTTPS API adresini girin."
            return
        }
        guard let base = URL(string: trimmedServerURL),
              base.scheme?.lowercased() == "https",
              base.host != nil,
              base.user == nil,
              base.password == nil,
              base.query == nil,
              base.fragment == nil else {
            connectionStatus = "Geçerli, kullanıcı bilgisi içermeyen HTTPS adresi gerekli."
            return
        }
        connectionTesting = true
        connectionStatus = nil
        defer { connectionTesting = false }
        do {
            let url = base.appending(path: "api/health")
            let (data, response) = try await URLSession.shared.data(from: url)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            let health = try JSONDecoder().decode(APIHealth.self, from: data)
            guard health.status == "ok" else { throw URLError(.cannotParseResponse) }
            var message = "API ve SQLite sağlık kontrolü başarılı."
            message += health.live_collection_configured ? " Canlı kaynak yapılandırması mevcut." : " Canlı kaynak yapılandırması bulunmuyor."
            if let latest = health.latest_scan, let status = latest.status {
                message += " Son tarama: \(status)."
            }
            connectionStatus = message
            await load(query: nil, category: nil)
        } catch {
            connectionStatus = "HTTPS API sağlık kontrolü başarısız. Sunucu adresini ve API durumunu kontrol edin."
        }
    }

    func saveServer() { UserDefaults.standard.set(serverURL, forKey: "gozihale_server") }
    func toggleFavorite(_ id: String) {
        if favorites.contains(id) { favorites.remove(id) } else { favorites.insert(id) }
        UserDefaults.standard.set(Array(favorites), forKey: "gozihale_favorites")
    }
}

struct ContentView: View {
    @StateObject private var model = TenderViewModel()
    @State private var searchText = ""
    @State private var selectedTab = 0
    @State private var selectedCategory: String? = nil
    @State private var selectedTender: Tender?

    private var filtered: [Tender] {
        let base = selectedTab == 2 ? model.tenders.filter { model.favorites.contains($0.id) } : model.tenders
        let categoryFiltered = selectedCategory == nil ? base : base.filter { $0.category == selectedCategory }
        guard !searchText.isEmpty else { return categoryFiltered }
        return categoryFiltered.filter {
            $0.title.localizedCaseInsensitiveContains(searchText) ||
            $0.institution.localizedCaseInsensitiveContains(searchText) ||
            $0.category.localizedCaseInsensitiveContains(searchText) ||
            ($0.city ?? "").localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        VStack(alignment: .leading, spacing: 5) {
                            Text("Gözİhale").font(.largeTitle.bold())
                            Text("Türkiye göz sağlığı satın alma fırsatları").foregroundStyle(.secondary)
                        }
                        HStack(spacing: 12) {
                            metricCard(title: "İlan", value: "\(model.tenders.count)", symbol: "doc.text")
                            metricCard(title: "Kategori", value: "\(Set(model.tenders.map{$0.category}).count)", symbol: "square.grid.2x2")
                            metricCard(title: "Takip", value: "\(model.favorites.count)", symbol: "bookmark")
                        }
                        if let message = model.errorMessage {
                            Label(message, systemImage: "wifi.exclamationmark").font(.footnote).foregroundStyle(.orange)
                                .padding().frame(maxWidth: .infinity, alignment: .leading).background(.orange.opacity(0.1)).clipShape(RoundedRectangle(cornerRadius: 12))
                        }
                        if model.loading { ProgressView("İlanlar yükleniyor…").frame(maxWidth: .infinity).padding() }
                        if filtered.isEmpty && !model.loading {
                            ContentUnavailableView("İlan bulunamadı", systemImage: "doc.text.magnifyingglass", description: Text("Sunucuda ilan bulunmuyor veya bağlantı kurulamadı."))
                        }
                        ForEach(filtered) { tender in tenderCard(tender) }
                    }.padding()
                }
                .navigationTitle("Ana Sayfa")
                .searchable(text: $searchText, prompt: "Cihaz, hastane veya şehir")
                .toolbar { ToolbarItem(placement: .topBarTrailing) { Button { Task { await model.load(query: searchText, category: selectedCategory) } } label: { Image(systemName: "arrow.clockwise") } } }
                .task(id: searchText + "|" + (selectedCategory ?? "")) {
                    try? await Task.sleep(nanoseconds: 350_000_000)
                    guard !Task.isCancelled else { return }
                    await model.load(query: searchText, category: selectedCategory)
                }
            }.tabItem { Label("Ana Sayfa", systemImage: "house") }.tag(0)

            NavigationStack {
                List {
                    Button("Tüm kategoriler") { selectedCategory = nil; selectedTab = 0 }
                    ForEach(Array(Set(model.tenders.map{$0.category})).sorted(), id: \.self) { category in
                        Button { selectedCategory = category; selectedTab = 0 } label: { Label(category, systemImage: "eye").badge(model.tenders.filter{$0.category == category}.count) }
                    }
                }.navigationTitle("Kategoriler")
            }.tabItem { Label("Kategoriler", systemImage: "square.grid.2x2") }.tag(1)

            NavigationStack {
                List {
                    if filtered.isEmpty {
                        ContentUnavailableView("Takip listesi boş", systemImage: "bookmark", description: Text("İlan kartındaki yer imi simgesine dokunarak takip ekleyin."))
                    } else {
                        ForEach(filtered) { tender in tenderCard(tender) }
                    }
                }.navigationTitle("Takip Listem")
            }.tabItem { Label("Takip", systemImage: "bookmark") }.tag(2)

            NavigationStack {
                Form {
                    Section("API bağlantısı") {
                        TextField("Sunucu URL", text: $model.serverURL)
                            .textInputAutocapitalization(.never).autocorrectionDisabled()
                        Text("Örnek: https://api.ornek.com — HTTP adresleri kabul edilmez.").font(.footnote).foregroundStyle(.secondary)
                        Button("Adresi kaydet ve bağlan") { model.saveServer(); Task { await model.testConnection() } }
                        Button("Bağlantıyı test et") { Task { await model.testConnection() } }
                    }
                    Section("Durum") {
                        if model.connectionTesting {
                            ProgressView("API sağlık kontrolü…")
                        }
                        if let status = model.connectionStatus {
                            Text(status).font(.footnote)
                        }
                        if let error = model.errorMessage {
                            Text(error).font(.footnote).foregroundStyle(.orange)
                        }
                        Text("Bağlantı testi /api/health uç noktasını ve SQLite durumunu kontrol eder.")
                            .font(.footnote).foregroundStyle(.secondary)
                    }
                    Section("Prototip oturumu") {
                        Button("Demo oturumundan çıkış yap", role: .destructive) { UserDefaults.standard.set(false, forKey: "gozihale_demo_session") }
                        Text("Demo oturumu gerçek kullanıcı doğrulaması değildir.").font(.footnote).foregroundStyle(.secondary)
                    }
                }.navigationTitle("Ayarlar")
            }.tabItem { Label("Ayarlar", systemImage: "gearshape") }.tag(3)
        }
        .sheet(item: $selectedTender) { tender in TenderDetailView(tender: tender) }
    }


    private func infoBadge(_ title: String, _ value: String, icon: String) -> some View { VStack(alignment: .leading, spacing: 4) { Label(title, systemImage: icon).font(.caption.bold()).foregroundStyle(.secondary); Text(value).font(.caption).lineLimit(3) }.frame(maxWidth: .infinity, alignment: .leading).padding(8).background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 10)) }

    private func metricCard(title: String, value: String, symbol: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: symbol).font(.title2)
            Text(value).font(.title.bold())
            Text(title).font(.caption).foregroundStyle(.secondary)
        }.frame(maxWidth: .infinity, alignment: .leading).padding()
            .background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 16))
    }

    private func tenderCard(_ tender: Tender) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(tender.category).font(.caption.bold()).padding(6).background(.blue.opacity(0.12)).clipShape(Capsule())
                Spacer()
                Button { model.toggleFavorite(tender.id) } label: {
                    Image(systemName: model.favorites.contains(tender.id) ? "bookmark.fill" : "bookmark")
                }.buttonStyle(.plain).accessibilityLabel("Takip durumunu değiştir")
                Text(tender.status).font(.caption).foregroundStyle(.secondary)
            }
            Button { selectedTender = tender } label: { VStack(alignment: .leading, spacing: 4) { Text(tender.title).font(.headline).foregroundStyle(.primary); Text(tender.institution).font(.subheadline).foregroundStyle(.primary) }.frame(maxWidth: .infinity, alignment: .leading) }.buttonStyle(.plain)
            Text("\(tender.city ?? "Şehir belirtilmemiş") • \(tender.deadline ?? "Son tarih belirtilmemiş")").font(.caption).foregroundStyle(.secondary)
            if let urgency = tender.urgency { Label(urgency, systemImage: "clock").font(.caption.bold()).foregroundStyle(urgency.contains("Kritik") || urgency.contains("Acil") || urgency == "Bugün" ? .orange : .secondary) }
            HStack(alignment: .top, spacing: 8) { infoBadge("İhale yöntemi", tender.procurement_method ?? "Belirtilmemiş", icon: "scale"); infoBadge("Ödeme süresi", tender.payment_terms ?? "Belirtilmemiş", icon: "creditcard") }
            if let summary = tender.summary, !summary.isEmpty { Text(summary).font(.footnote).lineLimit(3) }
            if let source = tender.source_url, let url = URL(string: source) {
                Link("İlan kaynağı", destination: url).font(.footnote)
            }
        }.frame(maxWidth: .infinity, alignment: .leading).padding()
            .background(.background).overlay(RoundedRectangle(cornerRadius: 16).stroke(.quaternary)).clipShape(RoundedRectangle(cornerRadius: 16))
    }
}


struct TenderDetailView: View {
 let tender: Tender
 var body: some View {
  NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 14) {
   Text(tender.category).font(.caption.bold()).padding(7).background(.blue.opacity(0.12)).clipShape(Capsule())
   Text(tender.title).font(.title2.bold())
   row("Kurum", tender.institution); row("Şehir", tender.city ?? "Belirtilmemiş"); row("Son tarih", tender.deadline ?? "Belirtilmemiş"); row("İhale yöntemi", tender.procurement_method ?? "İlan metninde tespit edilemedi"); row("Ödeme süresi", tender.payment_terms ?? "İlan metninde tespit edilemedi"); row("Kaynak", tender.source_name); row("Durum", tender.status)
   if let summary=tender.summary, !summary.isEmpty { Text("İlan özeti").font(.headline); Text(summary) }
   if let s=tender.source_url, let u=URL(string:s) { Link(destination:u) { Label("Kaynak sayfasını aç",systemImage:"arrow.up.right.square").frame(maxWidth:.infinity).padding().background(.blue.opacity(0.12)).clipShape(RoundedRectangle(cornerRadius:12)) } }
  }.padding() }.navigationTitle("İlan Detayı").navigationBarTitleDisplayMode(.inline) }
 }
 private func row(_ title:String,_ value:String)->some View { VStack(alignment:.leading,spacing:3) { Text(title).font(.caption).foregroundStyle(.secondary); Text(value) }.frame(maxWidth:.infinity,alignment:.leading).padding(.vertical,3) }
}
