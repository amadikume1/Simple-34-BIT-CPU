
import sys

variable_table = {
    "!SP": "0000000000000000",
    "!LCL":"1000000000000000",
    "!ARG": "0100000000000000",
    "!THIS":"1100000000000000",
    "!THAT":"0010000000000000",
    
    
}
symbol_table = {
    
    
    
}
instruction_map = {
    
    "@in,MemPos": "111",
    "@in,MemVal" : "001",
    "@in,Mem": "011",

    "@in,R1" : "100", 
    "@in,R2" : "110",
    "@in,R3" : "101",
    
    "@Set,R1" : "100000000000000001000",
    "@Set,R2" : "110000000000000001000",
    "@Set,R3" : "101000000000000001000",
    "@Set,MemPos" : "111000000000000001000",
    "@Set,MemVal" : "001000000001100001000",
    "@Set,Mem"     : "011100010000000001000",
    "@MemPos,ADD" :  "111100000110001000000",
    "@MemPos,SUB" :  "111100000110000100000",
    "R1ADDR2": "1100000010010000000000000000000000",
    "R1ADDR3": "1100000001010000000000000000000000",
    "R1ADDR1": "1100000000010000000000000000000000",
    "R1ADDMemPos": "1100000011010000000000000000000000",
    "R1ADDMemVal": "1101000000010000000000000000000000",
    "R2ADDR1": "1100001000010000000000000000000000",
    "R2ADDR2": "1100001010010000000000000000000000",
    "R2ADDR3": "1100001001010000000000000000000000",
    "R2ADDMemPos": "1100001011010000000000000000000000",
    "R2ADDMemVal": "1101001000010000000000000000000000",
    "R3ADDR1": "1100000100010000000000000000000000",
    "R3ADDR2": "1100000110010000000000000000000000",
    "R3ADDR3": "1100000101010000000000000000000000",
    "R3ADDMemVal": "1101000010010000000000000000000000",
    "R3ADDMemPos": "1100000111010000000000000000000000",
    "R3,ADD" : "000000000000000000000000000000",
    "R2,ADD" : "000000000000000000000000000000",
    "R1,ADD" : "000000000000000000000000000000",
    "MemValADDR1": "1110000000010000000000000000000000",
    "MemValADDR2": "1110000010010000000000000000000000",
    "MemValADDR3": "1110000001010000000000000000000000",
    "R1EQR2":   "1100000010011000000000000000000000",
    "R1GRATR2": "1100000010010100000000000000000000",
    "R1LESSR2": "1100000010001100000000000000000000",
    "R1ANDR2":  "1100000010000100000000000000000000",
    "R1ORR2":   "1100000010000010000000000000000000",

    "R1SUBR2": "1100000010001000000000000000000000",
    "R1SUBR3": "1100000001001000000000000000000000",
    "R1SUBR1": "1100000000001000000000000000000000",
    "R1SUBMemPos": "1100000011001000000000000000000000",
    "R1SUBMemVal": "1101000000001000000000000000000000",
               
    "R2SUBR1": "1100001000001000000000000000000000",
    "R2SUBR2": "1100001010001000000000000000000000",
    "R2SUBR3": "1100001001001000000000000000000000",
    "R2SUBMemPos": "1100001011001000000000000000000000",
    "R2SUBMemVal": "1101001000001000000000000000000000",
    "R3SUBR1": "1100000100001000000000000000000000",
    "R3SUBR2": "1100000110001000000000000000000000",
    "R3SUBR3": "1100000101001000000000000000000000",
    "R3SUBMemVal": "1101000010001000000000000000000000",
    "R3SUBMemPos": "1100000111001000000000000000000000",
    "R3,SUB" : "000000000000000000000000000000",
    "R2,SUB" : "000000000000000000000000000000",
    "R1,SUB" : "000000000000000000000000000000",
    "MemValSUBR1": "1110000000001000000000000000000000",
    "MemValSUBR2": "1110000010001000000000000000000000",
    "MemValSUBR3": "1110000001001000000000000000000000",
    
    "@NegR1" : "1001000000000100010000000000000000000",
    "@NegR2" : "1101000001000100010000000000000000000",
    "@NegR3" : "1011000000100100010000000000000000000",
    "@NegMemPos" : "1111000001100100010000000000000000000",
    "@NegMemVal" : "0011010000100100010000000000000000000",
    
    "@Clr,R1" : "1000000000000000010000000000000000000",
    "@Clr,R2" : "1100000000000000010000000000000000000",
    "@Clr,R3" : "1010000000000000010000000000000000000",
    "@Clr,MemPos" :"1110000000000000010000000000000000000",
    "@Clr,MemVal" :"0010000000000000010000000000000000000",
    "@Clr,Mem" :   "0110000000000000010000000000000000000",
    
    "@R1=R2" : "1001000001000000010000000000000000000",
    "@R1=R3" : "1001000000100000010000000000000000000",
    "@R1=MemPos":  "1001000001100000010000000000000000000",
    "@R1=MemVal":  "1001010000000000010000000000000000000",
    "@R1=Mem"   : "1001000100000010000000000000000000000",
    "@R2=R3" : "1101000000100000010000000000000000000",
    "@R2=R1" : "1011000000000000010000000000000000000",
    "@R2=MemVal": "1101010000000000010000000000000000000",
    "@R2=MemPos" :"1101000001100000010000000000000000000",
    "@R2=Mem"   : "1101000100000010000000000000000000000",
    "@R3=R2" :"1101000001000000010000000000000000000",
    "@R3=R1" :"1101000000000000010000000000000000000",
    "@R3=MemVal": "1011010000000000010000000000000000000",
    "@R3=MemPos" :"1011000001100000010000000000000000000",
    "@R3=Mem"   : "1011000100000010000000000000000000000",
    "@MemPos=R1" :"1101000000000000010000000000000000000",
    "@MemPos=R2" : "1111000001000000010000000000000000000",
    "@MemPos=R3" : "1111000000100000010000000000000000000",
    "@MemVal=R1" : "0011000000000000010000000000000000000",
    "@MemVal=R2" : "0011000001000000010000000000000000000",
    "@MemVal=R3" : "0011000000100000010000000000000000000",
    "@MemVal=MemPos" : "0011000001100000010000000000000000000",
    "@MemPos=MemVal":  "1111010000000000010000000000000000000",
    "@MemPos=Mem":     "1111000100000010000000000000000000000",
    "@MemVal=Mem":     "0011000100000010000000000000000000000",
    "@Mem=MemVal":     "0111010000000010000000000000000000000",
    "@MemInc"     :    "0110100010000010000001000000000000000",
    "@MemDec"     :    "0111000100000001000001000000000000000",
    
    
    "%JWZ":  "000000000000000000010",
    "%JWN":  "000000000000000000110",
    "%JWNOZ":"000000000000000000101",
    "%JWP":  "000000000000000000100",
    "%JWPOZ":"000000000000000000001",
    "%JWN0": "000000000000000000011",
    "%JMP":  "000000000000000000111",
    "\n" : "",
     " " : ""

        
    
    
    
    
    
    
}



