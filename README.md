Keylogger for linux/X that gathers aggregate stats about your
typing. The results include total keypress counts per measurement
window, plus a bit of detail about which keys you tend to type and
then backspace, and which ones you type right after using backspace.

Uses https://github.com/amoffat/pykeylogger for the X code.

Sample output (you get a line like this every 5 minutes):
    {
      "backspaced_counts": {".": 2, "a": 1, "d": 1, "e": 1, "p": 1, "t": 1},
      "backspaced_left_side": 4,
      "backspaced_right_side": 3,
      "high_typing_rate": 15.95,
      "keypresses": 31,
      "replaced_counts": {".": 2, "a": 1, "d": 1, "t": 3},
      "replaced_left_side": 5,
      "replaced_right_side": 2,
      "t": 1423726983.596,
      "window_secs": 30.002
    }
        