# Steffen's Scripts Repository

A collection of shell scripts and utilities for various tasks including timelapse processing, video creation, system maintenance, and monitoring.

## Timelapse Processing Scripts

### `monthly.py`
**Python script** for processing monthly timelapse data.

**Workflow:**
```
main()
  │
  ├→ setup_config() [config setup]
  │
  ├→ load_weather_data() [weather CSV → dict]
  │
  ├→ For each day_dir:
  │     │
  │     ├→ process_daily_directory()
  │     │     │
  │     │     ├→ archive_source_images()
  │     │     │       └→ tar pipe copy
  │     │     │
  │     │     ├→ get_weather_for_timestamp()
  │     │     │       └→ match EXIF timestamp to weather data
  │     │     │
  │     │     ├→ annotate_image()
  │     │     │     │
  │     │     │     ├→ _get_contrasting_text_color()
  │     │     │     │       └→ sample background, return contrasting color
  │     │     │     │
  │     │     │     └→ PIL annotate with timestamp, temp, wind
  │     │     │
  │     │     └→ ffmpeg timelapse creation
  │     │
  │     └→ process_daily_directory() [next day]
  │
  └→ create_monthly_video()
        └→ ffmpeg concat all daily MP4s
```

### `create-archive`
**Bash script** - archives timelapse JPGs and creates movies.

**Workflow:**
```
create-archive <dir>
  │
  ├→ process-tl-dir [annotate images with weather]
  │
  ├→ mkmov [create video]
  │
  └→ mv *.mp4 to archive structure
```

### `process-tl-dir`
**Ruby script** - annotates timelapse images with weather data.

**Workflow:**
```
process-tl-dir
  │
  ├→ load Weather data from CSV
  ├→ For each JPG:
  │     │
  │     ├→ exif_time() [extract timestamp]
  │     ├→ Weather.temperature()
  │     ├→ Weather.wind()
  │     └→ convert annotate (timestamp, temp, wind)
  └→ output to exif-* directory
```

### `process_footage`
**Bash script** - processes motion camera footage (Callisto, Ganymede, Phobos).

**Workflow:**
```
process_footage <camera> [-r]
  │
  ├→ setup paths (input/output/dir)
  ├→ uv run python process_videos.py
  ├→ [optional] rm -rf input_dir
  └→ mailx email with download link
```

### `concat-daily-movies`
**Bash script** - concatenates daily movies into monthly film.

**Workflow:**
```
concat-daily-movies
  │
  ├→ detect file extension (.webm or .mp4)
  ├→ create mylist.txt (ffmpeg concat list)
  ├→ ffmpeg -f concat → MONTH-month.EXT
  ├→ ffmpeg with audio → MONTH-sound.EXT
  └→ rm mylist.txt
```

### `monthly`
**Bash script** - orchestrates monthly timelapse processing.

**Workflow:**
```
monthly [-m month] [-y year]
  │
  ├→ canweather -v -m $MONTH -y $YEAR
  ├→ tar c source → tar -C archive -x
  ├→ find directories → create-archive
  ├→ concat-daily-movies (webm)
  └→ concat-daily-movies (x265)
```

## Video Creation Scripts

### `mkmov`
**Bash script** - creates videos from image sequences using ffmpeg.

**Features:**
- Multiple codecs: x264, x265, hevc, vp9, libsvtav1, iphone
- Two-pass encoding support (-2 flag)
- GPU encoding via NVENC
- Metadata embedding (title, author, year)

**Usage:** `mkmov -c CODEC -w WIDTH -q QUALITY -b BITRATE [-2] [-r FRAMERATE]`

### `build_ffmpeg_from_scratch`
**Bash script** - compiles ffmpeg from source with full codec support.

**Components:**
- x264, x265, libvpx, SVT-AV1
- libdav1d, opus, fdk-aac
- VMAF (Netflix)
- CUDA/NVENC support
- Installs to ~/ffmpeg_build

### `build_opencv_cuda`
**Bash script** - builds OpenCV with CUDA/cuDNN support.

**Components:**
- OpenCV 4.13.0 with CUDA
- cuDNN, CUDA_FAST_MATH
- Python 3.12 with numpy
- Uses uv for Python environment

## System Administration Scripts

### `update-all-machines`
**Bash script** - updates multiple machines via SSH.

**Machines:** europa, io, ganymede, callisto, titan, phobos, deimos, pihole

**Workflow:**
```
update-all-machines
  │
  ├→ ping check all machines
  ├→ For each node:
  │     │
  │     ├→ uname -a
  │     ├→ apt-get update && dist-upgrade
  │     └→ apt-get autoremove
  └→ pihole -up (DNS)
```

### `check-wifi`
**Bash script** - monitors WiFi connection and auto-reconnects if lost.

**Features:**
- Cron-triggered (every 5 minutes)
- Attempts 3 retries with 15s delay
- Auto-reboots if all retries fail
- Silent in non-interactive mode (cron)

### `linux-install-1.10.3.855.sh`
**Bash script** - initial system setup/script installation.

## Monitoring Scripts

