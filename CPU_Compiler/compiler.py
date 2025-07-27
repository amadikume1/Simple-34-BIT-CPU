# Compiler for a custom programming language that tokenizes input from a text file,
# processes expressions (e.g., memory access, function calls, conditionals), and generates VM code
import re
import random
import string
import sys




# Mapping of source language operators to intermediate code instructions.
operation_types = {
    "+": "add",
    "-": "sub",
    "*": "symbol",
    "==": "eq",
    "!=": "eq\npush constant: 0\neq",
    "": None,
    ">": "less",
    "<": "grat",
    "and": "and",
    "or": "or",
}



# Open input file for reading source code and output file for writing generated code.



try:

    
    with open(sys.argv[1], 'r+') as input_file:

        source_lines = input_file.readlines()

except Exception:
     
     print("Invalid File")
     

tokenized_lines = []



cleaned_lines = []

statement_locations = []


# Tokenize source code: remove empty strings and newlines, split into tokens
for i in range(len(source_lines)):
    current_line_index = i
    character_list = list(source_lines[i])
    
    
    
    # Remove empty strings and newlines from character list
    character_list = [c for c in source_lines[i] if c not in ("", "\n")]
            
                
    cleaned_lines.append("".join(character_list))

    separators = ["", " "]
    
    
    tokens = []
    
    # Split line into tokens, preserving delimiters like '};', '==', '!='.
    split_result = re.split("(};|==|!=|\W)", "".join(cleaned_lines))
    
    in_string = False
    
    
    # Filter out separators unless within a string literal.
    for i in split_result:
        
        if i == "'" and in_string:
            in_string = False
            
        
        elif i == "'" and not(in_string):
            in_string = True
            
        if (i not in separators) or in_string:
            tokens.append(i)
    
 
    
    if tokens != []:
        statement_locations.append(current_line_index)
        tokenized_lines.append(tokens)
 
    cleaned_lines.clear()


main_local_variables = []







def handle_memory_access(expression_line, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, i):
            #Process memory access expressions (e.g., RAM[5], var[3]), generating intermediate code for array indexing.
            #Allows for "nested" memeory aceeses (e.g RAM[5][1], index the value found in the 5th position in memory by 1)
    
            
            temp_wrapped_content = []
            count_square_brackets = 0
          
            
            memory_layers = []
            
            
            # Collect tokens for nested memory access (e.g., arr[3][2]).
            for idx in range(len(expression_line[i+1:])):
                    
                
                    temp_wrapped_content += [expression_line[idx+i+1]]
                    
                    if idx+i+1 >= len(expression_line):
                        
                        break
                    
                    if expression_line[idx+i+1] == '[':
                        
                        count_square_brackets+=1
                        
                    elif expression_line[idx+i+1] == ']':
                        count_square_brackets-=1
                        
                    if count_square_brackets == 0 and (len(expression_line) <= idx + i + 2 or expression_line[idx+i+2] != '['):
                        
                       
                   
                        memory_layers.append(temp_wrapped_content)
                        temp_wrapped_content = []
                       
                        break
                    
                    elif count_square_brackets == 0:
                        memory_layers.append(temp_wrapped_content)
                        temp_wrapped_content = []
                    
              
    
            if count_square_brackets != 0:
                
            
                return 0, [], ['Unclosed memory access']
           
            
           
            memory_processed_layers = []
            
            layer_count = 0
           
           
            # Process each nested memory access layer (e.g., index expressions within brackets).
            for ind in memory_layers:
                
                layer_count += 1
                
                
                if ind[1:-1] == []:
                
                    return 0, [], ['Empty memory access expression']
                
                _, _ , _, processed_memory_access, error_message = process_expression_line(ind[1:-1],main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, function_return_type)
                
                
           
                if len(error_message) != 0:
                    
                    return 0, [], error_message
                
                if (layer_count >= 1 and expression_line[i] != "RAM") or (layer_count >= 2 and expression_line[i] == "RAM"):
                    
                    
                    memory_processed_layers += processed_memory_access + ['add'] + ['point', 'push this: 0']
                else: 
                    memory_processed_layers += processed_memory_access + ['point', 'push this: 0']
                
            
            base_Memory_Offset = []
            
            
            # Determine base address for memory access (e.g., local variable, argument, or constant).
            
            if expression_line[i] != "RAM" and (expression_line[i] in current_Function_Local_Variables and in_function):
                
                
                base_Memory_Offset = [("push local: " + str(current_Function_Local_Variables.index(expression_line[i])))]
                
            elif expression_line[i] != "RAM" and (expression_line[i] in main_local_variables and not in_function):
                
                base_Memory_Offset = [("push local: " + str(main_local_variables.index(expression_line[i])))]
                
            elif expression_line[i] != "RAM" and expression_line[i] in current_Function_Arguments and in_function:
                
                 base_Memory_Offset = [("push argument: " + str(current_Function_Arguments[::-1].index(expression_line[i])))]  
                 
            elif expression_line[i].isnumeric():
                
                 base_Memory_Offset = ["push constant: " + expression_line[i]]  
                 
            
            # if the base offset is a more complex expression(e.g an expression within (), it is code was already processed
            elif expression_line[i] == "]" or expression_line[i] == ")" or expression_line[i] == "'":
                
                base_Memory_Offset = []
                
                
            
            
            
            compiled_memory_acess = base_Memory_Offset + memory_processed_layers
            

            return idx+1, compiled_memory_acess, []
            
            
            
   
   
   
   
   
   
   
            
