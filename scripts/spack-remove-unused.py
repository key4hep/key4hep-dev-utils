# This script will delete unused specs, this can happen when
# a new concretization is done and some specs change. The old ones
# are now invisible for spack and can't be easily uninstalled since
# spack will only see the new ones

# To check before what's going to be uninstall one can do
# spack python -c 'print([x.prefix for x in spack.store.STORE.db.query_local() if not any(x.satisfies(y) for y in spack.environment.active_environment().all_specs_generator())])'

# Usage is
# spack python spack-remove-unused.py

import spack.cmd.uninstall

specs = [x for x in spack.store.STORE.db.query_local() if not any(x.satisfies(y) for y in spack.environment.active_environment().all_specs_generator())]
spack.cmd.uninstall.do_uninstall(specs, True)
