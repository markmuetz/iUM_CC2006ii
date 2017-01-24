# TODO: Figure out how to animate this...
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
    pp1_node = dag.get_node('atmos.pp1.nc', 'stream1_no_wind')

    tcv = TwodCubeViewer(use_prev_settings=False)
    tcv.load(pp1_node.filename(config))
    tcv.add_disp(3)
    tcv.disp()

    precip = tcv._cubes[3].copy()
    precip_bot_ts = precip[:, 128:, :].collapsed(['grid_latitude', 'grid_longitude'], 
                                                 iris.analysis.MEAN)
    precip_top_ts = precip[:, :128, :].collapsed(['grid_latitude', 'grid_longitude'], 
                                                 iris.analysis.MEAN)

    #precip_bot_ts = iris.load('precip_bot_ts.nc')[0]
    #precip_top_ts = iris.load('precip_top_ts.nc')[0]
    calc_dominant_mode_freq(precip_bot_ts)

    #fig = plt.figure()
    #ax1 = fig.add_subplot(121)
    #ax2 = fig.add_subplot(122)

    #ax1.imshow(precip[1440].data, interpolation='nearest', origin='lower',
    #           vmax=vmax, vmin=vmin)
    #ax2.plot(precip_bot_ts.data)
    #ax2.plot(precip_top_ts.data)
    for i in range(1440, 1440+288):
        tcv.go(i)
        plot_ts(i, precip_bot_ts, precip_top_ts)
    return tcv, precip_bot_ts, precip_top_ts


if __name__ == '__main__':
    tcv, precip_bot_ts, precip_top_ts = main()
