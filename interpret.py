#!/usr/bin/env python3

import xml.etree.cElementTree as ET
import sys


class frame_mang():
    Frame_stack = []
    GF = {}
    TF = None
    LF = None
    source_doc = ''


def parser(xml_doc, program):
    # Funkcia prevedie nad kódom syntaktickú kontrolu a spracuje ho do formátu s ktorým sa lahšie pracuje

    no_arg_instructions = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']
    able_to_be_label = ['LABEL', 'CALL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ']
    var_symb_symb = ['ADD', 'SUB', 'MUL', 'IDIV', 'GT', 'LT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']
    const = ['int', 'string', 'bool', 'nil']
    symb = const + ['var']
    labels = []
    if list(xml_doc.attrib.values())[0] != 'IPPcode19':
        exit(32)
    args_singularity = []
    order_singularity = []
    for instruction in xml_doc:
        instruction[:] = sorted(instruction, key=lambda child: child.tag)  # Zoradí argumenty operacií
        args_singularity.append(instruction.get('order'))
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
            elif len(instruction) == 3:  # JUMPIFEQ/NEQ
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
        elif operation == 'READ':
            if len(instruction) != 2:
                sys.exit(32)
            if instruction[0].attrib['type'] != 'var':
                sys.exit(32)
            if instruction[1].attrib['type'] != 'type' or instruction[1].text not in ['int', 'string', 'bool']:
                sys.exit(32)

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
                if arg_value is None:
                    arg_value = ''
                if not isinstance(arg_value, str):
                    sys.exit(32)
                appearances = [i for i, a in enumerate(arg_value) if a == "\\"]
                offset = 0
                for position in appearances:
                    position -= offset
                    offset += 3
                    a = arg_value[:position]
                    b = arg_value[position+4:]
                    znak = arg_value[position+1:position+4]
                    try :
                        char = chr(int(znak))
                    except:
                        sys.exit(57)
                    arg_value = a+char+b

            elif arg_type == 'bool':
                if arg_value.lower() != 'true' and arg_value.lower() != 'false':
                    sys.exit(32)
            elif arg_type == 'nil':
                if arg_value != 'nil':
                    sys.exit(32)
            command.append({'type': arg_type, 'value': arg_value})
        program.append(command)
        order_singularity.append(command[1])
    program[:] = sorted(program, key=lambda x: int(x[1]))  # zoradi operacie podla order

    # Skontroluje ci nemá operácia argumenty s rovnakým poradím
    if len(args_singularity) != len(set(args_singularity)):
        sys.exit(32)
    # Skontroluje či nemá program operácie s rovnakým orderom
    if len(order_singularity) != len(set(order_singularity)):
        sys.exit(32)


def get_var_value(var, frame):
    # Funkcia vráti hodnotu premennej, pokiaľ existuje
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
    if value is None:
        sys.exit(56)
    return value


def get_symb_value(symb, frame):
    # Funkcia vráti hodnotu symbolu
    if symb['type'] in ['int', 'string', 'bool', 'nil']:
        if symb['type'] == 'nil':
            return ''
        return symb['value']
    else:
        return get_var_value(symb['value'], frame)


def get_symb_type(symb, frame):
    # Funkcia vráti typ symbolu
    if symb['type'] in ['int', 'string', 'bool', 'nil']:
        return symb['type']
    elif symb['type'] == 'var':
        value = get_var_value(symb['value'], frame)

        if value == 'nil':
            return 'nil'
        elif str(value).lower() == 'true' or str(value).lower() == 'false':
            return 'bool'
        else:
            try:
                int(value)
                return 'int'
            except:
                return 'string'


def incialize_var(var, frame):
    # Funkcia inicializuje premennú vo frame
    if 'GF' in var:
        frame.GF[var.split('GF@')[1]] = None
    elif 'TF' in var:
        if frame.TF is None:
            sys.exit(55)
        frame.TF[var.split('TF@')[1]] = None
    elif 'LF' in var:
        if frame.LF is None:
            sys.exit(55)
        frame.LF[var.split('LF@')[1]] = None


def update_var(var, frame, value):
    # Funkcia updatne hodnotu premennej, pokiaľ existuje
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
    # Funkcia nájde index operácie nasledujúcej po hľadanom lable
    for i in range(len(program)):
        if program[i][0] == 'LABEL':
            if program[i][2]['value'] == label:
                return i+1
    return None


call_stack = []
data_stack = []


