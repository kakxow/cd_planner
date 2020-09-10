from browser import document, html  # type: ignore

import data


TOTAL_TIME = 15 * 60 + 90  # 15 min fight length.
SCALE = 5
PIXELS = TOTAL_TIME * SCALE
STEP = 2 * SCALE
START_POS = 40 + 99

COLORS = {
    'paladin': ('#F58CBA', '#FAC7DD'),
    'druid': ('#FF7D0A', '#FF9D47'),
    'monk': ('#00FF96', '#47FFB3'),
    'disc_priest': ('#FFFF00', '#FFFF47'),
    'holy_priest': ('#A3A3A3', '#C2C2C2'),
    'shaman': ('#0070DE', '#1F8FFF'),
}


class Spec:
    name: str
    color_main: str
    color_cd: str

    def __init__(self, name: str):
        self.name = name
        self.color_main, self.color_cd = COLORS[name]


specs = [Spec('paladin'), Spec('druid'), Spec('monk'), Spec('disc_priest'), Spec('holy_priest'), Spec('shaman')]


class Ability:
    def __init__(
        self,
        name: str,
        duration: float,
        cool_down: float,
        spec: str,
        check: bool = True
    ):
        self.name = name
        self.duration = duration * SCALE
        self.cool_down = cool_down * SCALE
        self.color_main, self.color_cd = COLORS[spec]
        self.check = check


aw = Ability('Awenging Wrath', 20, 2 * 60, 'paladin')
am = Ability('Aura Mastery', 8, 3 * 60, 'paladin')
lh = Ability('Light\'s Hammmer', 14, 60, 'paladin', False)
ha = Ability('Holy Avenger', 20, 3 * 60, 'paladin', False)
ah = Ability('Ashen Hollow', 30, 4 * 60, 'paladin', False)

tranq = Ability('Tranquility', 10, 3 * 60, 'druid')
inner_peace = Ability('Tranquility Inner Peace', 16, 2 * 60, 'druid', False)
tree = Ability('Tree of Life', 30, 3 * 60, 'druid', False)
flourish = Ability('Flourish', 8, 1.5 * 60, 'druid', False)

yulon = Ability('Yu\'lon', 25, 3 * 60, 'monk')
revival = Ability('Revival', 5, 3 * 60, 'monk')
chi_ji = Ability('Chi-Ji', 25, 3 * 60, 'monk', False)
weapons = Ability('Weapons of Order', 30, 2 * 60, 'monk', False)

rapture = Ability('Rapture', 8, 1.5 * 60, 'disc_priest')
fiend = Ability('Shadow Fiend', 10, 3 * 60, 'disc_priest')
barrier = Ability('Power Word: Barrier', 10, 3 * 60, 'disc_priest')
spirit_shell = Ability('Spirit Shell', 10, 1 * 60, 'disc_priest', False)
evangelism = Ability('Evangelism', 6, 1.5 * 60, 'disc_priest', False)

hymn = Ability('Divine Hymn', 8, 3 * 60, 'holy_priest')
apotheosis = Ability('Apotheosis', 20, 2 * 60, 'holy_priest', False)
salvation = Ability('Holy Word: Salvation', 5, 6 * 60, 'holy_priest', False)
boon = Ability('Boon of the Ascended', 10, 3 * 60, 'holy_priest', False)

slt = Ability('Spirit Link Totem', 6, 3 * 60, 'shaman')
htt = Ability('Healing Tide Totem', 10, 3 * 60, 'shaman')
ancestral = Ability('Ancestral Protection Totem', 30, 5 * 60, 'shaman', False)
ascendance = Ability('Ascenance', 15, 3 * 60, 'shaman', False)


abilities = [var for _, var in locals().items() if type(var) == Ability]


