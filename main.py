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
import shutil
import time
import zipfile
from colorama import init
import watchdog.events
import watchdog.observers
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

    CLEAR_CONSOLE_UI = "bedrock_packer.clear_console"


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


class Extractor:
    def __init__(self) -> None:
        pass

    def extractAll(self, base_path: str, file: str):
        if not self.__isZip(file):
            raise Exception("File is not a zip file")

        # zip file
        file_path = os.path.join(base_path, file)
        abs_file_path = os.path.abspath(file_path)
        # extracted folder (will be same folder as zip file)
        extracted_folder_path = os.path.join(
            base_path, os.path.splitext(os.path.basename(file))[0]
        )
        abs_extracted_folder_path = os.path.abspath(extracted_folder_path)

        try:
            with zipfile.ZipFile(abs_file_path, "r") as zip_ref:
                zip_ref.extractall(abs_extracted_folder_path)

        except Exception as e:
            raise e

    def __isZip(self, file: str) -> bool:
        return file.endswith(".zip")


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
        pub.subscribe(
            self.run_clear_console_ui, EventType.CLEAR_CONSOLE_UI.value
        )

    def run_clear_console_ui(self):
        self.__clear_console()


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
        self.__extractor = Extractor()

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

        except KeyboardInterrupt:
            self.handle_exit()

    def handle_option(self, option: int):
        if option == options[0].value:
            self.handle_watch()

        elif option == options[1].value:
            self.handle_target_directory()

        elif option == options[2].value:
            self.handle_unzip_files()

        elif option == options[3].value:
            self.handle_help()

        elif option == options[4].value:
            self.handle_exit()

        else:
            print("Unknown option")
            exit(-1)

    def handle_watch(self):
        event_handler = watchdog.events.FileSystemEventHandler()
        event_handler.on_created = self.on_created
        event_handler.on_modified = self.on_modified
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, path=self.__mc_path, recursive=True)

        observer.start()
        print("Watching for changes..., Press Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

    def on_created(self, event):
        print(f"File created: {event.src_path}")
        # copy file to target directory
        shutil.copy(event.src_path, self.path)

    def on_modified(self, event):
        print(f"File modified: {event.src_path}")
        # copy file to target directory
        shutil.copy(event.src_path, self.path)

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
            elif self.path != target_dir:
                self.path = target_dir
                pub.sendMessage(
                    EventType.SUCCESS_SET_TARGET_DIRECTORY_UI.value,
                    target_dir=target_dir,
                )

            else:
                pub.sendMessage(
                    EventType.ERROR_CREATE_TARGET_DIRECTORY_UI.value,
                    error="Target directory already exists",
                )
        except Exception as e:
            pub.sendMessage(EventType.ERROR_CREATE_TARGET_DIRECTORY_UI.value, error=e)
            exit(-1)

    def handle_unzip_files(self):
        for file in os.listdir(self.path):
            try:
                self.__extractor.extractAll(self.path, file)
                print(f"File {file} sucessfully extracted!")
            except Exception as e:
                print(f"Error while extracting file {file}, Error:{e}")

    def handle_help(self):
        pass

    def handle_exit(self):
        pub.sendMessage(EventType.EXIT_UI.value)
        exit(0)


if __name__ == "__main__":
    app = BedrockPackerApp(".")
    app.run()