def handle_string_creation(expression_line, i, element_stack, function_names):
                
                #Generate code for string literals, converting characters to ASCII values and allocating memory.
       
                
                
                for idx in range(len(expression_line[i+1:])):
                    
                    if expression_line[i+1:][idx] == "'":
                        
                        break
                
                
                
                    
                if expression_line.count("'") <= 1:
                    
                    return 0, element_stack, ['Unclosed string']
                    
                
               
                skip_count = 0 
                
                
                string = expression_line[i+1:i+idx+1]
                
                
                string_length = len(string)
                string = [''.join(string)]
                
                
                if len(string[0]) == 1:
                      
                    element_stack.append("push constant: " + str(ord(string[0])))
                    skip_count = 2
                    
                    
                elif len(string[0]) > 1:
                    
                    
                    no_allocation_function =  not("MemAlloc" in function_names)
                        
                        
                    if no_allocation_function:
                                
                        error_message = ['"MemAlloc not defined: Cannot allocate memory for multi-character string'] 
                        
                        return 0, element_stack, error_message
                        
                            
                    chars = list(string[0])
                    char_temp = []
                    
                    for character in chars:
                        char_temp.append("push constant: " + str(ord(character)))
                        
                    
                    
                    
                    
                    element_stack +=  char_temp + ["call: #MemAlloc"] + ["push constant: " + str(len(chars)) ] + ["end: #MemAlloc"] + ["push constant: 11", "point"] + ['pop this: 0'] + ['push this: 0', 'point']
                
                    string_element_pop_instructions = []
                    
                    for i in range(len(chars)):
                        
                        string_element_pop_instructions += ['pop this: ' + str(i)]
                
                    
                    element_stack += string_element_pop_instructions[::-1] + ["push constant: 11", "point", "push this: 0", 'push constant: 2', 'sub', 'point', 'push constant: ' + str(len(chars)), 'pop this: 0', "push constant: 11", "point", "push this: 0"]
                        
              
                
               
                skip_count = string_length
                    
                return skip_count, element_stack, []

    
    
            
def handle_array_creation(expression_line, i, element_stack, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function):
            
            #Generate code for array literals, processing elements and allocating memory.
            string = expression_line
           
            count_square_brackets = 1
            temp_wrapped_content = []
            tokenized_lines = []
     
            
            
            in_parentheses = False
            in_brackets = False
            
            
            
            no_allocation_function =  not("MemAlloc" in function_names)
                        
                        
            if no_allocation_function:
                        
                error_message = ['"MemAlloc not defined: Cannot allocate memory for array'] 
                
                return 0, element_stack, error_message    
                
                        
            
            for idx in range(len(string[i + 1:])):
               
               
                if string[idx + i + 1] == '(':
                    
                    in_parentheses = True
                
                elif string[idx + i + 1] == '[':
                    count_square_brackets+=1
                    in_brackets = True
                    
                elif string[idx + i + 1] == ')':
                    
                    in_parentheses = False
                    
                
                elif string[idx + i + 1] == ']':
                    count_square_brackets-=1
                    in_brackets = False
              
                
                if string[idx + i + 1] == ',' and not(in_parentheses or in_brackets):
                    
                    tokenized_lines.append(temp_wrapped_content)
                    temp_wrapped_content = []
                    continue
                    
                if count_square_brackets == 0:
                    
                    break
                    
                else:
                    
                    temp_wrapped_content+= [string[idx + i + 1]]
                    
                    
            if count_square_brackets != 0:
                
            
                return 0, element_stack, ['Invalid array creation']     
                
                
             
            tokenized_lines.append(temp_wrapped_content) 
            
            
            
            
            array_creation_instructions = [] 
            
            
            for seg in tokenized_lines:
                
                if seg == []:
                    
                    return 0, element_stack, ['Invalid empty array element']  
                    
                _, _, _, processed_array_element, error_message = process_expression_line(seg,main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, function_return_type)
                    
                   
                if len(error_message) != 0:
                    
                    return 0, element_stack, error_message
                    
                array_creation_instructions += processed_array_element
                
                
                
            
           
            element_stack +=  array_creation_instructions + ["call: #MemAlloc"] + ["push constant: " + str(len(tokenized_lines)) ] + ["end: #MemAlloc"] + ["push constant: 11", "point"] + ['pop this: 0'] + ['push this: 0', 'point']
            
            
            array_element_pop_instructions = []
                    
            for i in range(len(tokenized_lines)):
                        
                    array_element_pop_instructions += ['pop this: ' + str(i)]
                
                    
            element_stack += array_element_pop_instructions[::-1] + ["push constant: 11", "point", "push this: 0", 'push constant: 2', 'sub', 'point', 'push constant: ' + str(len(tokenized_lines)), 'pop this: 0', "push constant: 11", "point", "push this: 0"]
                
            
           
            
           
            skip_count = idx
      
            
            return skip_count, element_stack, []
    
    
    
def handle_function_call(expression_line, i, compiled_expression, element_stack, function_arg_count, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function):
            
            #Generate code for function calls, validating argument count and processing arguments
            
            in_function_call = True
            
            
            parentheses_count = 1
            temp_wrapped_content = []
            tokenized_lines = []
     
            
            
          
            
        
            in_parentheses = False
            in_brackets = False
            for idx in range(len(expression_line[i+2:])):
                
                if i + idx + 2 >= len(expression_line):
                    break
                
                if expression_line[i+idx+2] == '[':
                    in_brackets = True
                    
                elif expression_line[i+idx+2] == ']':
                    
                    in_brackets = False
               
                elif expression_line[i+idx+2] == '(':
                    parentheses_count+=1
                    in_parentheses = True
                    
                elif expression_line[i+idx+2] == ')':
                    parentheses_count-=1
                    in_parentheses = False
                    
                if parentheses_count == 0:
                    tokenized_lines.append(temp_wrapped_content)
                    break
                
                if expression_line[i+idx+2] == ',' and not(in_parentheses or in_brackets):
                    
                    tokenized_lines.append(temp_wrapped_content)
                    temp_wrapped_content = []
                    
                else:
                    
                    temp_wrapped_content+= [expression_line[i+idx+2]]
                    
            
            
            
            if (tokenized_lines != [[]] and function_arg_count[expression_line[i]] != len(tokenized_lines) or (tokenized_lines == [[]] and function_arg_count[expression_line[i]] != 0)):
                
          
                return 0, compiled_expression, element_stack, ['Incorrect number of arguments for: ' + expression_line[i]]
            
            
           
            
                
            if parentheses_count != 0:
                
      
                return 0, compiled_expression, element_stack, ['Unclosed parentheses']
            
        
            
            compiled_expression += [("call: #" + expression_line[i])]
            
            
            
            if tokenized_lines != [[]]:
                for seg in tokenized_lines:
                    
                    _, _, _, Processed_Function_Argument, error_message = process_expression_line(seg,main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, function_return_type)
                    
                   
                    if len(error_message) != 0:
                        return 0, compiled_expression, element_stack,  error_message
                        
                    compiled_expression += Processed_Function_Argument
        
            
            
                
            element_stack += ["end: #" + expression_line[i]]
            
            
            
            skip_count = i+idx+2
            
            
            return skip_count, compiled_expression, element_stack, [] 
            
            




