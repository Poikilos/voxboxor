#!/usr/bin/env python3
from copy import deepcopy
import struct
from struct import Struct
from collections import namedtuple

from voxboxor import (
    # set_verbosity,
    echo0,
    echo1,
    echo2,
)

# See minetest/doc/protocol.txt:
# - Minetest ints are always big-endian
def to_u8(i):
    # TYPE_CONTROL = bytes((0,))
    # ^ In Python 2 it returns string '(0,)' (See
    #   <https://stackoverflow.com/a/9645259/4541104>).
    # Python 3 only:
    return i.to_bytes(1, 'big')

PROTOCOL_ID = 0x4f457403  # 32-bit
PEER_ID_INEXISTENT = 0  # 16-bit
TYPE_CONTROL = to_u8(0)
TYPE_ORIGINAL = to_u8(1)
TYPE_RELIABLE = to_u8(3)
U8_0 = to_u8(0)
CONTROLTYPE_SET_PEER_ID = to_u8(1)  # 8-bit CONTROLTYPE! 16-bit ID above
CONTROLTYPE_DISCO = to_u8(3)
SEQNUM_INITIAL = 65500  # 16-bit


def _to_c_like_u32(value):
    return int(value)

def _to_c_like_u16(value):
    return int(value)

_c_like_converters = {}
_c_like_converters['c'] = to_u8
_c_like_converters['H'] = _to_c_like_u16
_c_like_converters['L'] = _to_c_like_u32

_c_like_names = {}
_c_like_names['c'] = "u8"
_c_like_names['H'] = "u16"
_c_like_names['L'] = "u32"


def _get_aspect(packet_category, key, aspect):
    ''''
    Get a list of entries in an aspect in packetdefs. If the given
    aspect isn't specific to the key, '*' will be used. If the given
    aspect is 'values', the results are defaults so the corresponding
    values must be filled (the name is obtainable from the
    corresponding sequential entry in the 'names' aspect). The filled
    values will be converted to the correct C-like types by the
    get_packet_bytes function (which calls to_c_like automatically).

    Sequential arguments:
    packet_category -- 'basic', 'reliable', 'original', or 'control'
    key -- c_connect, or any other packet template
    aspect -- any aspect of the packet: 'types', 'names', or 'values'

    Returns:
    the list of entries for the given aspect.
    '''
    catdef = packetdefs[packet_category]
    # get       catdef[key][aspect]
    # otherwise catdef['*'][aspect]
    aspects = catdef.get(key)
    this_key = key
    if aspects is None:
        echo2("- using * since there are no aspects for catdef of key"
              " {}"
              "".format(key))
        this_key = '*'
        aspects = catdef['*']
    if aspect not in aspects:
        echo2("- using * since there is no aspect {} for aspects for catdef of key"
              " {}"
              "".format(aspect, key))
        this_key = '*'
        aspects = catdef['*']
    if aspect not in aspects:
        raise ValueError(
            "There is no aspect={} of category={} key={}"
            " (aspects={})"
            "".format(aspect, packet_category, this_key, aspects)
        )
    return aspects[aspect]


def to_c_like(name, value):
    for category, catdef in packetdefs.items():
        for key, aspects in catdef.items():
            for aspect, values in aspects.items():
                if aspect != 'values':
                    # echo2("")
                    # echo2("{} != values for {} {}"
                    #       "".format(aspect, category, key))
                    continue
                # Get everything else based on values.
                c_types = _get_aspect(category, key, 'types')
                names = _get_aspect(category, key, 'names')
                echo2("")
                echo2("{} {} values={}".format(category, key, values))
                echo2("{} {} c_types={}".format(category, key, c_types))
                echo2("{} {} names={}".format(category, key, names))
                for i in range(len(names)):
                    known_name = names[i]
                    if known_name == name:
                        c = c_types[i]
                        # f = _c_like_converters[c]
                        # return f(value)
                        echo2("to_c_like({}) converts to {}"
                              "".format(name, _c_like_names[c]))
                        return _c_like_converters[c](value)
    raise ValueError("to_c_like({}) converts to None".format(name))
    return None