def semantics(program,starting_position, frame):
    # Funkcia zabezpečuje sémanticku kontrolu všetkých operácii
    in_call = False
    for command in program[starting_position:]:
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
            call_stack.append(command[1])
            index = find_instr_index_after_label(program, command[2]['value'])
            if (index == None):
                sys.exit(52)
            semantics(program, index, frame)
        elif instruction == 'RETURN':
            try:
                index = call_stack.pop()
            except:
                sys.exit(56)
            in_call = True
        elif instruction == 'JUMP':
            semantics(program, find_instr_index_after_label(program, command[2]['value']), frame)
            in_call = True
        elif instruction in ['JUMPIFEQ','JUMPIFNEQ']:
            a_type = get_symb_type(command[3], frame)
            b_type = get_symb_type(command[4], frame)
            a = get_symb_value(command[3], frame)
            b = get_symb_value(command[4], frame)

            if a_type == b_type:
                if instruction == 'JUMPIFEQ':
                    if a == b:
                        semantics(program, find_instr_index_after_label(program, command[2]['value']), frame)
                        in_call = True
                else:
                    if a != b:
                        semantics(program, find_instr_index_after_label(program, command[2]['value']), frame)
                        in_call = True
            else:
                sys.exit(58)

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
            if a_type == 'nil' or b_type == 'nil':
                if instruction == 'EQ':
                    if a == b:
                        update_var(command[2]['value'], frame, 'true')
                    else:
                        update_var(command[2]['value'], frame, 'false')
                else:
                    sys.exit(53)
            elif a_type == b_type:
                if a_type == 'int':
                    if instruction == 'LT':
                        update_var(command[2]['value'], frame, str(int(a) < int(b)).lower())
                    elif instruction == 'GT':
                        update_var(command[2]['value'], frame, str(int(a) > int(b)).lower())
                    elif instruction == 'EQ':
                        update_var(command[2]['value'], frame, str(int(a) == int(b)).lower())

                elif a_type == 'string' or a_type == 'bool':
                    if instruction == 'LT':
                        update_var(command[2]['value'], frame, str(a < b).lower())
                    if instruction == 'GT':
                        update_var(command[2]['value'], frame, str(a > b).lower())
                    if instruction == 'EQ':
                        update_var(command[2]['value'], frame, str(a == b).lower())
            else:
                sys.exit(53)
        elif instruction in ['AND', 'OR']:
            a_type = get_symb_type(command[3], frame)
            b_type = get_symb_type(command[4], frame)
            a = get_symb_value(command[3], frame)
            b = get_symb_value(command[4], frame)

            if a == 'true':
                a = True
            else:
                a = False
            if b == 'true':
                b = True
            else:
                b = False
            if a_type == 'bool' and a_type == b_type:
                if instruction == 'AND':
                    update_var(command[2]['value'], frame, str(a and b).lower())
                if instruction == 'OR':
                    update_var(command[2]['value'], frame, str(a or b).lower())
            else :
                sys.exit(53)
        elif instruction == 'NOT':
            if get_symb_type(command[3], frame) == 'bool':
                value = get_symb_value(command[3], frame)
                if value == 'true':
                    value = True
                else:
                    value = False
                update_var(command[2]['value'], frame, str(not value).lower())
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
        elif instruction == 'READ':
            type = command[3]['value']
            if frame.source_doc == '':
                value = input()
            else:
                f = open(frame.source_doc)
                value = f.readline()
            if type == 'int':
                try:
                    value = int(value)
                except:
                    value = 0

            elif type == 'bool':
                if value.lower() == 'true':
                    value = 'true'
                else:
                    value = 'false'
            elif type == 'string':
                 try:
                     value = str(value)
                 except:
                    value = ''
            else:
                sys.exit(53)
            update_var(command[2]['value'], frame, value)
        elif instruction == 'WRITE':
            print(get_symb_value(command[2], frame), end='')
        elif instruction == 'CONCAT':
            a_type = get_symb_type(command[3], frame)
            b_type = get_symb_type(command[4], frame)
            if a_type == b_type and a_type == 'string':
                value = get_symb_value(command[3], frame) + get_symb_value(command[4],frame)
                update_var(command[2]['value'], frame, value)
            else:
                sys.exit(53)
        elif instruction == 'STRLEN':
            if get_symb_type(command[3],frame):
                update_var(command[2]['value'], frame, len(get_symb_value(command[3], frame)))
        elif instruction == 'GETCHAR':
            string = get_symb_value(command[3], frame)
            idx = get_symb_value(command[4], frame)
            if get_symb_type(command[3],frame) != 'string' or get_symb_type(command[4],frame) != 'int':
                sys.exit(53)
            try:
                new_value = string[int(idx)]
            except:
                sys.exit(58)
            update_var(command[2]['value'], frame, new_value)
        elif instruction == 'SETCHAR':
            value = get_var_value(command[2]['value'], frame)
            position = get_symb_value(command[3], frame)
            char = get_symb_value(command[4], frame)
            if get_symb_type(command[2],frame) != 'string' or get_symb_type(command[3],frame) != 'int' or get_symb_type(command[4],frame) != 'string':
                sys.exit(53)
            try:
                temp_list = list(value)
                temp_list[int(position)] = char[0]
                value = ''.join(temp_list)
            except:
                sys.exit(58)
            update_var(command[2]['value'], frame, value)
        elif instruction == 'TYPE':
            update_var(command[2]['value'], frame, get_symb_type(command[3], frame))
        elif instruction == 'EXIT':
            exit_code = get_symb_value(command[2], frame)
            try:
                exit_code = int(exit_code)
            except:
                sys.exit(53)
            if 0 <= exit_code <= 49:
                sys.exit(exit_code)
            else:
                sys.exit(57)
        elif instruction == 'DPRINT':
            sys.stderr.write(get_symb_value(command[2], frame))
        elif instruction == 'BREAK':
            pass
        if in_call:
            break


xml_doc = ''
program = []
frame = frame_mang()
for s in sys.argv:
    if "--help" in s:
        if len(sys.argv) != 2:
            sys.exit(10)
        print("----------------------------------------------------------------------------------------\n"
              "INTERPRET HELP:\n"
              "Program načíta XML reprezentáciu programu zo zadaného súboru a tento program s využitím\n"
              "štandartného vstupu a výstupu interpretuje.\n"
              "----------------------------------------------------------------------------------------\n"
              "Spúštanie:\n"
              "./interpret.py --source=%súbor_so_vstupným_xml --input=%súbor_s_input_údajmi")
        exit(0)
    elif "--source=" in s:
        for line in open(s.split('--source=')[1]):
            xml_doc += line
        try:
            xml_doc = ET.fromstring(xml_doc)
        except:
            exit(31)  # V prípade zlého XML

    elif "--input=" in s:
        frame.source_doc = s.split('--input=')[1]
if xml_doc == frame.source_doc:
    exit(11)
else:
    if xml_doc == 0:
        xml_doc = ET.fromstring(sys.stdin)

parser(xml_doc, program)
semantics(program, 0, frame)

