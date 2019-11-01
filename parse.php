<?php
#!/usr/bin/php

$able_to_be_label = array('LABEL','CALL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ');//array s operaciami, za ktorymi moze nasledovat label
$able_to_be_symb = array_merge(array('int','string','bool','nil','var'));//operacie ktore mozu byt symbol
$last_operation= '';
class token{
    public $value = '';
    public $type = '';
    public $name = '';
    public $order = 0;
    public $line = 0;
    public $operation = '';
    public $end = false;

    /**
     * Funkcia spracuje token, urci jeho typ, skontroluje syntax.
     **/
    function define_token(){
        //Nahradenie nepovolených znakov
        $this->value = str_replace('&','&amp;',$this->value);
        $this->value = str_replace('<','&lt;',$this->value);
        $this->value = str_replace('>','&gt;',$this->value);
        if(strcasecmp($this->value, '.IPPcode19')==0){
            $this->type = 'HEAD';
        }else if($this->order == 0){
            $this->operation = strtoupper(substr($this->value,0,strlen($this->value)));
            $GLOBALS['last_operation']= $this->operation;
        }
        else if (strpos($this->value, '#')!==false) {
            $this->type = 'COMMENT';
        }
        else if(strcmp($this->value, 'int')==0 || strcmp($this->value, 'string')==0 || strcmp($this->value, 'bool')==0){
                $this->type = 'type';
            }
        else if(strpos($this->value, 'string@')!==false){
            $this->type = 'string';
            $this->value = explode('string@',$this->value)[1];

            //kontrola ci sa v stringu nenachádza niečo ako ah\oj
            if(preg_match('/\\\[a-zA-Z]/', $this->value, $output_array))
            {
                exit(23);
            }
            //kontrola ci sa v stringu nenachadza nieco ako po\32sdd
            if(strpos($this->value,"\\")!==false){
                if(preg_match('/\\\[0-9][0-9][^0-9]/',$this->value,$matches)){
                    exit(23);
                }

            }

        }
        else if(strpos($this->value, 'bool@')!==false){
            $this->type = 'bool';
            $this->value = explode('bool@',$this->value)[1];
            if(strcmp($this->value,'true') != 0 && strcmp($this->value, 'false') != 0){
                exit(23);
            }
        }
        else if(strpos($this->value, 'int@')!==false){
            $this->type = 'int';
            $this->value = explode('int@',$this->value)[1];
            //kontrola aby int nebol float
            if(is_numeric($this->value) && strpos($this->value, ".") !== false){
                exit(23);
            }
            if(!is_numeric($this->value)){
                exit(23);
            }
        }
        else if(strpos($this->value, 'nil@')!==false){
            $this->type = 'nil';
            $this->value = explode('nil@',$this->value)[1];
            if($this->value!='nil'){
                exit(23);
            }
        }
        else if(strpos($this->value, 'GF@')!==false){
            $this->type = 'var';
            $this->name = explode('GF@',$this->value)[1];
        }
        else if(strpos($this->value, 'LF@')!==false){
            $this->type = 'var';
            $this->name = explode('LF@',$this->value)[1];
        }
        else if(strpos($this->value, 'TF@')!==false){
            $this->type = 'var';
            $this->name = explode('TF@',$this->value)[1];
        }
        else if(in_array( $GLOBALS['last_operation'], $GLOBALS['able_to_be_label'])){
            $this->type = "label";
            $this->name = $this->value;
        }
        else {
            $this->type = "UNDEF";
        }
        if($this->type == 'var'){
            if(strpos($this->value,'[')!==false || strpos($this->value,']')!==false || strpos($this->value,'(')!==false || strpos($this->value,')')!==false ){
                exit(23);
            }
            //kontrola ci premenna zacina pismenom alebo povolenym specialnym znakom
            if(!preg_match('/^[a-zA-Z-_$&%*!?]/', $this->name, $match)){
                exit(23);
            }
        }
    }

}

/**
 * funkcia na vytvaranie tokenov
 **/
