from enum import Enum, auto
import time
import watchdog
from pubsub import pub

class EventType(Enum):
    MAIN_UI = "bedrock_packer.main"
    EXIT_UI = "bedrock_packer.exit"

class BedrockPackerUI:
    def __init__(self) -> None:
        pub.subscribe(self.run_main_ui, EventType.MAIN_UI.value)
        pub.subscribe(self.run_exit_ui, EventType.EXIT_UI.value)

    def run_main_ui(self):
        print("Running file BedrockPacker application..")
        print("Pick one option below:")
        print("----------------------")
        print("1- Start Watching")
        print("2- Set target directory (where resource packs will be copied)")
        print("3- Unzip all (unzips all of copied packs)")
        print("4- Help command")
        print("6- Exit")

    def run_exit_ui(self):
        print("Exiting file BedrockPacker application..")
        time.sleep(1)
        print("BedrockPacker successfully exited!")


class BedrockPackerApp:
    def __init__(self, path):
        self.path = path
        self.__ui = BedrockPackerUI()

    def run(self):
        pub.sendMessage(EventType.MAIN_UI.value)
        try:
            while True:
                option = input("Your option:\n")
                self.handle_option(int(option))
                pass
        except KeyboardInterrupt:
            self.handle_exit()

    def handle_option(self, option: int):
        if option == 1:
            self.handle_watch()
            pass
        elif option == 2:
            self.handle_target_directory()
            pass
        elif option == 3:
            self.handle_unzip_files()

        elif option == 4:
            self.handle_help()
            pass
        elif option == 6:
            self.handle_exit()
            pass
        else:
            print("Unknown option")
            exit(-1)

    def handle_watch(self):
        pass

    def handle_target_directory(self):

        print("Type your target directory which resource packs will be saved:")

        target_dir = input()

        print(f"Successfully changed target directory to {target_dir}")

        self.path = target_dir
        pass

    def handle_unzip_files(self):
        pass

    def handle_help(self):
        pass

    def handle_exit(self):
        pub.sendMessage(EventType.EXIT_UI.value)
        exit(0)


if __name__ == "__main__":
    app = BedrockPackerApp(".")
    app.run()
