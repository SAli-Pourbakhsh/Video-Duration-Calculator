"""
Video Duration Calculator & Time Manager
Author: SeyedAli Pourbakhsh
Description: Professional tool with Smart Parsing, Undo functionality, and optimized performance.
"""

import os
import sys
import re
import time
from datetime import timedelta
from typing import List, Tuple

# --- Dependency Management ---
try:
    from colorama import init, Fore, Style, Back
    # Support for both MoviePy v1.0 and v2.0+
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip
except ImportError as e:
    print("CRITICAL ERROR: Required libraries failed to import.")
    print(f"Details: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# Initialize Colorama
init(autoreset=True)

# --- Configuration ---
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v', '.ts', '.webm')

# UI Elements
DIVIDER = f"{Fore.CYAN}{'-' * 60}{Style.RESET_ALL}"
THICK_DIVIDER = f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}"

def clear_screen() -> None:
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner() -> None:
    """Displays the main application banner."""
    clear_screen()
    print(THICK_DIVIDER)
    print(f"{Fore.WHITE}{Style.BRIGHT}      VIDEO DURATION CALCULATOR & TIME MANAGER      {Style.RESET_ALL}")
    print(f"{Fore.CYAN}            Created by: SeyedAli Pourbakhsh         {Style.RESET_ALL}")
    print(THICK_DIVIDER)
    print("")

def format_seconds(seconds: float) -> str:
    """Formats seconds into HH:MM:SS string."""
    seconds = int(round(seconds))
    return str(timedelta(seconds=seconds))

def smart_parse_time(time_str: str, ambiguity_mode: str) -> int:
    """
    Smartly parses a time string based on its structure.
    Returns total seconds.
    """
    if not time_str or ':' not in time_str:
        return 0
    
    parts = time_str.split(':')
    clean_parts = []
    
    for p in parts:
        # Extract leading digits from each part
        match = re.search(r'^(\d+)', p.strip())
        if match:
            clean_parts.append(int(match.group(1)))
            
    if not clean_parts: return 0

    h, m, s = 0, 0, 0
    
    # --- LOGIC CORE ---
    if len(clean_parts) == 3:
        # Case: 1:20:30 (Always HH:MM:SS)
        h, m, s = clean_parts[0], clean_parts[1], clean_parts[2]
        
    elif len(clean_parts) == 2:
        # Case: 10:30 (Depends on user preference)
        if ambiguity_mode == '2': 
            # User chose Hours:Minutes
            h, m = clean_parts[0], clean_parts[1]
        else:
            # User chose Minutes:Seconds (Default)
            m, s = clean_parts[0], clean_parts[1]
            
    return (h * 3600) + (m * 60) + s

def process_manual_input() -> Tuple[float, int]:
    """Handles manual copy-paste input with UNDO functionality."""
    print_banner()
    print(f"{Back.BLUE}{Fore.WHITE} MODE: Manual Input {Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}[?] Configuration for 2-part times (e.g., '10:30'):{Style.RESET_ALL}")
    print(f"    {Fore.GREEN}[1]{Style.RESET_ALL} Treat as MM:SS (Default)")
    print(f"    {Fore.WHITE}[2]{Style.RESET_ALL} Treat as HH:MM")
    
    mode = input(f"\n{Fore.GREEN}>> Selection (default 1): {Style.RESET_ALL}").strip()
    if mode not in ['1', '2']: mode = '1'

    print(DIVIDER)
    print(f"{Fore.CYAN}INSTRUCTIONS:{Style.RESET_ALL}")
    print("1. Paste your list of times.")
    print(f"2. Type {Fore.YELLOW}'undo'{Style.RESET_ALL} to remove last item.")
    print(f"3. Type {Fore.YELLOW}'calc'{Style.RESET_ALL} on a new line to finish.")
    print(DIVIDER)
    
    # History list for Undo functionality
    history: List[int] = []
    
    print(f"{Fore.MAGENTA}Waiting for input...{Style.RESET_ALL}\n")

    while True:
        try:
            raw_line = input()
            stripped_line = raw_line.lower().strip()
            
            # --- COMMANDS ---
            if stripped_line in ['calc', 'done', 'exit', 'end', 'finish']:
                break
            
            # UNDO Command
            if stripped_line in ['undo', 'z', '-']:
                if history:
                    removed = history.pop()
                    # Updated: Removed "Current Total" display as requested
                    print(f"{Fore.RED}   [-] Undo: Removed {format_seconds(removed)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}   [!] Nothing to undo.{Style.RESET_ALL}")
                continue

            # --- PROCESSING ---
            # Regex: Must contain at least one colon between digits
            found_times = re.findall(r'\d+\s*:\s*\d+(?:\s*:\s*\d+)?', raw_line)
            
            # Fallback for clean lines
            if not found_times and ':' in stripped_line:
                 sec = smart_parse_time(raw_line, mode)
                 if sec > 0:
                    history.append(sec)
                    count = len(history)
                    print(f"{Fore.GREEN}[#{count:02d}] Added:{Style.RESET_ALL} {raw_line.strip()} -> {format_seconds(sec)}")

            # Process matches
            for t in found_times:
                sec = smart_parse_time(t, mode)
                if sec > 0:
                    history.append(sec)
                    count = len(history)
                    print(f"{Fore.GREEN}[#{count:02d}] Added:{Style.RESET_ALL} {t} -> {format_seconds(sec)}")
            
        except KeyboardInterrupt:
            break
            
    return sum(history), len(history)

