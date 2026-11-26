import SwiftUI

struct Tender: Identifiable {
    let id = UUID()
    let title: String
    let institution: String
    let city: String
    let category: String
    let deadline: String
    let status: String
}

struct ContentView: View {
    @State private var searchText = ""
    @State private var selectedTab = 0

    private let samples = [
        Tender(title: "OCT cihazı alımı", institution: "Örnek Üniversite Hastanesi", city: "Ankara", category: "OCT", deadline: "İhale tarihi takip edilecek", status: "Yeni"),
        Tender(title: "Fako cihazı ve sarf malzemeleri", institution: "Örnek Şehir Hastanesi", city: "İstanbul", category: "Fako", deadline: "İhale tarihi takip edilecek", status: "Takip"),
        Tender(title: "Optik biyometri cihazı", institution: "Örnek Devlet Hastanesi", city: "İzmir", category: "Biyometri", deadline: "İhale tarihi takip edilecek", status: "Yeni")
    ]

    private var filtered: [Tender] {
        guard !searchText.isEmpty else { return samples }
        return samples.filter { item in
            item.title.localizedCaseInsensitiveContains(searchText) ||
            item.institution.localizedCaseInsensitiveContains(searchText) ||
            item.category.localizedCaseInsensitiveContains(searchText) ||
            item.city.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        dashboardHeader
                        HStack(spacing: 12) {
                            metricCard(title: "Yeni İlan", value: "0", symbol: "bell.badge")
                            metricCard(title: "Takip", value: "0", symbol: "bookmark")
                            metricCard(title: "Yaklaşan", value: "0", symbol: "calendar")
                        }
                        Text("Örnek ekran — henüz canlı ilan verisi bağlı değil.")
                            .font(.footnote).foregroundStyle(.secondary)
                        ForEach(filtered) { tender in
                            tenderCard(tender)
                        }
                    }.padding()
                }
                .navigationTitle("Gözİhale")
                .searchable(text: $searchText, prompt: "Cihaz, hastane veya şehir")
            }.tabItem { Label("Ana Sayfa", systemImage: "house") }.tag(0)

            NavigationStack {
                List {
                    ForEach(["OCT / OCT-A", "Fako cihazı", "Fako sarf", "Optik biyometri", "Topografi", "YAG / SLT", "Fundus kamera", "Göz mikroskobu", "Tonometre", "Görme alanı", "Refraktometre", "Lensmetre", "Mikroperimetri", "Diğer"], id: \.self) { category in
                        Label(category, systemImage: "eye")
                    }
                }.navigationTitle("Kategoriler")
            }.tabItem { Label("Kategoriler", systemImage: "square.grid.2x2") }.tag(1)

            NavigationStack {
                ContentUnavailableView("Kaydedilen ilanlar", systemImage: "bookmark", description: Text("Favori ilanlarınız burada görünecek."))
                    .navigationTitle("Takip Listem")
            }.tabItem { Label("Takip", systemImage: "bookmark") }.tag(2)

            NavigationStack {
                ContentUnavailableView("Ayarlar", systemImage: "gearshape", description: Text("Bildirim ve filtre ayarları burada yer alacak."))
                    .navigationTitle("Ayarlar")
            }.tabItem { Label("Ayarlar", systemImage: "gearshape") }.tag(3)
        }
    }

    private var dashboardHeader: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Gözİhale").font(.largeTitle.bold())
            Text("Türkiye göz sağlığı satın alma fırsatları").foregroundStyle(.secondary)
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
            HStack { Text(tender.category).font(.caption.bold()).padding(6).background(.blue.opacity(0.12)).clipShape(Capsule()); Spacer(); Text(tender.status).font(.caption).foregroundStyle(.secondary) }
            Text(tender.title).font(.headline)
            Text(tender.institution).font(.subheadline)
            Text("\(tender.city) • \(tender.deadline)").font(.caption).foregroundStyle(.secondary)
        }.frame(maxWidth: .infinity, alignment: .leading).padding()
            .background(.background).overlay(RoundedRectangle(cornerRadius: 16).stroke(.quaternary)).clipShape(RoundedRectangle(cornerRadius: 16))
    }
}
