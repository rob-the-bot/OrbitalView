This program (`OrbitalView.py`)


# Usage

1. Double click `startOrbitalView.bat` to start the program
2. You can see the live view from the small GUI
3. Press s to start recording, q to quit (close the window doesn't do anything). The detailed info about encoding is shown in the terminal.
4. This program also supports receiving UDP trigger from any other programs to start/end recording. The port it uses for UDP is Port 6611 (line 53 in `OrbitalView.py`).

# Deployment (Windows)
1. Install Miniconda, check the box with says `Add Miniconda3 to my PATH environment variable` (this enables activating environment from a bat file)
2. Create a conda environment with Python 3.7 (3.8 seems to break opencv in multiprocessing)
`conda create -n spinview python=3.7`

3. Use conda to install numpy with mkl (current numpy (1.19.4) with openblas in Windows >= 2004 is broken) and opencv
`conda install numpy opencv`

4. `pip install simple_pyspin ffmpeg-python`
5. Download ffmpeg binary and add its location to Windows Environment Path
6. Download the Spinnaker Python library (https://meta.box.lenovo.com/v/link/view/a1995795ffba47dbbe45771477319cc3). Make sure it's the correct Python version (Spinnake/Windows/Python/spinnaker_python-xxxxxx-cp37-cp37m-win_amd64.zip). Unzip and install the wheel file --- navigate to the direction and do `pip install the_whl_file_that_got_unzipped.whl`
7. Possibly need to update you NVIDIA GPU driver to enable GPU accelerated encoding


# Deployment (other platforms)
This program works in Mac and Linux. However, to enable GPU acceleration, you need to have ffmpeg compiled with `--enable-nvenc`, which is only default in Windows. So you need to compile ffmpeg with `--enable-nvenc` yourself in other platforms to utilise GPU.

It might been tricky to get nvenc to work in Mac. You might need to change from GPU encoding to CPU encoding (line 91-95). CPU encoding usually doesn't give you 500FPS so you need to give more detailed parameters in line 95 (for example, make use ultrafast preset and use sensible crf number).
