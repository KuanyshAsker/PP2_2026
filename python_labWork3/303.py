to_digit = {"ONE":"1",
            "TWO":"2",
            "THR":"3",
            "FOU":"4",
            "FIV":"5",
            "SIX":"6",
            "SEV":"7",
            "EIG":"8",
            "NIN":"9",
            "ZER":"0"}
to_code = {"0":"ZER",
            "1":"ONE",
            "2":"TWO",
            "3":"THR",
            "4":"FOU",
            "5":"FIV",
            "6":"SIX",
            "7":"SEV",
            "8":"EIG",
            "9":"NIN"}
def decode(t):
    digits = []
    for i in range(0, len(t), 3):
        digits.append(to_digit[t[i:i+3]]) 
    return int("".join(digits))
def encode(x):
    if x == 0:
        return "ZER"
    s = str(x)
    out = []
    for ch in s:
        out.append(to_code[ch])
    return "".join(out)
s = input()
op_pos = -1
op = ""
for i, ch in enumerate(s):
    if ch in "+-*–−": #there are three types of minuses, so that's why I added remaining two of them
        op_pos = i
        op = ch
        break
a_str = s[:op_pos]
b_str = s[op_pos+1:]
a = decode(a_str)
b = decode(b_str)
if op == "+":
    res = a + b
elif op == "*" :
    res = a * b
else:
    res = a - b
print(encode(res))