# "for" variables each have a purpose. Some standard purposes include:
# - c_connect: client's first packet requesting a connection
# - s_connect: server's response to a connection request from a client

basic_h_p = "LHc"
basic_h_p_names = ('protocol_id', 'sender_peer_id', 'channel')
basic_h_p_values_for = {}
basic_h_p_values_for['c_connect'] = (PROTOCOL_ID, PEER_ID_INEXISTENT, U8_0)
basic_h_p_values_for['s_connected'] = (PROTOCOL_ID, PEER_ID_INEXISTENT, U8_0)
basic_h_p_values_for['c_disconnect'] = (PROTOCOL_ID, None, U8_0)
reliable_h_p = "cH"
reliable_h_p_names = ('type', 'seqnum')
reliable_h_p_values_for = {}
reliable_h_p_values_for['c_connect'] = (TYPE_RELIABLE, SEQNUM_INITIAL)
reliable_h_p_values_for['s_connected'] = (TYPE_RELIABLE, SEQNUM_INITIAL)
# There is no reliable packet header for disconnect, only basic+control
orig_h_p = "c"
orig_h_p_names = ('type',)
orig_h_p_values_for = {}
orig_h_p_values_for['c_connect'] = (TYPE_ORIGINAL,)

# control packets (c_ if from this client, s_ if from server):
control_p_for = {}
# There is no control packet for c_connect, only an original packet.
control_p_for['s_connected'] = "ccH"
control_p_for['c_disconnect'] = "cc"
control_p_names_for = {}
control_p_names_for['s_connected'] = ('type', 'controltype', 'peer_id_new')
control_p_names_for['c_disconnect'] = ('type', 'controltype')
control_p_values_for = {}
control_p_values_for['s_connected'] = (TYPE_CONTROL, CONTROLTYPE_SET_PEER_ID, None)
control_p_values_for['c_disconnect'] = (TYPE_CONTROL, CONTROLTYPE_DISCO)

packetdefs = {}
packetdefs['basic'] = {}
packetdefs['basic']['*'] = {}
packetdefs['basic']['*']['types'] = basic_h_p
packetdefs['basic']['*']['names'] = basic_h_p_names
for key, values in basic_h_p_values_for.items():
    packetdefs['basic'][key] = {}
    packetdefs['basic'][key]['values'] = values

packetdefs['reliable'] = {}
packetdefs['reliable']['*'] = {}
packetdefs['reliable']['*']['types'] = reliable_h_p
packetdefs['reliable']['*']['names'] = reliable_h_p_names
for key, values in reliable_h_p_values_for.items():
    packetdefs['reliable'][key] = {}
    packetdefs['reliable'][key]['values'] = values

packetdefs['original'] = {}
packetdefs['original']['*'] = {}
packetdefs['original']['*']['types'] = orig_h_p
packetdefs['original']['*']['names'] = orig_h_p_names
# packetdefs['original']['c_connect']['values'] = orig_h_p_values_for['c_connect']
for key, values in orig_h_p_values_for.items():
    packetdefs['original'][key] = {}
    packetdefs['original'][key]['values'] = values

packetdefs['control'] = {}
for key, values in control_p_values_for.items():
    packetdefs['control'][key] = {}
    packetdefs['control'][key]['types'] = control_p_for[key]
    packetdefs['control'][key]['names'] = control_p_names_for[key]
    packetdefs['control'][key]['values'] = values


# See https://docs.python.org/3/library/struct.html:
# 'H': unsigned 16-bit int
# 'c': char (unsigned byte)
# '>': big-endian



