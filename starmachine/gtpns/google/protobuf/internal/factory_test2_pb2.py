# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/protobuf/internal/factory_test2.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import starmachine.gtpns.google.protobuf.internal.factory_test1_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='google/protobuf/internal/factory_test2.proto',
  package='google.protobuf.python.internal',
  serialized_pb='\n,google/protobuf/internal/factory_test2.proto\x12\x1fgoogle.protobuf.python.internal\x1a,google/protobuf/internal/factory_test1.proto\"\xa9\n\n\x0f\x46\x61\x63tory2Message\x12\x11\n\tmandatory\x18\x01 \x02(\x05\x12\x45\n\x0e\x66\x61\x63tory_2_enum\x18\x02 \x01(\x0e\x32-.google.protobuf.python.internal.Factory2Enum\x12\x62\n\x15nested_factory_2_enum\x18\x03 \x01(\x0e\x32\x43.google.protobuf.python.internal.Factory2Message.NestedFactory2Enum\x12h\n\x18nested_factory_2_message\x18\x04 \x01(\x0b\x32\x46.google.protobuf.python.internal.Factory2Message.NestedFactory2Message\x12K\n\x11\x66\x61\x63tory_1_message\x18\x05 \x01(\x0b\x32\x30.google.protobuf.python.internal.Factory1Message\x12\x45\n\x0e\x66\x61\x63tory_1_enum\x18\x06 \x01(\x0e\x32-.google.protobuf.python.internal.Factory1Enum\x12\x62\n\x15nested_factory_1_enum\x18\x07 \x01(\x0e\x32\x43.google.protobuf.python.internal.Factory1Message.NestedFactory1Enum\x12h\n\x18nested_factory_1_message\x18\x08 \x01(\x0b\x32\x46.google.protobuf.python.internal.Factory1Message.NestedFactory1Message\x12J\n\x10\x63ircular_message\x18\t \x01(\x0b\x32\x30.google.protobuf.python.internal.Factory2Message\x12\x14\n\x0cscalar_value\x18\n \x01(\t\x12\x12\n\nlist_value\x18\x0b \x03(\t\x12I\n\x07grouped\x18\x0c \x03(\n28.google.protobuf.python.internal.Factory2Message.Grouped\x12:\n\x04loop\x18\x0f \x01(\x0b\x32,.google.protobuf.python.internal.LoopMessage\x12\x1e\n\x10int_with_default\x18\x10 \x01(\x05:\x04\x31\x37\x37\x36\x12!\n\x13\x64ouble_with_default\x18\x11 \x01(\x01:\x04\x39.99\x12(\n\x13string_with_default\x18\x12 \x01(\t:\x0bhello world\x12 \n\x11\x62ool_with_default\x18\x13 \x01(\x08:\x05\x66\x61lse\x12[\n\x11\x65num_with_default\x18\x14 \x01(\x0e\x32-.google.protobuf.python.internal.Factory2Enum:\x11\x46\x41\x43TORY_2_VALUE_1\x1a&\n\x15NestedFactory2Message\x12\r\n\x05value\x18\x01 \x01(\t\x1a)\n\x07Grouped\x12\x0e\n\x06part_1\x18\r \x01(\t\x12\x0e\n\x06part_2\x18\x0e \x01(\t\"P\n\x12NestedFactory2Enum\x12\x1c\n\x18NESTED_FACTORY_2_VALUE_0\x10\x00\x12\x1c\n\x18NESTED_FACTORY_2_VALUE_1\x10\x01\"M\n\x0bLoopMessage\x12>\n\x04loop\x18\x01 \x01(\x0b\x32\x30.google.protobuf.python.internal.Factory2Message*<\n\x0c\x46\x61\x63tory2Enum\x12\x15\n\x11\x46\x41\x43TORY_2_VALUE_0\x10\x00\x12\x15\n\x11\x46\x41\x43TORY_2_VALUE_1\x10\x01')

