#!/usr/bin/env python3

import xml.etree.cElementTree as ET
import sys
from operator import itemgetter
class frame_mang():
    Frame_stack = []
    GF = {}
    TF = None
    LF = None


def parser(xml_doc, program):

    no_arg_instructions = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']
    able_to_be_label = ['LABEL', 'CALL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ']
    var_symb_symb = ['ADD', 'SUB', 'MUL', 'IDIV', 'GT', 'LT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']
    const = ['int', 'string', 'bool', 'nil']
    symb = const + ['var']
    labels = []
    if list(xml_doc.attrib.values())[0] != 'IPPcode19':
        exit(32)

    for instruction in xml_doc:
        instruction[:] = sorted(instruction, key=lambda child: child.tag) #sort args

        command = []
        operation = instruction.get('opcode').upper()
        if operation in no_arg_instructions:
            if len(instruction) != 0:
                exit(32)

        # NO ARG INSTRUCTION
        elif operation in no_arg_instructions:
            if len(instruction) != 0:
                exit(32)

        # LABELS
        elif operation in able_to_be_label:
            if operation in ['LABEL', 'CALL', 'JUMP']:
                if len(instruction) != 1:
                    exit(32)
                if operation == 'LABEL':
                    label = instruction[0].text
                    if label in labels:
                        sys.exit(52)
                    else:
                        labels.append(label)
            elif len(instruction) == 3:#JUMPIFEQ/NEQ
                if instruction[1].attrib['type'] not in symb or instruction[2].attrib['type'] not in symb:
                    exit(32)
            else:
                exit(32)
            if instruction[0].attrib['type'] != 'label':
                exit(32)

        # VAR
        elif operation in ['DEFVAR', 'POPS']:
            if len(instruction) != 1:
                exit(32)
            if instruction[0].attrib['type'] != 'var':
                exit(32)

        # SYMB
        elif operation in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']:
            if len(instruction) != 1:
                exit(32)
            if instruction[0].attrib['type'] not in symb:
                exit(32)

        # VAR SYMB
        elif operation in ['MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT']:
            if len(instruction) != 2:
                exit(32)
            if instruction[0].attrib['type'] != 'var':
                exit(32)
            if instruction[1].attrib['type'] not in symb:
                exit(32)

        # VAR SYMB SYMB
        elif operation in var_symb_symb:
            if len(instruction) != 3:
                exit(32)
            if instruction[0].attrib['type'] != 'var':
                exit(32)
            if instruction[1].attrib['type'] not in symb:
                exit(32)
            if instruction[2].attrib['type'] not in symb:
                exit(32)
        else:
            exit(32)
        command.append(operation)
        command.append(instruction.get('order'))
        for args in instruction:
            arg_type = args.attrib['type']
            arg_value = args.text
            if arg_type == 'int':
                try:
                    int(arg_value)
                except:
                    sys.exit(32)
            elif arg_type == 'string':
                if not isinstance(arg_value, str):
                    sys.exit(32)
            elif arg_type == 'bool':
                if arg_value.lower() != 'true' and arg_value.lower() != 'false':
                    sys.exit(32)
            elif arg_type == 'nil':
                if arg_value != 'nil':
                    sys.exit(32)
            command.append({'type': arg_type, 'value': arg_value})
        program.append(command)
    program[:] = sorted(program, key=lambda x: int(x[1]))


def get_var_value(var, frame):
    if 'GF' in var:
        name = var.split('GF@')[1]
        if name in frame.GF.keys():
             value = frame.GF[name]
        else:
            sys.exit(54)

    elif 'TF' in var:
        if frame.TF is None:
            sys.exit(55)
        name = var.split('TF@')[1]
        if name in frame.TF.keys():
             value = frame.TF[name]
        else:
            sys.exit(54)

    elif 'LF' in var:
        if frame.LF is None:
            sys.exit(55)
        name = var.split('LF@')[1]
        if name in frame.LF.keys():
            value = frame.LF[name]
        else:
            sys.exit(54)
    return value


def get_symb_value(symb, frame):
    if symb['type'] in ['int', 'string', 'bool', 'nil']:
        return symb['value']
    else:
        return get_var_value(symb['value'], frame)


def get_symb_type(symb, frame):
    if symb['type'] in ['int', 'string', 'bool', 'nil']:
        return symb['type']
    elif symb['type'] == 'var':
        value = get_var_value(symb['value'], frame)
        try:
            int(value)
            return 'int'
        except:
            if value == 'nil':
                return 'nil'
            elif value.lower() == 'true' or value.lower() == 'false':
                return 'bool'
            else:
                return 'string'


def incialize_var(var, frame):
    if 'GF' in var:
        frame.GF[var.split('GF@')[1]] = ''
    elif 'TF' in var:
        if frame.TF is None:
            sys.exit(55)
        frame.TF[var.split('TF@')[1]] = ''
    elif 'LF' in var:
        if frame.LF is None:
            sys.exit(55)
        frame.LF[var.split('LF@')[1]] = ''


def update_var(var, frame, value):
    if 'GF' in var:
        name = var.split('GF@')[1]
        if name in frame.GF.keys():
            frame.GF[name] = value
        else:
            sys.exit(54)

    elif 'TF' in var:
        if frame.TF is None:
            sys.exit(55)
        name = var.split('TF@')[1]
        if name in frame.TF.keys():
            frame.TF[name] = value
        else:
            sys.exit(54)

    elif 'LF' in var:
        if frame.LF is None:
            sys.exit(55)
        name = var.split('LF@')[1]
        if name in frame.LF.keys():
            frame.LF[name] = value
        else:
            sys.exit(54)