def get_packet_format(origin, purpose):
    '''
    Sequential arguments:
    origin -- must be client or server
    purpose -- Set the purpose to determine the packet structure. For
        example, if the origin is "client" and the purpose is "connect",
        then for constructing the packet the "c_connect" key will be
        used to access the correct values from basic_h_p_values_for +
        reliable_h_p_values_for + orig_h_p_values_for (The
        orig_h_p* objects are used to construct a connect packet,
        but the control_p* objects are used for other purposes). To
        allow a client to connect, set origin="server" and
        purpose="connected".

    Returns:
    a tuple of pack, pack_names, defaults, fieldsdef:
    - pack: a string of Struct format characters, one char per field
    - pack_names: a list of name strings (only unique to category, not
      to entire packet), one per field
    - defaults: default values corresponding to the fields
    - fieldsdef: a list of tuples, where each is a category and the
      count of entries. The length of fieldsdef does *not* correspond
      to the number of fields like the other returns do, but the total
      of all counts does. There is one fieldsdef entry for each
      category.
    '''
    fieldsdef = []
    o_pre = None
    if origin == "server":
        o_pre = "s"
    elif origin == "client":
        o_pre = "c"
    else:
        raise ValueError("Origin must be client or server.")
    key = o_pre + "_" + purpose
    pack = None
    pack_names = None
    defaults = None
    try_defaults = basic_h_p_values_for.get(key)
    if try_defaults is None:
        raise ValueError("There is no basic header for {}".format(key))
    if not isinstance(try_defaults, tuple):
        raise ValueError(
            "basic_h_p_values_for['{}'] must be a tuple".format(key)
        )
    defaults = deepcopy(try_defaults)
    # deepcopy unnecessary for tuple since immutable; but would be for
    #   list (each of them including further down) since modified below.

    if len(basic_h_p_names) != len(basic_h_p):
        raise ValueError(
            "Bad packed definition: length {} != {}"
            " for basic_h_p_names <- basic_h_p"
            "".format(len(basic_h_p_names), len(basic_h_p), key)
        )


    if not isinstance(basic_h_p_names, tuple):
        raise ValueError(
            "basic_h_p_names must be a tuple"
        )
    pack_names = deepcopy(basic_h_p_names)

    if not isinstance(basic_h_p, str):
        raise ValueError(
            "basic_h_p must be a str"
        )
    pack = basic_h_p
    fieldsdef.append(('basic', len(basic_h_p)))

    reliable_h_p_values = reliable_h_p_values_for.get(key)
    if reliable_h_p_values is not None:
        pack += reliable_h_p
        if len(reliable_h_p_names) != len(reliable_h_p_values):
            raise ValueError(
                "Bad packed definition: length {} != {}"
                " for reliable_h_p_names <- reliable_h_p_values"
                "".format(len(reliable_h_p_names),
                          len(reliable_h_p_values), key)
            )
        pack_names += reliable_h_p_names
        defaults += reliable_h_p_values
        fieldsdef.append(('reliable', len(reliable_h_p_values)))

    orig_h_p_values = orig_h_p_values_for.get(key)
    control_p_values = control_p_values_for.get(key)
    if orig_h_p_values is not None:
        pack += orig_h_p
        if len(orig_h_p_names) != len(orig_h_p_values_for[key]):
            raise ValueError(
                "Bad packed definition: length {} != {}"
                " for orig_h_p_names <- orig_h_p_values_for[{}]"
                "".format(len(orig_h_p_names),
                          len(orig_h_p_values_for[key]), key)
            )
        pack_names += orig_h_p_names
        defaults += orig_h_p_values_for[key]
        fieldsdef.append(('original', len(orig_h_p_values_for[key])))
    elif control_p_values:
        pack += control_p_for[key]
        if len(control_p_names_for[key]) != len(control_p_values):
            raise ValueError(
                "Bad packed definition: length {} != {}"
                " for orig_h_p_names <- orig_h_p_values_for[{}]"
                "".format(len(control_p_names_for[key]),
                          len(control_p_values), key)
            )
        pack_names += control_p_names_for[key]
        defaults += control_p_values
        fieldsdef.append(('control', len(control_p_values)))
    else:
        raise ValueError(
            "Only a connect packet (one with an original packet header)"
            " doesn't have a control packet."
        )

    if (len(pack) != len(pack_names)) or len(pack) != len(defaults):
        debug_parts = []
        for pair in fieldsdef:
            debug_parts.append(pair[0])
        raise ValueError(
            "The packet definitions are bad for {} {}"
            "--lengths don't match after combining {} ({})"
            " len({}) != len({}): "
            "len(pack)={}, len(pack_names)={}, len(defaults)={}"
            "".format(origin, purpose,
                      "+".join(debug_parts), pack,
                      pack_names, defaults,
                      len(pack), len(pack_names), len(defaults))
        )

    return pack, pack_names, defaults, fieldsdef


