# CHANGES

## 2026-03-12: mkmov refactor to Ruby

### Summary
Converted `mkmov` from bash script to Ruby using OptionParser, maintaining all ffmpeg encoding functionality.

### Changes

#### Removed
- Bash-only implementation with `getopts` for CLI parsing
- Environment variable dependencies (`PRESET`, `LOG_LEVEL`, `VERBOSE`, `DEBUG`)
- Hardcoded input patterns without CLI override

#### Added
- Ruby implementation using `OptionParser` from standard library
- Comprehensive CLI option validation (codec, preset, log level)
- All encoding variants: x264, x265/hevc, vp9, iphone, nvenc variants
- Two-pass encoding support for x264, vp9, and HEVC codecs
- Metadata embedding (title, author, year, copyright, description)

#### Fixed
- Hardcoded `264_nvenc` encoder bug (now uses correct encoder based on `--codec` option)
- Function visibility issues with OptionParser callbacks
- Syntax errors with method calls

### CLI Options

```
mkmov [options]

Options:
  -c CODEC, --codec=CODEC      Video codec (default: x264)
                               Valid: x264, x265, hevc, vp9, iphone, libsvtav1,
                                      264_nvenc, hevc_nvenc, av1_nvenc
  -i INPUT, --input=INPUT      Input file (required for iphone codec)
  -w WIDTH, --width=WIDTH      Output width in pixels (default: 1920)
  -q QUALITY, --quality=QUALITY
                               CRF quality value (default: 20, lower = better)
  -b BITRATE, --bitrate=BITRATE
                               Bitrate for ffmpeg (default: 5000k)
  -r FRAMERATE, --framerate=FRAMERATE
                               Framerate (default: 24)
  -p PRESET, --preset=PRESET   Encoding preset (default: medium)
                               Valid: ultrafast, superfast, veryfast, faster,
                                      fast, medium, slow, slower, veryslow
  -l LOG_LEVEL, --log-level=LOG_LEVEL
                               ffmpeg log level (default: error)
  -t THREADS, --threads=THREADS
                               Number of threads (default: 4)
  -2, --twopass                Enable two-pass encoding
  -v, --verbose                Enable verbose output
  -d, --debug                  Enable debug mode
  -h, --help                   Show help message
```

### Usage Examples

```bash
# Basic encoding with defaults
mkmov -c x264

# Custom width, quality, and preset
mkmov -c x264 -w 1280 -q 15 -p veryfast

# VP9 with two-pass encoding
mkmov -c vp9 -2 -r 30

# HEVC with custom bitrate
mkmov -c hevc -w 1920 -q 23 -b 3500k

# iPhone codec (requires input file)
mkmov -c iphone -i video.MTS

# Verbose output
mkmov -c x264 -v
```

### Output Format

Creates a movie file named:
```
{FDATE}-{CODEC}-q{QUALITY}-b{BITRATE}-w{WIDTH}-fr{FRAMERATE}.mp4/webm
```

Where FDATE is extracted from the first input file's modification date.

## 2026-03-11: create-24h-movie refactor to Ruby

### Summary
Converted `create-24h-movie` from bash script to Ruby, matching the style of `process-tl-dir`.

### Changes

#### Removed
- Bash-only implementation with shell scripting
- Manual parameter parsing with `if/then` conditionals
- Shell quoting workarounds

#### Added
- Ruby class-based structure (`Create24hMovie`)
- Thor gem for command-line argument handling
- Comprehensive help output with examples
- Proper error handling with `rescue` blocks
- Exit codes with meaningful error messages

#### Improvements
- **CLI options:** `-i/--interval`, `-r/--rate`, `-v/--verbose`, `-t/--target-dir`, `-h/--help`
- **Help system:** Displayed when run without arguments
- **Error messages:** Color-coded with descriptive output
- **Path handling:** Proper `~/` expansion via `Pathname`
- **Environment variables:** `MOVIES`, `INTERVAL`, `RATE`, `VERBOSE`
- **Code organization:** Clear separation of concerns with private methods

### Usage

```bash
create-24h-movie [options] <timelapse-directory>

Options:
    -i INTERVAL, --interval=INTERVAL    Time interval between frames in seconds (default: 120)
    -r RATE, --rate=RATE                Frame rate (default: 30, use 25 for PAL)
    -v, --verbose                       Enable verbose output
    -t TARGET_DIR, --target-dir=TARGET_DIR
                                        Working directory (default: current directory)

Examples:
    create-24h-movie 20240101
    create-24h-movie 20240101 -v
    INTERVAL=60 create-24h-movie 20240101
```
