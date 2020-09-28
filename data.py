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

    def to_json(self):
        return {
            'name': self.name,
            'color_main': self.color_main,
            'color_cd': self.color_cd,
        }


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

    def to_json(self):
        return {
            'name': self.name,
            'duration': self.duration,
            'cool_down': self.cool_down,
            'spec': self.spec,
            'color_main': self.color_main,
            'color_cd': self.color_cd,
            'check': self.check,
        }


hpal = Spec('Paladin Holy', ('#F58CBA', '#FAC7DD'))
rdruid = Spec('Druid Restoration', ('#FF7D0A', '#FFBE85'))
mwmonk = Spec('Monk Mistweaver', ('#00FF96', '#99FFD5'))
discpriest = Spec('Priest Discipline', ('#7EDDF9', '#C5EFFC'))
hpriest = Spec('Priest Holy', ('#A3A3A3', '#CCCCCC'))
rshaman = Spec('Shaman Restoration', ('#0070DE', '#5CADFF'))

specs = [var for _, var in locals().items() if type(var) == Spec]
specs_dict = {spec.name: spec for spec in specs}


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
abilities_dict = {a.name: a for a in abilities}


for spec in specs:
    spec.abilities = [abil for abil in abilities if abil.spec == spec]

phases = {
    'Form Ranks': [
        ('0:30', '0:55'),
        ('3:00', '3:25'),
        ('5:30', '5:55')
    ],
    'Stand Alone': [
        ('1:30', '2:00'),
        ('4:00', '4:30')
    ],
    'Deferred Sentence': [
        ('2:00', '2:30'),
        ('4:30', '5:00')
    ],
    'Obey or Suffer': [
        ('2:30', '3:00'),
        ('5:00', '5:30')
    ],
}

boss_casts = {
    'Form Ranks': (
        '0:30',
        '0:40',
        '0:50',
        '3:00',
        '3:10',
        '3:20',
        '5:30',
        '5:40',
        '5:50',
    ),
    'Spark': (
        '0:30',
        '0:45',
        '1:00',
        '2:05',
        '2:20',
        '2:35',
        '3:35',
        '3:50',
        '4:05',
    ),
    'Eruption': (
        '0:55',
        '2:40',
        '4:25',
        '6:10',
    ),
    'Charge': (
        '0:35',
        '1:15',
        '1:55',
        '2:35',
        '3:20',
        '4:00',
        '4:45',
        '5:20',
        '6:05',
        '6:45',
    ),
    'Burst': (
        '1:40',
        '3:25',
        '5:15',
        '7:00',
    ),
}

bosses = {
    'The Queen\'s Court': (phases, boss_casts),
    'Queen Aszhara': ({}, {}),
}
