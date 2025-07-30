#!/usr/bin/env python3
"""
Timelapse Video Generation Script

(refactored by gemini.google.com)

This script processes a month's worth of timelapse images by:
1. Archiving the raw JPGs from a source directory.
2. Annotating each image with timestamp and weather data.
3. Creating a daily timelapse video (MP4) from the annotated images.
4. Concatenating all daily videos into a single monthly timelapse.
"""

import argparse
import csv
import logging
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import piexif
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---

@dataclass
class Config:
    """Holds all configuration parameters for the timelapse script."""
    month: int
    year: int
    base_dir: Path
    archive_dir: Path
    publish_dir: Path
    weather_data_file: Path
    ffmpeg_framerate: int = 30
    ffmpeg_bitrate: str = "5000k"
    ffmpeg_codec: str = "libsvtav1" # Or "libx264" for wider compatibility
    verbose: bool = False
    quiet: bool = False
    nice_level: int = 10

def get_last_month_and_year() -> Tuple[int, int]:
    """Returns the month and year of the previous month."""
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_last_month.month, last_day_of_last_month.year

def setup_config() -> Config:
    """Parses command-line arguments and returns a Config object."""
    parser = argparse.ArgumentParser(description="Process timelapse for a given month and year.")
    parser.add_argument('-m', '--month', type=int, help='Month as MM (1-12)')
    parser.add_argument('-y', '--year', type=int, help='Year as YYYY')
    parser.add_argument('-d', '--dir', type=Path, default=Path('/srv/timelapse/io'), help='Base directory for timelapse jpgs')
    parser.add_argument('-a', '--archive', type=Path, default=None, help='Archive directory for timelapse data')
    parser.add_argument('-p', '--publish', type=Path, default=Path('/srv/timelapse/publish'), help='Directory to publish finished movies')
    parser.add_argument('--nice', type=int, default=10, help='Set the niceness level for ffmpeg commands (0 to disable, default: 10)')

    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument('-v', '--verbose', action='store_true', help='Enable verbose (DEBUG) logging')
    log_level_group.add_argument('-q', '--quiet', action='store_true', help='Suppress all non-error messages (for cron jobs)')
    args = parser.parse_args()

    last_month, last_year = get_last_month_and_year()
    month = args.month or last_month
    year = args.year or last_year

    # Generate a default archive path if not provided
    archive_dir = args.archive
    if not archive_dir:
        month_long_name = datetime(year, month, 1).strftime('%B')
        archive_dir = Path(f"/usb_drives/my_book/archive/timelapse/river/{year}/{month:02d}-{month_long_name}")

    weather_file = Path(f"/var/lib/weather/goc/weather-{year}-{month:02d}.csv")

    return Config(
        month=month,
        year=year,
        base_dir=args.dir,
        archive_dir=archive_dir,
        publish_dir=args.publish,
        weather_data_file=weather_file,
        verbose=args.verbose,
        quiet=args.quiet,
        nice_level=args.nice,
    )

# --- Utility Functions ---

