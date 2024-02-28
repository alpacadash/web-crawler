from pathlib import Path
import sys

class TokenList:
    def __init__(self):
        self.tokens = []
        self.max = ('',0)
        self.count = 1
#The runtime complexity of split_by_non_alpha is O(n^4) because increase_count() which has O(n) complexity is nested with
#two nested for loops and is in "if" which has search_content which has O(n) complexity as its condition. Therefore,
#O(n)*O(n)*O(n)*O(n) = O(n^4)
    def tokenize(self, path):
        file = None
        try:
            file =open(path, mode='r', encoding='utf8')
            for line in file:
                print('Tokenizing...' + str(self.count))
                line = line.strip()
                arr = self.split_by_non_alpha(line)
                if len(arr) > self.max[1]:
                    self.max = (line, len(arr))
                for content in arr:
                    if(self.search_content(content.lower())):
                        self.increase_count(content.lower())
                    else:
                        self.tokens.append((content.lower(), 1))
                self.count += 1

        except(FileNotFoundError,IOError):
            return 'Invalid File'
            exit()

        finally:
            file.close()
#The runtime complexity of split_by_non_alpha is O(n) because this function iterates through each character in the string once
    def split_by_non_alpha(self, string):
        list = []
        temp = ''
        for ch in string:
            if ch.isalpha() or ch.isdigit():
                temp += ch
            else:
                if temp:
                    list.append(temp)
                    temp = ''
        if temp:
            list.append(temp)
        return list
#The runtime complexity of search_content is O(n) because this function iterates through each token in the list of tokens
    def search_content(self, content):
        for name, _ in self.tokens:
            if name == content:
                return True
        return False
#The runtime complexity of increase_count is O(n) because this function iterates through the list to find the token with matching name
    def increase_count(self, content):
        for i, (name, number) in enumerate(self.tokens):
            if name == content:
                self.tokens[i] = (name, number+1)
                break
#The runtime complexity of sort is O(n) because the "sorted()" function has a time complexity of O(n log n)
    def sort(self):
        self.tokens = sorted(self.tokens, key=lambda x: (-x[1], x[0]))
#The runtime complexity of sort is O(n) because the "sort()" has O(n) complexity and so does the for loop. Therefore O(n) + O(n) = O(n)
    def print(self):
        self.sort()
        for content, count in self.tokens:
            print(f"{content}\t{count}")

    def write_to_file(self, filename, header, contents):
        f = open(filename, mode='w', encoding='utf8')
        f.write("The longest page: ")
        f.write(self.max[0])
        f.write("\n")
        f.write(header)
        if type(contents) is list:
            for item in contents:
                f.write(str(item) + "\n")
        elif type(contents) is tuple:
            f.write(str(contents[0]) + " " + str(contents[1]) + "\n")
        else:
            for key,value in contents.items():
                f.write(str(key) + ": " + str(value) + "\n")
        f.close()

if __name__ == '__main__':
    path = Path(sys.argv[1])
    #path2 = Path(sys.argv[2])
    run = TokenList()
    run.tokenize(path)
    #run.tokenize(path2)
    run.print()
    run.write_to_file("commonWords.txt", "CommandWords:\n\n", run.tokens)
