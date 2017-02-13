import os
import subprocess as sp

import numpy as np
import pylab as plt
import matplotlib.patches as patches

import iris

import omnium as om
from omnium.experimental.twod_cube_viewer import TwodCubeViewer

SETTINGS = [{'expt': 'strong_shear',
             'output_dir': 'w_qcl_strong_shear',
             'group_name': 'stream1_2Kpdy_strong_shear',
             'plot_name': 'w_qcl_strong_shear',
             'time_index': 2742},
            {'expt': 'no_wind',
             'output_dir': 'w_qcl_no_wind',
             'group_name': 'stream1_2Kpdy_cooling',
             'plot_name': 'w_qcl_no_wind',
             'time_index': 1448}]

def main():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()
    plt.ion()

    for setting in SETTINGS:
        output_dir = os.path.join(output, setting['output_dir'])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pp1_node = dag.get_node('atmos.pp1.nc', setting['group_name'])

        tcv = TwodCubeViewer(use_prev_settings=False)
        tcv.load(pp1_node.filename(config))

        w = tcv._cubes[6].copy()
        qcl = tcv._cubes[2].copy()

        fig = plt.figure(setting['plot_name'])
        fig.set_size_inches(8, 4)

        time_index = setting['time_index']
        fig.clf()

        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        im = ax1.imshow(w[time_index].data, interpolation='nearest', origin='lower',
                        vmax=10, vmin=-5)
        ax1.set_xlabel('(km)')
        ax1.set_ylabel('(km)')
        ax1.yaxis.set_ticks_position('left')

        if setting['expt'] == 'no_wind':
            ax1.add_patch(patches.Rectangle((100, 180), 20, 20, fill=False))

        cbar = fig.colorbar(im, ax=ax1, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.ax.set_ylabel('w (m s$^{-1}$)')

        im2 = ax2.imshow(qcl[time_index].data * 1000, interpolation='nearest', 
                         origin='lower', cmap='Blues',
                         vmin=0, vmax=1)
        ax2.set_xlabel('(km)')
        ax2.set_yticklabels([])
        cbar = fig.colorbar(im2, ax=ax2, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.ax.set_ylabel('qcl (g kg$^{-1}$)')
        cbar.set_ticks(np.linspace(0, 1, 6))
        cbar.ax.set_xticklabels(np.linspace(0, 1, 6))

        if setting['expt'] == 'no_wind':
            ax2.add_patch(patches.Rectangle((100, 180), 20, 20, fill=False))

        plt.tight_layout(h_pad=1.0)
        plt.savefig(os.path.join(output_dir, '{}_{}.png'.format(setting['plot_name'], time_index)))
        plt.pause(0.1)

        if setting['expt'] == 'no_wind':
            fig = plt.figure('no_wind_cell_splitting')
            fig.set_size_inches(8, 2)

            time_index = setting['time_index']
            fig.clf()

            for i in range(1, 5):
                ax = fig.add_subplot(1, 5, i)

                im = ax.imshow(w[time_index + i].data[180:200, 100:120], interpolation='nearest', origin='lower',
                                vmax=10, vmin=-5)
                if i != 1:
                    ax.set_yticklabels([])
                else:
                    ax.set_ylabel('(km)')

                ax.set_xlabel('(km)')
            plt.savefig(os.path.join(output_dir, '{}_{}.png'.format('no_wind_cell_splitting', time_index)))
            plt.pause(0.1)


if __name__ == '__main__':
    main()