def handle_parenthesis(expression_line, i, compiled_expression, element_stack, operation_stack, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function):
            
            #Process parenthesized expressions, evaluating contents and combining with surrounding operations.
            
            temp_wrapped_content = []
            parenthesis_count = 0
          
          
            for idx in range(len(expression_line[i:])):
                 
                   
                    if expression_line[idx+i] == '(':
                        parenthesis_count+=1
                        
                    elif expression_line[idx+i] == ')':
                        parenthesis_count-=1
                        
                    if parenthesis_count == 0:
                        temp_wrapped_content += [expression_line[idx+i]]
                        break
                    
                    
                        
                    temp_wrapped_content += [expression_line[idx+i]]
                    
    
            if parenthesis_count != 0 or (len(expression_line) > idx+i + 1  and (expression_line[idx+i+1] == "(" or expression_line[idx+i+1] == ")")):
                
                return 0, compiled_expression, element_stack, operation_stack, ['Unclosed parentheses']
            
            if temp_wrapped_content[1:-1] == []:
                
                return 0, compiled_expression, element_stack, operation_stack, ['Empty parenthesized expression']
                
                
                
            _, _, _, Processed_Perenthesis, error_message = process_expression_line(temp_wrapped_content[1:-1],main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, function_return_type)
            
            
            if len(error_message) != 0:
                    return 0, compiled_expression, element_stack, operation_stack, error_message
                    
        
            error_message = []
            if len(operation_stack) == 0:
                 error_message = []
                 
            else:
                
                error_message = [operation_stack[-1]]
                
                
            
            
            compiled_expression = compiled_expression + element_stack + operation_stack[:-1][::-1] + Processed_Perenthesis + error_message
            
            operation_stack = []
            element_stack = []
            
            
            
            
            
            skip_count = idx - 1
            
            return skip_count, compiled_expression, element_stack, operation_stack, []
            
            
            


         
def process_expression_line(
    expression_line,
    main_local_variables,
    current_Function_Arguments,
    current_Function_Local_Variables,
    function_names,
    in_function, function_return_type
):
    
    #Evaluate an expression line, handling literals, variables, operators, and function calls
    
    element_stack, operation_stack = [], []
    errors  = []
    compiled_expression = []
  
    in_function_call, in_parentheses = False, False
    after_string = False
    skip_count = 0
    
    previous_element_type = ''
    current_element_type = ''
    
    
 
    
    for i in range(len(expression_line)):
       
        
        
        
        if skip_count != 0:
            
            
            
            skip_count-=1
            continue
        
        
        if (expression_line[i] == "RAM" or (expression_line[i] in current_Function_Local_Variables and in_function) or (expression_line[i] in current_Function_Arguments and in_function) or (expression_line[i] in main_local_variables and not in_function) or (expression_line[i] == ')' or expression_line[i] == ']' or after_string) or (expression_line[i].isnumeric()))  and (len(expression_line) > i + 1) and expression_line[i + 1] == "[":
            
            
          
            current_element_type = 'value'
            
              
           
            skip_count, compiled_memory_acess, error_message = handle_memory_access(expression_line, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, i)
                
            
            if len(error_message) != 0:
                
                return in_function, element_stack, operation_stack, compiled_expression, error_message
                
                
                
    
            compiled_expression = compiled_expression + element_stack + operation_stack[:-1][::-1] + compiled_memory_acess
            
       
            
            operation_stack = []
            element_stack = []
            
            
            after_string = False
            previous_element_type = current_element_type
            
            continue
            
        
        
            

        elif expression_line[i] == 'true':
                current_element_type = 'value'
                element_stack.append("push constant: 1")
                
                previous_element_type = current_element_type
                
                after_string = False
                
                continue
            
        elif expression_line[i] == 'false':
                current_element_type = 'value'
                element_stack.append("push constant: 0")
                
                previous_element_type = current_element_type
                
                after_string = False
                
                continue
                
        elif expression_line[i].isnumeric():
                current_element_type = 'value'
                element_stack.append("push constant: " + expression_line[i])
                previous_element_type = current_element_type
            
                after_string = False
                
                continue

        elif expression_line[i] in operation_types:
                current_element_type = 'op'
                operation_stack.append(operation_types[expression_line[i]])
                
                if (i == 0 and current_element_type == 'op') or (current_element_type == 'op' and previous_element_type == 'op'):
            
                       compiled_expression.append("push constant: 0")
                       
                previous_element_type = current_element_type
            
                after_string = False
                
                continue
                
                
        elif expression_line[i][0] == "'" and not(after_string):
            
              
                    
                current_element_type = 'value'
                
           
                
                skip_count, element_stack, error_message = handle_string_creation(expression_line, i, element_stack, function_names)
                
                after_string = True
                
                if len(error_message) != 0:
                    
                    return in_function, element_stack, operation_stack, compiled_expression, error_message
                    
                previous_element_type = current_element_type
            
               
                
                continue
                    


        
        elif expression_line[i] == "[":
          
            
            current_element_type = 'value'
            
            skip_count, element_stack, error_message = handle_array_creation(expression_line, i, element_stack, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function)
                
            if len(error_message) != 0:
                    
                return in_function, element_stack, operation_stack, compiled_expression, error_message
                
            previous_element_type = current_element_type
            
            after_string = False
            
            continue
                
                
            
            
            

        elif expression_line[i] in function_names and len(expression_line) > i + 1 and expression_line[i + 1] == '(' :
            
            current_element_type = 'value'
            
            in_function_call = True
            
            
            skip_count, compiled_expression, element_stack, error_message = handle_function_call(expression_line, i, compiled_expression, element_stack, function_arg_count, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function)
            
            
            
            if len(error_message) != 0:
                    
                return in_function, element_stack, operation_stack, compiled_expression, error_message
                
            previous_element_type = current_element_type
            
            after_string = False
            
            continue
                
            





        elif expression_line[i] == "(" and not in_function_call:
            
            current_element_type = 'value'
            
            in_parentheses = True
            
           
            skip_count, compiled_expression, element_stack, operation_stack, error_message = handle_parenthesis(expression_line, i, compiled_expression, element_stack, operation_stack, main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function)
            
            if len(error_message) != 0:
                    
                return in_function, element_stack, operation_stack, compiled_expression, error_message
                
            previous_element_type = current_element_type
            
            after_string = False
            
            continue
            
            
            
           
            
        
        
      
        elif expression_line[i] in current_Function_Local_Variables and in_function:
            current_element_type = 'value'
           
            compiled_expression.append("push local: " + str(current_Function_Local_Variables.index(expression_line[i])))
            previous_element_type = current_element_type
            
            after_string = False
            
            continue

        elif expression_line[i] in main_local_variables and not in_function:
            current_element_type = 'value'
            
            
            compiled_expression.append("push local: " + str(main_local_variables.index(expression_line[i])))
            
            previous_element_type = current_element_type
            
            after_string = False
            
            continue
            
        elif expression_line[i] in current_Function_Arguments and in_function:
            current_element_type = 'value'
            
            compiled_expression.append("push argument: " + str(current_Function_Arguments[::-1].index(expression_line[i])))

            
            previous_element_type = current_element_type
            
            after_string = False
            
            continue
        
        
            
            
        if  (expression_line.count(']') != expression_line.count('[')):
            
            return in_function, element_stack, operation_stack, compiled_expression, ['Unmatched brackets']
            
        if (expression_line.count(')') != expression_line.count('(')):
            
            return in_function, element_stack, operation_stack, compiled_expression, ['Unmatched parentheses']
      
        if expression_line[i] != "'" and expression_line[i] != "]" and expression_line[i] != ")":
            
            return in_function, element_stack, operation_stack, compiled_expression, ['Invalid syntax']
        
       
        after_string = False
    
    
    
    if current_element_type == 'op':

        return in_function, element_stack, operation_stack, compiled_expression, ['Invalid syntax: Incomplete expression']
    
    compiled_expression += element_stack + operation_stack[::-1]
    element_stack = []
    operation_stack = []
    
    
    
    
    
    return in_function, element_stack, operation_stack, compiled_expression, errors 
















