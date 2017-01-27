import os
import subprocess as sp

import numpy as np
import pylab as plt

import iris

import omnium as om
from omnium.experimental.twod_cube_viewer import TwodCubeViewer


SETTINGS = [{'output_dir': 'w_qcl_strong_shear',
             'group_name': 'stream1_2Kpdy_strong_shear',
             'delay': 20,
             'plot_name': 'plot1',
             'gifname': 'w_qcl_strong_shear',
             'range': range(2700, 2790)},
            {'output_dir': 'w_qcl_no_wind',
             'group_name': 'stream1_2Kpdy_cooling',
             'delay': 50,
             'plot_name': 'plot',
             'gifname': 'w_qcl_no_wind',
             'range': range(1440, 1500)}]


def main():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()

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
        for i in setting['range']:
            print(i)
            fig.clf()
            fig.suptitle('Time: {0:.2f} days'.format(i / 144.))
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            im = ax1.imshow(w[i].data, interpolation='nearest', origin='lower',
                            vmax=10, vmin=-5)
            ax1.set_xlabel('(km)')
            ax1.set_ylabel('(km)')
            ax1.yaxis.set_ticks_position('left')

            #cbaxes = fig.add_axes([0.1, 0.1, 0.03, 0.8])
            cbar = fig.colorbar(im, ax=ax1, orientation='horizontal')
            #cbaxes.yaxis.set_ticks_position('left')
            #cbaxes.yaxis.set_label_position('left')
            cbar.ax.set_xlabel('w (m s$^{-1}$)')

            im2 = ax2.imshow(qcl[i].data * 1000, interpolation='nearest', 
                             origin='lower', cmap='Blues',
                             vmin=0, vmax=1)
            ax2.set_xlabel('(km)')
            ax2.set_yticklabels([])
            cbar = fig.colorbar(im2, ax=ax2, orientation='horizontal')
            cbar.ax.set_xlabel('qcl (g kg$^{-1}$)')
            cbar.set_ticks(np.linspace(0, 1, 6))
            cbar.ax.set_xticklabels(np.linspace(0, 1, 6))

            plt.savefig(os.path.join(output_dir, '{}_{}.png'.format(setting['plot_name'], i)))

        os.chdir(output_dir)
        cmd_tpl = 'convert -delay {delay} -loop 1 {plot_name}*.png {gifname}.gif'
        cmd = cmd_tpl.format(**setting) 
        print(cmd)
        sp.call(cmd.split())
        os.chdir(cwd)


if __name__ == '__main__':
    main()
