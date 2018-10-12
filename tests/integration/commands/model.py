#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#


class ArgumentBase(object):

    def __init__(self, required=False, default=None):
        self.required = required
        self.default = default

    def attach(self, field_name):
        self.field_name = field_name
        return self.default

    def value(self, model):
        value = getattr(model, self.field_name, None)

        if value is None:
            if self.required:
                raise Exception("{} is required".format(self.field_name))
            else:
                value = self.default

        return value

    def format(self, model):
        raise NotImplemented("Base class has no implementation")


class NamedArgument(ArgumentBase):

    def __init__(self, argument, required=False, default=None, flag=False):
        self.argument = argument
        self.flag = flag

        if flag and default is None:
            default = False

        super(NamedArgument, self).__init__(required=required, default=default)

    def format(self, model):
        value = self.value(model)

        if self.flag:
            return self.argument if value else ""

        if value is None:
            return ""

        return "{} \"{}\"".format(self.argument, value)


class ArgumentFormatter(object):

    def __init__(self, arguments):
        self.arguments = arguments

    def get_run_cmd(self, model, positional_arguments):
        args = " ".join(
            filter(lambda fmt: fmt != "",
                   map(lambda arg: arg.format(model), self.arguments)))

        positional_args = " ".join(
            map(lambda arg: "\"{}\"".format(arg), positional_arguments))

        cmd = "{} {} {}".format(model.binary, args, positional_args)

        return cmd


class ModelBase(type):
    """
    Metaclass for command wrapper Models
    """

    def __new__(cls, name, bases, attributes):
        """
        Construct a new Model class
        """

        module = attributes.pop('__module__')
        new_class = super(ModelBase, cls).__new__(
                cls, name, bases, {'__module__': module})

        if 'binary' not in attributes:
            raise Exception("Model class needs to have a binary")

        # Hack to allow us building Model class without specifying binary, but
        # failing to build any subclass of Model without binary
        if attributes['binary'] is None:
            del attributes['binary']

        arguments = []
        # Populating with attributes
        for name, attribute in attributes.viewitems():
            if isinstance(attribute, ArgumentBase):
                setattr(new_class, name, attribute.attach(name))
                arguments.append(attribute)
            else:
                setattr(new_class, name, attribute)

        formatter = ArgumentFormatter(arguments)
        setattr(new_class, "__formatter__", formatter)

        return new_class


class Model(object):
    __metaclass__ = ModelBase

    binary = None

    def get_run_cmd(self, *positional_arguments):
        return self.__formatter__.get_run_cmd(self, positional_arguments)