main_local_variables = []
current_Function_Arguments = []
current_Function_Local_Variables = []
function_names = []
function_arg_count = {}
function_return_type = {}
in_function = False
in_main_function = False
in_function_call = False
in_parentheses = True
in_offset_memory_access = False
if_stack_labels = []
in_conditional_block = False
conditional_type_stack = []
generated_code = []
conditional_statement_indices = []
in_elseif_chain = False
current_while_labels = []
while_loop_depth = 0
return_label = ""
current_function = ""
has_return = False
error_message = []
skip_count = 0
reserved_keywords = {'break', 'continue', 'RAM', 'if', 'while', 'elseif', 'else'}





def handle_variable_assignment(tokenized_lines, statement_idx, generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, reserved_keywords):
    
            
            
            
            is_invalid_assignment_format = tokenized_lines[statement_idx].count('=') != 1
            
            is_null_assignment = tokenized_lines[statement_idx][-1] == '='
            
            
            
            if is_invalid_assignment_format:
     
                error_message = ['Invalid assignment']
                
                return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                
            if is_null_assignment:
                
                error_message = ['Empty assignment']
                
                return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                
                
            
            in_direct_memory_acess = tokenized_lines[statement_idx][0] == "RAM"
            in_offset_memory_access = (tokenized_lines[statement_idx][0] in main_local_variables or tokenized_lines[statement_idx][0] in current_Function_Local_Variables or tokenized_lines[statement_idx][0] in current_Function_Arguments) and len(tokenized_lines[statement_idx]) > 3 and tokenized_lines[statement_idx][1] == "["
            
            
            
            
            
            
            is_free_variable = (tokenized_lines[statement_idx][0] in main_local_variables or tokenized_lines[statement_idx][0] in current_Function_Local_Variables or tokenized_lines[statement_idx][0] in current_Function_Arguments) and not in_offset_memory_access
            
            is_new_variable = tokenized_lines[statement_idx][0] == "int"
            
            
            
           
        
    
           
            
            
            if not in_direct_memory_acess and not in_offset_memory_access and is_new_variable:
                
                variable_assignment_tokens = tokenized_lines[statement_idx][3:]
                
                
                
            elif not in_direct_memory_acess and not in_offset_memory_access and is_free_variable:
               
                
                
                variable_assignment_tokens = tokenized_lines[statement_idx][2:]
                
            elif in_direct_memory_acess or in_offset_memory_access:
    
                variable_assignment_tokens = tokenized_lines[statement_idx][1:]
                
                
                
    
            if in_function and not in_direct_memory_acess and not in_offset_memory_access and is_new_variable and not(tokenized_lines[statement_idx][1] in current_Function_Local_Variables):
                
                
                
                if not(tokenized_lines[statement_idx][1].isalpha()):
                    
                    current_Function_Name = function_names[-1]
                    
                    error_message = ['Local Variable: ' + tokenized_lines[statement_idx][1] + ': Has invalid characters in: ' + current_Function_Name]
                    
                    
                    
                    return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                    
                
                
                if tokenized_lines[statement_idx][1] in reserved_keywords:
                    
                    error_message = [tokenized_lines[statement_idx][1] + ' is not a valid variable name']
                    
                    
                    
                    return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                
                
                current_Function_Local_Variables.append(tokenized_lines[statement_idx][1])
                
              
    
            elif not in_function and not in_direct_memory_acess and not in_offset_memory_access and is_new_variable and not(tokenized_lines[statement_idx][1] in main_local_variables):
                
                if not(tokenized_lines[statement_idx][1].isalpha()):
                    
                    error_message = ['Invalid characters in main variable name']
                    
                    return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                    
                    
                main_local_variables.append(tokenized_lines[statement_idx][1])
    
            if is_free_variable:
                current_statement_tokens = tokenized_lines[statement_idx]
                
            elif is_new_variable:
                
                current_statement_tokens = tokenized_lines[statement_idx][1:]
            
          
           
            
            pre_Variable_Assign = []
            post_Variable_Assign = []
            
            
           
            if not(is_free_variable or is_new_variable):
                
                temp_wrapped_content = []
              
                
                
                
                
                in_function, element_stack, operation_stack, compiled_code , errors  = process_expression_line(tokenized_lines[statement_idx][:tokenized_lines[statement_idx].index("=")],main_local_variables,current_Function_Arguments,current_Function_Local_Variables,function_names,in_function, function_return_type)
                
                
                if len(errors ) != 0:
                        
                        error_message = errors 
                        
                        return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                
            
                
                
                
                variable_assignment_tokens = tokenized_lines[statement_idx][tokenized_lines[statement_idx].index("=")+1:]
                
                
                
                compiled_code  = compiled_code [:-2]
                
       
                
                        
                pre_Variable_Assign = compiled_code  + ["point"]
                    
                post_Variable_Assign = ["pop this: 0"]
                
                   
                
            else:
                
        
                
               
                if in_function and current_statement_tokens[1] == "=" and current_statement_tokens[0] in current_Function_Local_Variables:
                    
                    post_Variable_Assign = ["pop local: " + str(current_Function_Local_Variables.index(current_statement_tokens[0]))]
    
                elif not in_function and current_statement_tokens[1] == "=" and current_statement_tokens[0] in main_local_variables:
                    post_Variable_Assign = ["pop local: " + str(main_local_variables.index(current_statement_tokens[0]))]
                    
                elif in_function and current_statement_tokens[1] == "=" and current_statement_tokens[0] in current_Function_Arguments:
                    
                    post_Variable_Assign = ["pop argument: " + str(current_Function_Arguments.index(current_statement_tokens[0]))]
    
    
    
            
            
            in_function, element_stack, operation_stack, compiled_code , errors  = process_expression_line(
                variable_assignment_tokens,
                main_local_variables,
                current_Function_Arguments,
                current_Function_Local_Variables,
                function_names,
                in_function, function_return_type
            )
            
            if len(errors ) != 0:
                        
                        error_message = errors 
                        
                        return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message
                
                
            
            
            
    
            
            translation =  compiled_code  + pre_Variable_Assign + post_Variable_Assign
            
      
      
      
         
            generated_code += translation
            
            
            return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, []
            
            
            









