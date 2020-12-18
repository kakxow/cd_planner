import json
from types import MethodType

from browser import document, html, ajax, window  # type: ignore

import data  # type: ignore
from data import START_POS, SCALE, PIXELS, Ability, abilities


def factory_activate_abl(box):
    ability_id = box.id.lstrip('box-')
    div = box.parent
    spec_id = div.id.lstrip('options-')
    spec = document[f'spec-{spec_id}']
    bar = [el for el in spec.children if el.id == f'abl-{ability_id}'][0]

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
            spec_div <= Spec(spec_obj, i)

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
    lbl = document[f'lbl-{spec_id}']

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


def px_to_float(px: str) -> float:
    return float(px[:-2])


def px_to_time(px: str) -> str:
    time_stamp = int((px_to_float(px) - START_POS) / SCALE)
    return f'{time_stamp // 60}:{time_stamp % 60:02d}'


def float_to_time(n: float) -> str:
    time_stamp = int((n - START_POS) / SCALE)
    return f'{time_stamp // 60}:{time_stamp % 60:02d}'


class Draggable(html.DIV):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def move(self, delta: int, target=None):
        new_pos = self.offsetLeft - delta
        new_pos_right = new_pos + self.ability.cool_down
        obstacles_right = \
            False if not self._right else px_to_float(self._right.style.left) < new_pos_right
        obstacles_left = \
            False if not self._left else px_to_float(self._left.style.right) > new_pos

        if obstacles_left and delta > 0:
            self._left.move(SCALE, self)
        elif obstacles_right and delta < 0:
            self._right.move(-SCALE, self)
        elif new_pos <= PIXELS and new_pos >= START_POS:
            self._move(new_pos)
            if target:
                target.move(delta)

    def _move(self, new_pos: int):
        self.style.left = f'{new_pos}px'
        self.style.right = f'{new_pos + self.ability.cool_down}px'
        self.tooltip.text = px_to_time(self.style.left)


class AbilityBar(Draggable):
    """Draggable bar with ability name"""
    def __init__(self, ability: Ability, position: float, id: str):
        super().__init__(Class='ability-bar higher20')
        self.ability = ability
        self.pos = position
        self.id = f"abl-bar-{ability.name}{id}"

        self <= self._content()
        self.tooltip = html.SPAN(px_to_time(self.style.left), Class='tooltiptext')
        self <= self.tooltip

    @classmethod
    def new(cls, bar: html.DIV, ability: Ability):
        bar.ability = ability
        bar.drag = MethodType(cls.drag, bar)
        bar.move = MethodType(cls.move, bar)
        bar._move = MethodType(cls._move, bar)
        bar.tooltip = bar.select('.tooltiptext')[0]
        return bar

    def _content(self):
        self.style.left = f'{self.pos}px'
        self.style.right = f'{self.pos + self.ability.cool_down}px'
        self.style.width = self.ability.cool_down

        duration_style = {
            'max-width': self.ability.duration,
            'width': self.ability.duration,
            'background-color': self.ability.color_main,
        }
        duration = html.TD(
            self.ability.name,
            style=duration_style,
            Class='duration'
        )

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


class AbilityRow(html.DIV):
    """Several draggable bars in one row"""
    def __init__(self, ability: Ability, id_: int):
        self.ability = ability
        abl_id = f'abl-{ability.name}{id_}'
        super().__init__(id=abl_id, Class='tooltip abl-bar')
        self._bars = [AbilityBar(ability, START_POS, '0')]
        self.bind_bars()

        self.btn_add = html.BUTTON('+', Class='btn-add', id=f'btn-{ability.name}{id_}')
        self.btn_add.unbind('click')
        self.btn_add.bind('click', self.add_bar())
        self <= self.btn_add
        self <= self._bars
        if not ability.check:
            self.style.visibility = 'hidden'
            self.style.height = '0px'

    @classmethod
    def new(cls, bar: html.DIV):
        bar.add_bar = MethodType(cls.add_bar, bar)
        bar.bind_bars = MethodType(cls.bind_bars, bar)

        ability_id = bar.id.lstrip('abl-')
        ability_name = ability_id[:-1]
        ability = next(abl for abl in abilities if abl.name == ability_name)
        bar.ability = ability
        abl_bars = bar.select('.ability-bar')
        bar._bars = [AbilityBar.new(abl_bar, ability) for abl_bar in abl_bars]
        bar.bind_bars()

        bar.btn_add = document[f'btn-{ability_id}']
        bar.btn_add.unbind('click')
        bar.btn_add.bind('click', bar.add_bar())
        return bar

    def add_bar(self):
        def adder(ev):
            bar_count = len(self._bars)
            last_bar = self._bars[-1]
            new_bar = AbilityBar(self.ability, px_to_float(last_bar.style.right), id=bar_count)
            self._bars.append(new_bar)
            self.bind_bars()
            self <= self._bars
        return adder

    def bind_bars(self):
        bar_count = len(self._bars)
        for i, bar in enumerate(self._bars):
            bar._left = self._bars[i - 1] if i > 0 else None
            bar._right = None if i == (bar_count - 1) else self._bars[i + 1]
            bar.unbind('mousedown')
            bar.bind('mousedown', bar.drag)