_FACTORY2ENUM = _descriptor.EnumDescriptor(
  name='Factory2Enum',
  full_name='google.protobuf.python.internal.Factory2Enum',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='FACTORY_2_VALUE_0', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FACTORY_2_VALUE_1', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1530,
  serialized_end=1590,
)

Factory2Enum = enum_type_wrapper.EnumTypeWrapper(_FACTORY2ENUM)
FACTORY_2_VALUE_0 = 0
FACTORY_2_VALUE_1 = 1


_FACTORY2MESSAGE_NESTEDFACTORY2ENUM = _descriptor.EnumDescriptor(
  name='NestedFactory2Enum',
  full_name='google.protobuf.python.internal.Factory2Message.NestedFactory2Enum',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NESTED_FACTORY_2_VALUE_0', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NESTED_FACTORY_2_VALUE_1', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1369,
  serialized_end=1449,
)


_FACTORY2MESSAGE_NESTEDFACTORY2MESSAGE = _descriptor.Descriptor(
  name='NestedFactory2Message',
  full_name='google.protobuf.python.internal.Factory2Message.NestedFactory2Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='google.protobuf.python.internal.Factory2Message.NestedFactory2Message.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1286,
  serialized_end=1324,
)

_FACTORY2MESSAGE_GROUPED = _descriptor.Descriptor(
  name='Grouped',
  full_name='google.protobuf.python.internal.Factory2Message.Grouped',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='part_1', full_name='google.protobuf.python.internal.Factory2Message.Grouped.part_1', index=0,
      number=13, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='part_2', full_name='google.protobuf.python.internal.Factory2Message.Grouped.part_2', index=1,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1326,
  serialized_end=1367,
)

