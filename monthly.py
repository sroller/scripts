#!/usr/bin/env python

# --- Imports ---
import sys
import os
import shutil
import glob
import tempfile
import re
import csv
import subprocess
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import piexif

# --- Argument Parsing ---
def get_last_month_and_year():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    return last_month.month, last_month.year

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Process timelapse for a given month and year.")
    parser.add_argument('-m', '--month', type=int, help='Month as MM (01-12)')
    parser.add_argument('-y', '--year', type=int, help='Year as YYYY')
    parser.add_argument('-d', '--dir', type=str, default='/srv/timelapse/io', help='Base directory for timelapse jpgs')
    parser.add_argument('-a', '--archive', type=str, default=None, help='Archive directory for timelapse data')
    parser.add_argument('-p', '--publish', type=str, default='/srv/timelapse/publish', help='Directory to publish finished movies')
    args = parser.parse_args()
    month, year = args.month, args.year
    base_dir = args.dir
    archive_dir = args.archive
    publish_dir = args.publish
    if not month or not year:
        last_month, last_year = get_last_month_and_year()
        month = month or last_month
        year = year or last_year
    if not archive_dir:
        month_long_name = datetime(year, month, 1).strftime('%B')
        archive_dir = f"/usb_drives/my_book/archive/timelapse/river/{year}/{month:02d}-{month_long_name}"
    return month, year, base_dir, archive_dir, publish_dir


MONTH, YEAR, BASE_DIR, ARCHIVE_DIR, PUBLISH_DIR = parse_args()

# --- Constants ---
WEATHER_DATA_FILE = f"/var/lib/weather/goc/weather-{YEAR}-{MONTH:02d}.csv"

