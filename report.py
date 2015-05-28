from __future__ import division
import json
import datetime
import pandas as pd
from ggplot import ggplot, aes, geom_bar, ggsave, geom_point, ylim, stat_smooth, ggtitle

rows = []
for filename in [
        'plus.log',
        'dash.log',
]:
    for line in open(filename):
        row = json.loads(line)
        if not row['keypresses']:
            continue
            
        row['t'] = datetime.datetime.fromtimestamp(row['t'])
        row['filename'] = filename

        for attr in [
                "backspaced_left_side",
                "backspaced_right_side",
                "replaced_left_side",
                "replaced_right_side",
                ]:
            row['norm_' + attr] = row.get(attr, 0) / row['keypresses']
        
        rows.append(row)
rows.sort(key=lambda r: r['t'])
frame = pd.DataFrame(rows)

fm = pd.melt(
    frame,
    id_vars=[
        't',
        #'filename'
    ],
    value_vars=[
        #"norm_backspaced_left_side",
        #"norm_backspaced_right_side",
        #"high_typing_rate",
        #"keypresses",
        "norm_replaced_left_side",
        "norm_replaced_right_side",
        # "window_secs",
    ])
#print fm

p = (ggplot(aes(x='t', y='value',
                color='variable',
                #shape='filename'
            ),
            data=fm)
     + stat_smooth(span=.3)
#    + geom_point()
     + ylim(low=0)
     + ggtitle(title="replacement keys used after backspace, per typed keys")
     #+ ggtitle(title="backspaced keys per typed keys")
     )

ggsave(plot=p, filename='/tmp/typo.png',
       width=20, height=10,
       units='in',
       dpi=80,
)
