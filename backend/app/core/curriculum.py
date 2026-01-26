"""
LK20 Kompetansemål for Matematikk
Komplett datastruktur fra 1. klasse til VG3

Struktur:
- Hvert klassetrinn har hovedområder
- Hvert hovedområde har kompetansemål
- Hvert kompetansemål har metadata for agent-beslutninger
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Klassetrinn(str, Enum):
    """Alle klassetrinn i norsk skole."""
    TRINN_1 = "1"
    TRINN_2 = "2"
    TRINN_3 = "3"
    TRINN_4 = "4"
    TRINN_5 = "5"
    TRINN_6 = "6"
    TRINN_7 = "7"
    TRINN_8 = "8"
    TRINN_9 = "9"
    TRINN_10 = "10"
    VG1_1T = "1t"
    VG1_1P = "1p"
    VG2_2P = "2p"
    VG2_R1 = "r1"
    VG2_S1 = "s1"
    VG3_R2 = "r2"
    VG3_S2 = "s2"


class Aldersnivaa(str, Enum):
    """Pedagogisk aldersnivå for agent-valg."""
    BARNESKOLE_SMAA = "barneskole_små"      # 1.-4. trinn
    BARNESKOLE_STORE = "barneskole_store"   # 5.-7. trinn
    UNGDOMSSKOLE = "ungdomsskole"           # 8.-10. trinn
    VGS_GRUNNLEGGENDE = "vgs_grunnleggende" # 1T, 1P, 2P
    VGS_AVANSERT = "vgs_avansert"           # R1, R2, S1, S2


class Hovedomraade(str, Enum):
    """Hovedområder i matematikk."""
    TALL_OG_TALLFORSTAELSE = "tall_og_tallforståelse"
    ALGEBRA = "algebra"
    FUNKSJONER = "funksjoner"
    GEOMETRI = "geometri"
    MAALING = "måling"
    STATISTIKK = "statistikk"
    SANNSYNLIGHET = "sannsynlighet"
    KOMBINATORIKK = "kombinatorikk"
    OKONOMI = "økonomi"
    MODELLERING = "modellering"
    DERIVASJON = "derivasjon"
    INTEGRASJON = "integrasjon"
    VEKTORER = "vektorer"
    DIFFERENSIALLIKNINGER = "differensiallikninger"


class Figurbehov(str, Enum):
    """Typisk figurbehov for kompetansemålet."""
    INGEN = "ingen"
    ENKEL = "enkel"           # Tallinje, enkel tabell - Typst klarer
    MIDDELS = "middels"       # Koordinatsystem, enkle grafer
    KOMPLEKS = "kompleks"     # TikZ/pgfplots påkrevd


class Abstraksjonsnivaa(str, Enum):
    """Grad av abstraksjon i oppgavene."""
    KONKRET = "konkret"       # Fysiske objekter, konkreter
    SEMI_ABSTRAKT = "semi"    # Bilder, representasjoner
    ABSTRAKT = "abstrakt"     # Symboler, variabler


class Ferdighetstype(str, Enum):
    """Type matematisk ferdighet."""
    PROSEDYRE = "prosedyre"           # Regneteknikk
    BEGREPSFORSTAELSE = "begrep"      # Forstå konsepter
    PROBLEMLOSNING = "problem"         # Anvende i nye situasjoner
    RESONNERING = "resonnering"       # Argumentere, bevise
    MODELLERING = "modellering"       # Oversette virkelighet til matematikk
    KOMMUNIKASJON = "kommunikasjon"   # Forklare, presentere


class Kompetansemaal(BaseModel):
    """Et enkelt kompetansemål med metadata."""
    id: str                                    # Unik ID, f.eks. "MAT01-04_tall_01"
    tekst: str                                 # Kompetansemålteksten fra LK20
    klassetrinn: Klassetrinn
    hovedomraade: Hovedomraade
    
    # Metadata for agent-beslutninger
    figurbehov: Figurbehov = Figurbehov.INGEN
    abstraksjonsnivaa: Abstraksjonsnivaa = Abstraksjonsnivaa.KONKRET
    typiske_ferdigheter: list[Ferdighetstype] = []
    
    # Pedagogiske hint til agentene
    typiske_figurer: list[str] = []           # F.eks. ["tallinje", "tieramme"]
    tallomraade: Optional[str] = None         # F.eks. "1-20", "negative tall"
    forutsetninger: list[str] = []            # ID-er til forutgående mål
    nøkkelord: list[str] = []                 # For søk og matching


# =============================================================================
# BARNESKOLE 1.-4. TRINN
# =============================================================================

TRINN_1_MAAL = [
    Kompetansemaal(
        id="MAT01-04_tall_01",
        tekst="Telle til 100, dele opp og bygge mengder opp til 10, sette sammen og dele opp tiergrupper",
        klassetrinn=Klassetrinn.TRINN_1,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["tieramme", "tellebrikker", "fingre"],
        tallomraade="1-100",
        nøkkelord=["telle", "mengde", "tiergruppe", "tall"]
    ),
    Kompetansemaal(
        id="MAT01-04_tall_02",
        tekst="Utforske og bruke tallenes egenskaper, rekkefølge, posisjonssystem og bruke ulike representasjoner",
        klassetrinn=Klassetrinn.TRINN_1,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["hundretabell", "tallinje", "base10_blokker"],
        tallomraade="1-100",
        nøkkelord=["posisjonssystem", "tiergruppe", "enere", "tiere"]
    ),
    Kompetansemaal(
        id="MAT01-04_regning_01",
        tekst="Utforske og løse addisjon og subtraksjon i praktiske situasjoner og bruke ulike strategier",
        klassetrinn=Klassetrinn.TRINN_1,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["tallinje", "tieramme", "tellebrikker"],
        tallomraade="1-20",
        nøkkelord=["addisjon", "subtraksjon", "pluss", "minus", "legge til", "trekke fra"]
    ),
    Kompetansemaal(
        id="MAT01-04_monster_01",
        tekst="Kjenne igjen og beskrive repeterende mønster og lage egne mønster",
        klassetrinn=Klassetrinn.TRINN_1,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.KOMMUNIKASJON],
        typiske_figurer=["mønsterrekke", "farger", "former"],
        nøkkelord=["mønster", "gjenta", "rekkefølge"]
    ),
    Kompetansemaal(
        id="MAT01-04_geo_01",
        tekst="Kjenne igjen og beskrive trekant, sirkel, kvadrat og rektangel, og sortere og sette ord på egenskaper",
        klassetrinn=Klassetrinn.TRINN_1,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["trekant", "sirkel", "kvadrat", "rektangel"],
        nøkkelord=["form", "figur", "side", "hjørne"]
    ),
    Kompetansemaal(
        id="MAT01-04_maaling_01",
        tekst="Bruke ikke-standardiserte måleenheter til å måle lengde og sammenligne størrelser",
        klassetrinn=Klassetrinn.TRINN_1,
        hovedomraade=Hovedomraade.MAALING,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=[],
        nøkkelord=["måle", "lengde", "kort", "lang", "sammenligne"]
    ),
]

TRINN_2_MAAL = [
    Kompetansemaal(
        id="MAT02_tall_01",
        tekst="Telle, dele opp og bygge mengder opp til 100 og utforske partall og oddetall",
        klassetrinn=Klassetrinn.TRINN_2,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["hundretabell", "base10_blokker"],
        tallomraade="1-100",
        forutsetninger=["MAT01-04_tall_01"],
        nøkkelord=["partall", "oddetall", "mengde", "telle"]
    ),
    Kompetansemaal(
        id="MAT02_regning_01",
        tekst="Automatisere tallfakta i addisjon og subtraksjon med tierovergang",
        klassetrinn=Klassetrinn.TRINN_2,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=["tallinje", "tieramme"],
        tallomraade="1-100",
        forutsetninger=["MAT01-04_regning_01"],
        nøkkelord=["tierovergang", "addisjon", "subtraksjon", "hoderegning"]
    ),
    Kompetansemaal(
        id="MAT02_mult_01",
        tekst="Utforske multiplikasjon som gjentatt addisjon og dele opp i like grupper",
        klassetrinn=Klassetrinn.TRINN_2,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["rutenett", "grupperinger"],
        tallomraade="gangetabell 1-5",
        nøkkelord=["multiplikasjon", "gange", "grupper", "gjentatt addisjon"]
    ),
    Kompetansemaal(
        id="MAT02_maaling_01",
        tekst="Måle lengde med meter og centimeter og sammenligne størrelser",
        klassetrinn=Klassetrinn.TRINN_2,
        hovedomraade=Hovedomraade.MAALING,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=["linjal_illustrasjon"],
        nøkkelord=["meter", "centimeter", "lengde", "måle"]
    ),
]

TRINN_3_MAAL = [
    Kompetansemaal(
        id="MAT03_tall_01",
        tekst="Forstå og bruke posisjonssystemet for tall opp til 1000",
        klassetrinn=Klassetrinn.TRINN_3,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["base10_blokker", "posisjonstabeller"],
        tallomraade="1-1000",
        forutsetninger=["MAT02_tall_01"],
        nøkkelord=["posisjonssystem", "enere", "tiere", "hundrere"]
    ),
    Kompetansemaal(
        id="MAT03_mult_01",
        tekst="Automatisere multiplikasjonstabellene 1-10 og bruke dem i hoderegning og oppstilling",
        klassetrinn=Klassetrinn.TRINN_3,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=["gangetabell", "rutenett"],
        tallomraade="gangetabell 1-10",
        forutsetninger=["MAT02_mult_01"],
        nøkkelord=["gangetabell", "multiplikasjon", "hoderegning"]
    ),
    Kompetansemaal(
        id="MAT03_div_01",
        tekst="Utforske og bruke divisjon som deling og måling",
        klassetrinn=Klassetrinn.TRINN_3,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["grupperinger", "deling_illustrasjon"],
        tallomraade="divisjon innenfor gangetabellen",
        nøkkelord=["divisjon", "dele", "fordele", "måling"]
    ),
    Kompetansemaal(
        id="MAT03_brok_01",
        tekst="Utforske, beskrive og sammenligne enkle brøker som del av mengde og del av hel",
        klassetrinn=Klassetrinn.TRINN_3,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["brøksirkel", "brøkrektangel", "mengde_deling"],
        tallomraade="enkle brøker: 1/2, 1/3, 1/4",
        nøkkelord=["brøk", "halvpart", "tredel", "firedel", "del av"]
    ),
]

TRINN_4_MAAL = [
    Kompetansemaal(
        id="MAT04_tall_01",
        tekst="Forstå og bruke posisjonssystemet for tall opp til 10 000 og utforske negative tall",
        klassetrinn=Klassetrinn.TRINN_4,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["tallinje_med_negative", "termometer"],
        tallomraade="negative tall til 10 000",
        forutsetninger=["MAT03_tall_01"],
        nøkkelord=["negative tall", "posisjonssystem", "store tall"]
    ),
    Kompetansemaal(
        id="MAT04_regning_01",
        tekst="Bruke regnestrategier og standardalgoritmer for addisjon, subtraksjon, multiplikasjon og divisjon",
        klassetrinn=Klassetrinn.TRINN_4,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=["oppstilling"],
        tallomraade="flersifrede tall",
        forutsetninger=["MAT03_mult_01", "MAT03_div_01"],
        nøkkelord=["algoritme", "oppstilling", "hoderegning", "strategi"]
    ),
    Kompetansemaal(
        id="MAT04_brok_01",
        tekst="Utvide og forkorte brøker, og utforske sammenhengen mellom brøk og desimaltall",
        klassetrinn=Klassetrinn.TRINN_4,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.PROSEDYRE],
        typiske_figurer=["brøksirkel", "tallinje_med_brok"],
        tallomraade="brøker og desimaltall",
        forutsetninger=["MAT03_brok_01"],
        nøkkelord=["brøk", "desimaltall", "utvide", "forkorte"]
    ),
    Kompetansemaal(
        id="MAT04_geo_01",
        tekst="Utforske, beskrive og argumentere for egenskaper ved to- og tredimensjonale figurer",
        klassetrinn=Klassetrinn.TRINN_4,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["polygoner", "terning", "sylinder", "kjegle"],
        nøkkelord=["trekant", "firkant", "terning", "kule", "hjørne", "kant", "flate"]
    ),
]

# =============================================================================
# MELLOMTRINN 5.-7. TRINN
# =============================================================================

TRINN_5_MAAL = [
    Kompetansemaal(
        id="MAT05_tall_01",
        tekst="Bruke posisjonssystemet til å beskrive og sammenligne desimaltall",
        klassetrinn=Klassetrinn.TRINN_5,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["tallinje_desimal", "posisjonstabeller"],
        tallomraade="desimaltall with flere desimaler",
        forutsetninger=["MAT04_tall_01"],
        nøkkelord=["desimaltall", "tideler", "hundredeler", "sammenligne"]
    ),
    Kompetansemaal(
        id="MAT05_brok_01",
        tekst="Addere og subtrahere brøker med ulik nevner og blandet tall",
        klassetrinn=Klassetrinn.TRINN_5,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["brøkillustrasjon"],
        tallomraade="brøker med ulik nevner",
        forutsetninger=["MAT04_brok_01"],
        nøkkelord=["brøk", "fellesnevner", "addisjon", "subtraksjon", "blandet tall"]
    ),
    Kompetansemaal(
        id="MAT05_prosent_01",
        tekst="Utforske sammenhengen mellom brøk, desimaltall og prosent og bruke dette i praktiske situasjoner",
        klassetrinn=Klassetrinn.TRINN_5,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["prosent_sirkel", "hundrerrutenett"],
        tallomraade="prosent, brøk, desimaltall",
        nøkkelord=["prosent", "brøk", "desimaltall", "omregning"]
    ),
    Kompetansemaal(
        id="MAT05_algebra_01",
        tekst="Bruke variabler og formler til å uttrykke sammenhenger og regne med enkle bokstavuttrykk",
        klassetrinn=Klassetrinn.TRINN_5,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.PROSEDYRE],
        typiske_figurer=[],
        nøkkelord=["variabel", "formel", "bokstavuttrykk", "ukjent"]
    ),
    Kompetansemaal(
        id="MAT05_geo_01",
        tekst="Beregne omkrets og areal av rektangler og trekanter",
        klassetrinn=Klassetrinn.TRINN_5,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["rektangel_med_mål", "trekant_med_mål", "rutenett_areal"],
        nøkkelord=["omkrets", "areal", "rektangel", "trekant", "formel"]
    ),
    Kompetansemaal(
        id="MAT05_stat_01",
        tekst="Samle inn, sortere og representere data i tabeller og diagrammer, og vurdere hva som egner seg",
        klassetrinn=Klassetrinn.TRINN_5,
        hovedomraade=Hovedomraade.STATISTIKK,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.KOMMUNIKASJON],
        typiske_figurer=["søylediagram", "linjediagram", "kakediagram"],
        nøkkelord=["data", "tabell", "diagram", "søyle", "statistikk"]
    ),
]

TRINN_6_MAAL = [
    Kompetansemaal(
        id="MAT06_brok_01",
        tekst="Multiplisere og dividere brøker og desimaltall",
        klassetrinn=Klassetrinn.TRINN_6,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=["brøkillustrasjon_multiplikasjon"],
        tallomraade="brøker og desimaltall",
        forutsetninger=["MAT05_brok_01"],
        nøkkelord=["brøk", "desimaltall", "multiplikasjon", "divisjon"]
    ),
    Kompetansemaal(
        id="MAT06_forhold_01",
        tekst="Utforske og beskrive forhold og proporsjonalitet",
        klassetrinn=Klassetrinn.TRINN_6,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["forholdstabell"],
        nøkkelord=["forhold", "proporsjonalitet", "forholdstall"]
    ),
    Kompetansemaal(
        id="MAT06_geo_01",
        tekst="Utforske og beskrive symmetri i mønster og figurer og bruke koordinatsystemet",
        klassetrinn=Klassetrinn.TRINN_6,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["symmetri_figur", "koordinatsystem_enkelt"],
        nøkkelord=["symmetri", "speiling", "koordinatsystem", "punkt"]
    ),
    Kompetansemaal(
        id="MAT06_stat_01",
        tekst="Bruke gjennomsnitt, typetall og median til å sammenligne datasett",
        klassetrinn=Klassetrinn.TRINN_6,
        hovedomraade=Hovedomraade.STATISTIKK,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["punktdiagram", "tallinje_median"],
        nøkkelord=["gjennomsnitt", "median", "typetall", "sentralmål"]
    ),
]

TRINN_7_MAAL = [
    Kompetansemaal(
        id="MAT07_tall_01",
        tekst="Utvikle og bruke regneregler for negative tall",
        klassetrinn=Klassetrinn.TRINN_7,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["tallinje_negativ"],
        tallomraade="negative tall",
        forutsetninger=["MAT04_tall_01"],
        nøkkelord=["negative tall", "fortegn", "addisjon", "subtraksjon"]
    ),
    Kompetansemaal(
        id="MAT07_potens_01",
        tekst="Utforske og bruke potenser og rotuttrykk",
        klassetrinn=Klassetrinn.TRINN_7,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=[],
        nøkkelord=["potens", "eksponent", "grunntall", "rot", "kvadratrot"]
    ),
    Kompetansemaal(
        id="MAT07_algebra_01",
        tekst="Behandle og faktorisere algebraiske uttrykk, og bruke dette i likninger",
        klassetrinn=Klassetrinn.TRINN_7,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=[],
        forutsetninger=["MAT05_algebra_01"],
        nøkkelord=["algebra", "faktorisering", "uttrykk", "likning"]
    ),
    Kompetansemaal(
        id="MAT07_likning_01",
        tekst="Løse likninger og ulikheter av første grad og tolke løsningene",
        klassetrinn=Klassetrinn.TRINN_7,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["tallinje_ulikhet"],
        nøkkelord=["likning", "ulikhet", "løsning", "ukjent"]
    ),
    Kompetansemaal(
        id="MAT07_sannsynlighet_01",
        tekst="Utforske og beskrive uniform og ikke-uniform sannsynlighet",
        klassetrinn=Klassetrinn.TRINN_7,
        hovedomraade=Hovedomraade.SANNSYNLIGHET,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["sannsynlighetstre_enkel", "terning", "spinner"],
        nøkkelord=["sannsynlighet", "utfall", "hendelse", "tilfeldig"]
    ),
]

# =============================================================================
# UNGDOMSSKOLE 8.-10. TRINN
# =============================================================================

TRINN_8_MAAL = [
    Kompetansemaal(
        id="MAT08_tall_01",
        tekst="Utforske og bruke tall skrevet på standardform og veksle mellom ulike representasjoner av tall",
        klassetrinn=Klassetrinn.TRINN_8,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=[],
        nøkkelord=["standardform", "titallspotens", "store tall", "små tall"]
    ),
    Kompetansemaal(
        id="MAT08_potens_01",
        tekst="Utforske og beskrive strukturer og forandringer i geometriske mønster og tallmønster med figurer, ord og formler",
        klassetrinn=Klassetrinn.TRINN_8,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["mønster_figur", "tallrekke"],
        forutsetninger=["MAT07_potens_01"],
        nøkkelord=["mønster", "formel", "generalisere", "rekke"]
    ),
    Kompetansemaal(
        id="MAT08_algebra_01",
        tekst="Utforske, generalisere og bruke potensregler",
        klassetrinn=Klassetrinn.TRINN_8,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=[],
        forutsetninger=["MAT07_potens_01"],
        nøkkelord=["potensregler", "eksponent", "multiplikasjon", "divisjon", "potens av potens"]
    ),
    Kompetansemaal(
        id="MAT08_funksjon_01",
        tekst="Utforske og beskrive lineære og proporsjonale sammenhenger og representere dem på ulike måter",
        klassetrinn=Klassetrinn.TRINN_8,
        hovedomraade=Hovedomraade.FUNKSJONER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.MODELLERING],
        typiske_figurer=["koordinatsystem", "lineær_graf", "tabell"],
        nøkkelord=["lineær", "proporsjonalitet", "stigningstall", "graf", "funksjon"]
    ),
    Kompetansemaal(
        id="MAT08_geo_01",
        tekst="Utforske og argumentere for formler for areal og omkrets av sirkler og bruke dem i praktiske situasjoner",
        klassetrinn=Klassetrinn.TRINN_8,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["sirkel_med_radius", "sirkelsektor"],
        nøkkelord=["sirkel", "areal", "omkrets", "radius", "diameter", "pi"]
    ),
    Kompetansemaal(
        id="MAT08_pytagoras_01",
        tekst="Utforske og bruke Pytagoras' setning",
        klassetrinn=Klassetrinn.TRINN_8,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["rettvinklet_trekant", "pytagoras_bevis"],
        nøkkelord=["Pytagoras", "rettvinklet", "trekant", "hypotenus", "katet"]
    ),
]

TRINN_9_MAAL = [
    Kompetansemaal(
        id="MAT09_likning_01",
        tekst="Løse likningssett med to ukjente og tolke løsningene grafisk og algebraisk",
        klassetrinn=Klassetrinn.TRINN_9,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["koordinatsystem_to_linjer", "skjæringspunkt"],
        forutsetninger=["MAT07_likning_01", "MAT08_funksjon_01"],
        nøkkelord=["likningssett", "to ukjente", "innsettingsmetoden", "addisjonsmetoden", "grafisk løsning"]
    ),
    Kompetansemaal(
        id="MAT09_funksjon_01",
        tekst="Modellere situasjoner knyttet til eksponentiell vekst og lineær vekst, og sammenligne dem",
        klassetrinn=Klassetrinn.TRINN_9,
        hovedomraade=Hovedomraade.FUNKSJONER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.MODELLERING, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["eksponentiell_vs_lineær", "vekstgraf"],
        forutsetninger=["MAT08_funksjon_01"],
        nøkkelord=["eksponentiell vekst", "lineær vekst", "vekstfaktor", "modellering"]
    ),
    Kompetansemaal(
        id="MAT09_geo_01",
        tekst="Utforske og beskrive egenskaper ved to- og tredimensjonale figurer og bruke dem til problemløsning",
        klassetrinn=Klassetrinn.TRINN_9,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROBLEMLOSNING, Ferdighetstype.RESONNERING],
        typiske_figurer=["prisme", "sylinder", "kjegle", "kule", "tverrsnitt"],
        nøkkelord=["volum", "overflate", "tredimensjonal", "romfigur"]
    ),
    Kompetansemaal(
        id="MAT09_trig_01",
        tekst="Utforske og bruke trigonometri i rettvinklede trekanter",
        klassetrinn=Klassetrinn.TRINN_9,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["rettvinklet_trekant_trig", "hosliggende_motstående"],
        nøkkelord=["sinus", "cosinus", "tangens", "rettvinklet", "trigonometri"]
    ),
    Kompetansemaal(
        id="MAT09_stat_01",
        tekst="Analysere og presentere store datasett med digitale verktøy og vurdere kilder for feil",
        klassetrinn=Klassetrinn.TRINN_9,
        hovedomraade=Hovedomraade.STATISTIKK,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.KOMMUNIKASJON],
        typiske_figurer=["histogram", "boksplott", "spredningsdiagram"],
        nøkkelord=["datasett", "analyse", "diagram", "feilkilder"]
    ),
]

TRINN_10_MAAL = [
    Kompetansemaal(
        id="MAT10_algebra_01",
        tekst="Løse andregradslikninger og bruke disse i problemløsning",
        klassetrinn=Klassetrinn.TRINN_10,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["parabel", "nullpunkter_graf"],
        forutsetninger=["MAT07_likning_01"],
        nøkkelord=["andregradslikning", "abc-formelen", "faktorisering", "nullpunkt"]
    ),
    Kompetansemaal(
        id="MAT10_funksjon_01",
        tekst="Utforske og beskrive egenskaper ved polynomfunksjoner, rasjonale funksjoner og potensuttrykk",
        klassetrinn=Klassetrinn.TRINN_10,
        hovedomraade=Hovedomraade.FUNKSJONER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["polynomgraf", "rasjonal_funksjon_asymptote"],
        forutsetninger=["MAT09_funksjon_01"],
        nøkkelord=["polynom", "rasjonal funksjon", "asymptote", "nullpunkt", "ekstremalpunkt"]
    ),
    Kompetansemaal(
        id="MAT10_okonomi_01",
        tekst="Utforske matematiske modeller for personlig økonomi og vurdere valg knyttet til lån og sparing",
        klassetrinn=Klassetrinn.TRINN_10,
        hovedomraade=Hovedomraade.OKONOMI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.MODELLERING, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["vekstgraf_økonomi", "nedbetalingsplan"],
        nøkkelord=["rente", "lån", "sparing", "annuitet", "terminbeløp"]
    ),
    Kompetansemaal(
        id="MAT10_sannsynlighet_01",
        tekst="Beregne sannsynlighet ved hjelp av systematiske oppstillinger og bruke addisjons- og multiplikasjonssetningen",
        klassetrinn=Klassetrinn.TRINN_10,
        hovedomraade=Hovedomraade.SANNSYNLIGHET,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["venndiagram", "sannsynlighetstre"],
        forutsetninger=["MAT07_sannsynlighet_01"],
        nøkkelord=["sannsynlighet", "addisjonssetningen", "multiplikasjonssetningen", "betinget sannsynlighet"]
    ),
]

# =============================================================================
# VGS GRUNNLEGGENDE (1T, 1P, 2P)
# =============================================================================

VG1_1T_MAAL = [
    Kompetansemaal(
        id="1T_algebra_01",
        tekst="Utføre regneregler med potenser, røtter, formler, parentesuttrykk, rasjonale og kvadratiske uttrykk med og uten digitale verktøy",
        klassetrinn=Klassetrinn.VG1_1T,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=[],
        nøkkelord=["potenser", "røtter", "parenteser", "rasjonale uttrykk", "kvadratiske uttrykk"]
    ),
    Kompetansemaal(
        id="1T_likning_01",
        tekst="Løse lineære, kvadratiske likninger og likningssystemer med flere ukjente med og uten digitale verktøy",
        klassetrinn=Klassetrinn.VG1_1T,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["koordinatsystem_likningssett", "parabel_nullpunkt"],
        nøkkelord=["likning", "likningssett", "andregradslikning", "abc-formelen"]
    ),
    Kompetansemaal(
        id="1T_funksjon_01",
        tekst="Utforske og beskrive egenskaper ved polynomfunksjoner, rasjonale funksjoner, eksponentialfunksjoner og potensuttrykk med og uten digitale verktøy",
        klassetrinn=Klassetrinn.VG1_1T,
        hovedomraade=Hovedomraade.FUNKSJONER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["funksjonsplot", "asymptote", "nullpunkter_graf"],
        nøkkelord=["polynom", "rasjonal", "eksponentiell", "nullpunkt", "asymptote", "ekstremalpunkt"]
    ),
    Kompetansemaal(
        id="1T_geo_01",
        tekst="Analysere og løse problemer ved hjelp av trigonometri og bruke begrepene sinus, cosinus og tangens",
        klassetrinn=Klassetrinn.VG1_1T,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["rettvinklet_trekant_trig", "vilkårlig_trekant"],
        nøkkelord=["sinus", "cosinus", "tangens", "sinussetningen", "cosinussetningen"]
    ),
    Kompetansemaal(
        id="1T_vektor_01",
        tekst="Representere vektorer som piler og som koordinater, og regne med vektorer i planet",
        klassetrinn=Klassetrinn.VG1_1T,
        hovedomraade=Hovedomraade.VEKTORER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["vektor_2d", "vektoraddisjon", "skalarprodukt"],
        nøkkelord=["vektor", "koordinater", "addisjon", "skalarprodukt", "lengde"]
    ),
]

VG1_1P_MAAL = [
    Kompetansemaal(
        id="1P_tall_01",
        tekst="Bruke prosent, prosentpoeng, promille og vekstfaktor til å regne med praktiske problemstillinger",
        klassetrinn=Klassetrinn.VG1_1P,
        hovedomraade=Hovedomraade.TALL_OG_TALLFORSTAELSE,
        figurbehov=Figurbehov.INGEN,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=[],
        nøkkelord=["prosent", "prosentpoeng", "promille", "vekstfaktor"]
    ),
    Kompetansemaal(
        id="1P_okonomi_01",
        tekst="Lage og tolke budsjettet for en husholdning og reflektere over nøkkelord som inntekt, utgifter og sparing",
        klassetrinn=Klassetrinn.VG1_1P,
        hovedomraade=Hovedomraade.OKONOMI,
        figurbehov=Figurbehov.ENKEL,
        abstraksjonsnivaa=Abstraksjonsnivaa.KONKRET,
        typiske_ferdigheter=[Ferdighetstype.MODELLERING, Ferdighetstype.KOMMUNIKASJON],
        typiske_figurer=["budsjett_tabell", "kakediagram_økonomi"],
        nøkkelord=["budsjett", "inntekt", "utgift", "sparing"]
    ),
    Kompetansemaal(
        id="1P_stat_01",
        tekst="Planlegge, gjennomføre og presentere statistiske undersøkelser og vurdere og drøfte resultatene",
        klassetrinn=Klassetrinn.VG1_1P,
        hovedomraade=Hovedomraade.STATISTIKK,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.MODELLERING, Ferdighetstype.KOMMUNIKASJON],
        typiske_figurer=["histogram", "søylediagram", "boksplott"],
        nøkkelord=["statistisk undersøkelse", "presentasjon", "analyse"]
    ),
    Kompetansemaal(
        id="1P_funksjon_01",
        tekst="Utforske og beskrive lineære sammenhenger og bruke dem til å løse praktiske problemer",
        klassetrinn=Klassetrinn.VG1_1P,
        hovedomraade=Hovedomraade.FUNKSJONER,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.MODELLERING, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["lineær_graf_praktisk"],
        nøkkelord=["lineær", "stigningstall", "konstantledd", "praktisk"]
    ),
]

# =============================================================================
# VGS AVANSERT (R1, R2, S1, S2)
# =============================================================================

VG2_R1_MAAL = [
    Kompetansemaal(
        id="R1_algebra_01",
        tekst="Omforme og forenkle sammensatte rasjonale funksjoner og løse likninger og ulikheter med slike funksjoner",
        klassetrinn=Klassetrinn.VG2_R1,
        hovedomraade=Hovedomraade.ALGEBRA,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.PROBLEMLOSNING],
        typiske_figurer=["rasjonal_funksjon_asymptote", "ulikhet_fortegnslinje"],
        nøkkelord=["rasjonal funksjon", "faktorisering", "ulikhet", "fortegnsanalyse"]
    ),
    Kompetansemaal(
        id="R1_derivasjon_01",
        tekst="Utlede derivasjonsreglene for polynomfunksjoner, bruke dem til å drøfte polynomfunksjoner og begrunne fremgangsmåter",
        klassetrinn=Klassetrinn.VG2_R1,
        hovedomraade=Hovedomraade.DERIVASJON,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["funksjonsplot_med_tangent", "fortegnslinje_derivert", "ekstremalpunkt_graf"],
        nøkkelord=["derivasjon", "polynomfunksjon", "drøfting", "ekstremalpunkt", "vendepunkt"]
    ),
    Kompetansemaal(
        id="R1_derivasjon_02",
        tekst="Utlede produktregel, brøkregel og kjerneregel og bruke disse til å derivere sammensatte funksjoner",
        klassetrinn=Klassetrinn.VG2_R1,
        hovedomraade=Hovedomraade.DERIVASJON,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["sammensatt_funksjon_graf"],
        forutsetninger=["R1_derivasjon_01"],
        nøkkelord=["produktregel", "brøkregel", "kjerneregel", "sammensatt funksjon"]
    ),
    Kompetansemaal(
        id="R1_derivasjon_03",
        tekst="Derivere eksponentialfunksjoner, logaritmefunksjoner og trigonometriske funksjoner og bruke dem i modellering",
        klassetrinn=Klassetrinn.VG2_R1,
        hovedomraade=Hovedomraade.DERIVASJON,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.MODELLERING],
        typiske_figurer=["eksponentialfunksjon_graf", "sinuskurve", "logaritmefunksjon"],
        nøkkelord=["eksponentialfunksjon", "logaritme", "sinus", "cosinus", "modellering"]
    ),
    Kompetansemaal(
        id="R1_kombinatorikk_01",
        tekst="Beregne antall muligheter ved hjelp av produktregelen, permutasjoner og kombinasjoner",
        klassetrinn=Klassetrinn.VG2_R1,
        hovedomraade=Hovedomraade.KOMBINATORIKK,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["sannsynlighetstre", "kombinatorikk_grid"],
        nøkkelord=["kombinatorikk", "permutasjon", "kombinasjon", "fakultet"]
    ),
    Kompetansemaal(
        id="R1_sannsynlighet_01",
        tekst="Beregne sannsynligheter ved hjelp av betinget sannsynlighet, uavhengighet og Bayes' setning",
        klassetrinn=Klassetrinn.VG2_R1,
        hovedomraade=Hovedomraade.SANNSYNLIGHET,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["venndiagram", "sannsynlighetstre", "betinget_tabell"],
        nøkkelord=["betinget sannsynlighet", "uavhengighet", "Bayes"]
    ),
]

VG3_R2_MAAL = [
    Kompetansemaal(
        id="R2_integrasjon_01",
        tekst="Gjøre rede for definisjonen av bestemt integral og for integralet som grenseverdi av en sum",
        klassetrinn=Klassetrinn.VG3_R2,
        hovedomraade=Hovedomraade.INTEGRASJON,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["riemannsum", "areal_under_kurve", "grenseverdi_sum"],
        nøkkelord=["bestemt integral", "grenseverdi", "sum", "areal"]
    ),
    Kompetansemaal(
        id="R2_integrasjon_02",
        tekst="Beregne integraler ved hjelp av integrasjonsregler, delvis integrasjon og substitusjon",
        klassetrinn=Klassetrinn.VG3_R2,
        hovedomraade=Hovedomraade.INTEGRASJON,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE],
        typiske_figurer=[],
        forutsetninger=["R2_integrasjon_01"],
        nøkkelord=["integrasjon", "delvis integrasjon", "substitusjon", "antiderivasjon"]
    ),
    Kompetansemaal(
        id="R2_integrasjon_03",
        tekst="Bruke integrasjon til å beregne areal, volum og gjennomsnittlig verdi og i modellering",
        klassetrinn=Klassetrinn.VG3_R2,
        hovedomraade=Hovedomraade.INTEGRASJON,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROBLEMLOSNING, Ferdighetstype.MODELLERING],
        typiske_figurer=["areal_mellom_kurver", "omdreiningslegeme", "gjennomsnitt_graf"],
        forutsetninger=["R2_integrasjon_02"],
        nøkkelord=["areal", "volum", "omdreiningslegeme", "gjennomsnitt", "modellering"]
    ),
    Kompetansemaal(
        id="R2_difflikning_01",
        tekst="Modellere og løse differensiallikninger av første orden og tolke løsningene",
        klassetrinn=Klassetrinn.VG3_R2,
        hovedomraade=Hovedomraade.DIFFERENSIALLIKNINGER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.MODELLERING],
        typiske_figurer=["retningsfelt", "løsningskurver"],
        nøkkelord=["differensiallikning", "separabel", "retningsfelt", "modellering"]
    ),
    Kompetansemaal(
        id="R2_vektor_01",
        tekst="Utføre og analysere beregninger med vektorer i tre dimensjoner",
        klassetrinn=Klassetrinn.VG3_R2,
        hovedomraade=Hovedomraade.VEKTORER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["vektor_3d", "kryssprodukt_illustrasjon"],
        forutsetninger=["1T_vektor_01"],
        nøkkelord=["vektor", "3D", "kryssprodukt", "skalarprodukt", "rom"]
    ),
    Kompetansemaal(
        id="R2_romgeo_01",
        tekst="Utlede og bruke likninger for linjer og plan i rommet og beregne avstander og vinkler",
        klassetrinn=Klassetrinn.VG3_R2,
        hovedomraade=Hovedomraade.GEOMETRI,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["linje_i_rom", "plan_i_rom", "avstand_punkt_plan"],
        forutsetninger=["R2_vektor_01"],
        nøkkelord=["linje", "plan", "normalvektor", "parameterframstilling", "avstand", "vinkel"]
    ),
]

VG2_S1_MAAL = [
    Kompetansemaal(
        id="S1_okonomi_01",
        tekst="Utforske og forklare renteregning, lån og sparing, og beregne sluttverdi, nåverdi og årlige innbetalinger",
        klassetrinn=Klassetrinn.VG2_S1,
        hovedomraade=Hovedomraade.OKONOMI,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.SEMI_ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.MODELLERING],
        typiske_figurer=["vekstgraf_økonomi", "tidslinje_økonomi"],
        nøkkelord=["rente", "lån", "sparing", "nåverdi", "sluttverdi", "annuitet"]
    ),
    Kompetansemaal(
        id="S1_funksjon_01",
        tekst="Utforske, forstå og bruke ulike funksjoner, og bruke derivasjon til å analysere egenskaper ved funksjonene",
        klassetrinn=Klassetrinn.VG2_S1,
        hovedomraade=Hovedomraade.FUNKSJONER,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.BEGREPSFORSTAELSE, Ferdighetstype.RESONNERING],
        typiske_figurer=["funksjonsplot_drøfting", "ekstremalpunkt_graf"],
        nøkkelord=["funksjon", "derivasjon", "drøfting", "ekstremalpunkt"]
    ),
    Kompetansemaal(
        id="S1_sannsynlighet_01",
        tekst="Bruke sannsynlighetsfordelinger som binomisk og hypergeometrisk fordeling til å beregne sannsynligheter",
        klassetrinn=Klassetrinn.VG2_S1,
        hovedomraade=Hovedomraade.SANNSYNLIGHET,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["binomisk_søylediagram", "sannsynlighetsfordeling"],
        nøkkelord=["binomisk", "hypergeometrisk", "fordeling", "forventningsverdi"]
    ),
]

VG3_S2_MAAL = [
    Kompetansemaal(
        id="S2_statistikk_01",
        tekst="Planlegge og gjennomføre statistiske undersøkelser og bruke normalfordelingen til å beregne sannsynligheter",
        klassetrinn=Klassetrinn.VG3_S2,
        hovedomraade=Hovedomraade.STATISTIKK,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.MODELLERING],
        typiske_figurer=["normalfordeling_skravert", "z_tabell_illustrasjon"],
        nøkkelord=["normalfordeling", "standardavvik", "z-verdi", "sannsynlighet"]
    ),
    Kompetansemaal(
        id="S2_statistikk_02",
        tekst="Utføre hypotesetesting, beregne og tolke konfidensintervaller",
        klassetrinn=Klassetrinn.VG3_S2,
        hovedomraade=Hovedomraade.STATISTIKK,
        figurbehov=Figurbehov.MIDDELS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.RESONNERING],
        typiske_figurer=["konfidensintervall_graf", "hypotesetest_fordeling"],
        nøkkelord=["hypotesetest", "konfidensintervall", "signifikans", "nullhypotese"]
    ),
    Kompetansemaal(
        id="S2_integrasjon_01",
        tekst="Bruke integrasjon til å finne areal og beregne forventningsverdi og standardavvik til sannsynlighetsfordelinger",
        klassetrinn=Klassetrinn.VG3_S2,
        hovedomraade=Hovedomraade.INTEGRASJON,
        figurbehov=Figurbehov.KOMPLEKS,
        abstraksjonsnivaa=Abstraksjonsnivaa.ABSTRAKT,
        typiske_ferdigheter=[Ferdighetstype.PROSEDYRE, Ferdighetstype.BEGREPSFORSTAELSE],
        typiske_figurer=["tetthetsfunksjon_skravert", "areal_under_kurve"],
        nøkkelord=["integrasjon", "areal", "forventningsverdi", "tetthetsfunksjon"]
    ),
]


# =============================================================================
# GRENSER OG BEGRENSNINGER (For Agent-styring)
# =============================================================================

GRADE_BOUNDARIES = {
    "1-4": {
        "description": "Barnetrinnet - konkret, lekbasert matematikk",
        "allowed_concepts": [
            "Addisjon og subtraksjon opp til 1000",
            "Multiplikasjon (gangetabellen 1-10)",
            "Enkel divisjon med og uten rest",
            "Brøker som del av helhet (1/2, 1/4, 1/3)",
            "Geometriske grunnformer",
            "Klokka og tid",
        ],
        "forbidden_concepts": [
            "Negative tall", "Algebra", "Prosent", "Likninger", "Vektorer"
        ]
    },
    "5-7": {
        "description": "Mellomtrinnet - overgang til abstrakt tenkning",
        "allowed_concepts": [
            "Negative tall", "Desimaltall", "Brøkregning", "Prosent",
            "Enkle likninger (x + 5 = 12)", "Koordinatsystem", "Vinkler"
        ],
        "forbidden_concepts": [
            "Pytagoras", "Ligningssett", "Andregradslikninger", "Derivasjon"
        ]
    },
    "8-10": {
        "description": "Ungdomstrinnet - algebra og funksjoner",
        "allowed_concepts": [
            "Potensregler", "Bokstavregning", "Likninger", "Pytagoras",
            "Lineære funksjoner", "Likningssett", "Andregradslikninger (10. trinn)",
            "Trigonometri (sin, cos, tan i rettvinklet trekant)"
        ],
        "forbidden_concepts": [
            "Derivasjon", "Vektorer", "Logaritmer", "Integrasjon"
        ]
    },
    "vgs": {
        "description": "Videregående skole - formell og avansert matematikk",
        "allowed_concepts": [
            "Derivasjon", "Integrasjon", "Vektorer", "Logaritmer",
            "Sammensatte funksjoner", "Bevis", "Modellering"
        ],
        "forbidden_concepts": [
            "Partielle deriverte", "Lineær algebra (matriser)", "Komplekse tall"
        ]
    }
}

def get_grade_boundaries(grade: str) -> dict:
    """Henter grensebetingelser for et trinn."""
    grade_clean = grade.lower().replace(" ", "").replace(".", "")
    
    if grade_clean in ["1", "2", "3", "4"]: return GRADE_BOUNDARIES["1-4"]
    if grade_clean in ["5", "6", "7"]: return GRADE_BOUNDARIES["5-7"]
    if grade_clean in ["8", "9", "10"]: return GRADE_BOUNDARIES["8-10"]
    return GRADE_BOUNDARIES["vgs"]

def format_boundaries_for_prompt(grade: str) -> str:
    """Formaterer grensebetingelser for bruk i AI-prompts."""
    boundaries = get_grade_boundaries(grade)
    
    prompt = f"=== PEDAGOGISKE GRENSER FOR {grade.upper()} ===\n"
    prompt += f"Beskrivelse: {boundaries['description']}\n\n"
    
    prompt += "TILLATTE KONSEPTER (Hold deg innenfor disse):\n"
    for c in boundaries['allowed_concepts']:
        prompt += f"- {c}\n"
        
    prompt += "\nFORBUDTE KONSEPTER (IKKE bruk disse, for avansert):\n"
    for c in boundaries['forbidden_concepts']:
        prompt += f"- {c}\n"
        
    return prompt

# =============================================================================
# HJELPEFUNKSJONER
# =============================================================================

# Samle alle mål i én struktur
ALLE_KOMPETANSEMAAL: dict[Klassetrinn, list[Kompetansemaal]] = {
    Klassetrinn.TRINN_1: TRINN_1_MAAL,
    Klassetrinn.TRINN_2: TRINN_2_MAAL,
    Klassetrinn.TRINN_3: TRINN_3_MAAL,
    Klassetrinn.TRINN_4: TRINN_4_MAAL,
    Klassetrinn.TRINN_5: TRINN_5_MAAL,
    Klassetrinn.TRINN_6: TRINN_6_MAAL,
    Klassetrinn.TRINN_7: TRINN_7_MAAL,
    Klassetrinn.TRINN_8: TRINN_8_MAAL,
    Klassetrinn.TRINN_9: TRINN_9_MAAL,
    Klassetrinn.TRINN_10: TRINN_10_MAAL,
    Klassetrinn.VG1_1T: VG1_1T_MAAL,
    Klassetrinn.VG1_1P: VG1_1P_MAAL,
    Klassetrinn.VG2_R1: VG2_R1_MAAL,
    Klassetrinn.VG3_R2: VG3_R2_MAAL,
    Klassetrinn.VG2_S1: VG2_S1_MAAL,
    Klassetrinn.VG3_S2: VG3_S2_MAAL,
}


def get_aldersnivaa(klassetrinn: Klassetrinn) -> Aldersnivaa:
    """Bestem pedagogisk aldersnivå basert på klassetrinn."""
    mapping = {
        Klassetrinn.TRINN_1: Aldersnivaa.BARNESKOLE_SMAA,
        Klassetrinn.TRINN_2: Aldersnivaa.BARNESKOLE_SMAA,
        Klassetrinn.TRINN_3: Aldersnivaa.BARNESKOLE_SMAA,
        Klassetrinn.TRINN_4: Aldersnivaa.BARNESKOLE_SMAA,
        Klassetrinn.TRINN_5: Aldersnivaa.BARNESKOLE_STORE,
        Klassetrinn.TRINN_6: Aldersnivaa.BARNESKOLE_STORE,
        Klassetrinn.TRINN_7: Aldersnivaa.BARNESKOLE_STORE,
        Klassetrinn.TRINN_8: Aldersnivaa.UNGDOMSSKOLE,
        Klassetrinn.TRINN_9: Aldersnivaa.UNGDOMSSKOLE,
        Klassetrinn.TRINN_10: Aldersnivaa.UNGDOMSSKOLE,
        Klassetrinn.VG1_1T: Aldersnivaa.VGS_GRUNNLEGGENDE,
        Klassetrinn.VG1_1P: Aldersnivaa.VGS_GRUNNLEGGENDE,
        Klassetrinn.VG2_2P: Aldersnivaa.VGS_GRUNNLEGGENDE,
        Klassetrinn.VG2_R1: Aldersnivaa.VGS_AVANSERT,
        Klassetrinn.VG2_S1: Aldersnivaa.VGS_AVANSERT,
        Klassetrinn.VG3_R2: Aldersnivaa.VGS_AVANSERT,
        Klassetrinn.VG3_S2: Aldersnivaa.VGS_AVANSERT,
    }
    return mapping[klassetrinn]


def finn_kompetansemaal(
    klassetrinn: Optional[Klassetrinn] = None,
    hovedomraade: Optional[Hovedomraade] = None,
    søkeord: Optional[str] = None,
    figurbehov: Optional[Figurbehov] = None,
) -> list[Kompetansemaal]:
    """
    Fleksibelt søk etter kompetansemål.
    
    Eksempel:
        finn_kompetansemaal(klassetrinn=Klassetrinn.VG2_R1, hovedomraade=Hovedomraade.DERIVASJON)
        finn_kompetansemaal(søkeord="integral")
    """
    resultater = []
    
    for trinn, mål_liste in ALLE_KOMPETANSEMAAL.items():
        if klassetrinn and trinn != klassetrinn:
            continue
            
        for mål in mål_liste:
            if hovedomraade and mål.hovedomraade != hovedomraade:
                continue
            if figurbehov and mål.figurbehov != figurbehov:
                continue
            if søkeord:
                søkeord_lower = søkeord.lower()
                if not (
                    søkeord_lower in mål.tekst.lower() or
                    any(søkeord_lower in nw.lower() for nw in mål.nøkkelord)
                ):
                    continue
            
            resultater.append(mål)
    
    return resultater


def hent_forutsetninger(mål: Kompetansemaal) -> list[Kompetansemaal]:
    """Hent alle kompetansemål som er forutsetninger for dette målet."""
    forutsetning_maal = []
    
    for forutsetning_id in mål.forutsetninger:
        for trinn_maal in ALLE_KOMPETANSEMAAL.values():
            for m in trinn_maal:
                if m.id == forutsetning_id:
                    forutsetning_maal.append(m)
                    break
    
    return forutsetning_maal


def generer_figurbehov_rapport(klassetrinn: Klassetrinn) -> dict:
    """
    Generer oversikt over figurbehov for et klassetrinn.
    Nyttig for orkestratoren.
    """
    mål = ALLE_KOMPETANSEMAAL.get(klassetrinn, [])
    
    rapport = {
        "klassetrinn": klassetrinn.value,
        "totalt_antall_mål": len(mål),
        "figurbehov": {
            "ingen": 0,
            "enkel": 0,
            "middels": 0,
            "kompleks": 0
        },
        "anbefalt_format": "typst"  # Default
    }
    
    for m in mål:
        rapport["figurbehov"][m.figurbehov.value] += 1
    
    # Bestem anbefalt format
    kompleks_andel = rapport["figurbehov"]["kompleks"] / len(mål) if mål else 0
    
    if kompleks_andel > 0.5:
        rapport["anbefalt_format"] = "latex"
    elif kompleks_andel > 0.2:
        rapport["anbefalt_format"] = "hybrid"
    else:
        rapport["anbefalt_format"] = "typst"
    
    return rapport
