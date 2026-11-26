import SwiftUI

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
}

@MainActor
final class TenderViewModel: ObservableObject {
    @Published var tenders: [Tender] = []
    @Published var loading = false
    @Published var errorMessage: String?
    @Published var serverURL: String = UserDefaults.standard.string(forKey: "gozihale_server") ?? "http://127.0.0.1:8000"

    func load() async {
        guard let base = URL(string: serverURL.trimmingCharacters(in: .whitespacesAndNewlines)) else {
            errorMessage = "Sunucu adresi geçersiz."; return
        }
        loading = true; errorMessage = nil
        defer { loading = false }
        do {
            var url = base
            url.append(path: "api/tenders")
            let (data, response) = try await URLSession.shared.data(from: url)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw URLError(.badServerResponse) }
            tenders = try JSONDecoder().decode([Tender].self, from: data)
        } catch {
            errorMessage = "Sunucuya bağlanılamadı. Adresi ve sunucunun çalıştığını kontrol edin."
        }
    }

    func saveServer() {
        UserDefaults.standard.set(serverURL, forKey: "gozihale_server")
    }
}

struct ContentView: View {
    @StateObject private var model = TenderViewModel()
    @State private var searchText = ""
    @State private var selectedTab = 0

    private var filtered: [Tender] {
        guard !searchText.isEmpty else { return model.tenders }
        return model.tenders.filter {
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
                            metricCard(title: "İlan", value: "(model.tenders.count)", symbol: "doc.text")
                            metricCard(title: "Kategori", value: "(Set(model.tenders.map{$0.category}).count)", symbol: "square.grid.2x2")
                            metricCard(title: "Durum", value: model.errorMessage == nil ? "Bağlı" : "Çevrimdışı", symbol: "antenna.radiowaves.left.and.right")
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
                .toolbar { ToolbarItem(placement: .topBarTrailing) { Button { Task { await model.load() } } label: { Image(systemName: "arrow.clockwise") } } }
                .task { await model.load() }
            }.tabItem { Label("Ana Sayfa", systemImage: "house") }.tag(0)

            NavigationStack {
                List(Array(Set(model.tenders.map{$0.category})).sorted(), id: \.self) { category in
                    Label(category, systemImage: "eye").badge(model.tenders.filter{$0.category == category}.count)
                }.navigationTitle("Kategoriler")
            }.tabItem { Label("Kategoriler", systemImage: "square.grid.2x2") }.tag(1)

            NavigationStack {
                ContentUnavailableView("Takip Listem", systemImage: "bookmark", description: Text("Favori ilan özelliği sonraki aşamada eklenecek."))
                    .navigationTitle("Takip")
            }.tabItem { Label("Takip", systemImage: "bookmark") }.tag(2)

            NavigationStack {
                Form {
                    Section("API bağlantısı") {
                        TextField("Sunucu URL", text: $model.serverURL)
                            .textInputAutocapitalization(.never).autocorrectionDisabled()
                        Text("Örnek: http://192.168.1.20:8000").font(.footnote).foregroundStyle(.secondary)
                        Button("Adresi kaydet ve bağlan") { model.saveServer(); Task { await model.load() } }
                        Button("Bağlantıyı test et") { Task { await model.load() } }
                    }
                    Section("Durum") {
                        Text("Bu uygulama şu anda API prototipine bağlanabilir. Sunucunun internet üzerinden erişilebilir olması gerekir.")
                    }
                }.navigationTitle("Ayarlar")
            }.tabItem { Label("Ayarlar", systemImage: "gearshape") }.tag(3)
        }
    }

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
                Spacer(); Text(tender.status).font(.caption).foregroundStyle(.secondary)
            }
            Text(tender.title).font(.headline)
            Text(tender.institution).font(.subheadline)
            Text("\(tender.city ?? "Şehir belirtilmemiş") • \(tender.deadline ?? "Son tarih belirtilmemiş")").font(.caption).foregroundStyle(.secondary)
            if let summary = tender.summary, !summary.isEmpty { Text(summary).font(.footnote).lineLimit(3) }
            if let source = tender.source_url, let url = URL(string: source) {
                Link("İlan kaynağı", destination: url).font(.footnote)
            }
        }.frame(maxWidth: .infinity, alignment: .leading).padding()
            .background(.background).overlay(RoundedRectangle(cornerRadius: 16).stroke(.quaternary)).clipShape(RoundedRectangle(cornerRadius: 16))
    }
}
