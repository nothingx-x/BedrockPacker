###############################
#                            #
#        بسمه تعالی         #
#                            #
##############################

# Bedrock Packer is a CMD Application
# which copies minecraft bedrock edition "server downloaded resource packs"
# read instruction about how to build this software and furthure more contribute to it on wiki/contribute.md file.
# 02/06/25

from enum import Enum, auto
import os
from pathlib import Path
import time
import zipfile
from colorama import init
import watchdog
from pubsub import pub


class EventType(Enum):
    """
    EventTypes. retrieve value by using .value
    """

    MAIN_UI = "bedrock_packer.main"
    EXIT_UI = "bedrock_packer.exit"
    WATCH_UI = "bedrock_packer.watch"
    SET_TARGET_DIRECTORY_UI = "bedrock_packer.set_target_directory"
    SUCCESS_SET_TARGET_DIRECTORY_UI = "bedrock_packer.success_set_target_directory"
    SUCCESS_CREATE_TARGET_DIRECTORY_UI = (
        "bedrock_packer.success_create_target_directory"
    )
    ERROR_CREATE_TARGET_DIRECTORY_UI = "bedrock_packer.error_create_target_directory"
    UNZIP_FILES_UI = "bedrock_packer.unzip_files"
    SUCCESS_UNZIP_FILES_UI = "bedrock_packer.success_unzip_files"
    HELP_UI = "bedrock_packer.help"


class Option:
    """
    Application Options:
    @param value: int - option number
    @param description: str - brief description about option
    """

    def __init__(self, value: int, description: str):
        self.value = value
        self.description = description

    def __str__(self):
        return f"{self.value} - {self.description}"


# Default startup options array
options = [
    Option(1, "Start Watching"),
    Option(2, "Set target directory (where resource packs will be copied)"),
    Option(3, "Unzip all (unzips all of copied packs)"),
    Option(4, "Help command"),
    Option(6, "Exit"),
]


class BedrockPackerUI:
    """
    BedrockPackerUI initializes application ui handling using events
    """

    def __init__(self) -> None:
        init()

        # Subscribing to different ui events
        pub.subscribe(self.run_main_ui, EventType.MAIN_UI.value)
        pub.subscribe(self.run_exit_ui, EventType.EXIT_UI.value)
        pub.subscribe(
            self.run_set_target_directory_ui, EventType.SET_TARGET_DIRECTORY_UI.value
        )
        pub.subscribe(
            self.run_success_set_target_directory_ui,
            EventType.SUCCESS_SET_TARGET_DIRECTORY_UI.value,
        )
        pub.subscribe(
            self.run_success_create_target_directory_ui,
            EventType.SUCCESS_CREATE_TARGET_DIRECTORY_UI.value,
        )
        pub.subscribe(
            self.run_error_create_target_directory_ui,
            EventType.ERROR_CREATE_TARGET_DIRECTORY_UI.value,
        )

    def run_main_ui(self):
        self.__clear_console()
        print("Running file BedrockPacker application..")
        print("Pick one option below:")
        print("----------------------")
        for option in options:
            print(option)

    def run_exit_ui(self):
        print("Exiting file BedrockPacker application..")
        time.sleep(1)
        print("BedrockPacker successfully exited!")

    def run_set_target_directory_ui(self):
        print("Setting target directory..")
        print("Type your target directory which resource packs will be saved:")

    def run_success_set_target_directory_ui(self, target_dir: str = ""):
        print(f"Successfully changed target directory to {target_dir}")

    def run_success_create_target_directory_ui(self, target_dir: str = ""):
        print(f"Successfully created target directory {target_dir}")

    def run_error_create_target_directory_ui(self, error: str = ""):
        print(f"Error: {error}")

    def __clear_console(self):
        """
        Clears console using colorama library.
        crossplatform compatible
        """
        print("\033[2J\033[H", end="")


class BedrockPackerApp:
    def __init__(self, path):
        self.path = path
        self.__ui = BedrockPackerUI()
        self.__folder_name = "BedrockPacker"
        self.__mc_path = os.path.join(
            Path.home(),
            "AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalCache/minecraftpe/ResPackDownloads",
        )

    def run(self):
        """
        Runs Application and listen for different inputs
        """
        try:
            while True:
                time.sleep(1)
                pub.sendMessage(EventType.MAIN_UI.value)
                option = input("Your option:\n")
                self.handle_option(int(option))
                pass
        except KeyboardInterrupt:
            self.handle_exit()

    def handle_option(self, option: int):
        if option == options[0].value:
            self.handle_watch()
            pass
        elif option == options[1].value:
            self.handle_target_directory()
            pass
        elif option == options[2].value:
            self.handle_unzip_files()

        elif option == options[3].value:
            self.handle_help()
            pass
        elif option == options[4].value:
            self.handle_exit()
            pass
        else:
            print("Unknown option")
            exit(-1)

    def handle_watch(self):
        pass

    def handle_target_directory(self):
        """
        Create directory based on input if not exists.

        Change target directory based on input.

        @error: if directory exist or it's same as previous entered directory throw error
        """
        pub.sendMessage(EventType.SET_TARGET_DIRECTORY_UI.value)  # prompt input
        target_dir = input().strip()  # remove whitespaces

        target_dir = os.path.join(target_dir, self.__folder_name)
        try:
            if not os.path.exists(target_dir) and self.path != target_dir:
                self.path = target_dir
                pub.sendMessage(
                    EventType.SUCCESS_SET_TARGET_DIRECTORY_UI.value,
                    target_dir=target_dir,
                )
                os.makedirs(target_dir)
                pub.sendMessage(
                    EventType.SUCCESS_CREATE_TARGET_DIRECTORY_UI.value,
                    target_dir=target_dir,
                )

            elif os.path.isfile(target_dir):
                pub.sendMessage(
                    EventType.ERROR_CREATE_TARGET_DIRECTORY_UI.value,
                    error="Target directory is a file",
                )
            else:
                pub.sendMessage(
                    EventType.ERROR_CREATE_TARGET_DIRECTORY_UI.value,
                    error="Target directory already exists",
                )
        except Exception as e:
            pub.sendMessage(EventType.ERROR_CREATE_TARGET_DIRECTORY_UI.value, error=e)
            exit(-1)
        pass

    def handle_unzip_files(self):
        for file in os.listdir(self.path):
            if not file.endswith(".zip"):
                continue

            # zip file
            file_path = os.path.join(self.path, file)
            abs_file_path = os.path.abspath(file_path)
            # extracted folder (will be same folder as zip file)
            extracted_folder_path = os.path.join(
                self.path, os.path.splitext(os.path.basename(file))[0]
            )
            abs_extracted_folder_path = os.path.abspath(extracted_folder_path)

            try:
                with zipfile.ZipFile(abs_file_path, "r") as zip_ref:
                    zip_ref.extractall(abs_extracted_folder_path)

                print("Successfully unzipped files")
            except Exception as e:
                print(f"Error: {e}")
                exit(-1)
                

    def handle_help(self):
        pass

    def handle_exit(self):
        pub.sendMessage(EventType.EXIT_UI.value)
        exit(0)


if __name__ == "__main__":
    app = BedrockPackerApp(".")
    app.run()
