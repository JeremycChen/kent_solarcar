import os
import glob
import time

FOLDER = r"C:\Users\LattePanda\Downloads\BMSTool-V1.14.231\BMSTool-V1.14.23\SaveData"

def get_latest_csv(folder):
    """Return the path to the most recently modified .csv in `folder`."""
    csvs = glob.glob(os.path.join(folder, "*.csv"))
    if not csvs:
        raise FileNotFoundError("No CSV files found in %r" % folder)
    return max(csvs, key=os.path.getmtime)

def tail_csv(folder, sleep_secs=0.2):
    """Yield new lines as they’re written to the latest CSV in `folder`."""
    path = get_latest_csv(folder)
    with open(path, "r", newline="") as f:
        # Go straight to the end of file
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(sleep_secs)
                continue
            yield line.rstrip("\r\n")    # strip newline chars

if __name__ == "__main__":
    for row in tail_csv(FOLDER):
        print("New row:", row.split(","))
