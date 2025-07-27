"""
This script translates a high-level assembly-like language into a low-level
assembly code, specifically designed for a custom virtual machine or processor.
It handles function definitions, calls, stack operations (push/pop),
and arithmetic/logical operations.
"""


import random
import string
import sys

# This dictionary maps high-level assembly instructions to their low-level assembly templates.
# Each value is a multi-line string representing the sequence of operations for the corresponding instruction.

assembly_translation={
    
    'pushconstant': "@Set,MemPos: !SP \n@MemPos=Mem: \n@Set,Mem: \n@R3=Mem: \n@Set,MemPos: !SP \n@MemInc: \n",
    'poplocal':     "@Set,MemPos: !SP \n@MemDec:\n@MemPos=Mem:\n@MemVal=Mem: \n @Clr,Mem:\n@Set,MemPos: !LCL\n@MemPos=Mem:\n@MemPos,ADD: \n@Mem=MemVal:",
    'pushlocal': "@Set,MemPos: !LCL \n@MemPos=Mem: \n@MemPos,ADD: \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@R3=Mem:\n@Set,MemPos: !SP \n@MemInc:",
    'popargument':  "@Set,MemPos: !SP \n@MemDec:\n@MemPos=Mem:\n@MemVal=Mem: \n @Clr,Mem:\n@Set,MemPos: !ARG\n@MemPos=Mem:\n@MemPos,ADD: \n@Mem=MemVal:",
    'pushargument': "@Set,MemPos: !ARG \n@MemPos=Mem: \n@MemPos,ADD: \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n",
    'popthis': "@Set,MemPos: !SP \n@MemDec:\n@MemPos=Mem:\n@MemVal=Mem: \n @Clr,Mem:\n@Set,MemPos: !THIS\n@MemPos=Mem:\n@MemPos,ADD: \n@Mem=MemVal:",
    'pushthis': "@Set,MemPos: !THIS \n@MemPos=Mem: \n@MemPos,ADD: \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@R3=Mem: \n@Set,MemPos: !SP \n@MemInc: \n",
    'popthat': "@Set,MemPos: !SP \n@MemDec:\n@MemPos=Mem:\n@MemVal=Mem:\n@Set,MemPos: !THAT\n@MemPos=Mem:\n@MemPos,ADD: \n@Mem=MemVal:",
    'pushthat': "@Set,MemPos: !THAT \n@MemPos=Mem: \n@MemPos,ADD: \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n",
    'poptemp': "@Set,MemPos: !SP \n@MemDec:\n@MemPos=Mem:\n@MemVal=Mem:\n@Set,MemPos: 5\n@MemPos=Mem:\n@MemPos,ADD: \n@Mem=MemVal:",
    'pushtemp': "@Set,MemPos: 5 \n@MemPos=Mem: \n@MemPos,ADD: \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n",
    'point\n': "@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !THIS \n@Mem=MemVal: \n@Set,MemPos: !SP\n",
    'add\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R1ADDR2\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n',
    'sub\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R2SUBR1\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n',
    'less\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R1LESSR2\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n',
    'grat\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R1GRATR2\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n @Set,R1: 0\n @in,R3: R1ADDR3\n',
    'neg\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal: \n@NegR1: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R1:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n',
    'or\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R1ORR2\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n',
    'eq\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R1EQR2\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n @Set,R1: 0\n @in,R3: R1ADDR3\n',
    'and\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R1=MemVal:\n@Set,MemPos: !SP\n@MemDec:\n@MemPos=Mem: \n@MemVal=Mem:\n@Clr,Mem:\n@R2=MemVal:\n@in,R3: R1ANDR2\n@Set,MemPos: !SP \n@MemPos=Mem: \n@MemVal=R3:\n@Mem=MemVal:\n@Set,MemPos: !SP \n@MemInc: \n',
    'functionsave': '@Set,MemPos: !LCL \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n@Set,MemPos: !ARG \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n@Set,MemPos: !THIS \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n@Set,MemPos: !THAT \n@MemVal=Mem: \n@Set,MemPos: !SP \n@MemPos=Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n',
    'setlocal': '@MemVal=Mem: \n@Set,MemPos: !LCL \n@Mem=MemVal: \n@Set,MemPos: !SP \n@Set,R1: \n@MemVal=Mem: \n@in,Mem: MemValADDR1',
    'setargumnetpos': ' \n@Set,MemPos: !SP \n@R1=Mem: \n@Set,R2: \n@Set,MemPos: !ARG \n@in,Mem: R1SUBR2',
    'resetPos' : '@Set,MemPos: !SP \n\n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !THAT \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !THIS \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !ARG \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !LCL \n@Mem=MemVal: \n', 
    'removearg': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem:',
    'clrone\n': '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n',
    'resultonstack': '@Set,MemPos: !SP  \n@MemPos=Mem: \n@MemVal=R3: \n@Mem=MemVal: \n@Set,MemPos: !SP  \n@MemInc: \n',
    'call': '%JWP: \n',
    'end': '\n',
    'goto': '%JMP: \n',
    'if-false-goto': '%JWZ: \n',
    'if-true-goto': '%JWP: \n',
    'if-neg-goto': '%JWN: \n',

}


