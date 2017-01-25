import os

import numpy as np
import pylab as plt

import iris

import omnium as om
from omnium.experimental.twod_cube_viewer import TwodCubeViewer


def plot_ts(i, precip_bot_ts, precip_top_ts):
    plt.figure('precip_half_domain_ts')
    plt.clf()
    plt.plot(precip_bot_ts.data)
    plt.plot(precip_top_ts.data)
    plt.xlim((1440, 1440+288))
    plt.axvline(x=i)
    plt.pause(0.01)


def calc_dominant_mode_freq(precip_bot_ts):
    precip_ft = np.abs(np.fft.fft(precip_bot_ts[1440:2880].data))
    freq = np.fft.fftfreq(1440, d=600)
    # Skip initial max (mean ts != 0).
    freq_max = freq[np.argmax(precip_ft[1:]) + 1]
    print('{0:.3} s^-1'.format(freq_max))
    print('{0:.3} s'.format(1/freq_max))
    print('{0:.3} hr'.format((1/freq_max) /3600))


def main():
    config, process_classes, dag, proc_eng, stash = om.init()
    computer_name = config['computer_name']
    output = config['computers'][computer_name]['dirs']['output']
    output_half_domain = os.path.join(output, 'half_domain')
    if not os.path.exists(output_half_domain):
        os.makedirs(output_half_domain)

    pp1_node = dag.get_node('atmos.pp1.nc', 'stream1_no_wind')

    tcv = TwodCubeViewer(use_prev_settings=False)
    tcv.load(pp1_node.filename(config))
    tcv.add_disp(3)
    tcv.disp()

    precip = tcv._cubes[3].copy()
    vmax, vmin = precip[1440:1440 + 288].data.max(), precip[1440:1440 + 288].data.min()
    precip_bot_ts = precip[:, 128:, :].collapsed(['grid_latitude', 'grid_longitude'], 
                                                 iris.analysis.MEAN)
    precip_top_ts = precip[:, :128, :].collapsed(['grid_latitude', 'grid_longitude'], 
                                                 iris.analysis.MEAN)

    calc_dominant_mode_freq(precip_bot_ts)

    plt.ioff()
    fig = plt.figure()
    fig.set_size_inches(8, 3)
    for i in range(1440, 1440+288):
        print(i)
        fig.clf()
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        #plt.tight_layout()
        # precip data in kg m^-2 s^-1, convert to mm hr^-1 (x3600)
        im = ax1.imshow(precip[i].data * 3600, interpolation='nearest', origin='lower',
                        vmax=30, vmin=0, cmap='Blues')
        ax1.set_xlabel('(km)')
        ax1.set_ylabel('(km)')
        ax1.yaxis.tick_right()
        ax1.yaxis.set_label_position("right")
        cbaxes = fig.add_axes([0.1, 0.1, 0.03, 0.8])
        cbar = fig.colorbar(im, ax=ax1, cax=cbaxes)
        cbaxes.yaxis.set_ticks_position('left')
        cbaxes.yaxis.set_label_position('left')
        cbar.ax.set_ylabel('Precip. (mm hr$^{-1}$)')

        ax2.plot(np.linspace(0, 20, 2880), precip_bot_ts.data * 3600)
        ax2.plot(np.linspace(0, 20, 2880), precip_top_ts.data * 3600)
        ax2.set_xlim((10, 12))
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position("right")
        ax2.set_xlabel('Time (days)')
        ax2.set_ylabel('Precip. (mm hr$^{-1}$)')
        ax2.axvline(x=i/144.)

        #tcv.go(i)
        #plot_ts(i, precip_bot_ts, precip_top_ts)
        plt.savefig(os.path.join(output_half_domain, 'plot_{}.png'.format(i)))
    return tcv, precip_bot_ts, precip_top_ts


if __name__ == '__main__':
    tcv, precip_bot_ts, precip_top_ts = main()
