project('mauna-about')

subdir('po')
subdir('debian')

# install sources
install_subdir('src', install_dir : '/usr/share/mauna/mauna-about')
install_subdir('data', install_dir : '/usr/share/mauna/mauna-about')
install_subdir('ui', install_dir : '/usr/share/mauna/mauna-about')
install_subdir('css', install_dir : '/usr/share/mauna/mauna-about')

# icons
install_data('mauna-hardware-info.svg', install_dir : '/usr/share/icons/hicolor/scalable/apps')
install_data('mauna-about.svg', install_dir : '/usr/share/icons/hicolor/scalable/apps')
install_data('mauna-about-symbolic.svg', install_dir : '/usr/share/icons/hicolor/scalable/apps')

# polkit rule
install_data('top.mauna.pkexec.mauna-about.policy', install_dir : '/usr/share/polkit-1/actions/')

# desktop files
install_data('top.mauna.about.desktop', install_dir : '/usr/share/applications/')
install_data('top.mauna.about-hardware.desktop', install_dir : '/usr/share/applications/')
