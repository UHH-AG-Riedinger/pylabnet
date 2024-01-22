from pylabnet.network.core.service_base import ServiceBase
from pylabnet.network.core.client_base import ClientBase


class Service(ServiceBase):
    def exposed_EAFGetNow(self):
        return self._module.EAFGetNow()

    def exposed_EAFopen(self):
        return self._module.EAFopen()

    def exposed_EAFclose(self):
        return self._module.EAFclose()

    def exposed_EAFCheck(self, pid):
        return self._module.EAFCheck(pid)

    def exposed_EAFGetID(self, index):
        return self._module.EAFGetID(index)

    def expoed_EAFget_position(self):
        return self._module.EAFget_position()

    def exposed_EAFGetSDKVersion(self):
        return self._module.EAFGetSDKVersion()

    def exposed_EAFmove(self, steps):
        return self._module.EAFmove(steps)

    def exposed_EAFstop(self):
        return self._module.EAFstop()

    def exposed_EAFis_moving(self):
        return self._module.EAFis_moving()

    def exposed_EAFResetPosition(self, steps):
        return self._module.EAFResetPosition(steps)

    def exposed_EAFGetTemp(self):
        return self._module.EAFGetTemp()

    def exposed_EAFset_beep(self, beep):
        return self._module.EAFset_beep(beep)

    def exposed_EAFget_beep(self):
        return self._module.EAFget_beep()

    def exposed_EAFget_backlash(self):
        return self._module.EAFget_backlash()

    def exposed_EAFset_backlash(self, backlash):
        return self._module.EAFset_backlash(backlash)

    def exposed_EAFget_reverse(self):
        return self._module.EAFget_reverse()

    def exposed_EAFset_reverse(self, reverse):
        return self._module.EAFset_reverse(reverse)

    def exposed_EAFstep_range(self):
        return self._module.EAFstep_range()

    def exposed_EAFget_max_step(self):
        return self._module.EAFget_max_step()

    def exposed_EAFSetMaxStep(self, max_step):
        return self._module.EAFSetMaxStep(max_step)


class Client(ClientBase):
    def EAFGetNow(self):
        return self._service.exposed_EAFGetNow()

    def EAFopen(self):
        return self._service.exposed_EAFopen()

    def EAFclose(self):
        return self._service.exposed_EAFclose()

    def EAFCheck(self, pid):
        return self._service.exposed_EAFCheck(pid)

    def EAFGetID(self, index):
        return self._service.exposed_EAFGetID(index)

    def EAFget_position(self):
        return self._service.expoed_EAFget_position()

    def EAFGetSDKVersion(self):
        return self._service.exposed_EAFGetSDKVersion()

    def EAFmove(self, steps):
        return self._service.exposed_EAFmove(steps)

    def EAFstop(self):
        return self._service.exposed_EAFstop()

    def EAFis_moving(self):
        return self._service.exposed_EAFis_moving()

    def EAFResetPosition(self, steps):
        return self._service.exposed_EAFResetPosition(steps)

    def EAFGetTemp(self):
        return self._service.exposed_EAFGetTemp()

    def EAFset_beep(self, beep):
        return self._service.exposed_EAFset_beep(beep)

    def EAFget_beep(self):
        return self._service.exposed_EAFget_beep()

    def EAFget_backlash(self):
        return self._service.exposed_EAFget_backlash()

    def EAFset_backlash(self, backlash):
        return self._service.exposed_EAFset_backlash(backlash)

    def EAFget_reverse(self):
        return self._service.exposed_EAFget_reverse()

    def EAFset_reverse(self, reverse):
        return self._service.exposed_EAFset_reverse(reverse)

    def EAFstep_range(self):
        return self._service.exposed_EAFstep_range()

    def EAFget_max_step(self):
        return self._service.exposed_EAFget_max_step()

    def EAFSetMaxStep(self, max_step):
        return self._service.exposed_EAFSetMaxStep(max_step)
