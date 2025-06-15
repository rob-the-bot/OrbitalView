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

## Design choices

1. Currently the program defaults to use `nvenc` to ensure encoding speed (thus offloading the extensive encoding task from CPU to GPU), and `h264`codec for video playback compatibility.
However in the case of NVIDIA GPU isn't available or your `pyav` binary doesn't support it, [line 96-100](https://github.com/rob-the-bot/OrbitalView/blob/main/OrbitalView.py#L96) can be changed to use software encoding.
To ensure encoding speed >= 500 FPS, `preset` (defaults to `medium`) can be changed to `veryfast` or `ultrafast`.
2. `pyav` is currently used for encoding the frames.
With it, no serialization (converting each frame as strings) is needed to parse frame data from Python to a different ffmpeg process,
however this limits the types of hardware accelerated encoders being used&mdash;limited by the development status of `pyav` package.
If you'd like to use different types of hardware acceleration,
look at [previous version of the code](https://github.com/rob-the-bot/OrbitalView/commit/366ff4804132375f8ad5d41ced7a28b9c82615c2) where `ffmpeg-python` was used.
With this, any codecs supported by your `ffmpeg` binary are also supported by this Python program.
{`h264_qsv`, `hevc_qsv`, AMD encoders} were tested to be working on Windows.
Note that this shouldn't be needed most of the time, if software encoding can work for you as mentioned in step 1.

## Deployment

### Windows

1. Install [miniforge](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)
2. Create a conda environment, `conda create -n spinview`
3. Activate the environment, `conda activate spinview`
4. Use mamba to install numpy, opencv (for the liveview), pyav (for encoding)
`mamba install python=3.10 numpy opencv av`

5. `pip install simple_pyspin`
6. Download the Windows Python Spinnaker SDK 4.0.0.116 (December 14, 2023) [here](https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-download/spinnaker-sdk--download-files/).
Download the one for Python 3.10.
Unzip and install the wheel (whl) file&mdash;navigate to the directory, and do `pip install the_whl_file_that_got_unzipped.whl`
8. Make sure to have latest NVIDIA GPU driver to enable GPU accelerated encoding
9. Check that `h264_nvenc` is supported by the installed `pyav`, do `assert "h264_nvenc" in av.codecs_available` as suggested [here](https://github.com/PyAV-Org/PyAV/issues/596#issuecomment-755307214) in Python.

### Linux

Check step 9 above to see if `h264_nvenc` is supported.

### Mac

On Mac, you will have to change from GPU encoding to CPU encoding (line 91-95), or other types of hardware accelerated encoders (untested).
CPU encoding with default preset usually isn't fast enough for 500FPS,
so you need to give more detailed parameters in line 95 (for example, use `ultrafast` preset and use sensible `crf` number).

## Known issues
From SpinView (the proper GUI), we can see the recording rate fluctuates around 500FPS.
This is possibly due to hardware limitation to ensure a super stable FPS.

Basic benchmark was run using OrbitalView and the timestamp output was analysed.
The first 20 frames were recording at much lower FPS than 500.
For the subsequent frames, they have mean of 502 and standard deviation of 7.8 (tested on 2021-06-23).
