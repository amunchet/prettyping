import os
import time
import subprocess
from rich.console import Console
from rich.table import Table
import sys

# Function to perform a ping, adapting for Windows and Linux, and capturing RTT
def ping(host):
    if os.name == 'nt':  # If Windows
        # Execute the ping command and capture output
        result = subprocess.run(f"ping -n 1 {host}", stdout=subprocess.PIPE, text=True)
        if "Request timed out" in result.stdout or "Destination host unreachable" in result.stdout:
            return False, 0
        else:
            # Extract RTT (Round-trip time) from the output
            lines = result.stdout.splitlines()
            for line in lines:
                if "Average" in line:
                    rtt = int(line.split("Average = ")[1].replace("ms", ""))
                    return True, rtt
            return True, 0
    else:  # If Linux/Unix (including macOS)
        # Execute the ping command and capture output
        result = subprocess.run(f"ping -c 1 {host}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # Extract RTT from the output
            lines = result.stdout.splitlines()
            for line in lines:
                if "time=" in line:
                    rtt = float(line.split("time=")[1].split()[0])
                    return True, rtt
            return True, 0
        else:
            return False, 0

# Function to generate a table of ping success/failure percentages and average RTT
def draw_table(target, success, fail, avg_rtt):
    total = success + fail
    if total == 0:
        total = 1  # Avoid division by zero

    success_percent = (success / total) * 100
    fail_percent = (fail / total) * 100

    # Create a table using Rich
    table = Table(title="")
    table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Add rows to the table for success, fail percentages, and average RTT
    table.add_row("Target", target)
    table.add_row("Success %", f"{success_percent:.2f}%")
    table.add_row("Fail %", f"{fail_percent:.2f}%")
    table.add_row("Average RTT (ms)", f"{avg_rtt:.2f} ms")

    return table

def clear_screen():
    # Clear screen command for Windows or Linux
    os.system('cls' if os.name == 'nt' else 'clear')

def main(target="1.1.1.1"):
    console = Console()
    success = 0
    fail = 0
    total_rtt = 0
    

    while True:
        # Clear the screen before each update
        clear_screen()

        # Perform a ping and capture success/fail and RTT
        ping_success, rtt = ping(target)

        if ping_success:
            success += 1
            total_rtt += rtt
        else:
            fail += 1

        # Calculate the average RTT
        total_pings = success + fail
        avg_rtt = total_rtt / success if success > 0 else 0

        # Get the updated table
        table = draw_table(target, success, fail, avg_rtt)

        # Print the updated table
        console.print(table)

        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: [target to ping]")
    else:
        main(sys.argv[1])
