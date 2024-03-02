import os

def clean_directory():
    for filename in os.listdir("../outputs/training_data"):
        file_path = os.path.join("../outputs/training_data", filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"Ignored (not a file): {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    for filename in os.listdir("../outputs/"):
        file_path = os.path.join("../outputs/", filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"Ignored (not a file): {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

clean_directory()