def handle_return(tokenized_lines, statement_idx, generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, has_return, return_label):
    
            #Generate code for return statements, handling single or multiple return values
            
            return_input = tokenized_lines[statement_idx][1:]
            
            in_parentheses = False
            in_brackets = False
      
            temp_wrapped_content = []
         
            return_expressions = []
            
           
            
            for idx in range(len(return_input)):
                    
                    
                   
                    if return_input[idx] == '(':
                       
                        in_parentheses = True
                        
                    elif return_input[idx] == ')':
                       
                        in_parentheses = False
                        
                    elif return_input[idx] == '[':
                        
                        in_brackets = True
                        
                    elif return_input[idx] == ']':
                        
                        in_brackets = False
                    
                    if return_input[idx] == ',' and not(in_parentheses and in_brackets):
                       
                        return_expressions.append(temp_wrapped_content)
                        temp_wrapped_content = []
                        
                    else:
                        
                        temp_wrapped_content+= [return_input[idx]]
                        
            
            
                    
                                
            return_expressions.append(temp_wrapped_content)
            
         
                
          
                
            
            return_value_code = []
            
            
            
            for return_expr in return_expressions:
                
                
                in_function, element_stack, operation_stack, compiled_code , errors  = process_expression_line(
                    return_expr,
                    main_local_variables,
                    current_Function_Arguments,
                    current_Function_Local_Variables,
                    function_names,
                    in_function, function_return_type
                )
                
                
                
                if len(errors) != 0:
                        
                        error_message = errors 
                        
                        return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, has_return, error_message
                
                
            
                return_value_code += compiled_code 
                
                
            return_value_save_instructions = []
            
            
            not_null_return = return_expressions != [[]]
            
            
            if not_null_return:
                
                has_return = True
                
                single_return_value = len(return_expressions) == 1
                
                
                multiple_return_values = len(return_expressions) > 1
                
            
                if single_return_value:
                    
                    generated_code += return_value_code
                
                
                
                elif multiple_return_values:
                    
                    no_allocation_function =  not("MemAlloc" in function_names)
                        
                        
                    if no_allocation_function:
                        
                        error_message = ['"MemAlloc not defined: Cannot allocate memory for multiple return values'] 
                        
                        return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, has_return, error_message
                        
                        
                    
                    
                    generated_code +=  return_value_code + ["call: #MemAlloc"] + ["push constant: " + str(len(return_expressions)) ] + ["end: #MemAlloc"] + ["push constant: 10", "point"] + ['pop this: 0'] + ['push this: 0', 'point']
                    
                    for i in range(len(return_expressions)):
                        
                        return_value_save_instructions += ['pop this: ' + str(i)]
                
                    
                    generated_code += return_value_save_instructions[::-1] + ["push constant: 10", "point", "push this: 0", 'push constant: 2', 'sub', 'point', 'push constant: ' + str(len(return_expressions)), 'pop this: 0', "push constant: 10", "point", "push this: 0"]
               
           
            
           
                
            generated_code.append("goto: " + return_label)   
            
           
            
            
            return generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, has_return, []
            
        







