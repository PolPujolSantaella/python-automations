# Automatic Cleaning of Downloads Folder

This python script organize automatically all your files in your download folder in categories and subcategories, depends on type. Also, is prepared to be executed automatically in Windows using Task Scheduler.

## Main Categories

- **DOCUMENTS**: `.pdf`, `.doc`, `.docx`, `.txt`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv`  
  - Subcategorías: `WORD`, `EXCEL`, `POWERPOINT`, `PDF`, `NOTES`  
- **IMAGES**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.svg`, `.webp`  
- **VIDEOS**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.wmv`  
- **MUSIC**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`  
- **ARCHIVES**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`  
- **INSTALLERS**: `.exe`, `.msi`, `.apk`, `.dmg`  
- **CODE**: `.py`, `.js`, `.html`, `.css`, `.java`, `.c`, `.cpp`, `.sql`, `.json`, `.xml`  
- **OTHERS**: Files that doesn't match previous categories

## Configuration 
1. Clone or download the repository.
2. Create a file `.env` in the root path of the project with the path of your download folder:

```env
DOWNLOAD_PATH=<your_path>
```

3. Install necesary dependencies

```bash
pip install python-dotenv
```

## Guide
Execute the script from your terminal:

```bash
python clean_downloads.py
```

## Automate in Windows
To automate the execution of the script every day at 9 a.m:

1. Open Task Scheduler from Windows
2. Create a Basic Task:
    - Trigger: Daily at 9:00 AM
    - Action: Execute program
        - Program/Script: Path of your python.exe: `C:\Users\<your_user>\AppData\Local\Programs\Python\Python311\python.exe`
        - Arguments: `"C:\Users\<your_user>\Scripts\organize_downloads.py"`
        - Initialize in: `C:\Users\<your_user>\Scripts`
3. Save and test using Execute button.

### And then, Your Download Folder will be Cleaned ✨


