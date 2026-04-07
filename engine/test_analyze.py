from engine.analyze import DriftAnalyzer

def main():
    analyzer = DriftAnalyzer()
    result = analyzer.analyze("your text here")
    print(result)

if __name__ == "__main__":
    main()
