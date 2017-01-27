import os
import subprocess as sp

import numpy as np
import pylab as plt

import iris

import omnium as om
from omnium.experimental.twod_cube_viewer import TwodCubeViewer
from omnium.experimental.blobby import count_blobs_mask


SETTINGS = [{'group_name1': 'stream1_2Kpdy_cooling',
             'group_name2': 'stream1_2Kpdy_strong_shear' }]


def main():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()

    setting = SETTINGS[0]
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()
    output_dir = output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pp1_node_no_wind = dag.get_node('atmos.pp1.nc', setting['group_name1'])
    pp1_node_strong_shear = dag.get_node('atmos.pp1.nc', setting['group_name2'])

    proc = process_classes['count_clouds'](config, pp1_node_strong_shear)
    proc.load_modules()

    pp1_no_wind = iris.load(pp1_node_no_wind.filename(config))
    pp1_strong_shear = iris.load(pp1_node_strong_shear.filename(config))

    plt.ioff()
    fig = plt.figure()
    fig.set_size_inches(4, 5)

    for pp1 in [pp1_no_wind, pp1_strong_shear]:
        print('running')
        w = pp1[6]
        qcl = pp1[2]
        mask = ((w.data > 1) & (qcl.data > 0.001))
        proc._count_clouds(mask, 1440, 2000)
    #plt.show()

    plt.savefig(os.path.join(output_dir, 'clustering_analysis.png'))

if __name__ == '__main__':
    main()
