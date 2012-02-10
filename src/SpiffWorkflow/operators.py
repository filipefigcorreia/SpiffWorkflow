# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import re

class Attrib(object):
    """
    Used for marking a value such that it is recognized to be an
    attribute name by valueod().
    """
    def __init__(self, name):
        self.name = name

def valueof(scope, op):
    if op is None:
        return None
    elif isinstance(op, Attrib):
        return scope.get_attribute(op.name)
    else:
        return op

class Operator(object):
    """
    Abstract base class for all operators.
    """

    def __init__(self, *args):
        """
        Constructor.
        """
        if len(args) == 0:
            raise TypeException("Too few arguments")
        self.args = args

    def _get_values(self, task):
        values = []
        for arg in self.args:
            values.append(unicode(valueof(task, arg)))
        return values

    def _matches(self, task):
        raise Exception("Abstract class, do not call")

class Equal(Operator):
    """
    This class represents the EQUAL operator.
    """
    def _matches(self, task):
        values = self._get_values(task)
        last   = values[0]
        for value in values:
            if value != last:
                return False
            last = value
        return True

class NotEqual(Operator):
    """
    This class represents the NOT EQUAL operator.
    """
    def _matches(self, task):
        values = self._get_values(task)
        last   = values[0]
        for value in values:
            if value != last:
                return True
            last = value
        return False

class GreaterThan(Operator):
    """
    This class represents the GREATER THAN operator.
    """
    def __init__(self, left, right):
        """
        Constructor.
        """
        Operator.__init__(self, left, right)

    def _matches(self, task):
        left, right = self._get_values(task)
        return int(left) > int(right)

class LessThan(Operator):
    """
    This class represents the LESS THAN operator.
    """
    def __init__(self, left, right):
        """
        Constructor.
        """
        Operator.__init__(self, left, right)

    def _matches(self, task):
        left, right = self._get_values(task)
        return int(left) < int(right)

class Match(Operator):
    """
    This class represents the regular expression match operator.
    """
    def __init__(self, regex, *args):
        """
        Constructor.
        """
        Operator.__init__(self, *args)
        self.regex = re.compile(regex)

    def _matches(self, task):
        for value in self._get_values(task):
            if not self.regex.search(value):
                return False
        return True
