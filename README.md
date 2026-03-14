# Steffen's Scripts Repository

A collection of Ruby, Bash, and Python scripts for timelapse processing, video creation, motion camera footage processing, and system administration.

## Timelapse Processing

### `mkmov`
**Ruby script** - Creates videos from image sequences or video files using ffmpeg.

**Features:**
- Multiple codecs: x264, x265/hevc, vp9, libsvtav1, iphone, NVENC variants
- Two-pass encoding support (`-2` flag)
- Metadata embedding (title, author, year, copyright, description)
- Output filename format: `{FDATE}-{CODEC}-q{QUALITY}-b{BITRATE}-w{WIDTH}-fr{FRAMERATE}.mp4/webm`

**Usage:**
```bash
mkmov [options]

Options:
  -c CODEC, --codec=CODEC      Video codec (default: x264)
  -i INPUT, --input=INPUT      Input file (required for iphone codec)
  -w WIDTH, --width=WIDTH      Output width in pixels (default: 1920)
  -q QUALITY, --quality=QUALITY
                               CRF quality value (default: 20)
  -b BITRATE, --bitrate=BITRATE
                               Bitrate for ffmpeg (default: 5000k)
  -r FRAMERATE, --framerate=FRAMERATE
                               Framerate (default: 24)
  -p PRESET, --preset=PRESET   Encoding preset (default: medium)
  -l LOG_LEVEL, --log-level=LOG_LEVEL
                               ffmpeg log level (default: error)
  -t THREADS, --threads=THREADS
                               Number of threads (default: 4)
  -2, --twopass                Enable two-pass encoding
  -v, --verbose                Enable verbose output
  -d, --debug                  Enable debug mode
```

**Examples:**
```bash
mkmov -c x264
mkmov -c x264 -w 1280 -q 15 -p veryfast
mkmov -c vp9 -2 -r 30
mkmov -c hevc -w 1920 -q 23 -b 3500k
mkmov -c iphone -i video.MTS
```

### `process-tl-dir`
**Ruby script** - Annotates timelapse images with weather data (timestamp, temperature, wind).

**Usage:**
```bash
process-tl-dir [options] <directory>
```

**Workflow:**
1. Reads directory with JPGs
2. Extracts datetime from first and last images
3. Loads weather data from CSV for the timeframe
4. Annotates each image with EXIF timestamp, temperature, and wind
5. Outputs to `exif-*` directory

### `create-archive`
**Bash script** - Archives timelapse JPGs, annotates with weather, creates videos, and organizes by year/month.

**Usage:**
```bash
create-archive <timelapse-directory>
```

**Workflow:**
1. Runs `process-tl-dir` to annotate images with weather
2. Creates video using `mkmov -2 -c libsvtav1`
3. Organizes output to `/usb_drives/my_book/archive/movies/river/{YEAR}/{MONTH-Name}/`
4. Removes `exif-*` directory after processing

### `create-24h-movie`
**Ruby script** - Creates multiple video formats from a 24-hour timelapse directory.

**Usage:**
```bash
create-24h-movie [options] <timelapse-directory>

Options:
  -i INTERVAL, --interval=INTERVAL
                              Time interval between frames in seconds (default: 120)
  -r RATE, --rate=RATE      Frame rate (default: 30, use 25 for PAL)
  -v, --verbose             Enable verbose output
  -t TARGET_DIR, --target-dir=TARGET_DIR
                              Working directory (default: current directory)
```

**Workflow:**
1. Processes timelapse with `process-tl-dir`
2. Creates four video formats:
   - x264 (HD 1920x1080, 3500k bitrate)
   - vp9 (HD 1920x1080, 3500k bitrate, two-pass)
   - hevc (HD 1920x1080, 3500k bitrate, two-pass)
   - hevc HQ (default quality)
3. Moves videos to `~/movies/{month}/{x264,webm,x265,hq}/`

### `concat-daily-movies`
**Bash script** - Concatenates daily movies into a monthly film.