def handle_conditional(main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_arg_count, in_function, in_main_function, in_function_call, 
            in_parentheses,in_conditional_block, current_while_labels, while_loop_depth, return_label, current_function, has_return, error_message, skip_count, if_stack_labels, conditional_type_stack, generated_code, tokenized_lines, statement_idx):
    
    
            count_brackets = 1
            
          
            condition_body = []
            
            for i in tokenized_lines[statement_idx+1:]:
                
                
                
                if i[-1] == '{':
                    count_brackets += 1
                    
                if i[-1] == '};':
                    
                    count_brackets -= 1
                    
                if count_brackets == 0:
                    break
                 
                condition_body.append(i) 
                   
            if count_brackets != 0:
                
               error_message = ['Unclosed conditional block']
               return in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx
           
           
        
           
    
            in_conditional_block = True
            
    
          
           
            
            condition_end_label = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=7)
            )
    
            while_start_label = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=7)
            )
            
            
            
            is_if_statement = tokenized_lines[statement_idx][0] == "if"
            is_while_loop = tokenized_lines[statement_idx][0] == "while"
            is_elseif_statement = tokenized_lines[statement_idx][0] == "elseif"
            is_else_statement = tokenized_lines[statement_idx][0] == "else"
            
    
            if is_if_statement:
                
                
                if_stack_labels.append(condition_end_label)
                conditional_type_stack.append("if")
                
                
                
                
            if is_while_loop:
                
                
                generated_code += [("label: " + while_start_label)]
                if_stack_labels.append([condition_end_label, while_start_label])
                conditional_type_stack.append("while")
                while_loop_depth += 1
               
                current_while_labels = [condition_end_label, while_start_label]
                
    
            if is_elseif_statement:
                
                
                
                if_stack_labels.append(condition_end_label)
                conditional_type_stack.append("elseif")
                
                
                
            if is_else_statement:
                
        

                if_stack_labels.append(condition_end_label)
                conditional_type_stack.append("else")
                
                
    
            current_statement_tokens = tokenized_lines[statement_idx]
    
            
            
            
            misplaced_opening_bracket = current_statement_tokens[-1] != "{"
    
    
    
    
    
    
    
            if misplaced_opening_bracket:
                
                    error_message = ['Malformed conditional']
                    return  in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx
                    
            
            
            
               
            condition_tokens = tokenized_lines[statement_idx][1:-1]
            
            has_defined_condition = len(condition_tokens) != 0 
            
            
            if is_else_statement:
                
                
                
                if has_defined_condition:
                    error_message = ['Invalid else format']
                    return in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx
                    
            
            
            if not(is_else_statement):
                
              
                if not(has_defined_condition):
                    
                    error_message = ['invalid conditinal  format']
                    
                    return  in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx
                
                
                in_function, element_stack, operation_stack, compiled_code , errors  = process_expression_line(
                    condition_tokens,
                    main_local_variables,
                    current_Function_Arguments,
                    current_Function_Local_Variables,
                    function_names,
                    in_function, function_return_type
                )
                
                
                if len(errors ) != 0:
                        
                        error_message = errors 
                        return  in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx
                
                
                
                generated_code += compiled_code 
                generated_code.append(("if-false-goto: " + condition_end_label))
            
            
            
            body_compiled_code, error_message, in_function, in_main_function, conditional_body_index = generate_code(condition_body, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_arg_count, in_function, in_main_function, in_function_call, 
            in_parentheses, [], 
            in_conditional_block, [], [], [], False, current_while_labels, while_loop_depth, 
            return_label, current_function, has_return, error_message, skip_count)
            
            
            
            
            if error_message != []:
                
                statement_idx = conditional_body_index + statement_idx+1
                
                return in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx
          
    
    
            
            generated_code += body_compiled_code
            
            body_compiled_code = []
        
            
            skip_count = len(condition_body)
            
            
            return in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, [], statement_idx











def handle_function_definition(tokenized_lines, statement_idx, in_conditional_block, in_function, function_names, generated_code, function_arg_count, in_main_function, reserved_keywords, current_Function_Arguments, return_label, current_function):
    
    
            #Define a function, validating syntax and generating function declaration code
            
            if in_conditional_block:
                
                error_message = ['Unclosed conditional block']
                return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message
            
            elif in_function:
               
                error_message = ['Unclosed function']
                return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message
            
            in_function = True
    
            current_function = tokenized_lines[statement_idx][1]
            
            if current_function in reserved_keywords:
                
                error_message = [current_function + ' is not a valid function name']
                return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message
                
            
            function_names.append(tokenized_lines[statement_idx][1])
            
            function_return_label = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=7)
            )
            
            return_label = (tokenized_lines[statement_idx][1] + function_return_label)
            
            
            
            
            
            
            
             
            if (tokenized_lines[statement_idx].count('{')  != 1) or tokenized_lines[statement_idx][-1] != '{':
                error_message = ['Malformed function start']
                return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message
                
                
            
            if (tokenized_lines[statement_idx].count(')')  != 1) and (tokenized_lines[statement_idx].count('(')  != 1):
                error_message = ['Invalid function definition']
                return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message
            
            if (tokenized_lines[statement_idx][2] != '(') or (tokenized_lines[statement_idx][-2] != ')'):
                
                error_message = ['Malformed function arguments']
                return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message
           
            
            function_arguments = "".join(tokenized_lines[statement_idx][3:-2])
    
            current_Function_Arguments = function_arguments.split(",")
            current_Function_Arguments = current_Function_Arguments[::-1]
            
            
            if current_Function_Arguments == [""]:
    
                generated_code.append(("!function:" + tokenized_lines[statement_idx][1] + ":0"))
                
                if tokenized_lines[statement_idx][1] == "Main":
                    in_function = False
                    in_main_function = True
                    
                function_arg_count[tokenized_lines[statement_idx][1]] = 0
            else:
                generated_code.append(("!function:" + tokenized_lines[statement_idx][1] + ":" + str(len(current_Function_Arguments))))
    
            
                function_arg_count[tokenized_lines[statement_idx][1]] = (len(current_Function_Arguments))
                
                
            
            
            
            return in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, []
            






