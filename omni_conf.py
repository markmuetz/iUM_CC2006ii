from collections import OrderedDict as odict

settings = {
    'ignore_warnings': True,
}

computer_name = open('computer.txt').read().strip()
computers = {
    'zerogravitas': {
        'dirs': {
            'um_output': '/home/markmuetz/um_output/um10.6_runs/20day/',
            'output': '/home/markmuetz/Dropbox/omni_output/iUM_CC2006ii/output',
            'output_cloud_stats': '/home/markmuetz/Dropbox/omni_output/iUM_CC2006ii/output_cloud_stats',
        }
    },
    'Z580': {
        'dirs': {
            'um_output': '/home/markmuetz/um_output/um10.6_runs/20day/',
            'output': '/home/markmuetz/Dropbox/omni_output/iUM_CC2006ii/output',
            'output_cloud_stats': '/home/markmuetz/Dropbox/omni_output/iUM_CC2006ii/output_cloud_stats',
        }
    },
}

expts = ['2Kpdy_cooling', 'no_wind', '16Kpdy_cooling', 'weak_shear', 'strong_shear',
        '2Kpdy_weak_shear', '2Kpdy_strong_shear']
comp = computers['zerogravitas']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/work_{}'.format(expt)
    comp['dirs']['results_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/results_{}'.format(expt)
    comp['dirs']['results_energy_ts' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/results_energy_ts_{}'.format(expt)

comp = computers['Z580']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/work_{}'.format(expt)
    comp['dirs']['results_energy_ts' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/results_energy_ts_{}'.format(expt)

batches = odict(('batch{}'.format(i), {'index': i}) for i in range(4))
groups = odict()
ngroups = odict()
nodes = odict()
nnodes = odict()

for expt in expts:
    groups['stream1_' + expt] = {
            'type': 'init',
            'base_dir': 'um_output',
            'batch': 'batch0',
            'filename_glob': 'iUM_CC2006_{}/work/2000??????????/atmos/atmos.pp1.nc'.format(expt),
            }

    surf_base_nodes = ['precip_ts', 'shf_ts', 'lhf_ts', 'evap_ts', 'pfe_ts']
    surf_base_vars = ['precip', 'shf', 'lhf']

    groups['surf_timeseries_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'results_energy_ts' + expt,
        'batch': 'batch1',
        'nodes': [bn + '_' + expt for bn in surf_base_nodes],
    }

    for bn, bv in zip(surf_base_nodes, surf_base_vars):
	nodes[bn + '_' + expt] = {
	    'type': 'from_group',
	    'from_group': 'stream1_' + expt,
	    'variable': bv,
	    'process': 'domain_mean',
	}

    groups['surf_ts_plots_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output',
        'batch': 'batch2',
        'nodes': ['surf_ts_plots_' + expt],
    }

    groups['surf_energy_ts_plots_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output',
        'batch': 'batch2',
        'nodes': ['surf_energy_ts_plots_' + expt],
    }

    nodes['evap_ts_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['lhf_ts_' + expt],
        'process': 'convert_energy_to_mass_flux',
    }

    nodes['pfe_ts_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['precip_ts_' + expt],
        'process': 'convert_mass_to_energy_flux',
    }

    nodes['surf_ts_plots_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['precip_ts_' + expt, 'evap_ts_' + expt],
        'process': 'plot_mass_flux_surf_timeseries',
    }

    nodes['surf_energy_ts_plots_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['lhf_ts_' + expt, 'shf_ts_' + expt, 'pfe_ts_' + expt],
        'process': 'plot_energy_surf_timeseries',
    }

    cc_nodes = []
    w_threshes = [1, 2, 5, 10]
    qcl_threshes = [0.001, 0.002, 0.003]
    cc_fmt = 'count_clouds_plots_w{}_qcl{}_{}'
    for w_thresh in w_threshes:
        for qcl_thresh in qcl_threshes:
            cc_nodes.append(cc_fmt.format(w_thresh, qcl_thresh, expt))

    groups['count_clouds' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output_cloud_stats',
        'batch': 'batch3',
        'nodes': cc_nodes,
    }
    for w_thresh in w_threshes:
        for qcl_thresh in qcl_threshes:
            nodes[cc_fmt.format(w_thresh, qcl_thresh, expt)] = {
                'type': 'from_group',
                'from_group': 'stream1_' + expt,
                'variable': 'w',
                'process': 'count_clouds',
                'process_kwargs': {'w_thresh': w_thresh, 'qcl_thresh': qcl_thresh, 'start_index': 1440, 'end_index': 2000},
    }


variables = {
    'precip': {
        'section': 4,
        'item': 203,
    },
    'shf': {
        'section': 3,
        'item': 217,
    },
    'lhf': {
        'section': 3,
        'item': 234,
    },
    'w': {
        'section': 0,
        'item': 150,
    },
}
    
process_options = {
}
