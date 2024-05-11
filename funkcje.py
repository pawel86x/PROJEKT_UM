import pandas as pd
import numpy as np
import RankingElo as re

kolumny: dict = {
    'INDEKS':'int32'
    ,'KRAJ':'string'
    ,'LIGA':'string'
    ,'SEZON':'string'
    ,'DATA_MECZU':'datetime64[ns]'
    ,'DRUZYNA_A':'string'
    ,'DRUZYNA_B':'string'
    ,'GOLE_A':'int32'
    ,'GOLE_B':'int32'
    ,'WYNIK':'int32'
    ,'PR1':'float64'
    ,'PRX':'float64'
    ,'PR2':'float64'
}

df = pd.read_excel(r'D:\plik.xlsx', sheet_name='DANE')
df = df.astype(kolumny).set_index('INDEKS')

druzyny_elo: dict = {}
druzyny_nr: dict = {}
n: int = 5
elo_minus_n: dict = {}
elo: re.Elo = re.Elo()
#for (kraj, liga, sezon), grupa in df.groupby(['KRAJ', 'LIGA', 'SEZON']):
for xxx, grupa in df.groupby(['KRAJ', 'LIGA', 'SEZON']):
    druzyny_elo[xxx] = {}
    elo_minus_n[xxx] = {}

    for id, mecz in grupa.iterrows():
        druzyna_a = mecz['DRUZYNA_A']
        druzyna_b = mecz['DRUZYNA_B']
        gole_a = mecz['GOLE_A']
        gole_b = mecz['GOLE_B']


        if druzyna_a not in druzyny_elo[xxx]:
            druzyny_elo[xxx][druzyna_a] = 1000
            druzyny_nr[druzyna_a] = 1
            elo_minus_n[xxx][druzyna_a] = []
        else:
            druzyny_nr[druzyna_a] += 1
        if druzyna_b not in druzyny_elo[xxx]:
            druzyny_elo[xxx][druzyna_b] = 1000
            druzyny_nr[druzyna_b] = 1
            elo_minus_n[xxx][druzyna_b] = []
        else:
            druzyny_nr[druzyna_b] += 1
        stary_elo_a = druzyny_elo[xxx][druzyna_a]
        stary_elo_b = druzyny_elo[xxx][druzyna_b]
        nowy_elo_a, nowy_elo_b = elo.nowe_rankingi(stary_elo_a, stary_elo_b, gole_a, gole_b)

        druzyny_elo[xxx][druzyna_a] = nowy_elo_a
        druzyny_elo[xxx][druzyna_b] = nowy_elo_b

        i = druzyny_nr[druzyna_a] - 1
        elo_minus_n[xxx][druzyna_a].append(stary_elo_a)
        if i < n:
            df.at[id, 'A_ELO_N'] = np.nan
        else:
            df.at[id, 'A_ELO_N'] = elo_minus_n[xxx][druzyna_a][i] - elo_minus_n[xxx][druzyna_a][i-n]
        i = druzyny_nr[druzyna_b] - 1
        elo_minus_n[xxx][druzyna_b].append(stary_elo_b)
        if i < n:
            df.at[id, 'B_ELO_N'] = np.nan
        else:
            df.at[id, 'B_ELO_N'] = elo_minus_n[xxx][druzyna_b][i] - elo_minus_n[xxx][druzyna_b][i-n]


        df.at[id, 'STARY_ELO_A'] = stary_elo_a
        df.at[id, 'STARY_ELO_B'] = stary_elo_b
        df.at[id, 'NOWY_ELO_A'] = nowy_elo_a
        df.at[id, 'NOWY_ELO_B'] = nowy_elo_b
        df.at[id, 'NR_MECZU_A'] = druzyny_nr[druzyna_a]
        df.at[id, 'NR_MECZU_B'] = druzyny_nr[druzyna_b]

sciezka = r'D:\STUDIA\UCZENIE MASZYNOWE\PROJEKT\dane_z_elov2.xlsx'
df.to_excel(sciezka, index=False)
