class Elo:
    def __init__(self, k: int=32, przewaga_a: int=100, wsp_400: int=400):
        self.__k = k
        self.__przewaga_a = przewaga_a
        self.__wsp_400 = wsp_400

    def __str__(self):
        return (f"k: {self.__k},\n przewaga gospodarza: {self.__przewaga_a},\n"
                f"czułość: {self.__wsp_400}")

    def __repr__(self):
        return f"Elo({self.__k, self.__przewaga_a, self.__wsp_400})"

    @property
    def k(self) -> int:
        return self.__k

    @k.setter
    def k(self, wartosc: int):
        self.__k = wartosc

    @property
    def przewaga_a(self) -> int:
        return self.__przewaga_a

    @przewaga_a.setter
    def przewaga_a(self, wartosc: int):
        self.__przewaga_a = wartosc

    @property
    def wsp_400(self) -> int:
        return self.__wsp_400

    @wsp_400.setter
    def wsp_400(self, wartosc: int):
        self.__wsp_400 = wartosc

    @staticmethod
    def wsp_goli(gole: int, typ: int=1) -> float:
        gole = abs(gole)
        if typ == 1:
            if gole <= 2:
                return 1 if gole <= 1 else 1.5
            else:
                return (11 + gole) / 8

    @staticmethod
    def wynik(gole_a: int, gole_b: int, typ: int=1) -> float:
        if typ == 1:
            return 1 if gole_a > gole_b else 0.5 if gole_a == gole_b else 0

    def oczekiwany_wynik(self, elo_a: float, elo_b: float, dom_a: bool=True, dom_b: bool=False) -> float:
        elo_a =+ self.__przewaga_a if dom_a else elo_a
        elo_b =+ self.__przewaga_a if dom_b else elo_b
        return 1 / (1 + 10 ** ((elo_b - elo_a) / self.__wsp_400))

    def nowe_rankingi(
            self, elo_a: float, elo_b: float, gole_a: int, gole_b: int,
            dom_a: bool=True, dom_b: bool=False, kto: str='oba'
    ) -> float | tuple:
        oczekiwany_a = self.oczekiwany_wynik(elo_a, elo_b, dom_a, dom_b)
        oczekiwany_b = 1 - oczekiwany_a
        wsp = self.wsp_goli(gole_a-gole_b) * self.__k
        wynik_a, wynik_b = self.wynik(gole_a, gole_b), self.wynik(gole_b, gole_a)

        nowy_elo_a = elo_a + wsp * (wynik_a - oczekiwany_a)
        nowy_elo_b = elo_b + wsp * (wynik_b - oczekiwany_b)
        kto = kto.lower()
        if kto in ['a', 'b']:
            return nowy_elo_a if kto == 'a' else nowy_elo_b
        else:
            return nowy_elo_a, nowy_elo_b
