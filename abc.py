import readline

def rlinput(prompt, prefill='joker'):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return raw_input(prompt)
   finally:
      readline.set_startup_hook()


rlinput('hello: ')

