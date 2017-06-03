Title: Serwer proxy w Ruscie (część 1)
Date: 2017-06-03
Category: rust
Tags: rust, foxy


# O czym będzie ten projekt?

## Motywacja
Jestem człowiekiem, który stale się czymś rozprasza. Często odwiedzam strony dla
programistów czy ludzi związanych ze startupami (m.in. Hacker News, lobste.rs),
nawet jeśli nie bardzo mam czas poczytać artykuły, które tam są linkowane. Jak
się można domyślać, niezbyt pomaga to w produktywnej pracy. Nie mam żadnego
problemu, kiedy jestem mocno zajęty, ale jeśli mam 2-3 minuty, bo coś mi się
kompiluje/mój map-reduce sie jeszcze nie skończył/czekam na odpowiedź od
kogoś/cokolwiek, to moim naturalnym odruchem jest przejrzenie wszystkich,
chociaż trochę interesujących mnie stron.

Próbowałem różnych rozszerzeń do Chrome, zmian w `/etc/hosts` czy blokowania
niektórych domen w domowym routerze, ale żadna z tych opcji mnie w pełni nie
zadowoliła (żadne z powyższych nie było wystarczająco elastyczne). Stąd pomysł
napisania własnego serwera proxy, którego zachowanie będę mógł do woli
konfigurować. Przykładowo:

- przekierowywać mnie z pewnych stron na inne,
- ograniczać dostęp do stron na pewien czas,
- opóźniać ładowanie stron (często takie opóźnienie pozwala mi na zreflektowanie
  się, że wcale nie chciałem zajrzeć na daną stronę i spędzić na niej połowy
  dnia),
- itd.

## Czemu Rust?
Moim podstawowym językiem był od zawsze C++, w pracy teraz używam Go, a idea
silnego kompilatora zdecydowanie do mnie przemawia. Dlatego chciałbym nauczyć
się Rusta. Poza tym, serwer proxy wydaje się na tyle prostym projektem, że mogę
w międzyczasie poznawać nowy język, ale na tyle trudnym, żebym mógł coś o nim
powiedzieć.

## Czego możecie oczekiwać?
Chciałbym, żeby to była relacja z mojej przygody z Rustem. Nigdy nie pisałem w
tym języku, więc raczej **nie pokazę jak pisać dobrze** w Ruscie, ale będę
starał się zgłębiać temat jak najbardziej, żeby nie pisać tutaj bzdur. Wiem
mniej więcej, o co chodzi z borrow checkerem i mam małe doświadczenie z językami
z systemem typów Hindleya-Milnera (OCaml), więc mam nadzieję, że nie będę
kompletnie zagubiony. ;)

## Czemu blog i czemu po polsku?
1. Mam nadzieję, że regularne pisanie zmotywuje mnie do regularnej nauki. ;)
2. Materiały o Ruscie widzę głównie po angielsku, więc może warto?


# Przygotowania

## Kompilator
Instalacja jest dziecinnie prosta: [rustup.rs](https://rustup.rs/). Część
dystrybucji będzie miała też Rusta w swoich repozytoriach.

Dla wygody, większość operacji (tworzenie projektów, kompilacja, uruchamianie
itd.) wykonuje się przy pomocy narzędzia o nazwie `cargo`. Nie zapomnijcie go
zainstalować, jeśli nie korzystacie z rustup.rs.

## Dokumentacja i inne materiały do nauki
Rust ma solidny zbiór materiałów do nauki wraz z dokumentacją języka i
biblioteki standardowej na swojej oficjalnej stronie
[rust-lang.org](https://www.rust-lang.org/).

## Moje środowisko
VIM + [Racer](https://github.com/phildawes/racer) +
[vim-racer](https://github.com/racer-rust/vim-racer). Racer jest narzędziem do
autouzupełniania dla Rusta.

# Koniec postu
Na dziś to koniec. W kolejnym poście będzie już trochę kodu. ;)