### `network_monitor`, `network_monitor2`
**Bash scripts** - network monitoring utilities.

### `check-disks`
**Bash script** - disk health/status check.

### `geo-coord`
**Bash script** - geographic coordinate lookup.

### `ip_to_host`
**Bash script** - IP to hostname resolution.

## Other Utilities

### `create_pdf.rb`
**Ruby script** - PDF creation utility.

### `csv.rb`
**Ruby script** - CSV processing.

### `kutil.rb`, `kwhydro.rb`
**Ruby scripts** - Kitchener utility scripts.

### `process_callisto_footage`, `process_ganymede_footage`
**Bash scripts** - camera-specific footage processing wrappers.

### `create-hevc`, `create-vp9`, `create-x264`
**Bash scripts** - codec-specific video creation wrappers.

### `create-monthly-movie`
**Bash script** - monthly movie creation.

### `create-foto-index`
**Bash script** - photo index creation.

### `timelapse`
**Bash script** - timelapse processing utility.

### `fill-gaps`
**Bash script** - fills gaps in timelapse sequences.

### `cpu-data`
**Bash script** - shows CPU temperature and frequency per core.

### `daily-job`, `hourly-job`
**Bash scripts** - cron job wrappers.

### `canweather` (referenced)
**Script** - weather data acquisition (not in directory).

### `create-archive`, `create-movie`, `create-hevc`, `create-vp9`, `create-x264`, `create-monthly-movie`, `create-foto-index`
**Bash scripts** - video creation and archive utilities.

### `timelapse`
**Bash script** - timelapse image capture.

### `process-tl-dir`
**Ruby script** - directory annotation with EXIF data.

### `process-tl-dir`
**Bash script** - timelapse directory annotation.

### `fill-gaps`
**Bash script** - fills gaps in timelapse sequences.

### `daily-job`, `hourly-job`
**Bash scripts** - cron job wrappers.

### `canweather` (referenced)
**Script** - weather data acquisition (not in directory).

## File Structure

```
/scripts/
├── monthly.py          # Main timelapse processor (Python)
├── create-archive      # Archive and create movies
├── process_footage     # Motion camera footage processing
├── concat-daily-movies # Monthly movie concatenation
├── monthly             # Monthly processing orchestration
├── mkmov               # Video creation utility
├── process-tl-dir      # Ruby annotation script
├── build_ffmpeg_from_scratch
├── build_opencv_cuda
├── update-all-machines
├── check-wifi
├── [other utilities]
└── README.md           # This file
```

## Typical Workflows

### Monthly Timelapse Processing
```bash
monthly -m 03 -y 2026
# or for last month:
monthly
```

### Camera Footage Processing
```bash
process_footage callisto --remove
process_footage ganymede --remove
process_footage phobos --remove
```

### Daily Timelapse Processing
```bash
create-archive /path/to/timelapse/jpgs
```

## Notes

- Many scripts use `/usr/local/share/fonts/Envy-Code-R-PR7/` fonts
- Weather data comes from `/var/lib/weather/goc/weather-YYYY-MM.csv`
- Archive paths typically under `/usb_drives/my_book/archive/`
- Scripts often use `nice` for CPU priority management
- Some scripts reference external paths (`/srv/timelapse/io`, `/seagate/www/`)

## Additional Scripts

### `process-all-footage`
**Bash script** - runs footage processing for all cameras (callisto, ganymede, phobos).

### `check-disks`
**Bash script** - disk health/status check.

### `create-archive`
**Bash script** - creates archive from timelapse directory.

### `mkmov`
**Bash script** - creates video from directory of JPGs.

### `create-monthly-movie`
**Bash script** - creates monthly movie from daily movies.

### `concat-daily-movies`
**Bash script** - concatenates daily movies into monthly movie.

### `create-hevc`, `create-vp9`, `create-x264`
**Bash scripts** - codec-specific video creation.

### `create-foto-index`
**Bash script** - creates photo index.

### `timelapse`
**Bash script** - timelapse processing utility.

### `fill-gaps`
**Bash script** - fills gaps in timelapse sequences.

### `process-tl-dir`
**Ruby script** - annotates timelapse directory with weather data.

### `daily-job`, `hourly-job`
**Bash scripts** - cron job wrappers.

### `canweather` (referenced)
**Script** - weather data acquisition utility.

### `cpu-data`
**Bash script** - shows CPU temperature and frequency per core.

### `geo-coord`
**Bash script** - shows IP, coordinates, sunrise/sunset.

### `ip_to_host`
**Bash script** - IP to hostname resolution.

### `check-wifi`
**Bash script** - monitors WiFi and auto-reconnects.

### `update-all-machines`
**Bash script** - updates multiple machines via SSH.

### `process_callisto_footage`, `process_ganymede_footage`
**Bash scripts** - camera-specific footage processing.

### `network_monitor`, `network_monitor2`
**Bash scripts** - network monitoring.

### `csv.rb`, `kutil.rb`, `kwhydro.rb`, `create_pdf.rb`
**Ruby scripts** - various utilities (CSV, Kitchener tools, PDF).