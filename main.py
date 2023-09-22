import tarfile
import sys
import cmd
import os
import argparse


class MyCmd(cmd.Cmd):
    intro = "VShell 2023 Mirea\n\u00A9Все права не защищены\n================"
    prompt = "\033[1m\033[32muser@USER_PC: /$ \033[0m"
    file = None
    current_directory = ""
    root_directory = ""

    def __init__(self):
        super().__init__()
        parser = argparse.ArgumentParser()
        parser.add_argument("filename")
        parser.add_argument("--script")
        args = parser.parse_args()
        filename = args.filename
        if os.path.exists(filename) and not os.path.isdir(filename) and tarfile.is_tarfile(filename):
            self.file = tarfile.TarFile(filename)
            self.root_directory = self.file.getnames()[0]
            self.current_directory = self.root_directory
        else:
            print("\033[1m\033[31mНеподдерживаемый формат файла!")
            sys.exit(0)

        if args.script is not None:
            sys.stdin = open("script", "r")

    def do_EOF(self, args):
        sys.stdin.close()
        sys.stdin = sys.__stdin__

    def do_exit(self, arg):
        if sys.stdin != sys.__stdin__:
            print(f"exit {arg}")
        if "--help" in arg:
            print("""
                  exit: exit
                        Выполняет выход из эмулятора vshell.
                  """)
        else:
            if self.file:
                self.file.close()
                self.file = None
            return True

    def do_ls(self, arg):
        if sys.stdin != sys.__stdin__:
            print(f"ls {arg}")
        if "--help" in arg:
            print("""
                  ls: ls [ФАЙЛ]
                        Выводит информацию о файлах (по умолчанию в текущем каталоге).
                  """)
        else:
            if arg == "":
                full_path = self.current_directory
            else:
                full_path = self.get_fullpath(arg)
            matches = []
            for elem in self.file.getnames():
                if full_path in elem and full_path != elem:
                    matches.append(elem.replace(full_path, "").split("/")[1])
            matches = list(set(matches))
            for match in matches:
                read_file = self.file.extractfile(f"{full_path}/{match}")
                if read_file is None:
                    print(f"\033[1m\033[34m{match}", end=" ")
                else:
                    print(f"\033[1m\033[33m{match}", end=" ")
                    read_file.close()
            print()

    def do_cd(self, arg):
        if sys.stdin != sys.__stdin__:
            print(f"cd {arg}")
        if "--help" in arg:
            print("""
                  cd: cd [ФАЙЛ]
                        Меняет текущую директорию (по умолчанию, на текущую директорию).
                  """)
        else:
            full_path = self.get_fullpath(arg)

            if full_path in self.file.getnames():
                if self.file.extractfile(full_path) is None:
                    self.current_directory = full_path
                    self.prompt = f"\033[1m\033[32muser: {full_path.replace('root', '/').replace('//', '/')}$ \033[0m"
                else:
                    print(f"vshell: cd: {full_path}: Это не каталог")
            else:
                print(f"vshell: cd: {full_path}: Нет такого файла или каталога")

    def do_pwd(self, arg):
        if sys.stdin != sys.__stdin__:
            print(f"pwd {arg}")
        if "--help" in arg:
            print("""
                  pwd: pwd
                        Печатает текущую директорию.
                  """)
        else:
            print(self.current_directory.replace('root', '/').replace('//', '/'))

    def do_cat(self, arg):
        if sys.stdin != sys.__stdin__:
            print(f"cat {arg}")
        if "--help" in arg:
            print("""
                  cat: cat [ФАЙЛ(-ы)]
                        Печатает слияние ФАЙЛ(-ов) в стандартный вывод.
                  """)
        else:
            paths = [self.get_fullpath(elem) for elem in arg.split()]
            content = ""
            for path in paths:
                if path in self.file.getnames():
                    read_file = self.file.extractfile(path)
                    if read_file is not None:
                        content += read_file.read().decode()
                        read_file.close()
                    else:
                        print("vshell: cat: Это каталог")
                else:
                    print(f"vshell: cat: {path}: Нет такого файла или каталога")
            print(content.rstrip())

    def get_fullpath(self, arg):
        if arg[0:2] == "..":
            full_path = arg.replace("..", "/".join(self.current_directory.split('/')[:-1]))
        elif arg[0] == "/":
            if arg == "/":
                full_path = self.root_directory
            else:
                full_path = self.root_directory + arg
        else:
            full_path = self.current_directory + "/" + arg

        return full_path


if __name__ == '__main__':
    MyCmd().cmdloop()
