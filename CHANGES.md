# CHANGES

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