class InstructionParser:
    
    def __init__(self, parsed_line):
        
        self.instruction_types = ["write", 'symbol', 'comment', 'jump','variable']
        self.raw_line = parsed_line
        
    def Instructiontype(self, line):
        if line[0][0] == '@':
            return self.instruction_types[0]
            
        elif (line[0][0] == "*" and line[0][1] == "*"):
            return self.instruction_types[2]
            
        elif line[0][0] == '#':
            
            return self.instruction_types[1]
        elif line[0][0] == '%':
            return self.instruction_types[3]
            
        elif line[0][0] == '!':
            return self.instruction_types[-1]
            
        else:
            
            return "INVALID"
        
            
            
    def whitespace(self):
        
        parsed_line = (self.raw_line).split(':')
        
        line_content = []
        for i in range(len(parsed_line)):
            e = list(parsed_line[i])
            for i in range(e.count(' ')):
                for i in e:
                    if i == " " or i == "\n":
                        e.remove(i)
            line_content.append(''.join(e))
            
        for i in range(len(line_content)):
        
            parsed_line[i] = line_content[i]
            
       
        
        
        
        
        
    
        return parsed_line
class InstructionDecoder:
    def __init__(self,decoded_message,y,line_number,i):
    
        self.instruction_types = decoded_message
        self.parts = y
        self.line_number = line_number
        self.i = i
        
    def decode(self):
        decoded_message = []
        if self.instruction_types == "write":
            if self.parts[1].isdigit():
                self.parts[1] = int(self.parts[1])
            
            for i in self.parts:
                
                if type(i) == type(1):
                    decoded_message.append(("{0:016b}".format(int(hex(i), 16))))
                
                elif i == '':
                    decoded_message.append('')
                
                elif type(i) !=(type(1)):
                    
                    if i[0] == '!':
                        decoded_message.append((variable_table[i])[::-1])
                        
                    elif i[0] == '#':
                        
                        decoded_message.append((symbol_table[i]))
                        
                    elif i in instruction_map:
                        decoded_message.append((instruction_map[i])[::-1])
                        
                    else:
                        
                        decoded_message = ["ERROR"]
                    
            
        elif self.instruction_types == "comment":
            decoded_message = None
            
        elif self.instruction_types == "jump":
            if self.parts[1].isdigit():
                self.parts[1] = int(self.parts[1])
               
            for i in self.parts:
                
                if type(i) == type(1):
                    decoded_message.append(("{0:016b}".format(int(hex(i), 16))))
                
                elif i == '':
                    decoded_message.append('')
                
                elif self.parts[0] == i and (type(i) !=(type(1))):
                    
                    
                    decoded_message.append((instruction_map[i])[::-1])
                elif self.parts[1] == i and (type(i) !=(type(1))):
                    decoded_message.append((symbol_table[i]))
            
        elif self.instruction_types == "symbol":
            
            
            
            cleaned_line = self.parts[0].split('\n')
            cleaned_line = ''.join(cleaned_line)
            cleaned_line = cleaned_line.split('#')
            self.parts[0] = '#'.join(cleaned_line)
            
            
            symbol_table[self.parts[0]] = self.line_number
        
            
            
            output_lines = symbol_table[self.parts[0]] + 1
            
            
            symbol_table[self.parts[0]] = ("{0:016b}".format(int(hex(output_lines), 16)))
            
            decoded_message=' '
            
        elif self.instruction_types == "variable":
             
            cleaned_line = self.parts[0].split('\n')
            cleaned_line = ''.join(cleaned_line)
            
            self.parts[0] = ''.join(cleaned_line)
            
            address = 16 + self.i
            variable_table[self.parts[0]] = address
            
            output_lines = variable_table[self.parts[0]]
            variable_table[self.parts[0]] = ("{0:016b}".format(int(hex(output_lines), 16)))[::-1]
            decoded_message=' '
             
        else:
            decoded_message = "dilavnI"
        if decoded_message != None:
            decoded_message = decoded_message[::-1]
        return decoded_message
        
        



