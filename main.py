import yaml

class Secrets:
    def __init__(self, fh):
        self.fh = fh
        self.data = yaml.load(fh)


def main():
    s = Secrets(open('file_format.yaml'))
    print(s.data)

if __name__ == "__main__":
    main()