def handle_block_end(current_Function_Local_Variables, return_label, in_function,in_conditional_block, has_return,in_main_function, conditional_type_stack, conditional_statement_indices, generated_code, while_loop_depth, in_elseif_chain,if_stack_labels, tokenized_lines, statement_idx, function_return_type, function_names):
    
            #Handle closing blocks (functions or conditionals), generating appropriate labels and return instructions
    
            if in_function and not in_conditional_block:
                
                current_Function_Local_Variables.clear()
                generated_code.append("label: " + return_label)
                
                if has_return:
                    generated_code.append("return")
                    
                else:
                    generated_code.append("push constant: 0")
                    generated_code.append("nullreturn")
                    
                function_return_type[function_names[-1]] = has_return
                    
                    
                
                has_return = False
                
                in_function = False
                
            elif not(in_function) and not in_conditional_block and in_main_function:
                
                in_main_function = False
                
                
                
            
            
    
            if in_conditional_block:
                
                
                if conditional_type_stack[-1] == "while":
                    
                    
                    generated_code.append('goto: ' + if_stack_labels[-1][1])
                    generated_code.append('label: ' + if_stack_labels[-1][0])
                    
                    while_loop_depth -= 1
                    
                    
                elif conditional_type_stack[-1] == "if":    
                    generated_code.append("")
                    
              
                   
                    generated_code.append('label: ' + if_stack_labels[-1])
                    
                    
                    
                    
                    conditional_statement_indices.append(len(generated_code) - 2)
                    
                elif conditional_type_stack[-1] == "elseif":
                    in_elseif_chain = True
                    
                    generated_code.append("")
                    generated_code.append("label: " + if_stack_labels[-1])
                    conditional_statement_indices.append(len(generated_code) - 2)
                    
               
                
                elif conditional_type_stack[-1] == "else":
                    
                    
                    generated_code.append("")
                    generated_code.append("label: " + if_stack_labels[-1])
                    conditional_statement_indices.append(len(generated_code) - 2)
                    
                    
                    
                    
                
                if  ((conditional_type_stack[-1] == "else") or (in_elseif_chain and tokenized_lines[statement_idx + 1][0] != "elseif" and tokenized_lines[statement_idx + 1][0] != "else") ):
                    
                    
                   
                    in_elseif_chain = False
                    
                 
                    for i in conditional_statement_indices:
                        prev = generated_code[i]
                        
                     
                        
                       
                        generated_code[i] = 'goto: ' + if_stack_labels[-1]
                        
                       
                        
                        generated_code.append(prev)
                    
                    conditional_statement_indices = []       
            
                
                
                    
                    
                   
                    
                if_stack_labels.remove(if_stack_labels[-1])
             
                
                conditional_type_stack = conditional_type_stack[:-1]
                
                    
                    
              
                
    
                
    
            
            if in_conditional_block:
                
                if (len(tokenized_lines) <= statement_idx + 1) or ((tokenized_lines[statement_idx+1][0] != "elseif") and (tokenized_lines[statement_idx+1][0] != "else")):
                   
                   conditional_statement_indices = []
                
                
                in_conditional_block = False
                
                
            return in_conditional_block, conditional_type_stack, if_stack_labels, conditional_statement_indices, generated_code, in_elseif_chain, while_loop_depth, in_main_function, in_function, has_return, current_Function_Local_Variables
                
    
    
    
    
def handle_inline_function_call(tokenized_lines, statement_idx, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_return_type, in_function, generated_code):
    
            #Generate code for inline function calls that do not assign return values
            
            if function_return_type[tokenized_lines[statement_idx][0]]:
                
                
                error_message = ['Function returns value but is not assigned to a variable']
                return generated_code, error_message
            
            in_function, element_stack, operation_stack, compiled_code , errors  = process_expression_line(
                    tokenized_lines[statement_idx],
                    main_local_variables,
                    current_Function_Arguments,
                    current_Function_Local_Variables,
                    function_names,
                    in_function, function_return_type
                )
            
            if len(errors ) != 0 and errors  != [tokenized_lines[statement_idx][0] + ': has no return value']:
                        
                        error_message = errors 
                        
                        return generated_code, error_message
                
            
            
            generated_code += compiled_code 
            
            return generated_code, []
            







