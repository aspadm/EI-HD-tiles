# How to build Windows version

1. Download Python 3.6+ embeddable x64 and extract it to "python" directory

2. Use [this][1] instruction to install pip tool into it

3. Install dependencies: `python\\python.exe -m pip install numpy==1.19.3 pyvips pillow pyyaml`

4. Download libvips and place dll files in "python" dir

5. Put `.py` file into separate `src` directory

6. Create corresponding `.bat` files with the content (replace `source_file` with the name of script):

    ```bat
    @echo off
    cd /D %~dp0
    set DONT_CHANGE_CWD=1
    python\python.exe src\source_file.py %*
    ```

[1]: https://www.christhoung.com/2018/07/15/embedded-python-windows/
