from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

OUT  = r"C:\Users\MSI\OneDrive\Pulpit\Portfolio\sprawozdanie.pdf"
LOGO = r"C:\Users\MSI\OneDrive\Pulpit\logo.jpg"
FD   = r"C:\Windows\Fonts"

W = 160  # usable width

class Doc(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_margins(25, 25, 25)
        self.set_auto_page_break(True, 22)
        for style, file in [("","arial.ttf"),("B","arialbd.ttf"),("I","ariali.ttf"),("BI","arialbi.ttf")]:
            self.add_font("Arial", style, os.path.join(FD, file))
        self.add_font("Mono", "", os.path.join(FD, "cour.ttf"))
        self.add_font("Sym",  "", os.path.join(FD, "seguisym.ttf"))

    def header(self):
        if self.page_no() > 2:
            self.set_font("Arial","I",8)
            self.set_text_color(130,130,130)
            self.cell(0,6,"Sprawozdanie z pracy projektowej – System zarządzania zadaniami zespołu (TASKOMAT)",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(180,180,180)
            self.set_line_width(0.2)
            self.line(25, self.get_y(), 185, self.get_y())
            self.ln(2)
            self.set_text_color(0,0,0)

    def footer(self):
        if self.page_no() > 2:
            self.set_y(-18)
            self.set_font("Arial","",9)
            self.set_text_color(130,130,130)
            self.cell(0,8,str(self.page_no()-2),align="C")
            self.set_text_color(0,0,0)

    # ── helpers ──────────────────────────────────────────────────────────
    def h1(self, num, title):
        self.set_font("Arial","B",15)
        self.set_text_color(20,50,110)
        self.ln(4)
        self.cell(0,10,f"Rozdział {num}.  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(20,50,110)
        self.set_line_width(0.5)
        self.line(25, self.get_y(), 185, self.get_y())
        self.ln(4)
        self.set_text_color(0,0,0)

    def h2(self, title):
        self.set_font("Arial","B",12)
        self.set_text_color(30,30,30)
        self.ln(3)
        self.cell(0,8,title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0,0,0)
        self.ln(1)

    def h3(self, title):
        self.set_font("Arial","BI",11)
        self.ln(2)
        self.cell(0,7,title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def p(self, text):
        self.set_font("Arial","",11)
        self.multi_cell(0,6,text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def li(self, label, rest="", indent=6):
        self.set_x(25 + indent)
        self.set_font("Arial","",11)
        self.cell(4,6,"•")
        if rest:
            self.set_font("Arial","B",11)
            self.cell(self.get_string_width(label)+1, 6, label)
            self.set_font("Arial","",11)
            self.multi_cell(0,6," "+rest, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.multi_cell(0,6,label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code(self, txt):
        self.set_font("Mono","",8.5)
        self.set_fill_color(242,242,242)
        self.set_draw_color(200,200,200)
        self.ln(1)
        self.multi_cell(0,5,txt, border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def table_header(self, cols, widths):
        self.set_font("Arial","B",9)
        self.set_fill_color(20,50,110)
        self.set_text_color(255,255,255)
        for col, w in zip(cols, widths):
            self.cell(w,7,col,border=1,fill=True,align="C")
        self.ln()
        self.set_text_color(0,0,0)

    def table_row(self, cells, widths, bold_first=False, shade=False):
        if shade:
            self.set_fill_color(235,240,252)
        else:
            self.set_fill_color(255,255,255)
        # first pass: compute max height
        h = 6
        for c, w in zip(cells, widths):
            font = "Sym" if c in ("✓","✔") else "Arial"
            self.set_font(font,"",9)
            lines = self.multi_cell(w,6,c,border=0,fill=False,dry_run=True,output="LINES")
            h = max(h, 6*len(lines))
        # second pass: draw cells at same y
        y0 = self.get_y()
        for i,(c,w) in enumerate(zip(cells,widths)):
            self.set_xy(self.get_x(), y0)
            if c in ("✓", "✔"):
                self.set_font("Sym","",11)
            elif i == 0 and bold_first:
                self.set_font("Arial","B",9)
            else:
                self.set_font("Arial","",9)
            self.multi_cell(w,h,c,border=1,fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_y(y0 + h)


def build():
    doc = Doc()

    # ════════════════════════════════════════════════════════════════════
    # STRONA TYTUŁOWA
    # ════════════════════════════════════════════════════════════════════
    doc.add_page()
    if os.path.exists(LOGO):
        doc.image(LOGO, x=72, y=28, w=66)
    doc.ln(70)
    doc.set_font("Arial","B",16)
    doc.set_text_color(20,50,110)
    doc.multi_cell(0,9,"Collegium Witelona Uczelnia Państwowa w Legnicy",align="C",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.set_font("Arial","",12)
    doc.set_text_color(60,60,60)
    doc.cell(0,8,"Kierunek: Informatyka",align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(18)
    doc.set_font("Arial","B",20)
    doc.set_text_color(0,0,0)
    doc.multi_cell(0,11,"Sprawozdanie z pracy projektowej",align="C",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(4)
    doc.set_font("Arial","B",14)
    doc.set_text_color(20,50,110)
    doc.multi_cell(0,8,"System zarządzania zadaniami zespołu",align="C",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.set_font("Arial","I",13)
    doc.cell(0,8,"TASKOMAT",align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(4)
    doc.set_font("Arial","",11)
    doc.set_text_color(60,60,60)
    doc.multi_cell(0,7,
        "Przedmioty: Bezpieczeństwo systemów informatycznych\n"
        "                Zarządzanie i monitorowanie projektów",
        align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(20)
    doc.set_text_color(0,0,0)
    doc.set_font("Arial","",12)
    data = [
        ("Autorzy:",       "Daniel Kozak, Emilia Małecka, Wiktor Semp"),
        ("Rok studiów:",   "III"),
        ("Grupa:",         "2(2)u"),
        ("Rok akademicki:","2025/2026"),
    ]
    for lbl, val in data:
        doc.set_x(50)
        doc.set_font("Arial","B",12); doc.cell(45,8,lbl)
        doc.set_font("Arial","",12); doc.cell(0,8,val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(28)
    doc.set_font("Arial","",12)
    doc.cell(0,8,"Legnica, maj 2026",align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ════════════════════════════════════════════════════════════════════
    # ROZDZIAŁ 1 – OPIS FUNKCJONALNY
    # ════════════════════════════════════════════════════════════════════
    doc.add_page()
    doc.h1(1, "Opis funkcjonalny systemu")

    doc.h2("1.1  Cel i zakres systemu")
    doc.p(
        "System Task Manager (TASKOMAT) jest wieloplatformową aplikacją przeznaczoną "
        "do zarządzania zadaniami w środowisku zespołowym. System umożliwia tworzenie "
        "i śledzenie zadań, zarządzanie projektami, komunikację między użytkownikami "
        "oraz monitorowanie postępów prac przez administratorów."
    )
    doc.p("System składa się z czterech głównych komponentów:")
    doc.li("REST API", "– centralne API odpowiedzialne za logikę biznesową i dostęp do danych, stanowiące punkt komunikacji dla wszystkich klientów,")
    doc.li("Aplikacja webowa", "– interfejs dostępny przez przeglądarkę internetową, pełniący rolę panelu administracyjnego,")
    doc.li("Aplikacja mobilna", "– natywna aplikacja na urządzenia mobilne (Android i iOS) zbudowana w technologii Flutter,")
    doc.li("Aplikacja desktopowa", "– aplikacja na system Windows zbudowana w technologii C# + .NET (WPF).")
    doc.ln(2)

    doc.h2("1.2  Role użytkowników")
    doc.p("System wyodrębnia dwie role użytkowników o różnych uprawnieniach:")
    doc.li("Użytkownik", "– standardowy uczestnik projektu posiadający dostęp do zarządzania własnymi zadaniami, komunikacji w ramach projektu oraz zarządzania profilem konta.")
    doc.li("Administrator", "– zarządca systemu z rozszerzonymi uprawnieniami do nadzorowania projektów, zarządzania użytkownikami, monitorowania aktywności i przeglądania logów bezpieczeństwa.")
    doc.ln(2)

    doc.h2("1.3  Lista funkcjonalności")
    doc.p(
        "Poniższa tabela przedstawia pełną listę funkcjonalności systemu wraz z ich "
        "dostępnością na poszczególnych platformach. Symbol * oznacza endpoint REST API, "
        "natomiast zaznaczenie w kolumnie platformy wskazuje na implementację danej "
        "funkcjonalności na konkretnej platformie klienckiej."
    )

    # tabela funkcjonalności
    cols   = ["OPZ","Funkcjonalność","API","Web","Mob.","Desk."]
    widths = [16, 82, 12, 12, 14, 14]
    rows = [
        ("SYS-01","Użytkownik może założyć konto w systemie","*","","✓","✓"),
        ("SYS-02","Użytkownik może zalogować się do aplikacji","*","","✓","✓"),
        ("SYS-03","Użytkownik może tworzyć nowe zadania","*","","✓","✓"),
        ("SYS-04","Użytkownik może edytować i usuwać zadania","*","","✓","✓"),
        ("SYS-05","Użytkownik może przypisywać zadania do innych użytkowników","*","","✓","✓"),
        ("SYS-06","Użytkownik może zmieniać status zadania (do wykonania / w trakcie / zakończone)","*","","✓","✓"),
        ("SYS-07","Użytkownik może przeglądać listę swoich zadań","*","","✓","✓"),
        ("SYS-08","Użytkownik może otrzymywać powiadomienia o zmianach w zadaniach","*","✓","✓","✓"),
        ("SYS-09","Użytkownik może zaakceptować zaproszenie do projektu od Administratora","*","","✓","✓"),
        ("SYS-10","Użytkownik może zarządzać swoim profilem i ustawieniami konta","*","✓","✓","✓"),
        ("SYS-11","Administrator może zalogować się w systemie","*","✓","","✓"),
        ("SYS-12","Administrator może dodawać, edytować i usuwać zadania","*","✓","",""),
        ("SYS-13","Administrator może tworzyć nowe projekty","*","✓","","✓"),
        ("SYS-14","Administrator może edytować uprawnienia użytkowników przypisanych do projektu","*","✓","","✓"),
        ("SYS-15","Administrator może przydzielać użytkowników do konkretnych zadań","*","✓","","✓"),
        ("SYS-16","Administrator może monitorować aktywność użytkowników w systemie","*","✓","",""),
        ("SYS-17","Administrator może przeglądać logi bezpieczeństwa","*","✓","",""),
        ("SYS-18","Administrator otrzymuje powiadomienia, gdy użytkownik doda lub zmieni status zadania","*","✓","","✓"),
        ("SYS-19","Administrator może blokować konta po wykryciu podejrzanych działań","*","✓","",""),
        ("SYS-20","Administrator może filtrować zadania według przypisanego użytkownika","*","✓","","✓"),
        ("SYS-21","Administrator może usuwać projekty z systemu","*","✓","","✓"),
    ]
    doc.table_header(cols, widths)
    for i, row in enumerate(rows):
        doc.table_row(list(row), widths, bold_first=True, shade=(i%2==0))
    doc.ln(4)

    doc.h2("1.4  Szczegółowy opis modułów funkcjonalnych")

    doc.h3("1.4.1  Moduł uwierzytelniania")
    doc.p(
        "Moduł uwierzytelniania stanowi fundament bezpieczeństwa systemu. Użytkownicy "
        "mogą rejestrować się i logować przy użyciu tradycyjnych danych uwierzytelniających "
        "(adres e-mail i hasło) lub przez mechanizm Google OAuth 2.0. Po pomyślnym "
        "uwierzytelnieniu system wydaje tokeny JWT: dostępowy o czasie życia 15 minut "
        "oraz odświeżający ważny przez 24 godziny. System obsługuje także dwuskładnikowe "
        "uwierzytelnianie (2FA) oparte na algorytmie TOTP."
    )

    doc.h3("1.4.2  Moduł zarządzania zadaniami")
    doc.p(
        "Zadanie jest podstawową jednostką pracy w systemie. Każde zadanie posiada tytuł, "
        "opis, termin wykonania oraz status. Obsługiwane statusy to: do wykonania, "
        "w trakcie i zakończone. Użytkownicy mogą tworzyć, edytować i usuwać własne "
        "zadania oraz przypisywać je innym członkom projektu. Administrator posiada "
        "pełną kontrolę nad wszystkimi zadaniami w systemie."
    )

    doc.h3("1.4.3  Moduł zarządzania projektami")
    doc.p(
        "Projekty grupują powiązane zadania i użytkowników. Administrator tworzy projekt, "
        "a następnie zaprasza wybranych użytkowników. Po zaakceptowaniu zaproszenia "
        "użytkownik uzyskuje dostęp do zadań w ramach projektu. Administrator może "
        "edytować uprawnienia członków, przydzielać zadania i usuwać projekty."
    )

    doc.h3("1.4.4  Moduł powiadomień")
    doc.p(
        "System generuje powiadomienia informujące o kluczowych zdarzeniach: zmianie "
        "statusu zadania, nowym przypisaniu czy wysłaniu zaproszenia do projektu. "
        "Powiadomienia dostępne są na wszystkich platformach, co zapewnia spójne "
        "doświadczenie niezależnie od używanego urządzenia."
    )

    doc.h3("1.4.5  Moduł bezpieczeństwa i audytu")
    doc.p(
        "Administrator posiada wyspecjalizowany interfejs do monitorowania bezpieczeństwa "
        "systemu. Obejmuje on przeglądanie logów bezpieczeństwa, śledzenie aktywności "
        "użytkowników oraz możliwość natychmiastowego zablokowania konta w przypadku "
        "wykrycia podejrzanej aktywności (np. wielokrotnych nieudanych prób logowania)."
    )

    # ════════════════════════════════════════════════════════════════════
    # ROZDZIAŁ 2 – OPIS TECHNOLOGICZNY
    # ════════════════════════════════════════════════════════════════════
    doc.add_page()
    doc.h1(2, "Opis technologiczny")

    doc.h2("2.1  Architektura systemu")
    doc.p(
        "System oparty jest na architekturze klient-serwer z centralnym REST API jako "
        "jedynym punktem komunikacji. Trzy niezależne klienty (webowy, mobilny, desktopowy) "
        "komunikują się z API wyłącznie przez protokół HTTPS z tokenami JWT, co zapewnia "
        "spójne mechanizmy bezpieczeństwa na wszystkich platformach."
    )
    doc.code(
        "                   ┌──────────────────────┐\n"
        "                   │     REST API          │\n"
        "                   │  Django + JWT + MySQL │\n"
        "                   └──────────┬───────────┘\n"
        "            ┌─────────────────┼─────────────────┐\n"
        "            ▼                 ▼                  ▼\n"
        "  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐\n"
        "  │ Aplik. webowa│  │ Aplik. mob.  │  │ Aplik. desk. │\n"
        "  │    Django    │  │   Flutter    │  │  C# + WPF    │\n"
        "  └──────────────┘  └──────────────┘  └──────────────┘"
    )

    doc.h2("2.2  Backend – REST API")
    doc.h3("2.2.1  Technologie i biblioteki")
    cols   = ["Technologia / Biblioteka", "Zastosowanie"]
    widths = [80, 80]
    rows2 = [
        ("Python 3.x",                        "Język programowania"),
        ("Django 6.0.3",                      "Framework webowy"),
        ("Django REST Framework 3.16.1",      "Budowa REST API"),
        ("djangorestframework-simplejwt 5.5.1","Obsługa tokenów JWT"),
        ("PyJWT 2.12.1",                      "Generowanie i walidacja tokenów JWT"),
        ("MySQL",                              "Produkcyjna baza danych"),
        ("SQLite",                             "Lokalna baza danych (środ. deweloperskie)"),
        ("dj-database-url 3.1.2",             "Konfiguracja bazy przez zmienną środowiskową"),
        ("Gunicorn 25.3.0",                   "Serwer WSGI dla środowiska produkcyjnego"),
        ("WhiteNoise 6.12.0",                 "Serwowanie plików statycznych"),
        ("python-dotenv 1.2.2",               "Zarządzanie zmiennymi środowiskowymi"),
    ]
    doc.table_header(cols, widths)
    for i,row in enumerate(rows2):
        doc.table_row(list(row), widths, shade=(i%2==0))
    doc.ln(4)

    doc.h3("2.2.2  Struktura modułów Django")
    for m, d in [
        ("users",        "rejestracja, logowanie, zarządzanie profilem, reset hasła"),
        ("tasks",        "pełne operacje CRUD na zadaniach"),
        ("projects",     "zarządzanie projektami"),
        ("invitations",  "system zaproszeń do projektów"),
        ("notifications","powiadomienia systemowe"),
        ("admin_login",  "uwierzytelnianie administratora"),
        ("main_page",    "główny widok aplikacji webowej"),
    ]:
        doc.li(m, "– " + d)
    doc.ln(2)

    doc.h3("2.2.3  Główne endpointy REST API")
    cols   = ["Ścieżka", "Opis"]
    widths = [80, 80]
    ep = [
        ("POST /api/token",              "Uzyskanie tokenów JWT (logowanie)"),
        ("POST /api/token/refresh",      "Odświeżenie tokenu dostępowego"),
        ("POST /api/auth/",              "Rejestracja nowego użytkownika"),
        ("GET|PUT /api/users",           "Operacje na danych użytkowników"),
        ("POST /api/users/logout/",      "Wylogowanie (unieważnienie tokenu)"),
        ("GET|POST|PUT|DELETE /api/tasks","Operacje CRUD na zadaniach"),
        ("GET|POST|PUT|DELETE /api/projects","Operacje CRUD na projektach"),
        ("GET|POST /api/invitations",    "Zarządzanie zaproszeniami"),
        ("GET /api/notifications",       "Pobieranie powiadomień"),
        ("GET /api/docs/",               "Dokumentacja API (Swagger / ReDoc)"),
    ]
    doc.table_header(cols, widths)
    for i,row in enumerate(ep):
        doc.table_row(list(row), widths, shade=(i%2==0))
    doc.ln(4)

    doc.h3("2.2.4  Mechanizmy bezpieczeństwa")
    for lbl, desc in [
        ("JWT (JSON Web Tokens)","tokeny dostępowe o czasie życia 15 min, tokeny odświeżające ważne 24 h,"),
        ("OAuth 2.0 (Google Sign-In)","logowanie przez konto Google,"),
        ("2FA / TOTP","dwuskładnikowe uwierzytelnianie oparte na algorytmie jednorazowych haseł opartych na czasie,"),
        ("HTTPS / TLS","szyfrowanie całej komunikacji klient–serwer,"),
        ("Haszowanie haseł","algorytmy bcrypt / PBKDF2,"),
        ("Reset hasła tokenami jednorazowymi","link do resetu wysyłany na adres e-mail użytkownika,"),
        ("Ochrona CSRF","middleware Django z konfiguracją zaufanych źródeł,"),
        ("Walidatory hasła","wymagania dotyczące złożoności (długość, niepodobność do loginu, brak popularnych wartości)."),
    ]:
        doc.li(lbl, "– " + desc)
    doc.ln(2)

    doc.h2("2.3  Aplikacja webowa")
    doc.p("Aplikacja webowa pełni rolę panelu administracyjnego systemu, dostępnego z poziomu dowolnej przeglądarki internetowej.")
    cols   = ["Technologia", "Zastosowanie"]
    widths = [70, 90]
    doc.table_header(cols, widths)
    for i,row in enumerate([
        ("Python + Django",  "Logika serwerowa, obsługa żądań HTTP"),
        ("Django Templates", "Renderowanie HTML po stronie serwera"),
        ("Bootstrap 5",      "Responsywny framework CSS"),
        ("Crispy Forms",     "Formatowanie formularzy Django"),
    ]):
        doc.table_row(list(row), widths, shade=(i%2==0))
    doc.ln(4)

    doc.h2("2.4  Aplikacja mobilna")
    doc.p(
        "Aplikacja mobilna zapewnia pełny dostęp do systemu z urządzeń przenośnych. "
        "Dzięki technologii Flutter zbudowana jest jako pojedyncza baza kodu działająca "
        "natywnie na platformach Android i iOS."
    )
    cols   = ["Biblioteka", "Zastosowanie"]
    widths = [75, 85]
    doc.table_header(cols, widths)
    for i,row in enumerate([
        ("Flutter SDK ^3.10.7",              "Framework UI (Android + iOS)"),
        ("Dart",                             "Język programowania"),
        ("http ^1.2.0",                      "Komunikacja z REST API"),
        ("flutter_secure_storage ^9.0.0",    "Bezpieczne przechowywanie tokenów JWT"),
        ("provider ^6.1.2",                  "Zarządzanie stanem (wzorzec Provider)"),
        ("go_router ^14.2.7",               "Nawigacja między ekranami"),
        ("pin_code_fields ^8.0.0",          "Interfejs wprowadzania kodu 2FA"),
        ("shared_preferences ^2.3.2",       "Lokalne przechowywanie ustawień"),
        ("intl ^0.20.2",                    "Internacjonalizacja i formatowanie dat"),
    ]):
        doc.table_row(list(row), widths, shade=(i%2==0))
    doc.ln(4)
    doc.p("Tokeny JWT przechowywane są w bezpiecznym schowku systemu operacyjnego (flutter_secure_storage), co chroni je przed dostępem innych aplikacji.")

    doc.h2("2.5  Aplikacja desktopowa")
    doc.p("Aplikacja desktopowa działa w środowisku Windows i udostępnia pełen zestaw funkcjonalności dla użytkowników końcowych oraz administratorów.")
    cols   = ["Technologia / Biblioteka", "Zastosowanie"]
    widths = [80, 80]
    doc.table_header(cols, widths)
    for i,row in enumerate([
        ("C# + .NET 10.0",                   "Język i platforma programistyczna"),
        ("WPF (Windows Presentation Foundation)","Framework interfejsu użytkownika"),
        ("CommunityToolkit.Mvvm 8.4.0",      "Implementacja wzorca MVVM"),
        ("Entity Framework Core (SQLite) 10.0.0","Lokalna baza danych"),
        ("Newtonsoft.Json 13.0.4",           "Serializacja i deserializacja JSON"),
    ]):
        doc.table_row(list(row), widths, shade=(i%2==0))
    doc.ln(4)
    doc.p(
        "Aplikacja desktopowa zaprojektowana jest zgodnie ze wzorcem MVVM. "
        "Komunikacja z REST API odbywa się przez klasę ApiService.cs, natomiast "
        "lokalna baza danych SQLite zarządzana przez AppDbContext.cs pełni rolę "
        "lokalnej pamięci podręcznej."
    )

    doc.h2("2.6  Infrastruktura i wdrożenie")
    doc.h3("2.6.1  Konteneryzacja – Docker")
    doc.p("Backend systemu jest w pełni skonteneryzowany. Dostępne są dwie konfiguracje Docker Compose:")
    doc.li("docker-compose.yml", "– środowisko deweloperskie,")
    doc.li("docker-compose.prod.yml", "– środowisko produkcyjne (Gunicorn + WhiteNoise).")
    doc.ln(2)

    doc.h3("2.6.2  Potok CI/CD – GitHub Actions")
    doc.p(
        "Repozytorium zawiera skonfigurowany potok ciągłej integracji "
        "(.github/workflows/ci.yml), uruchamiany automatycznie przy każdym "
        "wypchnięciu zmian do gałęzi main. Pipeline wykonuje: "
        "1) budowanie obrazu Docker z argumentami środowiskowymi, "
        "2) uruchomienie pakietu testów Django (python manage.py test)."
    )

    doc.h3("2.6.3  Wdrożenie produkcyjne")
    doc.p(
        "System produkcyjny hostowany jest na platformie Render. "
        "Dostęp do aplikacji możliwy jest przez zabezpieczone połączenie HTTPS pod adresem: "
        "https://system-zarzadzania-zespolem-bsizmp.onrender.com"
    )
    doc.p("Kod źródłowy projektu dostępny jest w repozytorium GitHub: "
          "https://github.com/Wsemp/System-zarzadzania-zespolem-BSIZMP")

    # ════════════════════════════════════════════════════════════════════
    # ROZDZIAŁ 3 – PODZIAŁ OBOWIĄZKÓW
    # ════════════════════════════════════════════════════════════════════
    doc.add_page()
    doc.h1(3, "Podział obowiązków i odpowiedzialności w zespole")

    doc.h2("3.1  Ogólny podział prac")
    doc.p(
        "Prace projektowe zostały równo podzielone pomiędzy trzech członków zespołu "
        "według specjalizacji technologicznych. Każda osoba była wyłącznie odpowiedzialna "
        "za jedną platformę kliencką, a cały zespół współpracował przy projektowaniu "
        "wspólnego kontraktu API."
    )
    cols   = ["Członek zespołu", "Platforma", "Zakres odpowiedzialności"]
    widths = [42, 32, 86]
    doc.table_header(cols, widths)
    for i, row in enumerate([
        ("Wiktor Semp",   "Aplikacja webowa",
         "REST API i aplik. webowa w Django; JWT, OAuth 2.0; panel admina; Docker; CI/CD; wdrożenie na Render"),
        ("Daniel Kozak",  "Aplikacja desktopowa",
         "Aplik. desktopowa C# + .NET (WPF); klient REST API; JWT w .NET; SQLite; architektura MVVM"),
        ("Emilia Małecka","Aplikacja mobilna",
         "Aplik. mobilna Flutter/Dart; bezpieczne przechowywanie tokenów; interfejs 2FA (TOTP); Provider; go_router"),
    ]):
        doc.table_row(list(row), widths, bold_first=True, shade=(i%2==0))
    doc.ln(4)

    doc.h2("3.2  Wiktor Semp – Aplikacja webowa i backend")
    doc.p("Wiktor Semp odpowiadał za implementację całego backendu i warstwy webowej. W ramach obowiązków zrealizował:")
    for t in [
        "konfigurację projektu Django i struktury aplikacji (moduły: users, tasks, projects, invitations, notifications, admin_login, main_page),",
        "implementację REST API przy użyciu Django REST Framework ze wszystkimi endpointami CRUD,",
        "konfigurację uwierzytelniania JWT (czas życia tokenów, odświeżanie),",
        "integrację logowania przez Google OAuth 2.0,",
        "implementację resetu hasła z tokenami jednorazowymi wysyłanymi pocztą elektroniczną,",
        "konfigurację ochrony CSRF i nagłówków bezpieczeństwa,",
        "przygotowanie konfiguracji Docker (deweloperskiej i produkcyjnej),",
        "uruchomienie potoku CI/CD w GitHub Actions,",
        "wdrożenie systemu na platformę Render wraz z konfiguracją środowiska produkcyjnego.",
    ]:
        doc.li(t)
    doc.ln(2)

    doc.h2("3.3  Daniel Kozak – Aplikacja desktopowa")
    doc.p("Daniel Kozak odpowiadał za implementację aplikacji desktopowej w technologii C# + .NET. W ramach obowiązków zrealizował:")
    for t in [
        "architekturę aplikacji WPF opartą na wzorcu MVVM (CommunityToolkit.Mvvm),",
        "implementację widoków: logowania (LoginView.xaml), rejestracji (RegisterWindow.xaml), głównego okna (MainWindow.xaml), dodawania zadań (AddTaskWindow.xaml),",
        "implementację serwisu API (ApiService.cs) komunikującego się z REST API przez HttpClient,",
        "obsługę tokenów JWT – przechowywanie, odświeżanie i wylogowywanie w środowisku Windows,",
        "implementację lokalnej bazy danych SQLite przez Entity Framework Core (AppDbContext.cs),",
        "obsługę modeli danych: UserModel, TaskModel, ProjectModel, NotificationModel, InvitationModel, UserCredential, UserLogin,",
        "implementację serwisu powiadomień (NotificationService.cs).",
    ]:
        doc.li(t)
    doc.ln(2)

    doc.h2("3.4  Emilia Małecka – Aplikacja mobilna")
    doc.p("Emilia Małecka odpowiadała za implementację aplikacji mobilnej w technologii Flutter. W ramach obowiązków zrealizowała:")
    for t in [
        "architekturę aplikacji Flutter z wzorcem Provider do zarządzania stanem,",
        "implementację warstw aplikacji: core, models, providers, screens, services, widgets,",
        "bezpieczne przechowywanie tokenów JWT przy użyciu flutter_secure_storage (szyfrowany schowek systemu operacyjnego),",
        "implementację interfejsu użytkownika dla dwuskładnikowego uwierzytelniania (2FA / TOTP) z komponentem pin_code_fields,",
        "konfigurację nawigacji przy użyciu go_router,",
        "implementację warstwy usług komunikującej się z REST API przez pakiet http,",
        "obsługę powiadomień na platformach Android i iOS.",
    ]:
        doc.li(t)

    # ════════════════════════════════════════════════════════════════════
    # ROZDZIAŁ 4 – INSTRUKCJA URUCHOMIENIA
    # ════════════════════════════════════════════════════════════════════
    doc.add_page()
    doc.h1(4, "Instrukcja lokalnego i zdalnego uruchomienia systemu")

    doc.h2("4.1  Wymagania wstępne")
    doc.p("Przed przystąpieniem do uruchomienia należy upewnić się, że w środowisku zainstalowane są:")
    for lbl, desc in [
        ("Git","– system kontroli wersji,"),
        ("Python 3.11+","– wymagany do uruchomienia backendu Django,"),
        ("Flutter SDK 3.10.7+","– wymagany do uruchomienia aplikacji mobilnej,"),
        ("Visual Studio 2022 lub JetBrains Rider","– z obsługą .NET 10, wymagany do aplikacji desktopowej,"),
        ("Docker Desktop","– opcjonalny, umożliwia uruchomienie backendu w kontenerze."),
    ]:
        doc.li(lbl, desc)
    doc.ln(2)

    doc.h2("4.2  Pobranie kodu źródłowego")
    doc.code(
        "git clone https://github.com/Wsemp/System-zarzadzania-zespolem-BSIZMP.git\n"
        "cd System-zarzadzania-zespolem-BSIZMP"
    )

    doc.h2("4.3  Lokalne uruchomienie")
    doc.h3("4.3.1  Backend – REST API (Django)")
    doc.p("1.  Przejdź do katalogu backendu i utwórz wirtualne środowisko:")
    doc.code(
        "cd webapp\n"
        "python -m venv venv\n\n"
        "# Windows:\n"
        "venv\\Scripts\\activate\n\n"
        "# Linux / macOS:\n"
        "source venv/bin/activate"
    )
    doc.p("2.  Zainstaluj zależności:")
    doc.code("pip install -r requirements.txt")
    doc.p("3.  Utwórz plik .env w katalogu webapp/:")
    doc.code(
        "SECRET_KEY=twoj-tajny-klucz-django\n"
        "DEBUG=True\n"
        "ALLOWED_HOSTS=localhost,127.0.0.1\n"
        "DATABASE_URL=sqlite:///db.sqlite3\n"
        "EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend"
    )
    doc.p("4.  Wykonaj migracje i utwórz konto administratora:")
    doc.code(
        "python manage.py migrate\n"
        "python manage.py createsuperuser"
    )
    doc.p("5.  Uruchom serwer deweloperski:")
    doc.code("python manage.py runserver")
    doc.p("API dostępne pod: http://127.0.0.1:8000/  |  Dokumentacja: http://127.0.0.1:8000/api/docs/")

    doc.h3("4.3.2  Alternatywnie – uruchomienie przez Docker")
    doc.code(
        "cd webapp\n"
        "docker-compose up --build"
    )

    doc.h3("4.3.3  Aplikacja mobilna (Flutter)")
    doc.p("1.  Przejdź do katalogu aplikacji mobilnej i pobierz zależności:")
    doc.code(
        "cd mobileapp\n"
        "flutter pub get"
    )
    doc.p(
        "2.  Upewnij się, że adres API wskazuje na lokalny backend: "
        "http://10.0.2.2:8000/api/ (emulator Android) lub "
        "http://192.168.x.x:8000/api/ (urządzenie fizyczne przez USB)."
    )
    doc.p("3.  Uruchom aplikację:")
    doc.code("flutter run")

    doc.h3("4.3.4  Aplikacja desktopowa (C# + .NET / WPF)")
    doc.p("1.  Otwórz plik desktopapp/desktopapp.slnx w Visual Studio 2022 lub JetBrains Rider.")
    doc.p("2.  W pliku Services/ApiService.cs ustaw adres lokalnego backendu:")
    doc.code('private const string BaseUrl = "http://localhost:8000/api/";')
    doc.p("3.  Przywróć pakiety NuGet (automatycznie przy otwarciu projektu) i uruchom:")
    doc.code(
        "# Visual Studio: klawisz F5\n\n"
        "# lub z terminala:\n"
        "dotnet run --project desktopapp/desktopapp/desktopapp.csproj"
    )

    doc.h2("4.4  Zdalne uruchomienie – środowisko produkcyjne")
    doc.h3("4.4.1  Dostęp do wdrożonej aplikacji")
    doc.p(
        "Aplikacja backendowa i webowa jest wdrożona na platformie Render i dostępna przez "
        "zabezpieczone połączenie HTTPS pod adresem:\n"
        "https://system-zarzadzania-zespolem-bsizmp.onrender.com"
    )

    doc.h3("4.4.2  Aplikacja mobilna z produkcyjnym API")
    doc.p("Aby zbudować plik instalacyjny APK z produkcyjnym backendem:")
    doc.code(
        "cd mobileapp\n"
        "flutter pub get\n"
        "flutter build apk --release\n\n"
        "# Wynikowy plik:\n"
        "# build/app/outputs/flutter-apk/app-release.apk"
    )

    doc.h3("4.4.3  Własna instancja produkcyjna")
    doc.p("1.  Skonfiguruj zmienne środowiskowe dla środowiska produkcyjnego:")
    doc.code(
        "SECRET_KEY=<silny-losowy-klucz>\n"
        "DEBUG=False\n"
        "ALLOWED_HOSTS=twoja-domena.com\n"
        "DATABASE_URL=mysql://user:pass@host:3306/dbname\n"
        "EMAIL_HOST=smtp.gmail.com\n"
        "EMAIL_PORT=587\n"
        "EMAIL_USE_TLS=True\n"
        "EMAIL_HOST_USER=adres@gmail.com\n"
        "EMAIL_HOST_PASSWORD=haslo-aplikacji"
    )
    doc.p("2.  Uruchom produkcyjną konfigurację Docker Compose:")
    doc.code("docker-compose -f docker-compose.prod.yml up -d --build")

    # ════════════════════════════════════════════════════════════════════
    # ROZDZIAŁ 5 – WNIOSKI PROJEKTOWE
    # ════════════════════════════════════════════════════════════════════
    doc.add_page()
    doc.h1(5, "Wnioski projektowe")

    doc.h2("5.1  Wiktor Semp")
    doc.p(
        "Realizacja projektu Task Manager była dla mnie bardzo wartościowym doświadczeniem "
        "praktycznym w obszarze tworzenia bezpiecznych systemów informatycznych. "
        "Implementacja backendu w Django REST Framework uświadomiła mi, jak wiele aspektów "
        "bezpieczeństwa należy uwzględniać już na etapie projektowania architektury – "
        "bezpieczeństwo nie może być traktowane jako funkcjonalność dodawana post factum."
    )
    doc.p(
        "Szczególnie pouczające okazało się wdrożenie mechanizmów uwierzytelniania JWT "
        "oraz integracja z OAuth 2.0. Zrozumiałem, że właściwe zarządzanie czasem życia "
        "tokenów i ich unieważnianiem jest kluczowe dla ochrony sesji użytkownika. "
        "Skonfigurowanie potoku CI/CD w GitHub Actions oraz wdrożenie na platformę Render "
        "pozwoliło mi zapoznać się z nowoczesnym podejściem DevSecOps."
    )
    doc.p(
        "Najtrudniejszym wyzwaniem była konfiguracja CORS i CSRF między wieloma klientami "
        "(webowym, mobilnym, desktopowym), gdyż każda platforma ma odmienne wymagania "
        "dotyczące nagłówków żądań. Projekt umocnił moje przekonanie, że bezpieczeństwo "
        "systemu jest zagadnieniem wielowymiarowym, wymagającym spójnego podejścia na "
        "wszystkich poziomach architektury."
    )

    doc.h2("5.2  Daniel Kozak")
    doc.p(
        "Udział w projekcie Task Manager pozwolił mi pogłębić wiedzę z zakresu programowania "
        "aplikacji desktopowych w technologii WPF z zastosowaniem wzorca MVVM. Implementacja "
        "klienta REST API w C# wymagała dokładnego zapoznania się z mechanizmami JWT oraz "
        "zarządzania cyklem życia tokenów w środowisku .NET."
    )
    doc.p(
        "Wzorzec MVVM okazał się bardzo dobrym wyborem architektonicznym – wyraźne "
        "rozdzielenie logiki biznesowej (ViewModels), modeli danych i interfejsu (Views) "
        "znacznie ułatwiło utrzymanie i testowanie kodu. Wyzwaniem była obsługa "
        "asynchronicznych żądań HTTP w aplikacji WPF z jednoczesnym zachowaniem "
        "responsywności interfejsu użytkownika."
    )
    doc.p(
        "Praca w trzyosobowym zespole nauczyła mnie znaczenia precyzyjnego kontraktu API – "
        "każda zmiana w backendzie musiała być natychmiast komunikowana, aby nie powodować "
        "regresji po stronie klienta desktopowego. Projekt uświadomił mi, że integracja "
        "bezpieczeństwa w aplikacjach desktopowych wymaga równie starannego podejścia jak "
        "w aplikacjach webowych, szczególnie w kontekście bezpiecznego przechowywania "
        "danych uwierzytelniających."
    )

    doc.h2("5.3  Emilia Małecka")
    doc.p(
        "Praca nad aplikacją mobilną w technologii Flutter była dla mnie cennym "
        "doświadczeniem, które pozwoliło mi poznać specyfikę tworzenia wieloplatformowych "
        "aplikacji mobilnych z silnym naciskiem na bezpieczeństwo. Implementacja bezpiecznego "
        "przechowywania tokenów JWT przy użyciu flutter_secure_storage uświadomiła mi, "
        "jak różne są wymagania bezpieczeństwa dla środowisk mobilnych w porównaniu "
        "z aplikacjami webowymi."
    )
    doc.p(
        "Implementacja dwuskładnikowego uwierzytelniania (2FA) z protokołem TOTP była "
        "technicznie najbardziej wymagającą częścią projektu. Konieczność zapewnienia "
        "intuicyjnego interfejsu dla procesu konfiguracji 2FA wymagała starannego "
        "przemyślenia przepływu ekranów i komunikatów błędów, tak aby była zrozumiała "
        "dla użytkowników nieposiadających doświadczenia technicznego."
    )
    doc.p(
        "Wzorzec zarządzania stanem oparty na Provider okazał się efektywny dla tej skali "
        "aplikacji. Projekt ugruntował moje przekonanie, że bezpieczeństwo mobilne jest "
        "osobną dyscypliną, wymagającą uwzględnienia specyfiki platform Android i iOS – "
        "zarządzania pamięcią, uprawnień systemowych oraz integracji z mechanizmami "
        "biometrycznymi urządzenia."
    )

    doc.output(OUT)
    print(f"PDF zapisany: {OUT}")


if __name__ == "__main__":
    build()
