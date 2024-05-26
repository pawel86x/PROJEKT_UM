import pandas as pd
import RankingElo as re

elo = re.Elo()
def wynik(gole_a: int, gole_b: int) -> int:
    """Rozstrzygnięcie meczu:
        1 - wygrana gospodarz, 0 - remis, 2 - wygrana gości"""
    return 1 if gole_a > gole_b else (2 if gole_a < gole_b else 0)

def czy_1x(gole_a: int, gole_b: int) -> int:
    return 1 if gole_a >= gole_b else 0

def czy_remis(gole_a: int, gole_b: int) -> int:
    return 1 if gole_a == gole_b else 0

def ograniczenie_goli(gole_a: int, gole_b: int, maks_roznica: int = 3, maks_gole: int = 3) -> tuple:
    """
    Ograniczenie wyniku aby zmniejszyć wpływ wysokich zwycięstw. Każda drużyna może maksymalnie strzelić
    maks_gole bramek, a różnica pomiędzy ilościami zdobytych bramek nie może być większa niż maks_różnica
    Najpierw ograniczana jest różnica abs(gole_a-gole_b) a potem liczba zdobytych bramek.
    """
    roznica = gole_a - gole_b

    if roznica > maks_roznica:
        gole_a = gole_b + maks_roznica
    if -roznica > maks_roznica:
        gole_b = gole_a + maks_roznica
    cofniecie = max(gole_a - maks_gole, gole_b - maks_gole, 0)
    return gole_a - cofniecie, gole_b - cofniecie

def prawdopodobienstwa_kursow(kursy: list[float] | tuple[float]) -> tuple[float]:
    pr = [0] * (len(kursy) + 1)
    try:
        suma = sum([1/k for k in kursy])
        pr = [1/(k*suma) for k in kursy]
    finally:
        return tuple(pr)

def marza(kursy: list[float] | tuple[float]) -> float:
        return sum([1 / k for k in kursy]) - 1

def wylicz_elo(df: pd.DataFrame, kol_gole_a='GOLE_A', kol_gole_b='GOLE_B', a_wyjsciowa='ELO_A', b_wyjsciowa='ELO_B') -> pd.DataFrame:
    for liga_sezon, grupa in df.groupby(['LIGA', 'SEZON']):
        druzyny_elo: dict = {}
        for id, mecz in grupa.iterrows():
            druzyna_a = mecz['DRUZYNA_A']
            druzyna_b = mecz['DRUZYNA_B']
            gole_a = mecz[kol_gole_a]
            gole_b = mecz[kol_gole_b]

            if druzyna_a not in druzyny_elo:
                druzyny_elo[druzyna_a] = 1000
            if druzyna_b not in druzyny_elo:
                druzyny_elo[druzyna_b] = 1000

            stary_elo_a = druzyny_elo[druzyna_a]
            stary_elo_b = druzyny_elo[druzyna_b]
            nowy_elo_a, nowy_elo_b = elo.nowe_rankingi(stary_elo_a, stary_elo_b, gole_a, gole_b)
            druzyny_elo[druzyna_a], druzyny_elo[druzyna_b] = nowy_elo_a, nowy_elo_b

            df.at[id, a_wyjsciowa] = stary_elo_a
            df.at[id, b_wyjsciowa] = stary_elo_b
    df[a_wyjsciowa] += elo.przewaga_a
    return df

def nr_meczu(df: pd.DataFrame) -> pd.DataFrame:
    for liga_sezon, grupa in df.groupby(['LIGA', 'SEZON']):
        druzyny = {}
        for id, mecz in grupa.iterrows():
            druzyna_a = mecz['DRUZYNA_A']
            druzyna_b = mecz['DRUZYNA_B']

            if druzyna_a not in druzyny:
                druzyny[druzyna_a] = 0
            if druzyna_b not in druzyny:
                druzyny[druzyna_b] = 0

            druzyny[druzyna_a] += 1
            druzyny[druzyna_b] += 1

            df.at[id, 'NR_MECZU_A'] = druzyny[druzyna_a]
            df.at[id, 'NR_MECZU_B'] = druzyny[druzyna_b]
    return df

