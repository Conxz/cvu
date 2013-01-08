import numpy as np
import pylab as pl
import matplotlib.path as m_path
import matplotlib.patches as m_patches
from mne.fixes import tril_indices
from matplotlib.backends.backend_wxagg import *
from matplotlib.backends.backend_wx import *
from matplotlib.backends.backend_agg import *
from matplotlib import *
from matplotlib.axes import Axes
import wx

def callbacque(event):
	print 'button=%d,x=%d,y=%d,xdata=%f,ydata=%f'%(event.button,event.x,event.y,
		event.xdata,event.ydata)
	#print type(event.inaxes)
	#print dir(event.inaxes.patches[217].get_path())
	#print type(event.inaxes.patches[217]) == matplotlib.patches.PathPatch
	#print type(event.canvas.figure.axes)
	ls=[]
	i=-1
	for patch in event.inaxes.patches:
		i+=1
		if type(patch) != matplotlib.patches.PathPatch:
			continue
		#print patch.get_ec()
		ls.append(i)
		#patch.set_ec((0,0,0,0))
	#event.inaxes.patches[9332].set_ec((.2,.9,.9,1.))
	#event.inaxes.patches[9452].set_ec((.2,.9,.9,1.))
	event.inaxes.patches[217].set_ec((.53,.84,.9,1.))
	event.inaxes.patches[217].set_zorder(4)
	event.canvas.draw()
	print len(ls)

def make_plot(parent,editor):
	global canvas
	fig=editor.object.figure
	panel=wx.Panel(parent,-1)
	canvas=FigureCanvasWxAgg(panel,-1,fig)
	toolbar=NavigationToolbar2Wx(canvas)
	toolbar.Realize()
	sizer=wx.BoxSizer(wx.VERTICAL)
	sizer.Add(canvas,1,wx.EXPAND|wx.ALL,1)
	sizer.Add(toolbar,0,wx.EXPAND|wx.ALL,1)
	panel.SetSizer(sizer)
	cid=canvas.mpl_connect('button_press_event',callbacque)
	return panel

