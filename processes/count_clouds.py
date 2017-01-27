from __future__ import division
from collections import OrderedDict as odict
import importlib

from omnium.processes import PylabProcess
from omnium.experimental.blobby import count_blobs_mask

OPTS = odict([('Evap', {'ylim': (0, 0.0004), 'yaxis': True}),
              ('Precip', {'ylim': (0, 0.0004), 'convolve': True})])


L = 2.501e6

# TODO: take from data.
LX = 256000
LY = 256000
NX = 256
NY = 256

# TODO: lifted from omnium/processes/iris_processes.py
# Rationalize (this is a better impl. anyway!).
def find_cube(cubes, section_item=None):
    section, item = section_item

    found = False
    for cube in cubes:
        cube_stash = cube.attributes['STASH']
        cube_section, cube_item = cube_stash.section, cube_stash.item
        if cube_section == section and cube_item == item:
            found = True
            break

    if not found:
        raise Exception('Could not find {}'.format(self.node))
    return cube


class Cloud(object):
    def __init__(self, x, y):
        self.x = x 
        self.y = y 


class CountClouds(PylabProcess):
    name = 'count_clouds'
    out_ext = 'png'

    def load_modules(self):
        self.np = importlib.import_module('numpy')
        self.plt = importlib.import_module('pylab')
        self.iris = importlib.import_module('iris')

    def load_upstream(self):
        super(CountClouds, self).load_upstream()
        node = self.node.from_nodes[0]
        filename = node.filename(self.config)
        self.data = self.iris.load(filename)
        return self.data

    def run(self, w_thresh, qcl_thresh, start_index, end_index):
        #super(CountClouds, self).run()
        cubes = self.data

        w = find_cube(cubes, (0, 150))
        qcl = find_cube(cubes, (0, 392))

        mask = ((w.data > w_thresh) & (qcl.data > qcl_thresh))

        self._count_clouds(mask, start_index, end_index)

    def _count_clouds(self, mask, start_index, end_index):
        dists = []
        total_clouds = 0
        for i in range(start_index, end_index):
            print(i)
            cloud_mask = count_blobs_mask(mask[i], diagonal=True)[1]
            cp = self._get_cloud_pos(cloud_mask)
            clouds = []
            for j in range(cp.shape[0]):
                clouds.append(Cloud(cp[j, 0], cp[j, 1]))
            total_clouds += len(clouds)
            new_dists = self._calc_cloud_stats(clouds)
            dists.extend(new_dists)
        mean_clouds = total_clouds/(end_index - start_index)

        n, bins, patch = self.plt.hist(dists, 1000)
        #fig = self.plt.figure()
        #fig.clf()

        areas = self.np.pi * (bins[1:]**2 - bins[:-1]**2)
        cloud_densities = n / areas

        # Normalize based on mean density over domain.
        # WRONG WAY TO DO IT!:
        # mean = cloud_densities[bins < LX / 2.].mean()
        # self.plt.plot((bins[:-1] + bins[1:]) / 2, cloud_densities / mean)
        # calculates the mean of the densities, not the mean density.

        # Correct way to normalize:
        # Divide the total number in a circle by the circle's area.
        imax = self.np.argmax(bins[1:] > (LX / 2))
        mean_density = n[:imax].sum() / (self.np.pi * bins[imax]**2)
        xpoints = (bins[:-1] + bins[1:]) / 2
        self.plt.plot(xpoints / 1000, cloud_densities / mean_density)
        self.plt.xlabel('Distance (km)')
        self.plt.ylabel('Normalized cloud number density')
        self.plt.axhline(y=1, ls='--')
        #print(bins[:21] / 1000)
        #print(n[:20])
        #print(cloud_densities[:20])

        self.plt.xlim((0, 60))
        self.plt.ylim((0, 25))
        #self.processed_data = fig

    def save(self):
        super(PylabProcess, self).save()
        filename = self.node.filename(self.config)
        self.plt.savefig(filename)
        self.saved = True

    def _get_cloud_pos(self, clouds):
        half_dx = LX / (2 * NX)
        half_dy = LY / (2 * NY)
        x = self.np.linspace(half_dx, LX - half_dx, NX)
        y = self.np.linspace(half_dy, LY - half_dy, NY)
        X, Y = self.np.meshgrid(x, y, indexing='xy')
        cloud_pos = []
        for i in range(1, clouds.max() + 1):
            # Averages the x, y coords of all cells with a given index to get each cloud's "centre of
            # mass"
            cloud_x = X[clouds == i].sum() / (clouds == i).sum()
            cloud_y = Y[clouds == i].sum() / (clouds == i).sum()
            cloud_pos.append((cloud_x, cloud_y))
        return self.np.array(cloud_pos)

    def _calc_min_dists(self, cloud, test_cloud):
        dists = []
        for ii in [-1, 0, 1]:
            for jj in [-1, 0, 1]:
                x = test_cloud.x + ii * LX
                y = test_cloud.y + jj * LY
                dist = self.np.sqrt((cloud.x - x)**2 + (cloud.y - y)**2)
                dists.append(dist)
        return dists

    def _calc_cloud_stats(self, clouds):
        dists = []
        for i in range(len(clouds)):
            cloud = clouds[i]
            for j in range(i + 1, len(clouds)):
                test_cloud = clouds[j]
                new_dists = self._calc_min_dists(cloud, test_cloud)
                dists.extend(new_dists)
        return dists
