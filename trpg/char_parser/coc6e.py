from .base import CharParser
import re


# TODO: use json schema to define
class Coc6eCharParser(CharParser):
    ordered_keys = ['basic_info', 'num_info', 'skills', 'background', 'luggage', 'extra',]
    editable = {
        'basic_info': ['克苏鲁神话点数', '力量', '体质', '意志', '敏捷', '外表', '体型', '智力', '教育', '财产'],
        'num_info': True,
        'skills': True,
    }
    checkable = {
        'num_info': ['心智点', '灵感', '幸运', '理智', '知识'],
        'skills': True,
    }

    line_regex = re.compile(r'^(.+):  (.+)$')

    def parse(self, text):
        detail_dict = {k: {} for k in self.ordered_keys}
        states = iter(self.ordered_keys)
        state = next(states)
        show_order = 0

        for line in text.splitlines():
            line = line.strip()
            if not line:
                # empty line should change state
                try:
                    state = next(states)
                except StopIteration:
                    pass
                continue

            match = self.line_regex.match(line)
            if not match:
                continue

            property_name = match.group(1)
            try:
                # int value
                property_value = int(match.group(2))
            except ValueError:
                # string value
                property_value = match.group(2)
                property_value = property_value.replace(r'\n', '\n')

            if state in ('background', 'luggage',):
                detail_dict[state] = property_value
            else:
                show_order += 1
                value_detail = {
                    'show_order': show_order,
                    'value': property_value,
                    'editable': False
                }
                editable = self.editable.get(state, {})
                if (editable is True) or (property_name in editable):
                    value_detail['editable'] = True
                checkable = self.checkable.get(state, {})
                if (checkable is True) or (property_name in checkable):
                    value_detail['checkable'] = True
                detail_dict[state][property_name] = value_detail

        if '姓名' not in detail_dict['basic_info']:
            raise ValueError('导入资料缺少“姓名”')
        else:
            detail_dict['name'] = detail_dict['basic_info']['姓名']['value']

        if '玩家' not in detail_dict['basic_info']:
            raise ValueError('导入资料缺少“玩家”')
        else:
            detail_dict['player'] = detail_dict['basic_info']['玩家']['value']

        self.details.update(detail_dict)
        return self.details
