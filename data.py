TOTAL_TIME = 15 * 60 + 90  # 15 min fight length.
SCALE = 5
PIXELS = TOTAL_TIME * SCALE
STEP = 2 * SCALE
START_POS = 40 + 99


class Spec:
    name: str
    color_main: str
    color_cd: str
    abilities: list

    def __init__(self, name: str, colors: tuple):
        self.name = name
        self.color_main, self.color_cd = colors


class Ability:
    def __init__(
        self,
        name: str,
        duration: float,
        cool_down: float,
        spec: Spec,
        check: bool = True
    ):
        self.name = name
        self.duration = duration * SCALE
        self.cool_down = cool_down * SCALE
        self.spec = spec
        self.color_main = spec.color_main
        self.color_cd = spec.color_cd
        self.check = check


hpal = Spec('Paladin', ('#F58CBA', '#FAC7DD'))
rdruid = Spec('Druid', ('#FF7D0A', '#FF9D47'))
mwmonk = Spec('Monk', ('#00FF96', '#47FFB3'))
discpriest = Spec('Discipline Priest', ('#FFFF00', '#FFFF47'))
hpriest = Spec('Holy Priest', ('#A3A3A3', '#C2C2C2'))
rshaman = Spec('Shaman', ('#0070DE', '#1F8FFF'))

specs = [var for _, var in locals().items() if type(var) == Spec]


aw = Ability('Awenging Wrath', 20, 2 * 60, hpal)
sw = Ability('Sanctified Wrath', 20 * 1.25, 2 * 60, hpal, False)
am = Ability('Aura Mastery', 8, 3 * 60, hpal)
lh = Ability('Light\'s Hammmer', 14, 60, hpal, False)
ha = Ability('Holy Avenger', 20, 3 * 60, hpal, False)
ah = Ability('Ashen Hollow', 30, 4 * 60, hpal, False)

tranq = Ability('Tranquility', 10, 3 * 60, rdruid)
inner_peace = Ability('Tranquility Inner Peace', 16, tranq.cool_down - 60, rdruid, False)
tree = Ability('Tree of Life', 30, 3 * 60, rdruid, False)
flourish = Ability('Flourish', 8, 1.5 * 60, rdruid, False)

revival = Ability('Revival', 5, 3 * 60, mwmonk)
yulon = Ability('Yu\'lon', 25, 3 * 60, mwmonk)
chi_ji = Ability('Chi-Ji', 25, 3 * 60, mwmonk, False)
weapons = Ability('Weapons of Order', 30, 2 * 60, mwmonk, False)

rapture = Ability('Rapture', 8, 1.5 * 60, discpriest)
fiend = Ability('Shadow Fiend', 10, 3 * 60, discpriest)
barrier = Ability('Power Word: Barrier', 10, 3 * 60, discpriest)
spirit_shell = Ability('Spirit Shell', 10, 1 * 60, discpriest, False)
evangelism = Ability('Evangelism', 6, 1.5 * 60, discpriest, False)
boon1 = Ability('Boon of the Ascended (d)', 10, 3 * 60, discpriest, False)

hymn = Ability('Divine Hymn', 8, 3 * 60, hpriest)
apotheosis = Ability('Apotheosis', 20, 2 * 60, hpriest, False)
salvation = Ability('Holy Word: Salvation', 5, 6 * 60, hpriest, False)
boon2 = Ability('Boon of the Ascended (h)', 10, 3 * 60, hpriest, False)

slt = Ability('Spirit Link Totem', 6, 3 * 60, rshaman)
htt = Ability('Healing Tide Totem', 10, 3 * 60, rshaman)
ancestral = Ability('Ancestral Protection Totem', 30, 5 * 60, rshaman, False)
ascendance = Ability('Ascendance', 15, 3 * 60, rshaman, False)


abilities = [var for _, var in locals().items() if type(var) == Ability]


for spec in specs:
    spec.abilities = [abil for abil in abilities if abil.spec == spec]
