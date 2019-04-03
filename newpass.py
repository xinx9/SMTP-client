import base64
import string
def AuthenticateEncode(Cin):
    salt = "447"
    Sin = Cin + salt
    Bin = Sin.encode("utf-8")
    Ein = base64.b64encode(Bin)
    return Ein

def AuthenticateDecode(Ein):
    salt = "447"
    Ein = Ein[2:].encode("utf-8")
    Sin = base64.b64decode(Ein)
    Sin = Sin.decode("utf-8")
    Cin = Sin[:len(Sin)-3]
    return Cin


encryption = AuthenticateEncode("someshit")
returncode = "330 " + str(encryption)
#print("\n\n" + returncode + "\n\n")

#e = returncode.split()[1]
#e = e[2:]

pw = returncode.split()[1]
print(pw[2:-1])
print("\nDecrypted password = " + AuthenticateDecode(pw))


