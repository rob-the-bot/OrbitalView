# OrbitalView

This program (`OrbitalView.py`) is used for recording at fast FPS with the FLIR grasshopper camera.
It

1. shows a live view @ 50FPS (since most monitors are still only 60Hz)
2. receives inputs from keyboard/UDP trigger to start/end recording
3. saves it @ 500FPS to a h264 encoded mp4 file with default playback @ 25FPS


## Usage

1. Launch `OrbitalView.py`
2. You can see the live view from the small GUI
3. Press `s` to start recording, `q` to quit (close the window from GUI doesn't do anything, sorry). The detailed info about encoding is shown in the terminal.
4. This program also supports receiving UDP trigger from any other programs to start/end recording. The port it uses for UDP is Port 6611 (line 53 in `OrbitalView.py`).

## Deployment (Windows)

1. Install [miniforge](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)
2. Create a conda environment, `conda create -n spinview`
3. Activate the environment, `conda activate spinview`
4. Use mamba to install numpy, opencv (for the liveview), pyav (for encoding)
`mamba install python=3.10 numpy opencv av`

5. `pip install simple_pyspin`
6. Download the Windows Python Spinnaker SDK 4.0.0.116 (December 14, 2023) [here](https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-download/spinnaker-sdk--download-files/)
7. Make sure to have latest NVIDIA GPU driver to enable GPU accelerated encoding


## Deployment (other platforms)
This program works in Mac and Linux. However, to enable GPU acceleration, you need to have ffmpeg compiled with `--enable-nvenc`, which is done for the binary released for Windows.
On other platforms, you need to compile ffmpeg from source to enable the `--enable-nvenc` flag to do GPU encoding.

On Mac, you might need to change from GPU encoding to CPU encoding (line 91-95).
CPU encoding with default preset usually isn't fast enough for 500FPS,
so you need to give more detailed parameters in line 95 (for example, use `ultrafast` preset and use sensible `crf` number).

## Known issues
From SpinView (the proper GUI), we can see the recording rate fluctuates around 500FPS.
This is possibly due to hardware limitation.

Basic benchmark was run using OrbitalView and the timestamp output was analysed.
The first 20 frames were recording at much lower FPS than 500.
For the subsequent frames, they have mean of 502 and standard deviation of 7.8 (tested on 2021-06-23).
