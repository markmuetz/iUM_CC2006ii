import os

import numpy as np
import pylab as plt

import omnium as om

u_relax_data = np.array([-8.0,-12.0,10.0,0.0,0.0])
uv_relax_height = np.array([0.0,1.0e3,12.0e3,14.5e3,40.0e3])

def main():
    plt.ion()
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    output_dir = output
    fig = plt.figure('wind_profile')
    plt.clf()
    fig.set_size_inches(4, 3)

    plt.plot(u_relax_data, uv_relax_height / 1e3, 'b-')
    plt.axvline(x=0, color='k', linestyle='--')
    plt.xlim((-15, 15))
    plt.ylim((0, 16))
    plt.xlabel('u (m s$^{-1}$)')
    plt.ylabel('height (km)')
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, '{}.png'.format('wind_profile_strong_shear')))

if __name__ == '__main__':
    main()
