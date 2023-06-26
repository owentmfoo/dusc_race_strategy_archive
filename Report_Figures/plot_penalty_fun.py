import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': False,
    'pgf.rcfonts': False,
    'font.size':8,
})

t10 = matplotlib.pyplot.colormaps.get('tab10')
red = t10.colors[3]

lower = np.linspace(0.001,10)
upper = np.linspace(90,100)

# If we were to simply plot pts, we'd lose most of the interesting
# details due to the outliers. So let's 'break' or 'cut-out' the y-axis
# into two portions - use the top (ax) for the outliers, and the bottom
# (ax2) for the details of the majority of our data
fig, (ax, ax2) = plt.subplots(1, 2, sharey=True)
# if SoCMax > 98:
#     costfun += SoCMax - 98  # Deadzone linear
# if SoCMin < 5:  # log barrier inf at SoCmin = 1
#     u = 5 - abs(SoCMin)
#     if u < 4:
#         costfun += 16 * np.log(1 - (u / 4) ** 2)
#     else:
#         costfun += 100
# plot the same data on both axes
ax.plot(lower,[(-25*np.log((u/5)**2)) if u < 5 else (0) for u in lower],c=red)
ax2.plot(upper, [u-98 if u > 98 else 0 for u in upper],c=red)

# zoom-in / limit the view to different portions of the data
ax.set_xlim(0, 10)  # outliers only
ax2.set_xlim(90, 100)  # most of the data
ax.set_ylim(0,50)
# ax.set_yscale('log')

# hide the spines between ax and ax2
# ax.spines['right'].set_visible(False)
# ax2.spines['left'].set_visible(False)
ax.yaxis.tick_left()
ax.tick_params(labelright=False)  # don't put tick labels at the top
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")

# This looks pretty good, and was fairly painless, but you can get that
# cut-out diagonal lines look with just a bit more work. The important
# thing to know here is that in axes coordinates, which are always
# between 0-1, spine endpoints are at these locations (0,0), (0,1),
# (1,0), and (1,1).  Thus, we just need to put the diagonals in the
# appropriate corners of each of our axes, and so long as we use the
# right transform and disable clipping.

d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass to plot, just so we don't keep repeating them
kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal


kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax2.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal

# What's cool about this is that now if we vary the distance between
# ax and ax2 via f.subplots_adjust(hspace=...) or plt.subplot_tool(),
# the diagonal lines will move accordingly, and stay right at the tips
# of the spines they are 'breaking'


fig.set_size_inches(3.5,2)
fig.subplots_adjust(top=0.97,bottom=0.2,hspace=0,wspace=0.1)
fig.supylabel("Panelty Function (% SoC)",fontsize = 8)
ax.set_xlabel("Min SoC (%)")
ax2.set_xlabel("Max SoC (%)")
ax.set_xticklabels([0,5,''])
ax2.set_xticklabels(['',95,100])

fig.set_dpi(150)
fig.show()
fig.savefig('E:\\solar_car_race_strategy\\Report\\pen_fun.png')