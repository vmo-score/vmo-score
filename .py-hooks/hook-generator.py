from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('vmo') + collect_submodules('snakes')