def setup_logging(verbose: bool, quiet: bool):
    """Configures basic logging."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
    )

def run_command(command: List[str], log_prefix: str = ""):
    """Executes a subprocess command and handles errors."""
    try:
        logging.info(f"{log_prefix} Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.debug(f"{log_prefix} Command successful. STDOUT: {result.stdout.strip()}")
        if result.stderr:
            logging.debug(f"{log_prefix} STDERR: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"{log_prefix} Command failed with exit code {e.returncode}.")
        logging.error(f"Command: {e.cmd}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"{log_prefix} An unexpected error occurred: {e}")
        sys.exit(1)

# --- Core Logic Functions ---

def load_weather_data(weather_file: Path) -> Dict[str, Dict]:
    """Loads weather data from a semicolon-delimited CSV file."""
    if not weather_file.exists():
        logging.error(f"Weather data file not found: {weather_file}. Exiting.")
        sys.exit(1)

    data = {}
    with weather_file.open(newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if len(row) < 3:
                logging.debug(f"Skipping short row in weather data: {row}")
                continue
            dt, temp, wind = row[0], row[1], row[2]
            try:
                data[dt] = {'temperature': float(temp), 'wind_speed': int(wind)}
                logging.debug(f"Parsed weather data: {dt} -> {data[dt]}")
            except (ValueError, IndexError):
                logging.warning(f"Could not parse weather data row: {row}")
    logging.info(f"Loaded {len(data)} weather data points from {weather_file}")
    return data

def archive_source_images(config: Config):
    """Copies the source images for the specified month to the archive directory."""
    if not config.base_dir.exists():
        logging.error(f"Base directory {config.base_dir} does not exist. Exiting.")
        sys.exit(1)

    config.archive_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{config.year}{config.month:02d}"
    
    daily_dirs = [d for d in config.base_dir.iterdir() if d.is_dir() and d.name.startswith(prefix)]

    if not daily_dirs:
        logging.error(f"No daily directories for {config.year}-{config.month:02d} found in {config.base_dir}. Exiting.")
        sys.exit(1)

    logging.info(f"Archiving {len(daily_dirs)} daily directories from {config.base_dir} to {config.archive_dir}.")
    for src_dir in sorted(daily_dirs):
        dest_dir = config.archive_dir / src_dir.name
        logging.info(f"Copying {src_dir} to {dest_dir}...")
        shutil.copytree(src_dir, dest_dir, copy_function=shutil.copy2, dirs_exist_ok=True, ignore=shutil.ignore_patterns('galerie.html'))

def get_weather_for_timestamp(dt_original_str: str, weather_data: Dict) -> Tuple[Optional[float], Optional[int]]:
    """Matches an EXIF timestamp string to the closest hourly weather data."""
    if not dt_original_str:
        return None, None
    try:
        # Key format in weather data is 'YYYY-MM-DDTHH:MM:SS'
        # EXIF format is 'YYYY:MM:DD HH:MM:SS'
        # We match based on the hour: 'YYYY-MM-DDTHH'
        dt_hour_prefix = dt_original_str.replace(":", "-", 2).replace(" ", "T")[:13]
        logging.debug(f"Searching for weather with prefix: {dt_hour_prefix}")
        for key, value in weather_data.items():
            if key.startswith(dt_hour_prefix):
                logging.debug(f"Found weather match: {key} -> {value}")
                return value.get('temperature'), value.get('wind_speed')
    except Exception as e:
        logging.warning(f"Could not match EXIF datetime '{dt_original_str}' to weather data: {e}")
    logging.debug(f"No weather data found for prefix: {dt_hour_prefix}")
    return None, None

def _get_contrasting_text_color(image: Image.Image, x: int, y: int, width: int, height: int) -> Tuple[int, int, int]:
    """Samples background and returns a contrasting grayscale color for text."""
    try:
        crop = image.crop((x, y, min(x + width, image.width), min(y + height, image.height)))
        pixels = list(crop.getdata())
        if not pixels:
            return (255, 255, 255) # Default to white
        
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)
        
        # Calculate luminance
        brightness = (avg_r * 299 + avg_g * 587 + avg_b * 114) / 1000
        color = (0, 0, 0) if brightness > 128 else (255, 255, 255)
        # logging.debug(f"Background brightness: {brightness:.2f}, chose text color: {color}")
        return color
    except Exception:
        return (255, 255, 255) # Default to white on error

def annotate_image(src_path: Path, dest_path: Path, dt_str: str, temp: Optional[float], wind: Optional[int]):
    """Annotates an image with metadata and saves it to the destination."""
    try:
        with Image.open(src_path) as image:
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("Envy Code R", 24)
            except IOError:
                logging.warning("Font 'Envy Code R' not found, using default.")
                font = ImageFont.load_default()

            # Prepare text lines
            dt_display = dt_str.rsplit(':', 1)[0] if dt_str else 'No Timestamp'
            temp_display = f"Temp: {temp}°C" if temp is not None else "Temp: N/A"
            wind_display = f"Wind: {wind} km/h" if wind is not None else "Wind: N/A"
            lines = [dt_display, temp_display, wind_display]

            # Calculate position
            line_height = font.getbbox("Tg")[3] # Height of a tall character
            max_width = max(font.getlength(line) for line in lines)
            x = image.width - max_width - 15
            y = 10
            
            # Determine text color based on background
            text_color = _get_contrasting_text_color(image, x, y, int(max_width), int(line_height * len(lines)))

            # Draw text
            for i, line in enumerate(lines):
                draw.text((x, y + i * (line_height + 5)), line, font=font, fill=text_color)
            
            image.save(dest_path)

    except Exception as e:
        logging.warning(f"Could not process image {src_path}, copying instead: {e}")
        shutil.copy2(src_path, dest_path)

def process_daily_directory(day_dir: Path, config: Config, weather_data: Dict):
    """Processes all images in a day's directory to create a daily video."""
    logging.info(f"Processing timelapse directory: {day_dir.name}")
    
    # Using rglob to find all JPGs in subdirectories
    jpg_files = sorted(list(day_dir.rglob('*.jpg')))
    if not jpg_files:
        logging.warning(f"No JPG files found in {day_dir}. Skipping.")
        return

    logging.info(f"Found {len(jpg_files)} JPG files to process.")

    # Create a temporary directory for annotated images
    with tempfile.TemporaryDirectory(prefix=f"{day_dir.name}-", dir=day_dir.parent) as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        logging.debug(f"Created temporary directory for annotations: {temp_dir}")
        
        # Annotate images and save to temp directory
        for idx, jpg_path in enumerate(jpg_files, start=1):
            try:
                exif_dict = piexif.load(str(jpg_path))
                dt_original = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal, b'').decode('utf-8')
            except Exception:
                dt_original = ''
            
            temp, wind = get_weather_for_timestamp(dt_original, weather_data)
            dest_jpg = temp_dir / f"img{idx:06d}.jpg"
            annotate_image(jpg_path, dest_jpg, dt_original, temp, wind)

        # Create daily movie with ffmpeg
        output_mp4 = config.publish_dir / f"{day_dir.name}.mp4"
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(config.ffmpeg_framerate),
            "-i", str(temp_dir / "img%06d.jpg"),
            "-c:v", config.ffmpeg_codec,
            "-b:v", config.ffmpeg_bitrate,
            "-pix_fmt", "yuv420p", # for compatibility
            str(output_mp4)
        ]
        if config.nice_level > 0 and shutil.which("nice"):
            logging.debug(f"Prepending nice command with level {config.nice_level}")
            ffmpeg_cmd = ["nice", "-n", str(config.nice_level)] + ffmpeg_cmd

        run_command(ffmpeg_cmd, log_prefix=f"[{day_dir.name}]")
        logging.info(f"Successfully created and published daily movie: {output_mp4}")


