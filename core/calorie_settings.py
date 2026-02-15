class CalorieSettings:
    def __init__(self, session_state):
        # Salvam obiectul session_state pentru a pastra setarile intre pagini
        self.session = session_state

        # Initializam valorile implicite daca nu exista deja in sesiune
        self._init_defaults()

    def _init_defaults(self):
        # Setam valori default doar daca nu exista deja in session_state
        self.session.setdefault("min_daily", 1800)      # limita minima zilnica
        self.session.setdefault("max_daily", 2500)      # limita maxima zilnica
        self.session.setdefault("min_weekly", 12000)    # limita minima saptamanala
        self.session.setdefault("max_weekly", 17500)    # limita maxima saptamanala
        self.session.setdefault("week_offset", 0)       # offset pentru navigarea intre saptamani

    # Getter si setter pentru limita minima zilnica
    @property
    def min_daily(self) -> int:
        return self.session["min_daily"]

    @min_daily.setter
    def min_daily(self, value: int):
        self.session["min_daily"] = value

    # Getter si setter pentru limita maxima zilnica
    @property
    def max_daily(self) -> int:
        return self.session["max_daily"]

    @max_daily.setter
    def max_daily(self, value: int):
        self.session["max_daily"] = value

    # Getter si setter pentru limita minima saptamanala
    @property
    def min_weekly(self) -> int:
        return self.session["min_weekly"]

    @min_weekly.setter
    def min_weekly(self, value: int):
        self.session["min_weekly"] = value

    # Getter si setter pentru limita maxima saptamanala
    @property
    def max_weekly(self) -> int:
        return self.session["max_weekly"]

    @max_weekly.setter
    def max_weekly(self, value: int):
        self.session["max_weekly"] = value

    # Getter si setter pentru offset-ul saptamanii (folosit la calendar)
    @property
    def week_offset(self) -> int:
        return self.session["week_offset"]

    @week_offset.setter
    def week_offset(self, value: int):
        self.session["week_offset"] = value