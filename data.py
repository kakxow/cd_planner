COLORS = {
    'Paladin': ('#F58CBA', '#FAC7DD'),
    'Druid': ('#FF7D0A', '#FF9D47'),
    'Monk': ('#00FF96', '#47FFB3'),
    'Discipline Priest': ('#FFFF00', '#FFFF47'),
    'Holy Priest': ('#A3A3A3', '#C2C2C2'),
    'Shaman': ('#0070DE', '#1F8FFF'),
}


class Spec:
    name: str
    color_main: str
    color_cd: str

    def __init__(self, name: str):
        self.name = name
        self.color_main, self.color_cd = COLORS[name]


specs = [Spec('Paladin'), Spec('Druid'), Spec('Monk'), Spec('Discipline Priest'), Spec('Holy Priest'), Spec('Shaman')]
