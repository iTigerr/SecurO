import random

def generate_password():
  chars = list("qwertyuiopasdfghjklzxcvbnm1234567890")
  
  length = random.randint(10,15)
  password = ""
  for i in range(length):
    char = random.choice(chars)
    password += char if random.randint(0,1) else char.upper()
  return password