import types

from browser import document, html  # type: ignore

import data
from data import START_POS, SCALE, PIXELS, Ability, abilities, STEP


def factory_activate_abl(box):
    ability_name = box.name.lstrip('box-')
    div = box.parent
    spec_id = div.id.lstrip('options-')
    spec = document[f'spec-{spec_id}']
    bar = [el for el in spec.children if el.id == f'abl-{ability_name}'][0]

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
    spec_id = box.id.lstrip('box-')
    spec = document[f'spec-{spec_id}']

    def _activate(ev):
        if spec.style.height == '0px':
            spec.style.height = ''
            spec.style.visibility = ''
            for abl_box in abl_boxes:
                abl_box.disabled = False
        else:
            spec.style.height = '0px'
            spec.style.visibility = 'hidden'
            for abl_box in abl_boxes:
                abl_box.disabled = True
    return _activate


def factory_change_specs(inp):
    spec_name = inp.id.lstrip('count-')
    spec_obj = next(spec for spec in data.specs if spec.name == spec_name)
    spec_div = document[f'spec-{spec_name}']
    opt_div = document[f'options-{spec_name}']

    def _add(ev):
        max_id = min(int(inp.value) - 1, 3)

        specs = spec_div.children
        for spec in specs:
            if int(spec.id[-1]) <= max_id:
                spec.style.height = ''
                spec.style.visibility = ''
            else:
                spec.style.height = '0px'
                spec.style.visibility = 'hidden'
        for i in range(len(specs), max_id + 1):
            spec_div <= SpecBar(spec_obj, i)

        opts = list(filter(lambda x: isinstance(x, html.DIV), opt_div.children))
        for spec_opts in opts:
            if int(spec_opts.id[-1]) <= max_id:
                spec_opts.style.height = ''
                spec_opts.style.visibility = ''
            else:
                spec_opts.style.height = '0px'
                spec_opts.style.visibility = 'hidden'
        for i in range(len(opts), max_id + 1):
            opt_div <= SpecOpts(spec_obj, i)
        ability_boxes()
        spec_boxes()
        nicknames_inputs()
    return _add


def factory_change_nick(inp):
    spec_id = inp.id.lstrip('nick-')
    options = document[f'options-{spec_id}']
    lbl = [el for el in options if el.textContent == spec_id[:-1]][0]

    def change_nick(ev):
        lbl.textContent = inp.value
    return change_nick


def ability_boxes():
    checkboxes = document.select('.ability-checkbox')
    for box in checkboxes:
        box.unbind('click')
        box.bind('click', factory_activate_abl(box))


def spec_boxes():
    checkboxes = document.select('.spec-checkbox')
    for box in checkboxes:
        box.unbind('click')
        box.bind('click', factory_activate_spec(box))


def spec_inps():
    spec_inputs = document.select('.spec-inp')
    for inp in spec_inputs:
        inp.unbind('input')
        inp.bind('input', factory_change_specs(inp))


def nicknames_inputs():
    inps = document.select('.spec-nick')
    for inp in inps:
        inp.unbind('input')
        inp.bind('input', factory_change_nick(inp))


def px_to_int(px: str) -> float:
    return float(px[:-2])


class Bar(html.DIV):
    def __init__(self, ability: Ability, position: float, id: str):
        super().__init__(Class='ability-bar higher20')
        self.ability = ability

        self.style = {
            'left': f'{position}px',
            'right': f'{position + ability.cool_down}px',
            'width': ability.cool_down,
        }
        self.id = f"abl-bar-{ability.name}{id}"
        self.tooltip = html.SPAN(self.time(), Class='tooltiptext')
        self <= self.tooltip
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

        tr = html.TR()
        tr <= duration
        tr <= cd
        tbody = html.TBODY()
        tbody <= tr
        ability_tbl = html.TABLE(Class='ability-tbl')
        ability_tbl <= tbody
        return ability_tbl

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


class BigBar(html.DIV):
    def __init__(self, ability: Ability):
        self.ability = ability
        abl_id = f'abl-{ability.name}'
        super().__init__(id=abl_id, Class='tooltip abl-bar')
        self._bars = [Bar(ability, START_POS, '0')]
        self.bind_bars()

        self.btn_add = html.BUTTON('+', Class='btn-add', id=f'btn-{ability.name}')
        self.btn_add.bind('click', self.add_bar())
        self <= self.btn_add
        self <= self._bars
        if not ability.check:
            self.style.visibility = 'hidden'
            self.style.height = '0px'

    @classmethod
    def new(cls, bar: html.DIV):
        bar.add_bar = types.MethodType(cls.add_bar, bar)
        bar.bind_bars = types.MethodType(cls.bind_bars, bar)

        ability_name = bar.id.lstrip('abl-')
        ability = next(abl for abl in abilities if abl.name == ability_name)
        bar.ability = ability
        abl_bars = bar.select('.ability-bar')
        bar._bars = [Bar.new(abl_bar, ability) for abl_bar in abl_bars]
        bar.bind_bars()

        bar.btn_add = document[f'btn-{bar.ability.name}']
        bar.btn_add.bind('click', bar.add_bar())
        return bar

    def add_bar(self):
        def adder(ev):
            bar_count = len(self._bars)
            last_bar = self._bars[-1]
            new_bar = Bar(self.ability, px_to_int(last_bar.style.right), id=bar_count)
            self._bars.append(new_bar)
            self.bind_bars()
            self <= self._bars
        return adder

    def bind_bars(self):
        bar_count = len(self._bars)
        for i, bar in enumerate(self._bars):
            bar._left = self._bars[i - 1] if i > 0 else None
            bar._right = None if i == (bar_count - 1) else self._bars[i + 1]
            bar.bind('mousedown', bar.drag)


class SpecBar(html.DIV):
    def __init__(self, spec: data.Spec, id: int):
        div_id = f'spec-{spec.name}{id}'
        super().__init__(id=div_id)
        self.spec = spec
        self._id = id
        self._fill()
        self.inp.bind('input', self.change_nick)

    def _fill(self):
        name = self.spec.name
        self.inp = html.INPUT(
            id=f'nick-{name}{self._id}',
            Class='spec-nick',
            type='text',
            name=name,
            value=name,
            size=12
        )
        self <= self.inp
        for ability in self.spec.abilities:
            self <= BigBar(ability)
            self <= html.BR()

    def change_nick(self, ev):
        pass

    @classmethod
    def new(cls, div: html.DIV):
        return div


class SpecOpts(html.DIV):
    def __init__(self, spec: data.Spec, id: int):
        div_id = f'options-{spec.name}{id}'
        super().__init__(id=div_id)
        self.spec = spec
        self._id = id
        self._fill()

    def _fill(self):
        name = self.spec.name
        inp = html.INPUT(
            id=f'box-{name}{self._id}',
            Class='spec-checkbox',
            type='checkbox',
            name=f'box-{name}',
            checked=True
        )
        self <= inp
        self <= html.LABEL(html.B(name))
        self <= html.BR()
        for ability in self.spec.abilities:
            name = ability.name
            inp = html.INPUT(
                id=f'box-{name}',
                Class='ability-checkbox',
                type='checkbox',
                name=f'box-{name}')
            if ability.check:
                inp.checked = True
            lbl = html.LABEL(name, For=name)
            self <= inp
            self <= lbl
            self <= html.BR()


if __name__ == '__main__':
    ability_boxes()
    spec_boxes()
    spec_inps()
    nicknames_inputs()
    abls = [BigBar.new(bar) for bar in document.select('.abl-bar')]
