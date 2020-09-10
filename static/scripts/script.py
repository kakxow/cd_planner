import types

from browser import document, html  # type: ignore

# import data
from data import START_POS, SCALE, PIXELS, Ability, abilities, STEP


def factory_activate_abl(box):
    ability_name = box.name.lstrip('box-')
    bar = document[f'abl-{ability_name}']

    def _activate(ev):
        if bar.style.height == '0px':
            bar.style.height = ''
            bar.style.visibility = ''
        else:
            bar.style.height = '0px'
            bar.style.visibility = 'hidden'
    return _activate


def factory_activate_spec(box):
    div = box.parent
    abl_boxes = div.select('.ability-checkbox')
    spec_name = box.name.lstrip('box-')
    spec = document[f'spec-{spec_name}']
    spec_count = document[f'count-{spec_name}']

    def _activate(ev):
        if spec.style.height == '0px':
            spec.style.height = ''
            spec.style.visibility = ''
            for abl_box in abl_boxes:
                abl_box.disabled = False
            spec_count.disabled = False
        else:
            spec.style.height = '0px'
            spec.style.visibility = 'hidden'
            for abl_box in abl_boxes:
                abl_box.disabled = True
            spec_count.disabled = True
    return _activate


def ability_boxes():
    checkboxes = document.select('.ability-checkbox')
    for box in checkboxes:
        box.bind('click', factory_activate_abl(box))


def spec_boxes():
    checkboxes = document.select('.spec-checkbox')
    for box in checkboxes:
        box.bind('click', factory_activate_spec(box))


def px_to_int(px: str) -> float:
    return float(px[:-2])


class Bar(html.DIV):
    def __init__(self, ability: Ability, position: float = START_POS):
        # self = html.DIV()
        super().__init__(Class='ability-bar higher20')
        self.ability = ability

        self.style = {
            'left': f'{position}px',
            'right': f'{position + ability.cool_down}px',
            'width': ability.cool_down,
        }
        self <= self._content()

    @classmethod
    def new(cls, bar: html.DIV, ability: Ability):
        bar.ability = ability
        bar.drag = types.MethodType(cls.drag, bar)
        bar.move = types.MethodType(cls.move, bar)
        bar.time = types.MethodType(cls.time, bar)
        bar._move = types.MethodType(cls._move, bar)
        bar.tooltip = bar.select('.tooltiptext')[0]
        return bar

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
        new_pos = self.offsetLeft - delta
        new_pos_right = new_pos + self.ability.cool_down
        obstacles_right = \
            False if not self._right else px_to_int(self._right.style.left) < new_pos_right
        obstacles_left = \
            False if not self._left else px_to_int(self._left.style.right) > new_pos

        if obstacles_left and delta > 0:
            self._left.move(STEP)
        elif obstacles_right and delta < 0:
            self._right.move(-STEP)
        elif new_pos <= PIXELS and new_pos >= START_POS:
            self._move(new_pos)

    def time(self) -> str:
        time_stamp = int((px_to_int(self.style.left) - START_POS) / SCALE)
        _time = f'{time_stamp // 60}:{time_stamp % 60:02d}'
        return _time

    def _move(self, new_pos: int):
        self.style.left = f'{new_pos}px'
        self.style.right = f'{new_pos + self.ability.cool_down}px'
        self.tooltip.text = self.time()


class BigBar:
    def __init__(self, bar: html.DIV):
        self.bar = bar
        ability_name = bar.id.lstrip('abl-')
        ability = next(abl for abl in abilities if abl.name == ability_name)
        self.ability = ability
        abl_bar_id = f'abl-bar-{self.ability.name}'
        self._bars = [Bar.new(document[abl_bar_id], ability)]
        self.bind_bars()

        self.btn_add = document[f'btn-{self.ability.name}']
        self.btn_add.bind('click', self.add_bar())

    def add_bar(self):
        def adder(ev):
            last_bar = self._bars[-1]
            new_bar = Bar(self.ability, px_to_int(last_bar.style.right))
            self._bars.append(new_bar)
            self.bind_bars()
            self.bar <= self._bars
        return adder

    def bind_bars(self):
        bar_count = len(self._bars)
        for i, bar in enumerate(self._bars):
            bar._left = self._bars[i - 1] if i > 0 else None
            bar._right = None if i == (bar_count - 1) else self._bars[i + 1]
            bar.bind('mousedown', bar.drag)


if __name__ == '__main__':
    ability_boxes()
    spec_boxes()
    # big_bars = document.select('.abl-bar')
    BIG_BARS = [BigBar(bar) for bar in document.select('.abl-bar')]
