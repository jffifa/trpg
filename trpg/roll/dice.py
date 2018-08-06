import re
import random
import typing
import functools
import operator


class Dice(object):
    """
    self.roll_cmd = [
        [(sign, x11, y11), x12],  # group 1
        [(sign, x21, y21), x22],  # group 2
    ]
    self.roll_result = [
        [[rand between [1,y11], rand between [1,y11], ...length of x11], x12],  # group 1
        ...
    ]
    """
    DEFAULT_ROLL_CMD = '1d6'
    DEFAULT_ROLL_AGAINST = ''

    GROUP_RE = re.compile(r'^(\d+#)?(.+)$')
    DICE_RE = re.compile(r'^([+-])?((\d+)?[dD](\d+)|(\d+))')

    __slots__ = ('roll_cmd', 'roll_against', 'roll_result', 'roll_result_desc')

    def __init__(self):
        self.roll_cmd = None
        self.roll_against = None
        self.roll_result = None
        self.roll_result_desc = {}

    @classmethod
    def recursive_sum(cls, x):
        if type(x) is list:
            return functools.reduce(operator.add, map(cls.recursive_sum, x))
        else:
            return x

    def roll(self, roll_cmd, roll_against, *args, **kwargs):
        roll_cmd = roll_cmd.replace(' ', '')
        if not roll_cmd:
            roll_cmd = self.DEFAULT_ROLL_CMD

        self.roll_cmd = self.parse_roll_cmd(roll_cmd, *args, **kwargs)
        self.roll_against = self.parse_roll_against(roll_against, *args, **kwargs)
        self.do_roll()
        self.proc_roll_result(*args, **kwargs)

    def do_roll(self):
        self.roll_result = []
        for group in self.roll_cmd:
            group_result = []
            for dice in group:
                if type(dice) is int:
                    group_result.append(dice)
                else:
                    v = []
                    for i in range(dice[1]):
                        x = random.randint(1, dice[2])
                        if dice[0] == '-':
                            x = -x
                        v.append(x)
                    group_result.append(v)
            self.roll_result.append(group_result)

    def parse_roll_cmd(self, roll_cmd, *args, **kwargs):
        """

        :param roll_cmd:
            例子: 3#1d6+d100-2d20-7 表示投掷 3组 骰子，每组骰子为1d6+1d100-2d20-7
            <roll_cmd> ::= [组数#] <带符号骰子> { <带符号骰子> }
            <带符号骰子> ::= { + | - } <骰子> | <数值>
            <骰子> ::= {X}dY
        :return:
        """
        group_cnt, dice_list_str = self.parse_group(roll_cmd)
        dice_list = self.parse_dice_list(dice_list_str)

        result = []
        for i in range(group_cnt):
            result.append(dice_list)
        return result

    def parse_group(self, roll_cmd):
        match = self.GROUP_RE.match(roll_cmd)
        if match:
            if match.group(1) is not None:
                group_cnt = int(match.group(1)[:-1])
            else:
                group_cnt = 1
        else:
            raise ValueError('Invalid group count in do_roll cmd: %s' % roll_cmd)
        return group_cnt, match.group(2)

    def parse_dice_list(self, dice_list_str):
        """

        :param dice_list_str:
        :return:
            a list of tuples (sign, x, y) in "<sign>xdy"
                          or ints in "<sign>x"
        """
        result = []
        while dice_list_str:
            match = self.DICE_RE.match(dice_list_str)
            if match:
                sign = match.group(1) or '+'
                if match.group(5):
                    x = int(sign+match.group(5))
                    result.append(x)
                else:  # XdY
                    x = int(match.group(3)) if match.group(3) else 1
                    y = int(match.group(4))
                    result.append((sign, x, y,))
            else:
                raise ValueError('Invalid dice str: %s' % dice_list_str)
            dice_list_str = dice_list_str[len(match.group(0)):]
        return result

    def parse_roll_against(self, roll_against, *args, **kwargs):
        raise NotImplementedError()

    def proc_roll_result(self, *args, **kwargs):
        """
        you are given chances to process do_roll result and describe it to roll_result_desc
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    @classmethod
    def show_dice_result(cls, dice_result) -> int:
        if type(dice_result) is list:
            value = sum(dice_result)
        else:
            value = dice_result
        return value

    @classmethod
    def show_group_result(cls, group_result) -> str:
        assert(len(group_result) > 0)
        s = cls.show_dice_result(group_result[0])
        res = str(s)
        for dice_result in group_result[1:]:
            v = cls.show_dice_result(dice_result)
            s += v
            res += ('+' if v>=0 else '') + str(v)
        if len(group_result) > 1:
            res += '='+str(s)
        return res

    @classmethod
    def show_result(cls, roll_result):
        """

        :return:
            get a string representing result
        """
        if len(roll_result) == 1:  # only 1 group
            return cls.show_group_result(roll_result[0])
        else:
            return '{%s}' % ', '.join(map(cls.show_group_result, roll_result))


class Coc6eDice(Dice):
    DEFAULT_ROLL_CMD = '1d100'
    ROLL_AGAINST_CHAR_RE = re.compile(r'^\{c:([^\}]+)\}')
    ROLL_AGAINST_VALUE_RE = re.compile(r'\{v:(\d+)([+-]\d+)?\}')
    '''\s*()\s*(\S+)'''

    __slots__ = ('get_char_details', )

    def __init__(self, get_char_details: typing.Callable[[str], typing.Optional[typing.Dict]]):
        self.get_char_details = get_char_details
        super(Coc6eDice, self).__init__()

    @classmethod
    def get_value_from_details(cls, details, comment):
        for grp in ['basic_info', 'num_info', 'skills']:
            if grp in details:
                for k, v in details[grp].items():
                    if v.get('checkable', False) and \
                            comment in k and \
                            type(v['value']) is int:
                        value = v['value']
                        value_str = str(value)
                        return k, value, value_str

        return comment, None, None

    def parse_roll_against(self, roll_against, *args, **kwargs):
        roll_against = roll_against.strip()
        char_name = kwargs.get('char_name')
        value = None
        value_str = None
        comment = None

        match = self.ROLL_AGAINST_CHAR_RE.match(roll_against)
        if match:
            char_name = match.group(1)
            roll_against = roll_against[len(match.group(0)):].lstrip()

        match = self.ROLL_AGAINST_VALUE_RE.match(roll_against)
        if match:
            value = int(match.group(1))
            value_str = match.group(1)
            if match.group(2) is not None:
                value += int(match.group(2))
                value_str += match.group(2)
            roll_against = roll_against[len(match.group(0)):].lstrip()

        if roll_against:
            comment = roll_against
            if value is None:  # try get value from character details
                details = self.get_char_details(char_name)
                if details:
                    comment, value, value_str = self.get_value_from_details(details, comment)

        return {
            'char_name': char_name if value is not None else None,
            'value': value,
            'value_str': value_str,
            'comment': comment,
        }

    def is_d100_roll(self):
        if len(self.roll_cmd) == 1 and len(self.roll_cmd[0]) == 1:
            dice = self.roll_cmd[0][0]
            if (type(dice) is tuple) and dice[0]=='+' and dice[1]==1 and dice[2]==100:
                return True
        return False

    def proc_roll_result(self, *args, **kwargs):
        if (self.roll_against['value'] is not None) and (
            len(self.roll_result) == 1
        ):  # only deal with one group do_roll result
            result_sum = self.recursive_sum(self.roll_result[0])
            if result_sum <= self.roll_against['value']:
                self.roll_result_desc['result'] = 'succ'
            else:
                self.roll_result_desc['result'] = 'fail'
            if self.is_d100_roll():  # d100 dice
                if result_sum > 95:
                    self.roll_result_desc['result'] = 'g_fail'
                elif self.roll_result_desc['result'] == 'succ' and result_sum <= 5:
                    self.roll_result_desc['result'] = 'g_succ'

