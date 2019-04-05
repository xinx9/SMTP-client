import base64
def AuthenticateDecode(Ein):
    salt = "447"
    Ein = Ein[2:-1]
    Sin = base64.b64decode(Ein)
    Sin = Sin.decode("utf-8")
    Cin = Sin[:len(Sin)-3]
    return Cin

f = open("db/.user-pass", "r")
x = f.read()

y = x.split()
for a in y:
	u = a.split(":")
	for h in u:
		print(AuthenticateDecode(h))