# Stores assembly code for defined functions, keyed by their label (e.g., '#FunctionName').
defined_functions={}
# Stores the return type (e.g., 'return\n' or 'nullreturn\n') for each function.
function_return_types={}

defined_labels= {}

class InputLineAnalyzer:
    
    """
    The InputLineAnalyzer class is responsible for analyzing a single line of input
    and determining its type, as well as cleaning up whitespace.
    """
    
    
    def __init__(self, input_line, assembly_translation):
        
        """
        Initializes the InputLineAnalyzer with a raw input line.
        """
        
        self.current_line = input_line
        
    def get_instruction_type(self):
        
        """
        Determines the type of instruction based on the beginning of the line.
        Returns a string indicating the instruction type (e.g., "function", "push", "call").
        """
        
            
        if self.current_line[0][0] == '!':
            return "function"
            
        elif self.current_line[:4] == 'push':
            
            return "push"
        
        elif self.current_line[:4] == 'call':
            
            return "call"
            
        elif self.current_line[:3] == 'end':
            return 'end'   
            
        elif self.current_line[:4] == 'goto':
            
            return "goto"
            
        elif self.current_line[:5] == 'label':
           
            return 'label'
        elif self.current_line[:3] == 'pop':
            return 'pop'
            
        elif self.current_line[:2] == 'if':
            return 'if'
            
        elif self.current_line in assembly_translation or self.current_line == 'return\n' or self.current_line == 'nullreturn\n':
            
            return 'algo'
            
        else:
            
            return "Invalid"
        
            
            
    def clean_whitespace(self):
        
        """
        Splits the current line by ':' and removes leading/trailing whitespace
        and newline characters from each part.
        Returns a list of cleaned parts.
        """
        
        parts = (self.current_line).split(':')
        
        cleaned_parts = []
        for i in range(len(parts)):
            # Convert to list to remove characters mutable, then join back
            char_list  = list(parts[i])
            # Remove all spaces and newlines
            for i in range(char_list .count(' ')):
                for i in char_list :
                    if i == " " or i == "\n":
                        char_list .remove(i)
            cleaned_parts.append(''.join(char_list))
            
            
        # Update the original 'parts' list with the cleaned versions    
        for i in range(len(cleaned_parts)):
        
            parts[i] = cleaned_parts[i]
            
        return parts