function create_token(&$tokens, &$new_token_value, &$order, $line){
    if ($new_token_value != ''){
        $token = new token;
        $token->value = $new_token_value;
        $token->order = $order;
        $order++;
        $token->define_token();
        $token->line = $line;
        array_push($tokens, $token );
        $new_token_value = '';

    }
}

/**
 * funkcia na oznacenie koncia riadku v arrayi
 **/
function create_line_end(&$tokens){
    $token = new token;
    $token->end = true;
    array_push($tokens,$token);
}

/**
 * funkcia na nacitanie tokenov
 **/
function scanner(&$tokens)
{
    $order = 0;
    $line = 0;
    $new_token_value = '';
    $file = file_get_contents("php://stdin");
    global $comment;
    $comment = false;
    foreach(str_split($file) as $char) {
        if($char == "\n"){
            $comment = false;
        }
        if($comment){
            $new_token_value = '';
            continue;
        }
        if ($char == '#') {
            if ($new_token_value != '') {
                create_token($tokens, $new_token_value,$order, $line);
            }
            $comment = true;

        }
        if ($char != ' ' && $char != "\n" && $char != "\0") {
            $new_token_value .= $char;
        } else {
            create_token($tokens, $new_token_value,$order, $line);

        }
        if ($char == "\n" ) {
            create_line_end($tokens);
            $order = 0;
            $line++;
        }

    }
    if ($new_token_value!=''){
        create_token($tokens, $new_token_value,$order, $line);
        create_line_end($tokens);
    }
}
/**
 * funkcia na vypis XML reprezentacie
 **/
function printer($token,$instruction,&$order){
    if($instruction == 'operation'){
        print("    <instruction order=\"{$order}\" opcode=\"{$token->operation}\">\n");
        $order++;
    }
    else if($instruction == 'arg'){
        print("        <arg{$token->order} type=\"{$token->type}\">{$token->value}</arg{$token->order}>\n");
    }

}

/**
 * Kontroluje ci za templatom nenasleduje este nieco co by tam nemalo byt
 **/
function check_end(&$tokens,&$end){
    if(next($tokens)) {
        if (!current($tokens)->end && current($tokens)->value != "#") {
            print("SYNTAX ERROR\n");
            exit(23);
        } else {
            print("    </instruction>\n");
            $end = true;
        }
    }
    else {
        print("    </instruction>\n");
        $end = true;
    }
}
/**
 * Funkcia vykonava syntakticku kontrolu
 **/