**Usage:**
```bash
concat-daily-movies
```

**Workflow:**
1. Detects file extension (.webm or .mp4)
2. Creates ffmpeg concat list (mylist.txt)
3. Concatenates to `MONTH-month.EXT`
4. Creates version with audio: `MONTH-sound.EXT`

### `monthly`
**Bash script** - Orchestrates monthly timelapse processing.

**Usage:**
```bash
monthly [-m month] [-y year]
```

**Workflow:**
1. Fetches weather data with `canweather`
2. Archives source images
3. Processes each day with `create-archive`
4. Concatenates daily movies (webm and x265)

## Motion Camera Footage Processing

### `process_footage`
**Bash script** - Processes motion camera footage for Callisto, Ganymede, and Phobos cameras.

**Usage:**
```bash
process_footage <camera> [-r]

Cameras: callisto | ganymede | phobos
Options:
  -r, --remove     Delete input directory after processing
```

**Workflow:**
1. Processes footage using Python script (`process_videos.py`)
2. Uploads to web server at `/seagate/www/rathaus/html/movies/`
3. Sends email notification with download link
4. Optionally removes input directory

## System Administration

### `update-all-machines`
**Bash script** - Updates multiple machines via SSH.

**Machines:** europa, io, ganymede, callisto, titan, phobos, deimos, pihole

**Usage:**
```bash
update-all-machines
```

### `check-wifi`
**Bash script** - Monitors WiFi connection and auto-reconnects if lost.

**Features:**
- Cron-triggered (every 5 minutes)
- Attempts 3 retries with 15s delay
- Auto-reboots if all retries fail
- Silent in non-interactive mode (cron)

### `check-disks`
**Bash script** - Disk health and status check.

## Build Scripts

### `build_ffmpeg_from_scratch`
**Bash script** - Compiles ffmpeg from source with full codec support.

**Components:**
- x264, x265, libvpx, SVT-AV1
- libdav1d, opus, fdk-aac
- VMAF (Netflix)
- CUDA/NVENC support
- Installs to `~/ffmpeg_build`

### `build_opencv_cuda`
**Bash script** - Builds OpenCV with CUDA/cuDNN support.

**Components:**
- OpenCV 4.13.0 with CUDA
- cuDNN, CUDA_FAST_MATH
- Python 3.12 with numpy
- Uses uv for Python environment

## Other Utilities

### `cpu-data`
**Bash script** - Shows CPU temperature and frequency per core.

### `geo-coord`
**Bash script** - Shows IP, coordinates, sunrise/sunset.

### `ip_to_host`
**Bash script** - IP to hostname resolution.

### `fill-gaps`
**Bash script** - Fills gaps in timelapse sequences.

### `jpg2mp4`
**Bash script** - Converts JPG images to MP4 video.

### `tl2mp4`
**Bash script** - Converts timelapse to MP4.

### `x264`
**Bash script** - x264 video encoding wrapper.

### `create-monthly-movie`
**Bash script** - Creates monthly movie from daily movies.

### `create-foto-index`
**Bash script** - Creates photo index.

### `insert-date`, `insert-exif`
**Bash scripts** - Date and EXIF insertion utilities.

### `take-picture`
**Bash script** - Captures images.

### `record`, `record-movie`
**Bash scripts** - Recording utilities.

### `network_monitor2`
**Bash script** - Network monitoring service for systemd.

**Features:**
- Monitors connection to TekSavvy gateway (mysavvy.teksavvy.com)
- Logs outages to `/var/log/network_monitor/`
- Alerts all terminals via `wall` for outages > 60 seconds
- Runs as a systemd service

**Usage:**
```bash
# Install service
sudo ln -sf /home/steffenr/scripts/network_monitor2.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable network_monitor2
sudo systemctl start network_monitor2

# View logs
sudo journalctl -u network_monitor2 -f
```

### `network_monitor_daily_report`
**Bash script** - Daily outage report with timeline.