def generate_code(tokenized_lines, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_arg_count, in_function, in_main_function, in_function_call,
              in_parentheses, if_stack_labels, 
              in_conditional_block, conditional_type_stack, generated_code, conditional_statement_indices, in_elseif_chain, current_while_labels, while_loop_depth, 
             return_label, current_function, has_return, error_message, skip_count):
    
    
    #Main code generation function, processing tokenized statements and dispatching to handlers.
    skip_count = 0

    
    
    for statement_idx in range(len(tokenized_lines)):
    
        
        
        
        code_inside_function = in_function or in_main_function
        
        
        if skip_count != 0:
            
            skip_count-=1
            continue
    
        if tokenized_lines[statement_idx] == []:
            continue
        
      
        comment_in_line = '/' in tokenized_lines[statement_idx] and tokenized_lines[statement_idx].index('/') + 1 < len(tokenized_lines[statement_idx]) and tokenized_lines[statement_idx][tokenized_lines[statement_idx].index('/') + 1] == '/'
        variable_assignment = tokenized_lines[statement_idx][0] == "int" or ((tokenized_lines[statement_idx][0] == "RAM" or tokenized_lines[statement_idx][0] in main_local_variables or tokenized_lines[statement_idx][0] in current_Function_Local_Variables or tokenized_lines[statement_idx][0] in current_Function_Arguments or tokenized_lines[statement_idx][0] == '('))
        return_statement = tokenized_lines[statement_idx][0] == "return"
        conditinal_statement = tokenized_lines[statement_idx][0] == "if" or tokenized_lines[statement_idx][0] == "while" or tokenized_lines[statement_idx][0] == "elseif" or  tokenized_lines[statement_idx][0] == "else"
        fucntion_definiton = tokenized_lines[statement_idx][0] == "def"
        while_break = tokenized_lines[statement_idx][0] == "break"
        while_continue = tokenized_lines[statement_idx][0] == "continue"
        end_block = tokenized_lines[statement_idx][-1] == "};"
        inline_fucntion_call = tokenized_lines[statement_idx][0] in function_names
        
        
        if comment_in_line:
            
           
            tokenized_lines[statement_idx] = tokenized_lines[statement_idx][:tokenized_lines[statement_idx].index('/')]
            
            if tokenized_lines[statement_idx] == []:
                
                continue
        
          
        
       
    
        if variable_assignment:
            
            if not(code_inside_function):
                
                error_message = ['Cannot write code outside of fucntion']
                
                break
                
            
            generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, error_message = handle_variable_assignment(tokenized_lines, statement_idx, generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, reserved_keywords)
            
            if len(error_message) != 0:
                
                break
                
          
             
          
            
          
          
          
          
          
          
            
            
        elif return_statement:
            
            if in_main_function:
                
                error_message = ['Return not allowed in main']
                break
            
            
            if not(code_inside_function):
                
                error_message = ['Cannot write code outside of fucntion']
                
                break
            
            
            generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, has_return, error_message = handle_return(tokenized_lines, statement_idx, generated_code, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, in_function, has_return, return_label)
            
            
            
            if len(error_message) != 0:
                
                break
           
            
        
            
            
            
            
            
            
           
           
           
    
        elif conditinal_statement:
            
            
            if not(code_inside_function):
                
                error_message = ['Cannot write code outside of fucntion']
                
                break
            
            
            in_conditional_block, skip_count, generated_code, condition_end_label, while_start_label, while_loop_depth, error_message, statement_idx = handle_conditional(main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_arg_count, in_function, in_main_function, in_function_call, 
            in_parentheses,in_conditional_block, current_while_labels, while_loop_depth, return_label, current_function, has_return, error_message, skip_count, if_stack_labels, conditional_type_stack, generated_code, tokenized_lines, statement_idx)
            
            if len(error_message) != 0:
                
                break
   
                
            continue
            
    
            
    
        elif fucntion_definiton:
            
            
            if (code_inside_function):
                
                error_message = ['Cannot write Function within Function']
                
                break
            
            
            in_conditional_block, in_function, in_main_function, current_Function_Arguments, current_function, function_names, return_label, generated_code, error_message = handle_function_definition(tokenized_lines, statement_idx, in_conditional_block, in_function, function_names, generated_code, function_arg_count, in_main_function, reserved_keywords, current_Function_Arguments, return_label, current_function)
            
            if len(error_message) != 0:
                
                break
            
            
            
        elif while_break:
            
            if not(code_inside_function):
                
                error_message = ['Cannot write code outside of fucntion']
                
                break
            
            
            if while_loop_depth == 0:
                error_message = ['Break not allowed outside while loop']
            generated_code.append("goto: " + current_while_labels[0])
            
            
            
            
        elif while_continue:
            
            if not(code_inside_function):
                
                error_message = ['Cannot write code outside of fucntion']
                
                break
            
            
            if while_loop_depth == 0:
                error_message = ['Continue not allowed outside while loop']
                break
            
            generated_code.append("goto: " + current_while_labels[1])
            
            
    
            
    
        elif end_block:
            
           
            
            in_conditional_block, conditional_type_stack, if_stack_labels, conditional_statement_indices, generated_code, in_elseif_chain, while_loop_depth, in_main_function, in_function, has_return, current_Function_Local_Variables = handle_block_end(current_Function_Local_Variables, return_label, in_function,in_conditional_block, has_return,in_main_function, conditional_type_stack, conditional_statement_indices, generated_code, while_loop_depth, in_elseif_chain,if_stack_labels, tokenized_lines, statement_idx, function_return_type, function_names)
                
    
    
        
        
        elif inline_fucntion_call:
            
            
            if not(code_inside_function):
                
                error_message = ['Cannot write code outside of fucntion']
                
                break
            
            generated_code, error_message = handle_inline_function_call(tokenized_lines, statement_idx, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_return_type, in_function, generated_code)
            
            if len(error_message) != 0:
                
                break
            
            
        else:
            
          
            
         
            error_message = ['Invalid command']
            break


    return generated_code, error_message, in_function, in_main_function, statement_idx
    
    
    
if len(tokenized_lines) != 0:
    
    generated_code, error_message, in_function, in_main_function, statement_idx = generate_code(tokenized_lines, main_local_variables, current_Function_Arguments, current_Function_Local_Variables, function_names, function_arg_count, in_function, in_main_function, in_function_call,
                 in_parentheses, if_stack_labels, 
                 in_conditional_block, conditional_type_stack, generated_code, conditional_statement_indices, in_elseif_chain, current_while_labels, while_loop_depth, 
                 return_label, current_function, has_return, error_message, skip_count)
    
    
    if (in_function or in_main_function) and len(error_message) == 0:
        
        error_message = ['Unclosed function']
        
    
    if function_names == [] and error_message == []:
        
        error_message = ['"Main" Fucntion dose not exist']
        
    
    elif error_message == [] and function_names[-1] != "Main":
        
        error_message = ['"Main" Fucntion must be last created fucntion']
        
    
        
        
    generated_code.append("return")
    
    
    if len(error_message) == 0:
    
        
        try:
             
             with open(sys.argv[2], "w") as output_file:
                
             
                for i in generated_code:
                    
                    if i != "":
                        output_file.write(i + '\n')

                print("Successfully Compiled")

        except:
             
             print("Invalid Output File")
                
    else:
        
        
        print('\nERROR MESSAGE: ' + error_message[0])
        print('\nline', statement_locations[statement_idx]+1, '-> ', ' '.join(tokenized_lines[statement_idx]))


else:
    
    print("Empty File")