_FACTORY2MESSAGE = _descriptor.Descriptor(
  name='Factory2Message',
  full_name='google.protobuf.python.internal.Factory2Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mandatory', full_name='google.protobuf.python.internal.Factory2Message.mandatory', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='factory_2_enum', full_name='google.protobuf.python.internal.Factory2Message.factory_2_enum', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nested_factory_2_enum', full_name='google.protobuf.python.internal.Factory2Message.nested_factory_2_enum', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nested_factory_2_message', full_name='google.protobuf.python.internal.Factory2Message.nested_factory_2_message', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='factory_1_message', full_name='google.protobuf.python.internal.Factory2Message.factory_1_message', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='factory_1_enum', full_name='google.protobuf.python.internal.Factory2Message.factory_1_enum', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nested_factory_1_enum', full_name='google.protobuf.python.internal.Factory2Message.nested_factory_1_enum', index=6,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nested_factory_1_message', full_name='google.protobuf.python.internal.Factory2Message.nested_factory_1_message', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='circular_message', full_name='google.protobuf.python.internal.Factory2Message.circular_message', index=8,
      number=9, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='scalar_value', full_name='google.protobuf.python.internal.Factory2Message.scalar_value', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='list_value', full_name='google.protobuf.python.internal.Factory2Message.list_value', index=10,
      number=11, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='grouped', full_name='google.protobuf.python.internal.Factory2Message.grouped', index=11,
      number=12, type=10, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='loop', full_name='google.protobuf.python.internal.Factory2Message.loop', index=12,
      number=15, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='int_with_default', full_name='google.protobuf.python.internal.Factory2Message.int_with_default', index=13,
      number=16, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=1776,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='double_with_default', full_name='google.protobuf.python.internal.Factory2Message.double_with_default', index=14,
      number=17, type=1, cpp_type=5, label=1,
      has_default_value=True, default_value=9.99,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='string_with_default', full_name='google.protobuf.python.internal.Factory2Message.string_with_default', index=15,
      number=18, type=9, cpp_type=9, label=1,
      has_default_value=True, default_value=unicode("hello world", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bool_with_default', full_name='google.protobuf.python.internal.Factory2Message.bool_with_default', index=16,
      number=19, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='enum_with_default', full_name='google.protobuf.python.internal.Factory2Message.enum_with_default', index=17,
      number=20, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_FACTORY2MESSAGE_NESTEDFACTORY2MESSAGE, _FACTORY2MESSAGE_GROUPED, ],
  enum_types=[
    _FACTORY2MESSAGE_NESTEDFACTORY2ENUM,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=128,
  serialized_end=1449,
)


_LOOPMESSAGE = _descriptor.Descriptor(
  name='LoopMessage',
  full_name='google.protobuf.python.internal.LoopMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='loop', full_name='google.protobuf.python.internal.LoopMessage.loop', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1451,
  serialized_end=1528,
)

_FACTORY2MESSAGE_NESTEDFACTORY2MESSAGE.containing_type = _FACTORY2MESSAGE;
_FACTORY2MESSAGE_GROUPED.containing_type = _FACTORY2MESSAGE;
_FACTORY2MESSAGE.fields_by_name['factory_2_enum'].enum_type = _FACTORY2ENUM
_FACTORY2MESSAGE.fields_by_name['nested_factory_2_enum'].enum_type = _FACTORY2MESSAGE_NESTEDFACTORY2ENUM
_FACTORY2MESSAGE.fields_by_name['nested_factory_2_message'].message_type = _FACTORY2MESSAGE_NESTEDFACTORY2MESSAGE
_FACTORY2MESSAGE.fields_by_name['factory_1_message'].message_type = google.protobuf.internal.factory_test1_pb2._FACTORY1MESSAGE
_FACTORY2MESSAGE.fields_by_name['factory_1_enum'].enum_type = google.protobuf.internal.factory_test1_pb2._FACTORY1ENUM
_FACTORY2MESSAGE.fields_by_name['nested_factory_1_enum'].enum_type = google.protobuf.internal.factory_test1_pb2._FACTORY1MESSAGE_NESTEDFACTORY1ENUM
_FACTORY2MESSAGE.fields_by_name['nested_factory_1_message'].message_type = google.protobuf.internal.factory_test1_pb2._FACTORY1MESSAGE_NESTEDFACTORY1MESSAGE
_FACTORY2MESSAGE.fields_by_name['circular_message'].message_type = _FACTORY2MESSAGE
_FACTORY2MESSAGE.fields_by_name['grouped'].message_type = _FACTORY2MESSAGE_GROUPED
_FACTORY2MESSAGE.fields_by_name['loop'].message_type = _LOOPMESSAGE
_FACTORY2MESSAGE.fields_by_name['enum_with_default'].enum_type = _FACTORY2ENUM
_FACTORY2MESSAGE_NESTEDFACTORY2ENUM.containing_type = _FACTORY2MESSAGE;
_LOOPMESSAGE.fields_by_name['loop'].message_type = _FACTORY2MESSAGE
DESCRIPTOR.message_types_by_name['Factory2Message'] = _FACTORY2MESSAGE
DESCRIPTOR.message_types_by_name['LoopMessage'] = _LOOPMESSAGE

class Factory2Message(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class NestedFactory2Message(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _FACTORY2MESSAGE_NESTEDFACTORY2MESSAGE

    # @@protoc_insertion_point(class_scope:google.protobuf.python.internal.Factory2Message.NestedFactory2Message)

  class Grouped(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _FACTORY2MESSAGE_GROUPED

    # @@protoc_insertion_point(class_scope:google.protobuf.python.internal.Factory2Message.Grouped)
  DESCRIPTOR = _FACTORY2MESSAGE

  # @@protoc_insertion_point(class_scope:google.protobuf.python.internal.Factory2Message)

class LoopMessage(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LOOPMESSAGE

  # @@protoc_insertion_point(class_scope:google.protobuf.python.internal.LoopMessage)


# @@protoc_insertion_point(module_scope)