# --- Weather Data Loading ---
def load_weather_data(weather_file):
    data = {}
    if not os.path.exists(weather_file):
        print(f"ERROR: Weather data file {weather_file} not found. Exiting.")
        sys.exit(1)
    with open(weather_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if len(row) >= 3:
                dt, temp, wind = row[0], row[1], row[2]
                try:
                    data[dt] = {
                        'temperature': float(temp),
                        'wind_speed': int(wind)
                    }
                except ValueError:
                    print(f"Warning: Could not parse weather data row: {row}")
    print(f"Loaded weather data for {YEAR}-{MONTH:02d} from {weather_file}")
    return data

weather_data = load_weather_data(WEATHER_DATA_FILE)

# --- Timelapse Archiving ---
def copy_month_to_archive(year, month, base_dir, archive_dir):
    # Helper function to copy files and preserve timestamps, maintaining directory structure
    def copy_with_timestamps(src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for root, dirs, files in os.walk(src):
            rel_root = os.path.relpath(root, src)
            target_root = os.path.join(dst, rel_root) if rel_root != '.' else dst
            if not os.path.exists(target_root):
                os.makedirs(target_root)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_root, file)
                shutil.copy2(src_file, dst_file)  # preserves timestamps
    month_str = f"{month:02d}"
    prefix = f"{year}{month_str}"
    if not os.path.exists(base_dir):
        print(f"ERROR: Base directory {base_dir} does not exist. Exiting.")
        sys.exit(1)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    found = False
    # Only preserve the original subdirectory structure when copying
    for entry in os.listdir(base_dir):
        full_path = os.path.join(base_dir, entry)
        if os.path.isdir(full_path) and entry.startswith(prefix):
            found = True
            dest = os.path.join(archive_dir, entry)
            if not os.path.exists(dest):
                os.makedirs(dest)
            print(f"Consolidating JPGs and galerie.html from {full_path} to {dest}")
            jpg_count = 0
            galerie_copied = False
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    if file.lower().endswith('.jpg'):
                        jpg_count += 1
                        dst_file = os.path.join(dest, f"img{jpg_count:06d}.jpg")
                        shutil.copy2(src_file, dst_file)
                    elif file == "galerie.html" and not galerie_copied:
                        dst_file = os.path.join(dest, "galerie.html")
                        shutil.copy2(src_file, dst_file)
                        galerie_copied = True
    if not found:
        print(f"ERROR: No directories for {year}-{month:02d} found in {base_dir}. Exiting.")
        sys.exit(1)

copy_month_to_archive(YEAR, MONTH, BASE_DIR, ARCHIVE_DIR)

# --- Timelapse Processing ---
def get_weather_for_exif(dt_original, weather_data):
    """Match EXIF DateTimeOriginal to weather data by hour."""
    temperature = None
    wind_speed = None
    weather_key = None
    if dt_original:
        try:
            dt_hour = dt_original.replace(':', '-', 2).replace(' ', 'T')[:13] + ':00:00'
            for key in weather_data:
                if key.startswith(dt_hour[:13]):
                    weather_key = key
                    break
            if weather_key:
                temperature = weather_data[weather_key]['temperature']
                wind_speed = weather_data[weather_key]['wind_speed']
        except Exception as e:
            print(f"Warning: Could not match EXIF datetime to weather data: {e}")
    return temperature, wind_speed

def annotate_image(jpg, dest_path, dt_original, temperature, wind_speed):
    """Annotate image with EXIF datetime, temperature, and wind speed."""
    try:
        image = Image.open(jpg)
        draw = ImageDraw.Draw(image)
        # Try to load 'Envy Code R' font at size 24, fallback to default if not found
        try:
            font = ImageFont.truetype("Envy Code R", 24)
        except Exception:
            print("Warning: 'Envy Code R' font not found, using default font.")
            font = ImageFont.load_default()

        # Format datetime to omit seconds
        if dt_original:
            try:
                dt_no_seconds = dt_original[:-3]
            except Exception:
                dt_no_seconds = dt_original
            text = dt_no_seconds
        else:
            text = 'No DateTimeOriginal'
        temp_text = f"Temp: {temperature}°C" if temperature is not None else "Temp: N/A"
        wind_text = f"Wind: {wind_speed} km/h" if wind_speed is not None else "Wind: N/A"
        print(f"Annotating {jpg} with DateTimeOriginal: {text}, temperature: {temperature}, wind speed: {wind_speed}")

        # Get text sizes
        text_width, text_height = font.getbbox(text)[2:4]
        temp_width, temp_height = font.getbbox(temp_text)[2:4]
        wind_width, wind_height = font.getbbox(wind_text)[2:4]
        x = image.width - max(text_width, temp_width, wind_width) - 10
        y = 10

        # Sample the background color at the annotation position (average over a small area)
        def get_avg_bg_color(img, x, y, w, h):
            crop = img.crop((max(x,0), max(y,0), min(x+w,img.width), min(y+h,img.height)))
            pixels = list(crop.getdata())
            if not pixels:
                return (255,255,255)
            r = sum([p[0] for p in pixels]) // len(pixels)
            g = sum([p[1] for p in pixels]) // len(pixels)
            b = sum([p[2] for p in pixels]) // len(pixels)
            return (r,g,b)

        # Use the area behind the first line of text for color detection
        bg_color = get_avg_bg_color(image, x, y, text_width, text_height)
        # Calculate brightness (simple average)
        brightness = sum(bg_color) / 3
        # Map brightness to text color: white for dark bg, gradually darker gray for lighter bg
        # brightness 0-255: 0=black, 255=white
        # Use a simple linear mapping: text_color = 255 - int(0.7 * brightness)
        # Clamp to at least 40 for visibility
        gray_value = max(40, 255 - int(0.7 * brightness))
        text_color = (gray_value, gray_value, gray_value)

        draw.text((x, y), text, font=font, fill=text_color)
        draw.text((x, y + text_height + 5), temp_text, font=font, fill=text_color)
        draw.text((x, y + text_height + temp_height + 10), wind_text, font=font, fill=text_color)
        image.save(dest_path)
    except Exception as e:
        print(f"Warning: Could not process image {jpg}: {e}")
        shutil.copy2(jpg, dest_path)

def process_tl_dir(day_dir):
    print(f"Processing timelapse directory: {day_dir}")
    if not os.path.exists(day_dir):
        print(f"ERROR: Day directory {day_dir} does not exist. Skipping.")
        return
    pattern = re.compile(r'^\d{8}-\d{4}$')
    subdirs = [d for d in os.listdir(day_dir)
              if os.path.isdir(os.path.join(day_dir, d)) and pattern.match(d)]
    subdirs.sort()
    jpg_files = []
    for subdir in subdirs:
        jpgs = glob.glob(os.path.join(day_dir, subdir, '*.jpg'))
        jpgs.sort()
        jpg_files.extend(jpgs)
    if not jpg_files:
        print(f"ERROR: No jpg files found in {day_dir}. Skipping.")
        return
    print(f"Found {len(jpg_files)} jpg files to process.")

    with tempfile.TemporaryDirectory() as temp_dir:
        for idx, jpg in enumerate(jpg_files, start=1):
            dest_name = f"tl{idx:06d}.jpg"
            dest_path = os.path.join(temp_dir, dest_name)
            try:
                exif_dict = piexif.load(jpg)
                dt_original = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal, b'').decode('utf-8')
            except Exception as e:
                print(f"Warning: Could not extract EXIF from {jpg}: {e}")
                dt_original = ''
            temperature, wind_speed = get_weather_for_exif(dt_original, weather_data)
            annotate_image(jpg, dest_path, dt_original, temperature, wind_speed)
        print(f"Copied and renamed all jpgs to {temp_dir}")

        # Create movie with ffmpeg
        day_basename = os.path.basename(day_dir)
        output_mp4 = os.path.join(day_dir, f"{day_basename}.mp4")
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-framerate", "30",
            "-i", os.path.join(temp_dir, "tl%06d.jpg"),
            "-c:v", "libsvtav1",
            "-b:v", "5000k",
            output_mp4
        ]
        print(f"Running ffmpeg to create {output_mp4}")
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Created movie: {output_mp4}")
            if not os.path.exists(PUBLISH_DIR):
                os.makedirs(PUBLISH_DIR)
            publish_path = os.path.join(PUBLISH_DIR, f"{day_basename}.mp4")
            shutil.move(output_mp4, publish_path)
            print(f"Published movie to {publish_path}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: ffmpeg failed for {day_dir} with exit code {e.returncode}. Command: {e.cmd}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Unexpected error running ffmpeg for {day_dir}: {e}")
            sys.exit(1)

def main():
    for entry in os.listdir(ARCHIVE_DIR):
        day_path = os.path.join(ARCHIVE_DIR, entry)
        if os.path.isdir(day_path) and entry.startswith(f"{YEAR}{MONTH:02d}"):
            process_tl_dir(day_path)

if __name__ == "__main__":
    main()
