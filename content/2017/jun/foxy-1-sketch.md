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

## Kompilator i środowisko
Instalacja jest dziecinnie prosta: [rustup.rs](https://rustup.rs/). Część
dystrybucji będzie miała też Rusta w swoich repozytoriach.

Dla wygody, większość operacji (tworzenie projektów, kompilacja, uruchamianie
itd.) wykonuje się przy pomocy narzędzia o nazwie `cargo`. Nie zapomnijcie go
zainstalować, jeśli nie korzystacie z rustup.rs.

## Dokumentacja i inne materiały do nauki
Rust ma solidny zbiór materiałów do nauki wraz z dokumentacją języka i
biblioteki standardowej na swojej oficjalnej stronie
[rust-lang.org](https://www.rust-lang.org/).


I had a lot of trouble setting up my laptop NVIDIA GPU with CUDA on Ubuntu
14.04. These steps might actually help somebody.

First, download the [NVIDIA CUDA Toolkit](http://developer.nvidia.com/cuda-downloads).

Remove all old NVIDIA-related drivers:

    :::rust
    use std::net;

    const PROXY_PORT :u16 = 4000;

    fn main() {
        let listener = net::TcpListener::bind(("127.0.0.1", PROXY_PORT)).unwrap();

        match listener.accept() {
            Ok((sock, _)) => handle_connection(sock),
            Err(e) => panic!("Error while accepting connection: {}", e),
        }
    }


    mod http;
    fn handle_connection(tcp: net::TcpStream) {
        let mut h = http::HttpStream::new(tcp);

        while !h.is_closed() {
            let request = match h.get() {
                Ok(r) => r,
                Err(e) => {
                    println!("Error while getting http request: {}", e);
                    return
                },
            };
            println!("Got: {:?}", request.to_string());
            h.send(&http::HttpResponse::new().status(200, "OK").build().to_packet());
        }
    }


Backup your `/etc/modprobe.d/blacklist.conf` and make sure it contains these lines:

    :::bash
    blacklist nouveau
    blacklist lbm-nouveau
    blacklist nvidia-173
    blacklist nvidia-96
    blacklist nvidia-current
    blacklist nvidia-173-updates
    blacklist nvidia-96-updates
    alias nvidia nvidia_current_updates
    alias nouveau off
    alias lbm-nouveau off
    options nouveau modeset=0

Add bumblebee and xorg-edgers repositories:

    :::bash
    sudo apt-add-repository ppa:bumblebee/stable -y
    sudo add-apt-repository ppa:xorg-edgers/ppa -y
    sudo apt-get update && sudo apt-get upgrade -y

Now it's time to install the CUDA toolkit (along with `nvidia-352` drivers).

    :::bash
    # This installs necessary headers.
    sudo apt-get install linux-source && sudo apt-get install linux-headers-$(uname -r)

    # USE THE REAL PACKAGE NAME BELOW
    sudo dpkg -i cuda-repo-ubuntu1404-7-5-local_7.5-18_amd64.deb

    sudo apt-get install cuda
    sudo apt-get update
    sudo apt-get dist-upgrade -y

Install bumblebee (to have switchable GPUs).

    :::bash
    sudo apt-get install bumblebee bumblebee-nvidia virtualgl virtualgl-libs virtualgl-libs-ia32:i386 virtualgl-libs:i386
    sudo usermod -a -G bumblebee $USER

Edit `/etc/bumblebee/bumblebee.conf` as follows:

* Change all occurences of `nvidia-current` to `nvidia-352`
* After `Driver=` insert `nvidia`
* After `KernelDriver=` insert `nvidia-352`
* (if having trouble with optirun) uncomment the `BusID` line and set it
  accordingly to what the comment above this line says.

Make sure that these lines are in `/etc/modprobe.d/bumblebee.conf`:

    :::bash
    blacklist nvidia-352
    blacklist nvidia-352-updates
    blacklist nvidia-experimental-352

    alias nvidia-uvm nvidia_352_uvm


After `reboot` everything should work fine. You can test it with:

    :::bash
    optirun glxspheres64
    # compare the performance with default GPU running the command above without optirun

If you need more help: [CUDA installation guide for Linux](http://developer.download.nvidia.com/compute/cuda/7.5/Prod/docs/sidebar/CUDA_Installation_Guide_Linux.pdf)