function parser(&$tokens){
    $var_symb_symb = array('ADD','SUB','MUL', 'IDIV', 'GT', 'LT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR');//operacie ktore maju ako argumenty OPERATION VAR SYMB SYMB
    $order = 1;
    if(!current($tokens)){
        exit(21);
    }
    if(current($tokens)->line==0){
        if(current($tokens)->type == 'HEAD'){
            if(!next($tokens)->end){
                exit(23);
            }
            print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            print("<program language=\"IPPcode19\">\n");
        }
        else{
            exit(21);
        }
    }
    while(next($tokens)){
        $end = false;
        $in = false;
        if(current($tokens)->end){
            continue;
        }
        //Pokial je operacia MOVE, INT2CHAR.. vypise ju do XMJ, zisti ci po nej nasleduje VAR pokial nie konci s exit code 23 pokial ano pokracuje dalej a zistuje ci nasleduje SYMB
        //pokial ano tak kontroluje ci uz nejde nic co by nemalo. Takto to funguje pre vsetky operacie
        if(current($tokens)->operation == 'MOVE' || current($tokens)->operation == 'INT2CHAR' || current($tokens)->operation == 'STRLEN' || current($tokens)->operation == 'TYPE' || current($tokens)->operation == 'NOT'){
            $in = true;
            printer(current($tokens),'operation',$order);
            if(next($tokens)->type == 'var'){
                printer(current($tokens),'arg',$order);
                if(in_array( next($tokens)->type, $GLOBALS['able_to_be_symb'])){
                    printer(current($tokens),'arg',$order);
                    check_end($tokens,$end);
                }
            }
        }
        else if(current($tokens)->operation == 'CREATEFRAME' || current($tokens)->operation == 'POPFRAME' || current($tokens)->operation == 'PUSHFRAME' || current($tokens)->operation == 'RETURN' || current($tokens)->operation == 'BREAK'){
            $in = true;
            printer(current($tokens),'operation',$order);
            check_end($tokens,$end);
        }
        else if(current($tokens)->operation == "DEFVAR" || current($tokens)->operation == "POPS") {
            $in = true;
            printer(current($tokens), 'operation',$order);
            if (next($tokens)->type == 'var') {
                printer(current($tokens), 'arg',$order);
                check_end($tokens, $end);
            }
        }
        else if(in_array(current($tokens)->operation, array_diff($GLOBALS['able_to_be_label'],array('JUMPIFEQ','JUMPIFNEQ')))){
            $in = true;
            printer(current($tokens), 'operation',$order);
            if(next($tokens)->type == 'label'){
                printer(current($tokens), 'arg',$order);
                check_end($tokens, $end);
            }
        }
        else if(current($tokens)->operation == "PUSHS" || current($tokens)->operation == "WRITE" || current($tokens)->operation == "EXIT" || current($tokens)->operation == "DPRINT"){
            $in = true;
            printer(current($tokens), 'operation',$order);
            if(in_array( next($tokens)->type, $GLOBALS['able_to_be_symb'])){
                printer(current($tokens),'arg',$order);
                check_end($tokens,$end);
            }
        }
        else if(in_array(current($tokens)->operation, $var_symb_symb)){
            $in = true;
            printer(current($tokens), 'operation',$order);
            if (next($tokens)->type == 'var') {
                printer(current($tokens), 'arg',$order);
                if(in_array( next($tokens)->type, $GLOBALS['able_to_be_symb'])){
                    printer(current($tokens),'arg',$order);
                    if(in_array( next($tokens)->type, $GLOBALS['able_to_be_symb'])) {
                        printer(current($tokens), 'arg',$order);
                        check_end($tokens, $end);
                    }
                }
            }
        }else if(current($tokens)->operation == 'READ') {
            $in = true;
            printer(current($tokens), 'operation',$order);
            if (next($tokens)->type == 'var') {
                printer(current($tokens), 'arg',$order);
                if(next($tokens)->type == 'type' ){
                    printer(current($tokens), 'arg',$order);
                    check_end($tokens, $end);
                }
            }
        }else if(current($tokens)->operation == 'JUMPIFEQ'||(current($tokens)->operation == 'JUMPIFNEQ')){
            $in = true;
            printer(current($tokens), 'operation',$order);
            if(next($tokens)->type == 'label'){
                printer(current($tokens), 'arg',$order);
                if(in_array( next($tokens)->type, $GLOBALS['able_to_be_symb'])){
                    printer(current($tokens),'arg',$order);
                    if(in_array( next($tokens)->type, $GLOBALS['able_to_be_symb'])) {
                        printer(current($tokens), 'arg',$order);
                        check_end($tokens, $end);
                    }
                }
            }
        }
        else if(current($tokens)->operation == '#'){
            $in = true;
            $end = true;
            next($tokens);
        }
        if(!$in){
            print("chybny operacny kod\n");
            exit(22);
        }
        if(!$end){
            print("SYNTAX ERROR\n");
            exit(23);
        }

    }
    print("</program>\n");
}
//Vypis helpu
if($argc == 2){
    if(!strcmp($argv[1],"--help")) {
        print("-------------------------------------------------------------------------
PARSER HELP:    
-Skript typu filtr (parse.php v jazyce PHP 7.3) načte ze standardního vstupu 
 zdrojový kód v IPPcode19 (viz sekce 6), zkontroluje lexikální a syntaktickou správnost kódu 
 a vypíše na standardní výstup XML reprezentaci programu dle specifikace v sekci
 
-------------------------------------------------------------------------
Spustanie:
 php parse.php < \"subor so zdrojovym kodom v jazyku IPPcode19\"
 
-------------------------------------------------------------------------\n");
        exit(0);
    }
}

if($argc == 1) {
    $tokens = array();
    scanner($tokens);
    parser($tokens);
}
else{
    print("nespravne argumenty pustenia\n");
    exit(10);
}





