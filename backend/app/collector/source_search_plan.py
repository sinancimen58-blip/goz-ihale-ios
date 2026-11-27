"""Source-specific ophthalmology notice discovery query plan."""
from .keywords import ALL_KEYWORDS

TERMS=[
"OCT", "OCT-A", "optik koherens tomografi", "fako", "fakoemülsifikasyon",
"fako cihazı", "fako sarf", "optik biyometri", "biyometri", "biometri", "kornea topografisi",
"topografi", "YAG lazer", "SLT lazer", "fundus kamera", "oftalmik mikroskop",
"yarık lamba", "biomikroskop", "pakimetri", "pachymetry", "biometri", "biyometri", "IOL", "göz içi lens", "intraocular lens", "tonometre", "görme alanı", "perimetre",
"refraktometre", "keratometre", "lensmetre", "mikroperimetri", "aberometre",
"oftalmik muayene ünitesi", "göz cihazı", "oftalmoloji", "oftalmik sarf",
"göz cerrahisi sarf", "göz hastalıkları cihaz", "glokom", "glaucoma", "RNFL", "ganglion cell analysis", "vitrektomi sarf", "retina cerrahisi sarf", "katarakt cerrahi sarf"
]
def build_source_query_plan():
    return [{"term":term,"source_targets":["EKAP","ilan.gov.tr","DMO","Resmî Gazete","KİK"],"verification":"original_notice_required"} for term in TERMS]