class Bar(html.DIV):
    def __init__(self, ability: Ability, position: float = START_POS):
        super().__init__(Class='ability-bar')
        self.ability = ability

        self.style = {
            'left': f'{position}px',
            'right': f'{position + ability.cool_down}px',
            'width': ability.cool_down,
        }
        self <= self._content()

    def _content(self):
        duration_style = {
            'max-width': self.ability.duration,
            'width': self.ability.duration,
            'background-color': self.ability.color_main,
        }
        duration = html.TD(self.ability.name, style=duration_style, Class='duration')

        cd_length = self.ability.cool_down - self.ability.duration
        cd_style = {
            'width': cd_length,
            'background-color': self.ability.color_cd,
        }
        cd = html.TD(style=cd_style)

        self.tooltip = html.SPAN(self.time(), Class='tooltiptext')

        ability_bar = html.TABLE(Class='tooltip ability-tbl')
        ability_bar <= duration
        ability_bar <= cd
        ability_bar <= self.tooltip
        return ability_bar

    def drag(self, ev):
        start_pos = ev.clientX

        def _stop_drag(ev):
            self.unbind('mousemove')
            self.unbind('mouseup')

        def _drag(ev):
            nonlocal start_pos
            delta = start_pos - ev.clientX
            start_pos = ev.clientX
            self.move(delta)

        self.bind('mouseup', _stop_drag)
        self.bind('mouseleave', _stop_drag)
        self.bind('mousemove', _drag)

    def move(self, delta: int):
        # print('move')
        new_pos = self.offsetLeft - delta
        new_pos_right = new_pos + self.ability.cool_down
        obstacles_right = \
            False if not self._right else px_to_int(self._right.style.left) < new_pos_right
        obstacles_left = \
            False if not self._left else px_to_int(self._left.style.right) > new_pos

        if obstacles_left and delta > 0:
            # print('movin left bud', locals())
            self._left.move(STEP)
        elif obstacles_right and delta < 0:
            # print('movin right bud', locals())
            self._right.move(-STEP)
        elif new_pos <= PIXELS and new_pos >= START_POS:
            # print('movin self', locals())
            self._move(new_pos)

    def time(self) -> str:
        time_stamp = int((px_to_int(self.style.left) - START_POS) / SCALE)
        _time = f'{time_stamp // 60}:{time_stamp % 60:02d}'
        return _time

    def _move(self, new_pos: int):
        self.style.left = f'{new_pos}px'
        self.style.right = f'{new_pos + self.ability.cool_down}px'
        self.tooltip.text = self.time()


class BigBar(html.DIV):
    def __init__(self, ability: Ability):
        self.ability = ability
        super().__init__(id=ability.name)
        # self.casts = int(PIXELS // ability.cool_down)
        self._bars = [Bar(ability)]
        self.bind_bars()

        self.btn_add = html.BUTTON('+', Class='lower20')
        self.btn_add.bind('click', self.add_bar())
        self <= self.btn_add
        self <= self._bars
        if not ability.check:
            self.style.visibility = 'hidden'
            self.style.height = '0px'

    def add_bar(self):
        def adder(ev):
            last_bar = self._bars[-1]
            new_bar = Bar(self.ability, px_to_int(last_bar.style.right))
            self._bars.append(new_bar)
            self.bind_bars()
            self <= self._bars
        return adder

    def bind_bars(self):
        bar_count = len(self._bars)
        for i, bar in enumerate(self._bars):
            bar._left = self._bars[i - 1] if i > 0 else None
            bar._right = None if i == (bar_count - 1) else self._bars[i + 1]
            print(bar, dir(bar))
            bar.bind('mousedown', bar.drag)

    def check(self):
        def _check(ev):
            leftest_el = self._bars[0]
            rightest_el = self._bars[-1]
            if px_to_int(leftest_el.style.left) + self.ability.duration < 0:
                self._bars = self._bars[1:]
            if px_to_int(rightest_el.style.right) - self.ability.cool_down > PIXELS:
                self._bars = self._bars[:-1]
            self.bind_bars()
        return _check


def px_to_int(px: str) -> float:
    return float(px[:-2])


class CheckBox(html.DIV):
    def __init__(self, ability: Ability):
        super().__init__()
        self.ability = ability
        name = ability.name
        self.checkbox = html.INPUT(type='checkbox', name=name, id=name, checked=ability.check)
        self.label = html.LABEL(name, For=name)
        self <= self.checkbox
        self <= self.label
        self.checkbox.bind('click', self.activate())

    def activate(self):
        def _activate(ev):
            bar = document[self.ability.name]
            if bar.style.height == '0px':
                bar.style.height = '22px'
                bar.style.visibility = 'visible'
            else:
                bar.style.height = '0px'
                bar.style.visibility = 'hidden'
        return _activate


def add_options():
    options = document['options']
    for ability in data.abilities:
        options <= CheckBox(ability)
        # name = ability.name
        # checkbox = html.INPUT(type='checkbox', name=name, id=name, checked=ability.check)
        # checkbox.bind('click', lambda ev: )
        # checkbox = CheckBox(ability)
        # options <= checkbox
        # options <= html.LABEL(name, For=name)
        # options <= html.BR()


if __name__ == '__main__':
    # import os
    # print(os.getcwd())

    main = document['main']

    for ability in abilities:
        main <= BigBar(ability)

    add_options()
