import os
import shutil
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

#-----------------------
# CONFIGURATION
#-----------------------

load_dotenv()

# Change your path to the downloads folder
DOWNLOADS_FOLDER = Path(os.getenv("DOWNLOAD_PATH"))


# CATEGORIES I USE MOST FREQUENTLY
CATEGORIES = {
    "DOCUMENTS": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
    "IMAGES": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"],
    "VIDEOS": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"],
    "MUSIC": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "ARCHIVES": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "INSTALLERS": [".exe", ".msi", ".apk", ".dmg"],
    "CODE": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".sql", ".json", ".xml"],
}

OTHERS = "OTHERS"


# SUBCATEGORIES
SUBCATEGORIES = {
    "WORD": [".doc", ".docx"],
    "EXCEL": [".xls", ".xlsx", ".csv"],
    "POWERPOINT": [".ppt", ".pptx"],
    "PDF": [".pdf"],
    "NOTES": [".txt"]
}


#----------------------
# FUNCTIONS
#----------------------

def create_folder(path: Path):
    """Create a folder if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    
def move_file(file: Path, target: Path):
    """Move a file to the target folder."""
    final_target = target / file.name
    counter = 1
    while target.exists():
        target = target / f"{file.stem}_{counter}{file.suffix}"
        counter += 1
    shutil.move(str(file), str(final_target))
    return final_target
        
def organize_files():
    """Classify and move files, returning statistics."""
    statistics = defaultdict(int)
    
    if not DOWNLOADS_FOLDER.exists():
        print(f"The specified path {DOWNLOADS_FOLDER} does not exist.")
        return None
    
    for file in DOWNLOADS_FOLDER.iterdir():
        if file.is_file():
            extension = file.suffix.lower()
            target_category = None
            
            for category, extensions in CATEGORIES.items():
                if extension in extensions:
                    target_category = category
                    break
            
            if not target_category:
                target_category = "OTHERS"
            
            target_folder = DOWNLOADS_FOLDER / target_category
            create_folder(target_folder)

            if target_category == "DOCUMENTS":
                subcategory = None
                for key, exts in SUBCATEGORIES.items():
                    if extension in exts:
                        subcategory = key
                        break
                if subcategory:
                    target_folder = target_folder / subcategory
                    create_folder(target_folder)

            move_file(file, target_folder)
            statistics[target_category] += 1
            
    return statistics

# ---------------------
# MAIN PROGRAM
# ---------------------
if __name__ == "__main__":
    print("Initializing file organization...")
    stats = organize_files()
    if stats is not None:
        print("Files organized succesfully")
        print("Summary:")
        total = sum(stats.values())
        for category, count in stats.items():
            print(f" - {category}: {count} files")
        print(f"    - Total moved: {total} files")
    else:
        print("No files were organized.")