def create_monthly_video(config: Config):
    """Concatenates all daily MP4s into a single monthly video."""
    logging.info("Starting monthly video concatenation.")
    config.publish_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"{config.year}{config.month:02d}"
    daily_mp4s = sorted(list(config.publish_dir.glob(f"{prefix}*.mp4")))
    logging.debug(f"Found daily MP4s for concatenation: {daily_mp4s}")

    if not daily_mp4s:
        logging.warning("No daily MP4s found to concatenate. Skipping monthly video.")
        return

    concat_list_path = config.publish_dir / f"concat_{prefix}.txt"
    with concat_list_path.open('w') as f:
        for mp4 in daily_mp4s:
            f.write(f"file '{mp4.resolve()}'\n")

    month_mp4_path = config.publish_dir / f"{prefix}-monthly-timelapse.mp4"
    ffmpeg_concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-c", "copy",
        str(month_mp4_path)
    ]
    if config.nice_level > 0 and shutil.which("nice"):
        logging.debug(f"Prepending nice command with level {config.nice_level}")
        ffmpeg_concat_cmd = ["nice", "-n", str(config.nice_level)] + ffmpeg_concat_cmd

    run_command(ffmpeg_concat_cmd, log_prefix="[Monthly Concat]")
    logging.info(f"Successfully created monthly movie: {month_mp4_path}")
    concat_list_path.unlink() # Clean up the temporary list file


def main():
    """Main execution function."""
    start_time = time.time()
    
    config = setup_config()
    setup_logging(config.verbose, config.quiet)
    logging.info(f"Starting timelapse processing for {config.year}-{config.month:02d}")
    logging.debug(f"Using configuration: {config}")

    # 1. Archive source images
    archive_source_images(config)

    # 2. Load weather data
    weather_data = load_weather_data(config.weather_data_file)
    
    # 3. Process each daily directory from the archive
    config.publish_dir.mkdir(parents=True, exist_ok=True)
    daily_archive_dirs = sorted([d for d in config.archive_dir.iterdir() if d.is_dir()])
    for day_dir in daily_archive_dirs:
        process_daily_directory(day_dir, config, weather_data)

    # 4. Concatenate daily videos into a monthly video
    create_monthly_video(config)
    
    elapsed = time.time() - start_time
    logging.info(f"Total runtime: {timedelta(seconds=elapsed)}")

if __name__ == "__main__":
    main()