class Spec(html.DIV):
    """Division with several ability rows belonging to one specialization or player"""
    def __init__(self, spec: data.Spec, id: int):
        div_id = f'spec-{spec.name}{id}'
        super().__init__(id=div_id, Class=div_id.rstrip(str(id)))
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
            self <= AbilityRow(ability, self._id)
            self <= html.BR()

    def change_nick(self, ev):
        pass

    @classmethod
    def new(cls, div: html.DIV):
        return div


class SpecOpts(html.DIV):
    """Set of options for a spec - spec on/off, abilities on/off."""
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
        self <= html.LABEL(html.B(name, id=f'lbl-{name}{self._id}'), For=f'box-{name}{self._id}')
        self <= html.BR()
        for ability in self.spec.abilities:
            name = ability.name
            inp = html.INPUT(
                id=f'box-{name}{self._id}',
                Class='ability-checkbox',
                type='checkbox',
                name=f'box-{name}{self._id}')
            if ability.check:
                inp.checked = True
            lbl = html.LABEL(name, For=f'box-{name}{self._id}')
            self <= inp
            self <= lbl
            self <= html.BR()
        self <= html.HR()


def phase_serialize():
    # Serialize phases to list of dicts.
    boss_phases = []
    phases = document['phases']
    for phase_div in phases.children:
        phase_name = phase_div.textContent.strip()
        try:
            phase = list(filter(lambda x: x['name'] == phase_name, boss_phases))[0]
        except IndexError:
            phase = dict(
                name=phase_name,
                color=phase_div.style['background-color'],
                intervals=[]
            )
        interval = [float_to_time(px_to_float(phase_div.style.left) - SCALE),
                    float_to_time(px_to_float(phase_div.style.right) - SCALE)]
        phase['intervals'].append(interval)
        if len(phase['intervals']) == 1:
            boss_phases.append(phase)
    return boss_phases


def casts_serialize():
    # Serialize boss casts to list of dicts.
    boss_casts = []
    boss_actions = document['boss-casts']
    for action_div in boss_actions.children:
        action = dict(
            guid='',
            name=action_div.text.strip(),
            color=action_div.children[0].style['background-color'],
            casts=[]
        )
        for cast in action_div.children:
            try:
                tooltip = cast.select('.tooltiptext')[0]
            except IndexError:
                link = cast
                action.guid = link.href.split('=')[1]
                continue
            text = tooltip.textContent.strip()
            time = text.split(' at')[1]
            action['casts'].append(time)
        boss_casts.append(action)
    return boss_casts


def layout_serialize():
    layout = []
    specs = document['specs']
    for spec_div in specs.children:
        spec = {
            'spec': {
                'name': spec_div.id.lstrip('spec-')
            },
            'players': []
        }
        for player in spec_div.children:
            inst = {
                'nick': player.select('input')[0].value,
                'is_visible': player.style.visibility != 'hidden',
                'abilities': []
            }
            for abl in player.select('.abl-bar'):
                ability = {
                    'casts': [],
                    'name': abl.id.lstrip('abl-')[:-1]
                }
                for a in abl.select('.ability-bar'):
                    tooltip = a.select('.tooltiptext')[0]
                    time = tooltip.textContent.strip()
                    ability['casts'].append(time)
                ability['is_visible'] = abl.style.visibility != 'hidden'
                inst['abilities'].append(ability)
            spec['players'].append(inst)
        layout.append(spec)
    # Without this line dragging brakes ^^.
    enable()
    return layout


def serialize(ev):
    seconds = (len(document.select('.timeline-ruler-tick')) /
               len(document.select('.timeline-ruler')))
    res = {
        'encounter': {
            'seconds': seconds,
            'name': document['boss-select'].selectedOptions[0].text,
            # 'phases': phase_serialize(),
            'boss_actions': casts_serialize()
        },
        'layout': layout_serialize()
    }
    send(res)


def send(d: dict):
    req = ajax.Ajax()
    req.open('POST', '/save_layout')
    req.set_header('content-type', 'application/json')
    _data = json.dumps(d)
    req.send(_data)
    req.bind('complete', show_msg)


def show_msg(req):
    document['modal'].style.display = 'block'
    p = document['modal-content']

    if req.status == 200:
        msg = f'{window.location.hostname}/planner/{req.text}'
        window.history.pushState({'page': 1}, '', f'/planner/{req.text}')

    else:
        msg = f'Error {req.status}'

    p.textContent = msg


def modal_and_save():
    btn = html.BUTTON('Save', id='save-btn')
    btn.bind('click', serialize)
    document <= btn

    span = document['close-modal']
    span.bind('click', close_modal)
    window.bind('keydown', esc_close_modal)


def esc_close_modal(ev):
    if ev.keyCode == 27:
        document['modal'].style.display = 'none'


def close_modal(ev):
    document['modal'].style.display = 'none'


def lock_unlock():
    lock_btn = document['lock']

    def _lock_bind(ev):
        if lock_btn.textContent == 'Lock':
            lock()
            lock_btn.textContent = 'Unlock'
        else:
            unlock()
            lock_btn.textContent = 'Lock'

    lock_btn.bind('click', _lock_bind)


def lock():
    for el in document.select('.ability-bar'):
        el.unbind('mousedown')
    for el in document.select('input'):
        el.disabled = True


def unlock():
    enable()
    for el in document.select('input'):
        el.disabled = False


def enable():
    [AbilityRow.new(bar) for bar in document.select('.abl-bar')]


if __name__ == '__main__':
    ability_boxes()
    spec_boxes()
    spec_inps()
    nicknames_inputs()
    enable()
    modal_and_save()
    # lock_unlock()