def oczekiwane_gole(df: pd.DataFrame,
               kol_gole_a='GOLE_A',
               kol_gole_b='GOLE_B',
               a_wyjsciowa='SILA_A',
               b_wyjsciowa='SILA_B'
               ) -> pd.DataFrame:
    for liga_sezon, grupa in df.groupby(['LIGA', 'SEZON']):
        for id, mecz in grupa.iterrows():
            filtr = (grupa['DATA'] < mecz['DATA']) & (grupa['DRUZYNA_A'] == mecz['DRUZYNA_A'])
            sr_a_dom_strzelone = grupa.loc[filtr, kol_gole_a].mean()
            sr_a_dom_stracone = grupa.loc[filtr,kol_gole_b].mean()
            filtr = (grupa['DATA'] < mecz['DATA']) & (grupa['DRUZYNA_B'] == mecz['DRUZYNA_B'])
            sr_b_wyjazd_strzelone = grupa.loc[filtr, kol_gole_b].mean()
            sr_b_wyjazd_stracone = grupa.loc[filtr, kol_gole_a].mean()
            filtr = (grupa['DATA'] < mecz['DATA'])
            sr_gole_a = grupa.loc[filtr, kol_gole_a].mean()
            sr_gole_b = grupa.loc[filtr, kol_gole_b].mean()
            try:
                df.at[id, a_wyjsciowa] = sr_a_dom_strzelone * sr_b_wyjazd_stracone / sr_gole_a
                df.at[id, b_wyjsciowa] = sr_b_wyjazd_strzelone * sr_a_dom_stracone / sr_gole_b
            except:
                df.at[id, a_wyjsciowa] = 0
                df.at[id, b_wyjsciowa] = 0
    return df.fillna(0)

def prawdopodobienstwa(df: pd.DataFrame) -> pd.DataFrame:
    for id, mecz in df.iterrows():
        df.at[id, 'PR1'], df.at[id, 'PRX'], df.at[id, 'PR2'] = (
            prawdopodobienstwa_kursow([df.at[id, 'B365H'], df.at[id, 'B365D'], df.at[id, 'B365A']])
        )
    return df.fillna(0)

def wyniki(df: pd.DataFrame) -> pd.DataFrame:
    for id, mecz in df.iterrows():
        df.at[id, 'GOLE_A_OGR'], df.at[id, 'GOLE_B_OGR'] = ograniczenie_goli(df.at[id, 'GOLE_A'], df.at[id, 'GOLE_B'])
        df.at[id, 'WYNIK'] = wynik(df.at[id, 'GOLE_A'], df.at[id, 'GOLE_B'])
        df.at[id, 'CZY_1X'] = czy_1x(df.at[id, 'GOLE_A'], df.at[id, 'GOLE_B'])
    return df

