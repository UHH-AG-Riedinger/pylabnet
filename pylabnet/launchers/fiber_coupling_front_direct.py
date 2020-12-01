from pylabnet.launchers.launcher import Launcher
from pylabnet.launchers.servers import thorlabs_pm320e
from pylabnet.scripts.fiber_coupling import power_monitor_direct

def main():

    launcher = Launcher(
        script=[power_monitor_direct],
        server_req=[thorlabs_pm320e],
        gui_req=[None],
        params=[None],
        auto_connect=False,
        config='fiber_front'
    )
    launcher.launch()


if __name__ == '__main__':
    main()
