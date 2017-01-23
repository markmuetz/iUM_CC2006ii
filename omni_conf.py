from collections import OrderedDict as odict

settings = {
    'ignore_warnings': True,
}

computer_name = open('computer.txt').read().strip()
computers = {
    'zerogravitas': {
        'dirs': {
            'um_output': '/home/markmuetz/um_output/um10.6_runs/20day/',
            'output': '/home/markmuetz/omni_output/iUM_CC2006ii/output',
            'output_cloud_stats': '/home/markmuetz/omni_output/iUM_CC2006ii/output_cloud_stats',
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

expts = ['2Kpdy_cooling', 'no_wind', '16Kpdy_cooling', 'weak_shear', 'strong_shear']
comp = computers['zerogravitas']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/work_{}'.format(expt)
    comp['dirs']['results_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/results_{}'.format(expt)

comp = computers['Z580']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/work_{}'.format(expt)
    comp['dirs']['results_' + expt] = '/home/markmuetz/omni_output/iUM_CC2006ii/results_{}'.format(expt)

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

    surf_base_nodes = ['precip_ts', 'shf_ts', 'lhf_ts', 'evap_ts']
    surf_base_vars = ['precip', 'shf', 'lhf']

    groups['surf_timeseries_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'results_' + expt,
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

    nodes['evap_ts_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['lhf_ts_' + expt],
        'process': 'convert_energy_to_mass_flux',
    }
    nodes['surf_ts_plots_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['precip_ts_' + expt, 'evap_ts_' + expt],
        'process': 'plot_mass_flux_surf_timeseries',
    }

    groups['count_clouds' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output_cloud_stats',
        'batch': 'batch3',
        'nodes': ['count_clouds_plots_w1_qcl0p001_' + expt],
    }
    nodes['count_clouds_plots_w1_qcl0p001_' + expt] = {
        'type': 'from_group',
        'from_group': 'stream1_' + expt,
        'variable': 'w',
        'process': 'count_clouds',
        'process_kwargs': {'w_thresh': 1, 'qcl_thresh': 0.001, 'start_index': 1440, 'end_index': 2000},
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