def n_poprzednich_meczy(df: pd.DataFrame, n: int, id: int, ab: str = 'A', dom_wyj: str = 'DW') -> dict:
    elo = re.Elo()
    druzyna = df.at[id, 'DRUZYNA_A'] if ab == 'A' else df.at[id, 'DRUZYNA_B']
    if dom_wyj == 'DW':
        filtr = (
                (df['ID'] < df.at[id, 'ID']) &
                ((df['DRUZYNA_A'] == druzyna) | (df['DRUZYNA_B'] == druzyna))
        )
    if dom_wyj == 'D':
        filtr = (
                (df['ID'] < df.at[id, 'ID']) &
                (df['DRUZYNA_A'] == druzyna)
        )
    if dom_wyj == 'W':
        filtr = (
                (df['ID'] < df.at[id, 'ID']) &
                (df['DRUZYNA_B'] == druzyna)
        )
    dane = df[filtr]
    dane = dane.tail(n) if n > 0 else dane
    przeciwnicy_elo = []
    przeciwnicy = []
    id_meczy = []
    wyniki = []
    punkty = 0
    for nr, wiersz in dane.iterrows():
        id_meczy.append(nr)
        if dane.at[nr, 'DRUZYNA_A'] == druzyna:
            przeciwnicy.append(dane.at[nr, 'DRUZYNA_B'])
            przeciwnicy_elo.append(dane.at[nr, 'ELO_B'])
            wyniki.append(elo.wynik(dane.at[nr, 'GOLE_A'], dane.at[nr, 'GOLE_B']))
            punkty += elo.punkty(dane.at[nr, 'GOLE_A'], dane.at[nr, 'GOLE_B'])
        if dane.at[nr, 'DRUZYNA_B'] == druzyna:
            przeciwnicy.append(dane.at[nr, 'DRUZYNA_A'])
            przeciwnicy_elo.append(dane.at[nr, 'ELO_A'])
            wyniki.append(elo.wynik(dane.at[nr, 'GOLE_B'], dane.at[nr, 'GOLE_A']))
            punkty += elo.punkty(dane.at[nr, 'GOLE_B'], dane.at[nr, 'GOLE_A'])
    liczba_meczy = len(dane)
    wynik_razem = sum(wyniki)
    wygrane = sum([1 if w==1 else 0 for w in wyniki])
    remisy = sum([1 if w==0.5 else 0 for w in wyniki])
    sr_wygrane = wygrane/liczba_meczy if liczba_meczy else 0
    sr_remisy = remisy/liczba_meczy if liczba_meczy else 0
    sr_punkty = punkty/liczba_meczy if liczba_meczy else 0
    return {'druzyna':druzyna,
            'przeciwnicy':przeciwnicy,
            'przeciwnicy_elo':przeciwnicy_elo,
            'id_meczy':id_meczy,
            'wyniki':wyniki,
            'wynik_razem':wynik_razem,
            'punkty':punkty,
            'liczba_meczy':len(dane),
            'wygrane':wygrane,
            'remisy':remisy,
            'sr_wygrane': sr_wygrane,
            'sr_remisy':sr_remisy,
            'sr_punkty':sr_punkty
            }

def wynik_ostatnie_n(df: pd.DataFrame, n: int = 6):
    elo = re.Elo()
    for liga_sezon, grupa in df.groupby(['LIGA', 'SEZON']):
        for id, mecz in grupa.iterrows():
            slownik_a_dw = n_poprzednich_meczy(grupa, id=id, n=n, ab='A', dom_wyj='DW')
            slownik_a_d = n_poprzednich_meczy(grupa, id=id, n=n, ab='A', dom_wyj='D')
            slownik_b_dw = n_poprzednich_meczy(grupa, id=id, n=n, ab='B', dom_wyj='DW')
            slownik_b_w = n_poprzednich_meczy(grupa, id=id, n=n, ab='B', dom_wyj='W')
            df.at[id, 'SR_WYGRANE_A_DOM_OST_6'] = slownik_a_d['sr_wygrane']
            df.at[id, 'SR_REMISY_A_DOM_OST_6'] = slownik_a_d['sr_remisy']
            df.at[id, 'SR_WYGRANE_A_OST_6'] = slownik_a_dw['sr_wygrane']
            df.at[id, 'SR_REMISY_A_OST_6'] = slownik_a_dw['sr_remisy']
            df.at[id, 'SR_WYGRANE_B_WYJ_OST_6'] = slownik_b_w['sr_wygrane']
            df.at[id, 'SR_REMISY_B_WYJ_OST_6'] = slownik_b_w['sr_remisy']
            df.at[id, 'SR_WYGRANE_B_OST_6'] = slownik_b_dw['sr_wygrane']
            df.at[id, 'SR_REMISY_B_OST_6'] = slownik_b_dw['sr_remisy']
            df.at[id, 'WYN_RANKINGOWY_A_DOM_6'] = elo.ranking_turniejowy(slownik_a_d['przeciwnicy_elo'], slownik_a_d['wynik_razem'])
            df.at[id, 'WYN_RANKINGOWY_B_WYJ_6'] = elo.ranking_turniejowy(slownik_b_w['przeciwnicy_elo'], slownik_b_w['wynik_razem'])
            df.at[id, 'WYN_RANKINGOWY_A_6'] = elo.ranking_turniejowy(slownik_a_dw['przeciwnicy_elo'],slownik_a_d['wynik_razem'])
            df.at[id, 'WYN_RANKINGOWY_B_6'] = elo.ranking_turniejowy(slownik_b_dw['przeciwnicy_elo'],slownik_b_w['wynik_razem'])
    return df
