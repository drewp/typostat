from __future__ import division
from pykeylogger import keylogger
import time
import json
import os.path

typable_keys = '`1234567890-=qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./ '
type_left_side = '12345qwertasdfgzxcvb'

def avg(x):
    return sum(x) / len(x)

def append_ring(ring, elem, max_size):
    # fails on max_size < 2
    ring[:] = ring[-max_size + 1:] + [elem]
    
class DetectBackspace(object):
    """
    You call on_key with new keypresses and we call these event methods:
    
      on_backspaced: The user pressed backspace and this is the
      recently-typed key that is probably the one getting erased.
    
      on_replaced: The user pressed backspace recently and this is
      probably the key that's being typed to replace the erased one.
    
      on_typed: The user typed another printable key and we don't
      think it was part of a correction.
    """
    def __init__(self, max_recent_keys_stored=10, max_secs_for_correction=3):
        """
        max_recent_keys_stored caps the number of keys we remember for untyping.

        Keystrokes more than max_secs_for_correction old will be ignored.
        """
        self.max_recent_keys_stored = max_recent_keys_stored
        self.max_secs_for_correction = max_secs_for_correction
        self.recently_typed = []
        self.recent_backspace_times = []
        
    def on_key(self, t, modifiers, keys):
        if keys == '<backspace>':
            self._on_backspace(t)
        elif keys and keys in typable_keys:
            self._on_typable(t, keys)
            
    def _on_backspace(self, t):
        if self.recently_typed:
            old_time, corrected = self.recently_typed.pop()
            if t - old_time < self.max_secs_for_correction:
                self.on_backspaced(t, corrected)
        append_ring(self.recent_backspace_times, t, self.max_recent_keys_stored)
        
    def _on_typable(self, t, key):
        append_ring(self.recently_typed, (t, key), self.max_recent_keys_stored)
        last_backspace = (self.recent_backspace_times.pop()
                          if self.recent_backspace_times else 0)
        if t - last_backspace < self.max_secs_for_correction:
            self.on_replaced(t, key)
        else:
            self.on_typed(t, key)
                
    def on_typed(self, t, key):
        print "type %r" % key

    def on_replaced(self, t, key):
        print "replaced with %r" % key
        
    def on_backspaced(self, t, key):
        print "backspaced %r" % key

class Analyzer(DetectBackspace):
    def __init__(self, out_path):
        DetectBackspace.__init__(self)
        self.out_path = out_path
        self.start_window()

    def flush(self):
        self.end_window()
        self.start_window()
                
    def start_window(self):
        self.window_start_time = time.time()
        self.keypresses = 0
        self.backspaced_counts = {} # key: count
        self.replaced_counts = {} # key: count
        self.key_gaps = [] # secs between presses
        self.last_press = None

    def on_typed(self, t, key):
        self.keypresses += 1
        if self.last_press is not None:
            self.key_gaps.append(t - self.last_press)
        self.last_press = t
        
    def on_backspaced(self, t, key):
        self.keypresses += 1
        self.backspaced_counts[key] = self.backspaced_counts.get(key, 0) + 1

    def on_replaced(self, t, key):
        self.keypresses += 1
        self.replaced_counts[key] = self.replaced_counts.get(key, 0) + 1
        
    def end_window(self):
        elapsed = round(time.time() - self.window_start_time, 3)
        gaps = sorted(self.key_gaps)
        low_gaps = gaps[:max(3, len(gaps) // 3)]
        report = {
            't': round(self.window_start_time, 3),
            'keypresses': self.keypresses,
            'window_secs': round(elapsed, 3),
            'backspaced_counts': self.backspaced_counts,
            'replaced_counts': self.replaced_counts,
            'high_typing_rate': round(1 / avg(low_gaps), 2) if low_gaps else 0,
        }
        self._add_side_counts(report)
        with open(self.out_path, 'a') as out:
            out.write(json.dumps(report, sort_keys=True) + '\n')

    def _add_side_counts(self, report):
        for attr in ['backspaced', 'replaced']:
            for side in ['left', 'right']:
                pred = lambda key: key in type_left_side
                if side == 'right':
                    pred = lambda key: key not in type_left_side
                report['%s_%s_side' % (attr, side)] = sum(
                    n for key, n in getattr(self, '%s_counts' % attr).items()
                    if pred(key))
        

out_path = os.path.expanduser('~/typostat.log')
print "appending to", out_path
analyzer = Analyzer(out_path)
keylogger.return_shifted_values = False
# first window is short so you can confirm things are working
window_end = time.time() + 3
while True:
    keylogger.log(lambda: time.time() > window_end, analyzer.on_key)
    window_end = time.time() + 30
    analyzer.flush()

