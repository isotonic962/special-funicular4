from engine.memory import MemoryWindow

def main():
    m = MemoryWindow(size=3)
    m.add("one")
    m.add("two")
    m.add("three")
    m.add("four")

    print("Memory contents:", m.get_texts())

if __name__ == "__main__":
    main()
