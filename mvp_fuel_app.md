# MVP -- Aplikacja do notowania wydatków na paliwo i zasięgu

**Data:** 24.08.2025\
**Opis (od użytkownika):** Aplikacja tylko dla mnie, dostęp z telefonu i
komputera (PWA). Chcę zapisywać: litry, kwotę w PLN, zasięg km przed i
po tankowaniu (z komputera auta) oraz przebieg przy każdym tankowaniu.
Automatyczne wyliczenia: cena/litr, średnie spalanie (z uwzględnieniem
niepełnych tankowań), koszt/100 km. Lista wpisów + proste wykresy. Bez
eksportu CSV. Dodatkowo wskaźnik „trafności prognozy zasięgu".

------------------------------------------------------------------------

## 1. Problem / potrzeba

-   Ręczne śledzenie kosztów paliwa oraz realnego zużycia by podejmować
    decyzje (styl jazdy, trasy, koszty).\
-   Notatki mają być szybkie (1 formularz), a analityka minimalna i
    czytelna.\
-   Dostęp z telefonu i desktopu, bez utraty czasu na instalacje --
    dlatego PWA.

## 2. Grupa docelowa

-   Jeden użytkownik (właściciel).\
-   Jeden samochód (na tę chwilę).\
-   Brak potrzeby współdzielenia danych i ról.

## 3. Kluczowe funkcje MVP

1)  **Rejestr tankowania**
    -   Pola: data/godzina, litry, kwota PLN, zasięg przed/po (z
        komputera), przebieg, **czy pełny bak** (`is_full_tank`:
        TAK/NIE).\
    -   Walidacje: `liters>0`, `amount_pln>0`, `odometer_km` rosnący,
        `range_after_km ≥ range_before_km`.
2)  **Automatyczne wyliczenia**
    -   **Cena/litr** = `amount_pln / liters`.\
    -   **Średnie spalanie (l/100 km)** -- metoda „full-to-full":
        -   Spalanie liczymy **tylko** od poprzedniego pełnego baku do
            kolejnego pełnego baku.\
        -   `distance = odometer_full_now − odometer_prev_full`\
        -   `fuel_used = suma(liters) ze wszystkich wpisów od prev_full (excl.) do nowego full (incl.)`\
        -   `consumption = (fuel_used / distance) * 100`\
        -   Dla odcinków bez „pełnego" -- spalanie = *brak danych*.
    -   **Koszt/100 km** dla odcinka full--full:
        -   `cost_per_100km = (suma(amount_pln) / distance) * 100`.
3)  **Trafność prognozy zasięgu**
    -   Dla wpisu *i* porównujemy `range_after_i` z **realnym
        dystansem** do kolejnego tankowania:
        -   `actual_distance = odometer_{i+1} − odometer_i`\
        -   `range_error_pct = |range_after_i − actual_distance| / max(range_after_i,1) * 100%`\
        -   **Accuracy** = `100% − range_error_pct` (przytnij 0--100%).\
    -   Prezentacja: wartość i trend (linia + średnia krocząca).
4)  **Lista wpisów + filtry**
    -   Kolumny: data, litry, kwota, cena/l, przebieg, dystans od
        poprzedniego wpisu, spalanie (jeśli pełny odcinek), koszt/100
        km, zasięg przed/po, `is_full_tank`.\
    -   Sortowanie po dacie (najnowsze u góry), filtr po `is_full_tank`.
5)  **Wykresy (analityka prosta)**
    -   Trend **ceny za litr** w czasie.\
    -   Trend **spalania l/100 km** (pokazuje tylko odcinki
        full--full).\
    -   Trend **trafności prognozy zasięgu**.
6)  **UX wprowadzania**
    -   Jeden formularz „Quick Add" z autofokusem i skrótem Enter =
        Zapisz.\
    -   Podpowiedzi/domknięcia: domyślna kwota lub litry na bazie
        poprzedniego wpisu (jako hint, nie auto-wypełnienie), domyślny
        `is_full_tank = TAK`.

## 4. Funkcje nice-to-have (po MVP)

-   Autouzupełnianie ceny/l w oparciu o ostatnie wpisy (wyliczenie w
    locie).\
-   Proste notatki/znaczniki (np. styl jazdy, trasa).\
-   Tryb offline z kolejką zapisów (rozszerzone cache).\
-   Ekran „insights" (średnia z 30/90 dni, sezonowość).\
-   Obsługa wielu pojazdów.

## 5. Propozycje stacków technologicznych

**Preferowany: Streamlit + Supabase (Postgres) -- PWA** - **Frontend**:
Streamlit (formularze, tabele, wykresy -- Altair/Plotly).\
- **Backend/DB**: Supabase (Postgres + Auth: e‑mail/hasło).\
- **Auth**: pojedyncze konto.\
- **Hosting**: Streamlit Community Cloud + Supabase (free tiers).

