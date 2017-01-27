import os
import subprocess as sp

import numpy as np
import pylab as plt

import iris

import omnium as om
from omnium.experimental.twod_cube_viewer import TwodCubeViewer
from omnium.experimental.blobby import count_blobs_mask


SETTINGS = [{'output_dir': 'clouds_no_wind',
             'group_name': 'stream1_2Kpdy_cooling',
             'delay': 50,
             'gifname': 'clouds_no_wind',
             'range': range(1440, 1500)}]


def main():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()

    proc = process_classes['count_clouds'](config, None)
    proc.load_modules()

    for setting in SETTINGS:
        print(setting['gifname'])
        output_dir = os.path.join(output, setting['output_dir'])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pp1_node = dag.get_node('atmos.pp1.nc', setting['group_name'])

        tcv = TwodCubeViewer(use_prev_settings=False)
        tcv.load(pp1_node.filename(config))

        w = tcv._cubes[6].copy()
        qcl = tcv._cubes[2].copy()

        plt.ioff()
        fig = plt.figure()
        fig.set_size_inches(8, 5)

        mask = ((w.data > 1) & (qcl.data > 0.001))

        dists = []
        total_clouds = 0
        for i in setting['range']:
            print(i)
            plt.clf()
            plt.title('Time: {0:.2f} days'.format(i / 144.))
            cloud_mask = count_blobs_mask(mask[i], diagonal=True)[1]
            cp = proc._get_cloud_pos(cloud_mask)
            clouds = []
            for j in range(cp.shape[0]):
                plt.plot(cp[j, 0] / 1000, cp[j, 1] / 1000, 'kx')

            plt.xlim((0, 256))
            plt.ylim((0, 256))

            plt.xlabel('(km)')
            plt.ylabel('(km)')

            plt.savefig(os.path.join(output_dir, 'plot_{}.png'.format(i)))

        os.chdir(output_dir)
        cmd_tpl = 'convert -delay {delay} -loop 1 *.png {gifname}.gif'
        cmd = cmd_tpl.format(**setting) 
        print(cmd)
        sp.call(cmd.split())
        os.chdir(cwd)


if __name__ == '__main__':
    main()