def find_instr_index_after_label(program, label):
    for i in range(len(program)):
        if program[i][0] == 'LABEL':
            if program[i][2]['value'] == label:
                return i+1


call_stack = []
data_stack = []


def semantics(program,starting_position, frame):
    in_call = False
    for idx,command in enumerate(program[starting_position:]):
        instruction = command[0]
        if instruction == 'DEFVAR':
            incialize_var(command[2]['value'], frame)
        elif instruction == 'MOVE':
            update_var(command[2]['value'], frame, command[3]['value'])
        elif instruction == 'CREATEFRAME':
            frame.TF = {}
        elif instruction == 'PUSHFRAME':
            if frame.TF is None:
                sys.exit(55)
            frame.Frame_stack.append(frame.TF)
            frame.LF = dict(frame.TF)
            frame.TF = None
        elif instruction == 'POPFRAME':
            if frame.LF is None:
                sys.exit(55)
            frame.TF = frame.Frame_stack.pop()
            frame.LF = None
        elif instruction == 'CALL':
            call_stack.append(idx+1)
            semantics(program, find_instr_index_after_label(program, command[2]['value']), frame)
            in_call=True
        elif instruction == 'RETURN':
            try:
                semantics(program,call_stack.pop(),frame)
            except:
                sys.exit(56)
        elif instruction == 'JUMP':
            semantics(program, find_instr_index_after_label(program, command[2]['value']), frame)
            in_call = True
        elif instruction == 'PUSHS':
            data_stack.append(get_symb_value(command[2], frame))
        elif instruction == 'POPS':
            try:
                value = data_stack.pop()
            except:
                sys.exit(56)
            update_var(command[2]['value'], frame, value)
        elif instruction in ['ADD', 'SUB', 'MUL', 'IDIV']:
            if get_symb_type(command[3], frame) == 'int' and get_symb_type(command[4], frame) == 'int':
                a = int(get_symb_value(command[3], frame))
                b = int(get_symb_value(command[4], frame))
                if b == 0:
                    sys.exit(57)  # zero division
                result = 0
                if instruction == 'ADD':
                    result = a+b
                elif instruction == 'SUB':
                    result = a-b
                elif instruction == 'MUL':
                    result = a*b
                elif instruction == 'IDIV':
                    result = a // b
                update_var(command[2]['value'], frame, result)
            else:
                sys.exit(53)  # incompatible operand types
        elif instruction in ['LT', 'GT', 'EQ']:
            a_type = get_symb_type(command[3], frame)
            b_type = get_symb_type(command[4], frame)
            a = get_symb_value(command[3], frame)
            b = get_symb_value(command[4], frame)
            if a_type == b_type:
                if a_type == 'nil':
                    if instruction == 'EQ':
                        update_var(command[2]['value'], frame, 'true')
                    else:
                        sys.exit(53)
                elif a_type == 'int':
                    if instruction == 'LT':
                        update_var(command[2]['value'], frame, int(a) < int(b))
                    elif instruction == 'GT':
                        update_var(command[2]['value'], frame, int(a) > int(b))
                    elif instruction == 'EQ':
                        update_var(command[2]['value'], frame, int(a) == int(b))

                elif a_type == 'string' or a_type == 'bool':
                    if instruction == 'LT':
                        update_var(command[2]['value'], frame, a < b)
                    if instruction == 'GT':
                        update_var(command[2]['value'], frame, a > b)
                    if instruction == 'EQ':
                        update_var(command[2]['value'], frame, a == b)
            else:
                sys.exit(53)
        elif instruction in ['AND', 'OR']:
            a_type = get_symb_type(command[3], frame)
            b_type = get_symb_type(command[4], frame)
            a = get_symb_value(command[3], frame)
            b = get_symb_value(command[4], frame)
            if a_type == 'bool' and a_type == b_type:
                if instruction == 'AND':
                    update_var(command[2]['value'], frame, a and b)
                if instruction == 'OR':
                    update_var(command[2]['value'], frame, a or b)
            else :
                sys.exit(53)
        elif instruction == 'NOT':
            if get_symb_type(command[3], frame) == 'bool':
                update_var(command[2]['value'], frame, not get_symb_value(command[3], frame))
            else :
                sys.exit(53)
        elif instruction == 'INT2CHAR':
            try:
                update_var(command[2]['value'], frame, chr(int(get_symb_value(command[3], frame))))
            except:
                sys.exit(58)
        elif instruction == 'STRI2INT':
            try:
                string = get_symb_value(command[3], frame)
                update_var(command[2]['value'], frame, ord(string[int(get_symb_value(command[4], frame))]))
            except:
                sys.exit(58)
        if in_call:
            break



xml_doc = ''
source_doc = ''
program = []
for s in sys.argv:
    if "--help" in s:
        print("HEEELP")
        exit(0)
    elif "--source=" in s:
        for line in open(s.split('--source=')[1]):
            xml_doc += line
        try:
            xml_doc = ET.fromstring(xml_doc)
        except:
            exit(31)# v pripade zleho XML

    elif "--input=" in s:
        for line in open(s.split('--input=')[1]):
            source_doc += line
if xml_doc == source_doc:
    exit(11)
else:
    if xml_doc == 0:
        xml_doc = ET.fromstring(sys.stdin)
    else:
        source_doc = sys.stdin
parser(xml_doc, program)
frame = frame_mang()
semantics(program, 0, frame)
print(frame.LF)