**Alternatywy:** - **n8n + Google Sheets/Airtable + prosty frontend
(Streamlit/HTML)** -- szybkie prototypowanie automatyzacji (np. alerty),
ale więcej „klejenia".\
- **Next.js (React) + Supabase + PWA** -- pełna kontrola UX, większy
nakład pracy.

## 6. Walidacja MVP

-   Kryteria sukcesu (2--4 tyg. użycia):
    -   Wprowadzenie ≥ 90% tankowań bez opóźnień (\>24h).\
    -   Brak „pustych" danych dzięki walidacjom (0 błędów krytycznych).\
    -   Wgląd w **spalanie** dla ≥ 80% dystansów (czyli większość
        odcinków full--full).\
    -   Zrozumiały trend **trafności prognozy** (co najmniej 5--6
        kolejnych punktów).\
-   Metody: dzienna rutina wpisu, przegląd wykresów raz/tydz., notatka
    co przeszkadza -\> iteracja.

## 7. Ryzyka i założenia

-   **Niepełne tankowania** utrudniają natychmiastowy odczyt spalania --
    obsłużone przez metodę full--full i flagę `is_full_tank`.\
-   **PWA**: mobilny UX Streamlit może mieć ograniczenia (klawiatura
    mobilna, scroll).\
-   **Jedno konto**: brak recov. 2FA na start -- pamiętaj o silnym haśle
    i e‑mailu odzyskiwania.\
-   **Dane z komputera auta (zasięg)** nie są metryką inżynieryjną --
    dlatego pokazujemy **accuracy**, nie „błąd absolutny" jako jedyny.

## 8. Plan + szacunkowy czas i koszt (1 osoba)

### 8.1. Backlog techniczny (MVP)

1)  **Schemat bazy (Supabase / Postgres)** -- 2--3h
    -   Tabela `fuel_entry`:
        -   `id uuid pk`, `created_at timestamptz default now()`,
            `ts timestamptz not null`,\
        -   `liters numeric(6,2)`, `amount_pln numeric(8,2)`,\
        -   `range_before_km int`, `range_after_km int`,\
        -   `odometer_km int`, `is_full_tank boolean default true`,\
        -   indeks po `ts`, constraint „odometer rosnący" egzekwowany
            aplikacyjnie.\
    -   (Opcj.) widok `consumption_segments` liczony w aplikacji (na
        start bez materializacji).
2)  **Aplikacja Streamlit** -- 10--14h
    -   Ekran **Quick Add** z walidacjami i autofokusem.\
    -   Ekran **Lista** z sortowaniem i filtrami.\
    -   Ekran **Analityka**: 3 wykresy (cena/l, spalanie, accuracy).\
    -   Funkcje pomocnicze: obliczanie odcinków full--full, accuracy,
        dystanse.
3)  **Auth (Supabase)** -- 1--2h
    -   Rejestracja jednego użytkownika, logowanie, ochrona widoków.
4)  **Styling/UX mobilny** -- 3--4h
    -   Uproszczone layouty, większe pola dotykowe, skróty klawiszowe na
        desktopie.
5)  **Testy + dane przykładowe** -- 2--3h
    -   Sprawdzenie edge cases (pierwszy wpis, brak poprzedniego full,
        bardzo małe dystanse).
6)  **Deploy (Streamlit Cloud + Supabase)** -- 1--2h

**Suma:** ok. **19--28 godzin** czystej pracy.

### 8.2. Koszty operacyjne

-   **Supabase (Free Tier)** -- 0 zł / mc na start.\
-   **Streamlit Community Cloud** -- 0 zł / mc na start.\
-   **Domena (opcjonalnie)** -- \~50--80 zł/rok (po MVP).

### 8.3. Kamienie milowe (1--2 tyg.)

-   **Dzień 1--2**: DB + Auth + Quick Add.\
-   **Dzień 3--4**: Lista + obliczenia full--full.\
-   **Dzień 5**: Wykresy + accuracy.\
-   **Dzień 6**: UX mobilny + testy.\
-   **Dzień 7**: Deploy i tygodniowa próba „w boju".

------------------------------------------------------------------------

### Załącznik: Algorytm „full-to-full" (precyzyjnie)

1)  Znajdź kolejne wpisy z `is_full_tank = true`: `F0`, `F1`, `F2`, ...\
2)  Dla odcinka `(F0, F1]`:
    -   `distance = odometer(F1) − odometer(F0)`\
    -   `fuel_used = Σ liters` z wpisów po `F0` aż do `F1` (włącznie).\
    -   `consumption_l_100 = (fuel_used / distance) * 100`,\
    -   `cost_per_100km = (Σ amount_pln / distance) * 100`.\
3)  Dla wpisu `Ei` (dowolnego): accuracy liczymy względem następnego
    wpisu `Ei+1`:
    -   `actual_distance = odometer(Ei+1) − odometer(Ei)`\
    -   `accuracy = clamp(100 − |range_after(Ei) − actual_distance| / max(range_after(Ei),1) * 100, 0, 100)`.
