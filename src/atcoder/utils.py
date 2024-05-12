import sys



def force_input(prompt: str) -> str:
    x = input(prompt)
    while True:
        try:
            if x:
                return x
            x = input(prompt)
        except KeyboardInterrupt:
            print("Interrupted. Exiting...")
            sys.exit(1)
        except EOFError:
            print("EOF. Exiting...")
            sys.exit(1)