def process_directory_scan() -> Tuple[float, int]:
    """Recursively scans a directory."""
    print_banner()
    print(f"{Back.BLUE}{Fore.WHITE} MODE: Directory Scan {Style.RESET_ALL}")
    
    path = input(f"\n{Fore.YELLOW}[?] Enter folder path: {Style.RESET_ALL}").strip().replace('"', '')

    if not os.path.exists(path):
        print(f"\n{Fore.RED}[!] Error: Path not found.{Style.RESET_ALL}")
        input("Press Enter to return...")
        return 0.0, 0

    print(f"\n{Fore.CYAN}Scanning directory...{Style.RESET_ALL}")
    print(DIVIDER)
    
    total_seconds = 0.0
    item_count = 0
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith(VIDEO_EXTENSIONS):
                full_path = os.path.join(root, file)
                try:
                    with VideoFileClip(full_path) as clip:
                        duration = clip.duration
                        total_seconds += duration
                        item_count += 1
                        print(f"{Fore.GREEN}[#{item_count:02d}]{Style.RESET_ALL} {file}")
                        print(f"      Duration: {format_seconds(duration)}")
                except Exception:
                    print(f"{Fore.RED}[!] Failed to read: {file}{Style.RESET_ALL}")

    return total_seconds, item_count

def show_final_report(total_seconds: float, count: int) -> None:
    """Displays the final results in a highlighted table."""
    if count == 0:
        print(f"\n{Fore.RED}[!] No valid items processed.{Style.RESET_ALL}")
        input("\nPress Enter to return...")
        return

    print(f"\n{THICK_DIVIDER}")
    print(f"{Fore.WHITE}{Style.BRIGHT}                  FINAL REPORT                  {Style.RESET_ALL}")
    print(THICK_DIVIDER)
    print(f" Total Items Processed: {Fore.YELLOW}{count}{Style.RESET_ALL}")
    print("")
    
    # Table Header
    print(f" {Fore.CYAN}+{'='*20}+{'='*20}+{Style.RESET_ALL}")
    print(f" {Fore.CYAN}|{Style.RESET_ALL} {Style.BRIGHT}{'PLAYBACK SPEED':<18}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Style.BRIGHT}{'TIME REQUIRED':<18}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL}")
    print(f" {Fore.CYAN}+{'='*20}+{'='*20}+{Style.RESET_ALL}")
    
    # 1.0x Speed (Highlighted Green)
    normal_time = format_seconds(total_seconds)
    print(f" {Fore.CYAN}|{Style.RESET_ALL} {Fore.GREEN}{'Normal (1.0x)':<18}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Fore.GREEN}{normal_time:<18}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL}")
    
    # Separator Line
    print(f" {Fore.CYAN}|{'-'*20}+{'-'*20}|{Style.RESET_ALL}")
    
    # Other Speeds
    high_priority_speeds = [1.5, 2.0, 2.5]
    all_speeds = [1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
    
    for speed in all_speeds:
        adjusted = total_seconds / speed
        label = f"{speed}x Speed"
        time_str = format_seconds(adjusted)
        
        row_color = (Fore.YELLOW + Style.BRIGHT) if speed in high_priority_speeds else Fore.WHITE
            
        print(f" {Fore.CYAN}|{Style.RESET_ALL} {row_color}{label:<18}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {row_color}{time_str:<18}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL}")
        
    print(f" {Fore.CYAN}+{'='*20}+{'='*20}+{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Created by SeyedAli Pourbakhsh{Style.RESET_ALL}")
    input(f"\nPress Enter to return to main menu...")

def main_menu():
    """Main application loop."""
    while True:
        print_banner()
        print(f"{Fore.WHITE}Select an option:{Style.RESET_ALL}\n")
        print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} Manual Input (Copy/Paste text)")
        print(f"  {Fore.GREEN}[2]{Style.RESET_ALL} Scan Folder (Automatic)")
        print(f"  {Fore.RED}[0]{Style.RESET_ALL} Exit")
        
        choice = input(f"\n{Fore.GREEN}>> Choice: {Style.RESET_ALL}").strip()
        
        if choice == '1':
            seconds, count = process_manual_input()
            show_final_report(seconds, count)
        elif choice == '2':
            seconds, count = process_directory_scan()
            if seconds > 0:
                show_final_report(seconds, count)
        elif choice == '0':
            print(f"\n{Fore.CYAN}Exiting... Goodbye!{Style.RESET_ALL}")
            time.sleep(1)
            sys.exit()
        else:
            pass 

if __name__ == "__main__":
    main_menu()