def get_packet_bytes(origin, purpose, values):
    '''
    Translate values to bytes in the form of a packet.

    Sequential arguments:
    origin -- See get_packet_format for documentation.
    purpose -- See get_packet_format for documentation.
    values -- This dict contains parameters if any are required. For
        example, s_connected is constructed by the server, and the
        third param of control_p_values_for['s_connected'] is None,
        and the third name of control_p_names_for['s_connected'] is
        peer_id_new, therefore the server must set values['peer_id_new']
        or an exception will be raised.
    '''
    pack, pack_names, pack_values, fieldsdef = get_packet_format(
        origin,
        purpose,
    )
    missing_keys = []
    for i in range(len(pack_values)):
        default_value = pack_values[i]
        if default_value is None:
            custom_value = values.get(pack_names[i])
            if custom_value is None:
                missing_keys.append(pack_names[i])
                continue
            pack_values = list(pack_values)
            pack_values[i] = to_c_like(pack_names[i], custom_value)
            pack_values = tuple(pack_values)
    if len(missing_keys) > 0:
        raise ValueError(
            "Constructing a {} {} packet requires values to have the"
            " keys with no default: {}"
            "".format(origin, purpose, missing_keys)
        )
    # See https://docs.python.org/3/library/struct.html:
    # '>': big-endian
    Packet = Struct(">"+pack)  # '>': Minetest is always big-endian
    try:
        return Packet.pack(*pack_values)
    except struct.error as ex:
        echo0(
            "Struct couldn't pack packet values for {} {}"
            " pack={}, pack_names={}, pack_values={}"
            " len(pack)={}, len(pack_names)={}, len(pack_values)={}"
            "".format(origin, purpose,
                      pack, pack_names, pack_values,
                      len(pack), len(pack_names), len(pack_values))
        )
        raise ex


class MinetestPacket:
    def __init__(self, names, values, fieldsdef):
        '''
        Sequential arguments:
        fieldsdef -- A list of tuples, each like (category, count) where
            the total of all counts is the same as len(names) and
            len(values).
        names -- a list of names of variables.
        values -- values that correspond to names by the same sequential
            index
        '''
        self.names = names
        self.values = values
        self.fieldsdef = fieldsdef

    def get(self, name, category='control'):
        '''
        Sequential arguments:
        category -- Names are not unique in a Minetest packet, only a
            packet section. The category name defines the packet
            section: 'basic', 'reliable', 'original', 'control
        '''
        cat_i = 0
        cat_name = self.fieldsdef[cat_i][0]
        cat_sub_i = 0
        for i in range(len(self.names)):
            if cat_sub_i == self.fieldsdef[cat_i][1]:
                cat_i += 1
                cat_name = self.fieldsdef[cat_i][0]
                cat_sub_i = 0
            if cat_name == category:
                if self.names[i] == name:
                    return self.values[i]
            cat_sub_i += 1
        raise KeyError("There is no {} in {}".format(name, category))


def bytes_to_packet(origin, purpose, packet_bytes):
    '''
    Translate a network UDP packet into a MinetestPacket object.

    Sequential arguments:
    origin -- See the get_packet_bytes documentation.
    purpose -- See the get_packet_bytes documentation.
    packet_bytes -- A set of packets generated by get_packet_bytes, but
        hopefully any packet created by any Minetest version will work
        eventually.
    '''
    # formerly packet_to_dict
    pack, pack_names, pack_values, fieldsdef = get_packet_format(
        origin,
        purpose,
    )
    del pack_values
    # See <https://docs.python.org/2/library/struct.html#struct.unpack>
    # Packet = Struct(">"+pack)  # '>': Minetest is always big-endian
    # PacketNT = namedtuple('Packet', pack_names)
    # return PacketNT._make(struct.unpack(">"+pack, packet_bytes))
    # ^ Above is impossible because there are duplicate field names :(
    values = struct.unpack(">"+pack, packet_bytes)
    return MinetestPacket(pack_names, values, fieldsdef)
