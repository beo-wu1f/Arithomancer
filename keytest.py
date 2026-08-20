import readchar

print("Press keys. Press ENTER to stop.")

while True:

    key = readchar.readkey()

    if key == readchar.key.ENTER:
        break

    print(f"You pressed: {repr(key)}")