class Lexer:
    
    """
    The Lexer class is responsible for converting parsed instruction parts
    into their corresponding low-level assembly code using predefined templates.
    """
    
    def __init__(self,instruction_type,instruction_parts, defined_labels):
        
        """
        Initializes the Lexer with the type of instruction and its parsed components.
        """
    
        self.instruction_type = instruction_type
        self.parsed_instruction = instruction_parts
        
    def generate_assembly(self):
        
        """
        Generates a list of assembly lines based on the instruction type and its parts.
        Returns a list of strings, where each string is an assembly line.
        Returns None if the instruction is just a newline.
        """
        
        generated_assembly_lines = []
        
        
        if self.parsed_instruction[0] == '\n':
            
            generated_assembly_lines = ''
        
            
        elif self.instruction_type == "call":
            
            # For 'call' instructions, a placeholder is added. Actual call logic is handled later.

    
            generated_assembly_lines.append('\n'+'call:' + self.parsed_instruction[1] + '\n')
            
        elif self.instruction_type == "end":
            
            # For 'end' instructions (function returns), a placeholder is added.
            # Actual return logic is handled later.
            
            generated_assembly_lines.append('\n'+'end:' + self.parsed_instruction[1] + '\n')
            
        elif self.instruction_type == 'label':
           
            # Labels are directly translated to assembly labels (prefixed with '#').
            
            generated_assembly_lines.append('#' + self.parsed_instruction[1] + '\n')
            
            
            
            
            
            
            
        elif self.instruction_type == "push" and self.parsed_instruction[0] in assembly_translation:
            
            # For 'push' instructions, retrieve the template and insert the constant/index.

            
            command_template_lines = (assembly_translation[self.parsed_instruction[0]])
            command_template_lines = command_template_lines.split('\n')
            
            
            # The value to push is inserted into the third line of the template.


            
            command_template_lines[2] = command_template_lines[2] + self.parsed_instruction[1] + '\n'
         
            
            generated_assembly_lines = command_template_lines + ['\n']
            
        elif self.instruction_type == "pop" and self.parsed_instruction[0] in assembly_translation:
            
            # For 'pop' instructions, retrieve the template and insert the memory address/index.

            command_template_lines = (assembly_translation[self.parsed_instruction[0]])
            
            
            # The destination address/index is inserted into the second-to-last line.
            command_template_lines = command_template_lines.split('\n')
            command_template_lines[-2] = command_template_lines[-2] + self.parsed_instruction[1] 
            
            
            
            
            
            generated_assembly_lines = command_template_lines + ['\n']
        
        elif self.instruction_type == "if" and self.parsed_instruction[0] in assembly_translation:
            
            # For 'if' instructions, generate assembly for conditional jumps.
            
            command_template_lines = (assembly_translation[self.parsed_instruction[0]])
            command_template_lines = command_template_lines.split('\n')
           
            
            conditional_jump_assembly=[]
            
            conditional_jump_assembly.append(assembly_translation['clrone\n'])
            
            
            
            
            if self.parsed_instruction[1].isnumeric():
            
            
                conditional_jump_assembly.append('@Set,R2: ' + self.parsed_instruction[1]+'\n')
            
            else:
                
                conditional_jump_assembly.append('@Set,R2: ' + defined_labels[self.parsed_instruction[1]] +'\n')
            
            
            # Append the jump command from translation table
            
            conditional_jump_assembly.append(command_template_lines[0] + ' 0' + '\n')
            
            generated_assembly_lines = conditional_jump_assembly + ['\n']
           
        elif self.instruction_type == "goto" and self.parsed_instruction[0] in assembly_translation:
            
            # For 'goto' instructions, generate assembly for unconditional jumps.
            command_template_lines = (assembly_translation[self.parsed_instruction[0]])
            command_template_lines = command_template_lines.split('\n')
        
            conditional_jump_assembly=[]
            
            
            if self.parsed_instruction[1].isnumeric():
            
            
                conditional_jump_assembly.append('@Set,R2: ' + self.parsed_instruction[1]+'\n')
            
            else:
                
                conditional_jump_assembly.append('@Set,R2: ' + defined_labels[self.parsed_instruction[1]] +'\n')
           
            
            # Append the jump command from translation table
            conditional_jump_assembly.append(command_template_lines[0] + ' 0' + '\n')
            
            
            
            
            generated_assembly_lines = conditional_jump_assembly + ['\n']
           
        elif self.instruction_type == 'algo' and self.parsed_instruction[0] in assembly_translation:
            
            # For arithmetic/logical operations, retrieve the pre-defined template.
            command_template_lines = assembly_translation[self.parsed_instruction[0]]
            generated_assembly_lines = command_template_lines.split('\n')
            
        
        else:
            
            generated_assembly_lines = "INVALID"
        
        return generated_assembly_lines
        

            
            
            
                    

        
        
        
        
           

