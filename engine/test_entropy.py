from engine.entropy import EntropyCalculator

def main():
    calc = EntropyCalculator()

    low = "hello hello hello hello"
    high = "chaos entropy drift engine unstable variance"

    print("Low entropy:", calc.analyze(low))
    print("High entropy:", calc.analyze(high))

if __name__ == "__main__":
    main()
