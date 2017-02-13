import os

import numpy as np
import pylab as plt

import iris

import omnium as om


SETTINGS = [{'output_dir': 'w_qcl_strong_shear',
             'group_name': 'stream1_2Kpdy_strong_shear',
             'plot_name': 'theta_q_strong_shear_moap',
             'gifname': 'theta_q_strong_shear'}]


def quo_vadis_plot():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()

    setting = SETTINGS[0]
    output_dir = output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pp1_node = dag.get_node('atmos.pp1.nc', setting['group_name'])

    input_dir = os.path.dirname(pp1_node.filename(config))
    f1 = os.path.join(input_dir, 'theta_near_surf_19dys.nc')
    f2 = os.path.join(input_dir, 'q_BL_19dys.nc')
    theta = iris.load(f1)[0]
    q = iris.load(f2)[0]

    plt.ioff()
    fig = plt.figure()
    fig.set_size_inches(8, 5)

    fig.clf()
    fig.suptitle('Time: {0:.2f} days'.format(19.))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    im = ax1.imshow(theta.data, interpolation='nearest', origin='lower')
    ax1.set_xlabel('(km)')
    ax1.set_ylabel('(km)')
    ax1.yaxis.set_ticks_position('left')

    #cbaxes = fig.add_axes([0.1, 0.1, 0.03, 0.8])
    cbar = fig.colorbar(im, ax=ax1, orientation='horizontal')
    #cbaxes.yaxis.set_ticks_position('left')
    #cbaxes.yaxis.set_label_position('left')
    cbar.ax.set_xlabel('$\\theta$ (K)')
    cbar.set_ticks(np.linspace(297, 300, 7))
    cbar.ax.set_xticklabels(np.linspace(297, 300, 7))

    im2 = ax2.imshow(q.data * 1000, interpolation='nearest', origin='lower')
    ax2.set_xlabel('(km)')
    ax2.set_yticklabels([])
    cbar = fig.colorbar(im2, ax=ax2, orientation='horizontal')
    cbar.ax.set_xlabel('q (g kg$^{-1}$)')

    plt.savefig(os.path.join(output_dir, 'BL_theta_q_19dys.png'))

def moap_plot():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    cwd = os.getcwd()

    setting = SETTINGS[0]
    print(setting['gifname'])
    output_dir = output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pp1_node = dag.get_node('atmos.pp1.nc', setting['group_name'])

    input_dir = os.path.dirname(pp1_node.filename(config))
    f1 = os.path.join(input_dir, 'theta_near_surf_19dys.nc')
    f2 = os.path.join(input_dir, 'q_BL_19dys.nc')
    theta = iris.load(f1)[0]
    q = iris.load(f2)[0]

    plt.ion()

    output_dir = os.path.join(output, setting['output_dir'])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fig = plt.figure(setting['plot_name'])
    fig.set_size_inches(8, 4)

    fig.clf()

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    im = ax1.imshow(theta.data, interpolation='nearest', origin='lower', vmin=297, vmax=300)
    ax1.set_xlabel('(km)')
    ax1.set_ylabel('(km)')
    ax1.yaxis.set_ticks_position('left')

    cbar = fig.colorbar(im, ax=ax1, orientation='vertical', fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel('$\\theta$ (K)')
    cbar.set_ticks(np.linspace(297, 300, 4))
    cbar.ax.set_xticklabels(np.linspace(297, 300, 4))

    im2 = ax2.imshow(q.data * 1000, interpolation='nearest', 
                     origin='lower', cmap='Blues', vmin=0, vmax=20)
    ax2.set_xlabel('(km)')
    ax2.set_yticklabels([])
    cbar = fig.colorbar(im2, ax=ax2, orientation='vertical', fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel('q (g kg$^{-1}$)')
    cbar.set_ticks(np.linspace(0, 20, 6))
    cbar.ax.set_xticklabels(np.linspace(0, 20, 6))

    plt.tight_layout(h_pad=1.0)
    plt.savefig(os.path.join(output_dir, '{}.png'.format(setting['plot_name'])))
    plt.pause(0.1)


if __name__ == '__main__':
    #quo_vadis_plot()
    moap_plot()