try:
    # Open the input file for reading    
    with open(sys.argv[1], "r") as input_file:
        # Read all lines from the input file

        input_lines = input_file.readlines()

except Exception:

    print("File Error")



    
# Open the output file for writing (this will create or overwrite 'test.txt')





def Compile_Assembly(input_lines, defined_functions, function_return_types):


    callstack = []
    # Initialize lists to store assembly code for main program and functions
    main_assembly_code = []
    
    # Start with a jump to Main function for program execution
    non_main_functions_assembly = ['@Set,R2: #Main \n%JMP: 0']
    
    
    # Stacks to keep track of return labels for nested function calls
    return_address_stack_main = []
    return_address_stack_functions = []
    
    
    
    for line in input_lines:
        
        command = InputLineAnalyzer(line, assembly_translation).clean_whitespace()
        
    
        
        if len(command) == 2 and command[0] == 'label' and not(command[1].isnumeric()):
            
            
            
            defined_labels[command[1]] = '#' + command[1]
            
    

    # First Pass: Process functions and populate defined_functions and function_return_types
    
    for i in range(len(input_lines)):
        current_instruction_type = InputLineAnalyzer(input_lines[i], assembly_translation).get_instruction_type()
        
        if current_instruction_type == "Invalid":
            
            return ["ERROR"], [str(input_lines.index(input_lines[i])+1) + ': invalid VM command']
            
        if current_instruction_type == 'function':
            
            
            function_assembly_lines=[]
            local_variable_count = 0
            current_line_index = input_lines.index(input_lines[i])
            current_instruction = input_lines[i]
            function_declaration_line = current_instruction # The line that declares the function (e.g., "!function:MyFunction:2")
            function_prologue_lines = []
            processed_local_declarations = [] # Keep track of local declarations to count them only once
            
            # Extract function name and number of arguments
            
            fucntion_split = InputLineAnalyzer(function_declaration_line, assembly_translation).clean_whitespace()
            
            
            if len(fucntion_split) != 3 or not((fucntion_split[-1].strip()).isnumeric()) or fucntion_split[1].isnumeric() or fucntion_split[1].isnumeric() or len(fucntion_split[1]) == 0 or fucntion_split[0] != '!function':
                
                return ["ERROR"], [str(current_line_index+1) + ': invalid function format']
                
        
            name = fucntion_split[1]
            argnum = fucntion_split[2]
    
    
    
            # Add function prologue only if it's not the main function
            if name != 'Main':
                function_prologue_lines.append('#' + name + '\n')
                # Save caller's LCL, ARG, THIS, THAT pointers on the stack
                
                function_prologue_lines.append(assembly_translation['functionsave'])
                
                
            # Process lines within the function until a 'return' or 'nullreturn' is found
            
            
                
            
            
            while (input_lines[current_line_index] != 'return\n' and input_lines[current_line_index] != 'nullreturn\n'):
                
                
                if input_lines[current_line_index] == (function_declaration_line+' \n') or input_lines[current_line_index] == function_declaration_line:
                    
                    # Skip the function declaration line itself
                    function_assembly_lines.append('\n')
                    
                else:
                    # Parse and lex the inner instruction
                    inner_instruction_type = InputLineAnalyzer(input_lines[current_line_index], assembly_translation).get_instruction_type()
                    inner_parsed_parts = InputLineAnalyzer(input_lines[current_line_index], assembly_translation).clean_whitespace()
                    
                    # Generate assembly for the inner instruction and append it
                    
                    
                   
                        
                    
                    
                    if inner_instruction_type == 'push' and len(inner_parsed_parts) != 2:
                        
                        return ["ERROR"], [str(current_line_index+1) + ': incorrect "push" format']
                        
                    
                  
                    if inner_instruction_type == 'push' and not(inner_parsed_parts[-1] in defined_labels or inner_parsed_parts[-1].isnumeric()):
                        
                        return ["ERROR"], [str(current_line_index+1) + ': invalid push value']
                        
                     
                        
                    if inner_instruction_type == 'goto' and not(inner_parsed_parts[-1] in defined_labels or inner_parsed_parts[-1].isnumeric()):
                        
                        return ["ERROR"], [str(current_line_index+1)  + ': invalid jmp']
                        
                        
                    
                    if inner_instruction_type == 'if' and not(inner_parsed_parts[-1] in defined_labels):
                        
                        return ["ERROR"], [str(current_line_index+1)  + ': invalid conditinal jump']
                        
                    
                    if inner_instruction_type == 'label' and (inner_parsed_parts[0] != 'label' or inner_parsed_parts[1] == '\n' or inner_parsed_parts[1].isnumeric()):
                        
                        return ["ERROR"], [str(current_line_index+1)  + ': invalid label']
                        
                    
                    lexer_output = Lexer(inner_instruction_type,inner_parsed_parts, defined_labels).generate_assembly()
                    
                    
                    
                    
                    
                    if lexer_output == "INVALID":
                        
                        return ["ERROR"], [str(current_line_index+1) + ': invalid VM command']
                    
                   
                  
                    function_assembly_lines.append('\n'.join(lexer_output))
                    
                    # Count local variables declared within the function
                    if inner_parsed_parts[0][3::] == 'local' and (not(''.join(inner_parsed_parts) in processed_local_declarations)):
                        local_variable_count += 1
                        processed_local_declarations.append(''.join(inner_parsed_parts))
                        
                    
                    
                
                current_line_index = current_line_index+1
                
                if current_line_index >= len(input_lines):
                
                    return ["ERROR"], ["No return for function: Line " + str(current_line_index+1)]
                
            
            # Add epilogue (return handling) if it's not the Main function
            if name != 'Main' and (input_lines[current_line_index] == 'return\n' or input_lines[current_line_index] == 'nullreturn\n'):
               
                # Adjust LCL pointer for local variables
                temp_command_lines = assembly_translation['setlocal'].split('\n')
                temp_command_lines[-3] = temp_command_lines[-3] + str(local_variable_count)
                function_prologue_lines.append('\n'.join(temp_command_lines))
                
                # Adjust ARG pointer to point to the return address
                temp_command_lines = assembly_translation['setargumnetpos'].split('\n')
                temp_command_lines[-3] = temp_command_lines[-3] + str(4 + int(argnum) + local_variable_count)
                function_prologue_lines.append('\n'.join(temp_command_lines) + '\n')
                
                
                # Combine prologue and function body
                function_prologue_lines.append(''.join(function_assembly_lines))
                function_assembly_lines = function_prologue_lines + ['\n']
                
                
                
            # Add stack cleanup and return jump if it's not the Main function
            if name != 'Main' and (input_lines[current_line_index] == 'return\n' or input_lines[current_line_index] == 'nullreturn\n'):  
                
                stack_cleanup_lines = []
                # Clean up local variables from the stack
                for i in range(local_variable_count):
                    stack_cleanup_lines.append('@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n')
               
                # Reset LCL, ARG, THIS, THAT to caller's state
                function_assembly_lines.append(''.join(stack_cleanup_lines) + assembly_translation['resetPos'])
                
                # Remove arguments from the stack
                for i in range(int(argnum)):
                    
                    function_assembly_lines.append(assembly_translation['removearg'] + '\n')
                    
                # Push return value (if any) to the stack
                function_assembly_lines.append(assembly_translation['resultonstack'])
                
                
                # Add a generic 'return' marker to be replaced later
                function_assembly_lines.append('\nreturn')
                
            
            
            
            # Store the assembled function code and its return type
            function_assembly_lines = (''.join(function_assembly_lines)).split('\n')
    
            defined_functions['#' + name] = ' \n'.join(function_assembly_lines)
            function_return_types['#' + name] = input_lines[current_line_index] 
        
    
    if not "#Main" in  defined_functions:
        
        return ["ERROR"], ["No 'Main' function"]
                
    
    # Second Pass: Resolve function calls and finalize assembly code
    for i in range(len(input_lines)):
        current_instruction_type = InputLineAnalyzer(input_lines[i], assembly_translation).get_instruction_type()
        
        
        # Process non-Main functions
    
        if current_instruction_type == 'function' and input_lines[i] != '!function:Main:0\n':
            
            function_name = ''.join(((''.join(((input_lines[i].split(':')[1]).split(' ')))).split('\n')))
            
            
            # Append the assembled function code and add a jump back to the return address
    
    
            if not('#'+ function_name in defined_functions):
                
                return ["ERROR"], [function_name + "dose not exist"]
                
            non_main_functions_assembly = non_main_functions_assembly + defined_functions['#'+ function_name].split('\n') + ['@MemDec: \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@R2=MemVal: \n@Set,MemPos: !SP \n@MemInc: \n@MemInc: \n%JMP: 0']
        
            
        
        # Process the Main function
        if current_instruction_type == 'function' and input_lines[i] == '!function:Main:0\n':
            
            
            function_name = ''.join(((''.join(((input_lines[i].split(':')[1]).split(' ')))).split('\n')))
           
            main_assembly_code = main_assembly_code + ['\n#Main'] + defined_functions['#'+ function_name].split('\n')
            
       
        
            # Resolve 'call' and 'end' instructions within non_main_functions_assembly
            for i in range(len(non_main_functions_assembly)):
                
                
                if non_main_functions_assembly[i][:4] == 'call':
                    
                    # Generate a unique return label for this call
                
                   
                    
                    function_name = ''.join(((''.join(((non_main_functions_assembly[i].split(':')[1]).split(' ')))).split('\n')))
                    
                    callstack.append(function_name)
                   
                    if not(function_name in defined_functions):
                        
                        return ["ERROR"], [function_name + "does not exist"]
                        
                        
                    return_label_id = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=8))
                    
                    return_address_stack_functions.append(return_label_id)     
                    
                    # Insert assembly to push the return address onto the stack before jumping to the function
                     
                    call_assembly_lines = '@Set,MemPos: !SP \n@MemPos=Mem: \n@Set,Mem: ' + '#' + return_label_id + '\n@R3=Mem: \n@Set,MemPos: !SP \n@MemInc:'
                    
                    non_main_functions_assembly[i] = call_assembly_lines
                    
                    
                    
                    
                if non_main_functions_assembly[i][:3] == 'end':
                    function_name = ''.join(((''.join(((non_main_functions_assembly[i].split(':')[1]).split(' ')))).split('\n')))
                    
                 
                    
                    if len(callstack) == 0:
                        
                        return ["ERROR"], [function_name + "no fucntion called"]
                    
                    called_fucntion_name = callstack.pop()
                    
                
                    if not(function_name in defined_functions):
                        
                        return ["ERROR"], [function_name + "does not exist"]
                        
                    if function_name != called_fucntion_name:
                        
                         return ["ERROR"], [function_name + "incorrect fucntion end"]
                        
                        
                    # Get the return address from the stack
                
                    call_assembly_lines = '@Set,R2: ' + function_name + '\n%JMP: ' + function_name + '\n #' + return_address_stack_functions[-1] + '\n'
                    
                    return_address_stack_functions.pop() # Remove the used return address
                    
                    # Assembly to retrieve return address and adjust stack after function call
                    return_address_setup = '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@Clr,Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc:'
                    null_return_adjustment = ''
                    
                    
                    
                    # If the function has a null return, adjust stack pointer
                    
                    if function_return_types[function_name] == 'nullreturn\n':
                        null_return_adjustment = '\n@MemDec:'
                        
                    non_main_functions_assembly[i] = call_assembly_lines + return_address_setup + null_return_adjustment
                    
            
            
            # Resolve 'call' and 'end' instructions within main_assembly_code
            
            for i in range(len(main_assembly_code)):
                
                
                if main_assembly_code[i][:4] == 'call':
                    
                    
                    
                    function_name = ''.join(((''.join(((main_assembly_code[i].split(':')[1]).split(' ')))).split('\n')))
                    
                    callstack.append(function_name)
                    
                    if not(function_name in defined_functions):
                        
                        return ["ERROR"], [function_name + " does not exist"]
                    
                    
                    return_label_id = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=8))
                                 
                                 
                    return_address_stack_main.append(return_label_id)  
                    
                    # Insert assembly to push the return address onto the stack before jumping to the function
                
                    call_assembly_lines = '@Set,MemPos: !SP \n@MemPos=Mem: \n@Set,Mem: ' + '#' + return_label_id + '\n@R3=Mem: \n@Set,MemPos: !SP \n@MemInc:'
                    main_assembly_code[i] = call_assembly_lines
                   
                    
                if main_assembly_code[i][:3] == 'end':
                   
              
                    function_name = ''.join(((''.join(((main_assembly_code[i].split(':')[1]).split(' ')))).split('\n')))
                    
                    
                    if len(callstack) == 0:
                        
                        return ["ERROR"], [function_name + "no fucntion called"]
                    
                    called_fucntion_name = callstack.pop()
                    
                
                    if not(function_name in defined_functions):
                        
                        return ["ERROR"], [function_name + "does not exist"]
                        
                    if function_name != called_fucntion_name:
                        
                         return ["ERROR"], [function_name + " incorrect fucntion end"]
                         
                         
                    
                    # Get the return address from the stack
                
                    call_assembly_lines = '@Set,R2: ' + function_name + '\n%JMP: ' + function_name + '\n #' + return_address_stack_main[-1] + '\n'
                    
                    return_address_stack_main = return_address_stack_main[:-1]
                    
                    # Assembly to retrieve return address and adjust stack after function call
                    return_address_setup = '@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@MemVal=Mem: \n@Clr,Mem: \n@Set,MemPos: !SP \n@MemDec: \n@MemPos=Mem: \n@Clr,Mem: \n@Mem=MemVal: \n@Set,MemPos: !SP \n@MemInc:'
                    
                    null_return_adjustment = ''
                    
                    # If the function has a null return, adjust stack pointer
    
                    if function_return_types[function_name] == 'nullreturn\n':
                        null_return_adjustment = '\n@MemDec:'
                        
                        
                    main_assembly_code[i] = call_assembly_lines + return_address_setup + null_return_adjustment
    
    if len(callstack) != 0:
        
        return ["ERROR"], ["Unclosed Funciton Call "]
        
    return  non_main_functions_assembly, main_assembly_code
  
  
  
 
try:
    # Open the output file for writing    
    output_file =  open(sys.argv[2], "w")
       

except Exception:

    print("File Error")
 
  
    
try:   
    non_main_functions_assembly, main_assembly_code = Compile_Assembly(input_lines, defined_functions, function_return_types) 
    
except Exception:
    
    print("ERROR FOUND")

else:
    if non_main_functions_assembly == ["ERROR"]:
        
        print("ERROR: Line", main_assembly_code[0])
    else:
        # Lines to be excluded from the final output (placeholders or empty lines)
        
        lines_to_exclude = ['return', ' ', None]                
        non_main_functions_assembly = [i for i in non_main_functions_assembly if i not in lines_to_exclude]
        main_assembly_code = [i for i in main_assembly_code if i not in lines_to_exclude]
        
        # Write the assembled non-main functions assembly to the output file
        
        output_file.write('\n'.join(non_main_functions_assembly)) 
        
        # Write the assembled main function assembly to the output file
        
        output_file.write('\n'.join(main_assembly_code))
        
        print("Successfully Compiled")
    # Close the output file
    
output_file.close()