def plot_connectivity_circle(con, node_names, indices=None, n_lines=None,
	node_angles=None, node_width=None,node_colors=None, facecolor='black',
	textcolor='white', node_edgecolor='black',linewidth=1.5, colormap='YlOrRd',
	vmin=None,vmax=None, colorbar=True, title=None):
    """Visualize connectivity as a circular graph.

Note: This code is based on the circle graph example by Nicolas P. Rougier
http://www.loria.fr/~rougier/coding/recipes.html

The code was adapted from MNE python

Parameters
----------
con : array
Connectivity scores. Can be a square matrix, or a 1D array. If a 1D
array is provided, "indices" has to be used to define the connection
indices.
node_names : list of str
Node names. The order corresponds to the order in con.
indices : tuple of arrays | None
Two arrays with indices of connections for which the connections
strenghts are defined in con. Only needed if con is a 1D array.
n_lines : int | None
If not None, only the n_lines strongest connections (strenght=abs(con))
are drawn.
node_angles : array, shape=(len(node_names,)) | None
Array with node positions in degrees. If None, the nodes are equally
spaced on the circle. See mne.viz.circular_layout.
node_width : float | None
Width of each node in degrees. If None, "360. / len(node_names)" is
used.
node_colors : list of tuples | list of str
List with the color to use for each node. If fewer colors than nodes
are provided, the colors will be repeated. Any color supported by
matplotlib can be used, e.g., RGBA tuples, named colors.
facecolor : str
Color to use for background. See matplotlib.colors.
textcolor : str
Color to use for text. See matplotlib.colors.
node_edgecolor : str
Color to use for lines around nodes. See matplotlib.colors.
linewidth : float
Line width to use for connections.
colormap : str
Colormap to use for coloring the connections.
vmin : float | None
Minimum value for colormap. If None, it is determined automatically.
vmax : float | None
Maximum value for colormap. If None, it is determined automatically.
c



defolorbar : bool
Display a colorbar or not.
title : str
The figure title.

Returns
-------
fig : instance of pyplot.Figure
The figure handle.
"""

    n_nodes = len(node_names)

    if node_angles is not None:
        if len(node_angles) != n_nodes:
            raise ValueError('node_angles has to be the same length '
                             'as node_names')
        # convert it to radians
        node_angles = node_angles * np.pi / 180
    else:
        # uniform layout on unit circle
        node_angles = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)

    if node_width is None:
        node_width = 2 * np.pi / n_nodes
    else:
        node_width = node_width * np.pi / 180

    if node_colors is not None:
        if len(node_colors) < n_nodes:
            node_colors = cycle(node_colors)
    else:
        # assign colors using colormap
        node_colors = [pl.cm.spectral(i / float(n_nodes))
                       for i in range(n_nodes)]

    # handle 1D and 2D connectivity information
    if con.ndim == 1:
        if indices is None:
            raise ValueError('indices has to be provided if con.ndim == 1')
    elif con.ndim == 2:
        if con.shape[0] != n_nodes or con.shape[1] != n_nodes:
            raise ValueError('con has to be 1D or a square matrix')
        # we use the lower-triangular part
        indices = tril_indices(n_nodes, -1)
        con = con[indices]
    else:
        raise ValueError('con has to be 1D or a square matrix')

    # get the colormap
    if isinstance(colormap, basestring):
        colormap = pl.get_cmap(colormap)

    # Make figure background the same colors as axes
    fig = pl.figure(figsize=(8, 8), facecolor=facecolor)

    # Use a polar axes
    axes = pl.subplot(111, polar=True, axisbg=facecolor)

    # No ticks, we'll put our own
    pl.xticks([])
    pl.yticks([])

    # Set y axes limit
    pl.ylim(0, 10)

    # Draw lines between connected nodes, only draw the strongest connections
    if n_lines is not None and len(con) > n_lines:
        con_thresh = np.sort(np.abs(con).ravel())[-n_lines]
    else:
        con_thresh = 0.

    # get the connections which we are drawing and sort by connection strength
    # this will allow us to draw the strongest connections first
    con_abs = np.abs(con)
    con_draw_idx = np.where(con_abs >= con_thresh)[0]

    con = con[con_draw_idx]
    con_abs = con_abs[con_draw_idx]
    indices = [ind[con_draw_idx] for ind in indices]

    # now sort them
    sort_idx = np.argsort(con_abs)
    con_abs = con_abs[sort_idx]
    con = con[sort_idx]
    indices = [ind[sort_idx] for ind in indices]

    # Get vmin vmax for color scaling
    if vmin is None:
        vmin = np.min(con[np.abs(con) >= con_thresh])
    if vmax is None:
        vmax = np.max(con)
    vrange = vmax - vmin

    # We want o add some "noise" to the start and end position of the
    # edges: We modulate the noise with the number of connections of the
    # node and the connection strength, such that the strongest connections
    # are closer to the node center
    nodes_n_con = np.zeros((n_nodes), dtype=np.int)
    for i, j in zip(indices[0], indices[1]):
        nodes_n_con[i] += 1
        nodes_n_con[j] += 1

    # initalize random number generator so plot is reproducible
    rng = np.random.mtrand.RandomState(seed=0)

    n_con = len(indices[0])
    noise_max = 0.25 * node_width
    start_noise = rng.uniform(-noise_max, noise_max, n_con)
    end_noise = rng.uniform(-noise_max, noise_max, n_con)

    nodes_n_con_seen = np.zeros_like(nodes_n_con)
    for i, (start, end) in enumerate(zip(indices[0], indices[1])):
        nodes_n_con_seen[start] += 1
        nodes_n_con_seen[end] += 1

        start_noise[i] *= ((nodes_n_con[start] - nodes_n_con_seen[start])
                           / float(nodes_n_con[start]))
        end_noise[i] *= ((nodes_n_con[end] - nodes_n_con_seen[end])
                         / float(nodes_n_con[end]))

    # scale connectivity for colormap (vmin<=>0, vmax<=>1)
    con_val_scaled = (con - vmin) / vrange

    # Finally, we draw the connections
    for pos, (i, j) in enumerate(zip(indices[0], indices[1])):
        # Start point
        t0, r0 = node_angles[i], 10

        # End point
        t1, r1 = node_angles[j], 10

        # Some noise in start and end point
        t0 += start_noise[pos]
        t1 += end_noise[pos]

        verts = [(t0, r0), (t0, 5), (t1, 5), (t1, r1)]
        codes = [m_path.Path.MOVETO, m_path.Path.CURVE4, m_path.Path.CURVE4,
                 m_path.Path.LINETO]
        path = m_path.Path(verts, codes)

        color = colormap(con_val_scaled[pos])

        # Actual line
        patch = m_patches.PathPatch(path, fill=False, edgecolor=color,
                                    linewidth=linewidth, alpha=1.)
        axes.add_patch(patch)

    # Draw ring with colored nodes
    radii = np.ones(n_nodes) * 10
    bars = axes.bar(node_angles, radii, width=node_width, bottom=9,
                    edgecolor=node_edgecolor, lw=2, facecolor='.9',
                    align='center',zorder=10)

    for bar, color in zip(bars, node_colors):
        bar.set_facecolor(color)

    # Draw node labels
    angles_deg = 180 * node_angles / np.pi
    for name, angle_rad, angle_deg in zip(node_names, node_angles, angles_deg):
        if angle_deg >= 270:
            ha = 'left'
        else:
            # Flip the label, so text is always upright
            angle_deg += 180
            ha = 'right'

        pl.text(angle_rad, 10.4, name, size=10, rotation=angle_deg,
                rotation_mode='anchor', horizontalalignment=ha,
                verticalalignment='center', color=textcolor)

    if title is not None:
        pl.subplots_adjust(left=0.2, bottom=0.2, right=0.8, top=0.75)
        pl.figtext(0.03, 0.95, title, color=textcolor, fontsize=14)
    else:
        pl.subplots_adjust(left=0.2, bottom=0.2, right=0.8, top=0.8)

    if colorbar:
        sm = pl.cm.ScalarMappable(cmap=colormap,
                                  norm=pl.normalize(vmin=vmin, vmax=vmax))
        sm.set_array(np.linspace(vmin, vmax))
        ax = fig.add_axes([.92, 0.03, .015, .25])
        cb = fig.colorbar(sm, cax=ax)
        cb_yticks = pl.getp(cb.ax.axes, 'yticklabels')
        pl.setp(cb_yticks, color=textcolor)

    return fig,indices