**Usage:**
```bash
./network_monitor_daily_report.sh <email_address>
```

**Cron job:** Runs daily at 8 AM, emails summary if outages occurred.

### `network_report`, `network_speed`
**Bash scripts** - Network monitoring and reporting.

### `health-check`
**Bash script** - System health check.

### `day-or-night`
**Bash script** - Determines if it's day or night.

### `start-motion`, `daily-motion`, `daily-motion-all`, `hourly_motion`
**Bash scripts** - Motion camera control and monitoring.

### `install-all`, `install-on-all`
**Bash scripts** - Installation utilities.

### `send-ip-addr`
**Bash script** - Sends IP address.

### `termsize`
**Bash script** - Reports terminal size.

### `path`
**Bash script** - Path manipulation utility.

### `time_measure`
**Bash script** - Timing utility.

### `du-all`
**Bash script** - Disk usage reporting.

### `website-change-checker`
**Bash script** - Checks for website changes.

### `iss-streamer`
**Bash script** - ISS streamer utility.

### `yt-dlp`
**Bash script** - YouTube download wrapper.

### `comfyui`
**Bash script** - ComfyUI wrapper.

### `start_open-webui`
**Bash script** - Starts Open WebUI.

### `setup_vim`
**Bash script** - Vim setup utility.

### `concat-footage`
**Bash script** - Concatenates footage.

### `wrap-timelapse`
**Bash script** - Timelapse wrapping utility.

### `foto`
**Bash script** - Photo utility.

### `daily.job`, `hourly.job`
**Bash scripts** - Cron job wrappers.

### `vmaf`
**Bash script** - VMAF quality measurement.

### `ffmpeg`, `ffplay`, `ffprobe`
**Scripts** - FFmpeg tools.

## Ruby Scripts

### `create_pdf.rb`
**Ruby script** - PDF creation utility.

### `csv.rb`
**Ruby script** - CSV processing.

### `kutil.rb`, `kwhydro.rb`
**Ruby scripts** - Kitchener utility scripts.

## File Structure

```
/scripts/
├── mkmov                          # Video creation (Ruby)
├── process-tl-dir                 # Weather annotation (Ruby)
├── create-archive                 # Archive and create movies
├── create-24h-movie               # 24h timelapse processing (Ruby)
├── concat-daily-movies            # Monthly movie concatenation
├── monthly                        # Monthly processing orchestration
├── process_footage                # Motion camera footage processing
├── build_ffmpeg_from_scratch      # FFmpeg build script
├── build_opencv_cuda              # OpenCV CUDA build script
├── update-all-machines            # System updates via SSH
├── check-wifi                     # WiFi monitoring
├── check-disks                    # Disk health check
├── [other utilities]
└── README.md                      # This file
```

## Typical Workflows

### Monthly Timelapse Processing
```bash
monthly -m 03 -y 2026
# or for last month:
monthly
```

### Single Day Processing
```bash
create-archive /path/to/timelapse/jpgs
```

### 24-Hour Movie Creation
```bash
create-24h-movie 20240101
create-24h-movie 20240101 -v
```

### Camera Footage Processing
```bash
process_footage callisto --remove
process_footage ganymede --remove
process_footage phobos --remove
```

### Video Creation with mkmov
```bash
# Basic encoding
mkmov -c x264

# Custom quality and width
mkmov -c x264 -w 1280 -q 15 -p veryfast

# VP9 two-pass
mkmov -c vp9 -2 -r 30

# HEVC with custom bitrate
mkmov -c hevc -w 1920 -q 23 -b 3500k
```

## Notes

- Weather data comes from `/var/lib/weather/goc/weather-YYYY-MM.csv`
- Archive paths typically under `/usb_drives/my_book/archive/movies/`
- Many scripts use `/usr/local/share/fonts/Envy-Code-R-PR7/` fonts
- Scripts often use `nice` for CPU priority management
- Some scripts reference external paths (`/srv/timelapse/io`, `/seagate/www/`)