def Generate_Binary(user_input):
    
    output_lines = []
    variable_count = 0
    
    for i in range(len(user_input)):  
                        
        
        y = InstructionParser(user_input[i]).whitespace()
        instruction_type = InstructionParser(0).Instructiontype(y)
        
       
        if instruction_type == "symbol":
           
            decoded_output = InstructionDecoder(instruction_type,y,i,variable_count).decode()
            
        
   
    for i in range(len(user_input)):  
        
                        
        
        y = InstructionParser(user_input[i]).whitespace()
        instruction_type = InstructionParser(0).Instructiontype(y)
        
        
        decoded_output = InstructionDecoder(instruction_type,y,i,variable_count).decode()
        
     
        
        
        if instruction_type == "variable":
            variable_count+=1
            
        if instruction_type == "symbol":
            
            output_lines.append('0000000000000000000000000000000000000')
        
        if not(decoded_output == None or decoded_output == "Invalid" or decoded_output == ' '):
            
           
                 
            output_lines.append(''.join(decoded_output))
            
    return output_lines





try:

    with  open(sys.argv[1], "r") as input_file:

        user_input = input_file.readlines()
        

except Exception:

    print("Invalid File")




try:
    output_lines = Generate_Binary(user_input)
    
except Exception:
    
    print("ERROR FOUND")

else:   

    try:

        output_file = open(sys.argv[2], "w")
    
        output_file.write("v2.0 raw\n")

    
        for i in output_lines:
            
            output_file.write(str(hex(int('0b'+i, 2))))
            output_file.write("\n")
            

            
        
        output_file.close()
        
        print("successfully executed")

    except Exception:

        print("Invalid File")



        
