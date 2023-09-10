import tarfile
import sys
import cmd
import os


class MyCmd(cmd.Cmd):
    intro = "VShell 2023 Mirea"
    prompt = "user: /$ "
    file = None
    current_directory = ""
    root_directory = ""

    def __init__(self):
        super().__init__()
        filename = sys.argv[1]
        if os.path.exists(filename) and not os.path.isdir(filename) and tarfile.is_tarfile(filename):
            self.file = tarfile.TarFile(filename)
            self.root_directory = self.file.getnames()[0]
            self.current_directory = self.root_directory
        else:
            print("Неподдерживаемый формат файла!")
            sys.exit(0)

    def do_exit(self, arg):
        if self.file:
            self.file.close()
            self.file = None
        return True

    def do_ls(self, arg):
        if arg == "":
            full_path = self.current_directory
        else:
            full_path = self.get_fullpath(arg)
        matches = []
        for elem in self.file.getnames():
            if full_path in elem and full_path != elem:
                matches.append(elem.replace(full_path, "").split("/")[1])
        matches = list(set(matches))
        print(" ".join([elem.split("/")[0] for elem in matches]))

    def do_cd(self, arg):
        full_path = self.get_fullpath(arg)

        if full_path in self.file.getnames():
            self.current_directory = full_path
            self.prompt = f"user: {full_path.replace('root', '/').replace('//', '/')}$ "
        else:
            print(f"vshell: cd: {full_path}: Нет такого файла или каталога")

    def do_pwd(self, arg):
        print(self.current_directory.replace('root', '/').replace('//', '/'))

    def do_cat(self, arg):
        paths = [self.get_fullpath(elem) for elem in arg.split()]
        content = ""
        for path in paths:
            if path in self.file.getnames():
                try:
                    read_file = self.file.extractfile(path)
                    content += read_file.read().decode()
                    read_file.close()
                except:
                    print("vshell: cat: Это каталог")
            else:
                print(f"vshell: cat: {path}: Нет такого файла или каталога")

    def get_fullpath(self, arg):
        if arg[0:2] == "..":
            full_path = arg.replace("..", "/".join(self.current_directory.split('/')[:-1]))
        elif arg[0] == "/":
            full_path = self.root_directory + arg
        else:
            full_path = self.current_directory + "/" + arg

        return full_path


if __name__ == '__main__':
    MyCmd().cmdloop()
